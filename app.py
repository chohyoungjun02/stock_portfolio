import mimetypes
import os
import re
import secrets

import yfinance as yf
from dotenv import load_dotenv
from flask import Flask, request

from routes.auth import auth_bp
from routes.chart import chart_bp
from routes.compare import compare_bp
from routes.fx import fx_bp
from routes.market import market_bp
from routes.pages import pages_bp
from routes.portfolio import portfolio_bp
from services.users import init_db

load_dotenv()

# Windows 레지스트리에 .js가 text/plain으로 등록된 경우 ES 모듈 로드가 막히므로 강제 지정
mimetypes.add_type('application/javascript', '.js')

# Vercel 서버리스는 /tmp만 쓰기 가능하므로 yfinance 캐시 위치 변경
if os.environ.get('VERCEL'):
    yf.set_tz_cache_location('/tmp/yfinance-cache')


def _load_secret_key(instance_path):
    """SECRET_KEY 환경변수 우선, 없으면 instance/secret_key 파일에 한 번 만들어 계속 사용
    (재시작마다 바뀌면 로그인이 풀리고 저장된 토스 키도 복호화할 수 없음)"""
    if os.environ.get('SECRET_KEY'):
        return os.environ['SECRET_KEY']
    path = os.path.join(instance_path, 'secret_key')
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(secrets.token_urlsafe(48))
    with open(path) as f:
        return f.read().strip()

# 앱인토스 미니앱(토스 앱 웹뷰) 출처: 실서비스·QR 테스트, SDK 3.0.x / 3.1.0+ 도메인
TOSS_MINIAPP_ORIGIN = re.compile(r'^https://[a-z0-9-]+\.(apps|private-apps|web|private-web)\.tossmini\.com$')


def _allow_toss_miniapp(response):
    """미니앱 번들이 /api/를 부를 수 있게 CORS 허용 (조회 API만 있고 쿠키는 쓰지 않음)"""
    origin = request.headers.get('Origin', '')
    if request.path.startswith('/api/') and TOSS_MINIAPP_ORIGIN.match(origin):
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Vary'] = 'Origin'
    return response


def create_app():
    on_vercel = bool(os.environ.get('VERCEL'))
    # Vercel은 /tmp만 쓰기 가능하고 재시작 시 사라지므로,
    # 배포본은 외부 DB(DATABASE_URL)와 고정 SECRET_KEY가 있을 때만 로그인 기능을 켬
    app = Flask(__name__, instance_path='/tmp/instance' if on_vercel else None)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.update(
        SECRET_KEY=_load_secret_key(app.instance_path),
        DB_PATH=os.path.join(app.instance_path, 'app.db'),
        AUTH_ENABLED=not on_vercel or bool(os.environ.get('DATABASE_URL') and os.environ.get('SECRET_KEY')),
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=on_vercel,
    )
    with app.app_context():
        init_db()

    app.register_blueprint(auth_bp)        # 회원가입 · 로그인 · 계좌 연동
    app.register_blueprint(pages_bp)       # 대시보드 화면
    app.register_blueprint(portfolio_bp)   # 보유 종목 API
    app.register_blueprint(fx_bp)          # 환율 API
    app.register_blueprint(chart_bp)       # 일봉 차트 API
    app.register_blueprint(market_bp)      # 시장 현황 · 뉴스 · 경제 일정 API
    app.register_blueprint(compare_bp)     # 종목 비교 API
    app.after_request(_allow_toss_miniapp)
    return app


app = create_app()

if __name__ == '__main__':
    # 개발 서버 실행
    app.run(debug=True, port=5000)

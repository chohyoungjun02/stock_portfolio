import mimetypes
import os
import secrets

import yfinance as yf
from dotenv import load_dotenv
from flask import Flask

from routes.auth import auth_bp
from routes.chart import chart_bp
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


def create_app():
    on_vercel = bool(os.environ.get('VERCEL'))
    # Vercel은 /tmp만 쓰기 가능 (재시작 시 사라지므로 배포본에서는 로그인 기능을 끔)
    app = Flask(__name__, instance_path='/tmp/instance' if on_vercel else None)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.update(
        SECRET_KEY=_load_secret_key(app.instance_path),
        DB_PATH=os.path.join(app.instance_path, 'app.db'),
        AUTH_ENABLED=not on_vercel,
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
    app.register_blueprint(market_bp)      # 시장 현황 API
    return app


app = create_app()

if __name__ == '__main__':
    # 개발 서버 실행
    app.run(debug=True, port=5000)

import mimetypes

from dotenv import load_dotenv
from flask import Flask

from routes.chart import chart_bp
from routes.fx import fx_bp
from routes.pages import pages_bp
from routes.portfolio import portfolio_bp

load_dotenv()

# Windows 레지스트리에 .js가 text/plain으로 등록된 경우 ES 모듈 로드가 막히므로 강제 지정
mimetypes.add_type('application/javascript', '.js')


def create_app():
    app = Flask(__name__)
    app.register_blueprint(pages_bp)       # 대시보드 화면
    app.register_blueprint(portfolio_bp)   # 보유 종목 API
    app.register_blueprint(fx_bp)          # 환율 API
    app.register_blueprint(chart_bp)       # 일봉 차트 API
    return app


app = create_app()

if __name__ == '__main__':
    # 개발 서버 실행
    app.run(debug=True, port=5000)

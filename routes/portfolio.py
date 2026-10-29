"""보유 종목 API"""
from flask import Blueprint, current_app, jsonify, session

from holding import get_my_holdings  # 보유 종목 조회 함수
from services.portfolio import normalize_holdings
from services.users import get_toss_keys

portfolio_bp = Blueprint('portfolio', __name__)


# 보유 종목 및 평가 데이터 조회 엔드포인트 (5초 폴링용)
@portfolio_bp.route('/api/holdings')
@portfolio_bp.route('/api/dashboard-data')
def dashboard_data():
    # action: 화면에서 로그인/연동 버튼을 보여줄지 결정
    if not current_app.config['AUTH_ENABLED']:
        return jsonify({"status": "error", "message": "이 사이트에서는 계좌 연동을 지원하지 않아요."}), 403
    if 'user_id' not in session:
        return jsonify({"status": "error", "action": "login",
                        "message": "로그인하고 계좌를 연동하면 보유 주식이 보여요."}), 401
    keys = get_toss_keys(session['user_id'])
    if not keys:
        return jsonify({"status": "error", "action": "link",
                        "message": "토스증권 계좌를 연동하면 보유 주식이 보여요."}), 400

    try:
        # 로그인한 회원이 연동한 키로 보유 종목 조회
        holdings_data = get_my_holdings(keys['client_id'], keys['client_secret'], keys['account_no'])
        if holdings_data:
            summary, holdings = normalize_holdings(holdings_data)
            return jsonify({
                "status": "success",
                "summary": summary,
                "holdings": holdings,
                "raw": holdings_data  # 필드 매핑 확인용 원본 응답
            })
        else:
            return jsonify({
                "status": "error",
                "message": "보유 종목 데이터를 불러올 수 없습니다."
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

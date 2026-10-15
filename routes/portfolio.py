"""보유 종목 API"""
from flask import Blueprint, jsonify

from holding import get_my_holdings  # 보유 종목 조회 함수
from services.portfolio import normalize_holdings

portfolio_bp = Blueprint('portfolio', __name__)


# 보유 종목 및 평가 데이터 조회 엔드포인트 (5초 폴링용)
@portfolio_bp.route('/api/holdings')
@portfolio_bp.route('/api/dashboard-data')
def dashboard_data():
    try:
        # holding.py 내부의 계좌 보유 종목 조회 호출
        holdings_data = get_my_holdings()
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

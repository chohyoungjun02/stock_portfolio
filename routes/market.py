"""시장 현황 API"""
from flask import Blueprint, jsonify

from services.market import get_market_overview

market_bp = Blueprint('market', __name__)


# 주요 지수 시세 + 시장 현황 키워드 (5분 캐시)
@market_bp.route('/api/market')
def market_overview():
    try:
        return jsonify({"status": "success", **get_market_overview()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

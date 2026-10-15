"""환율 API"""
from flask import Blueprint, jsonify

from services.fx import get_usd_krw

fx_bp = Blueprint('fx', __name__)


# 달러/원 환율 조회 엔드포인트 (60초 캐시)
@fx_bp.route('/api/fx')
def get_fx_rate():
    try:
        rate, stale = get_usd_krw()
        result = {"status": "success", "usd_krw": rate}
        if stale:
            result["stale"] = True
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

"""일봉 차트 API"""
from flask import Blueprint, jsonify, request

from services.chart import build_chart_payload

chart_bp = Blueprint('chart', __name__)


# 일봉 캔들 + 지표 + 신호 조회 엔드포인트
@chart_bp.route('/api/candles')
def get_candles():
    symbol = request.args.get('symbol', 'QLD').upper().strip()
    try:
        return jsonify({"status": "success", **build_chart_payload(symbol)})
    except LookupError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

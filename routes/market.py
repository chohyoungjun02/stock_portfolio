"""시장 현황 · 뉴스 API"""
from flask import Blueprint, jsonify, request

from services.market import get_market_overview
from services.news import NewsConfigError, get_stock_news, search_news

market_bp = Blueprint('market', __name__)


# 주요 지수 시세 + 시장 현황 키워드 (5분 캐시)
@market_bp.route('/api/market')
def market_overview():
    try:
        return jsonify({"status": "success", **get_market_overview()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 주요 단일 종목 뉴스, q가 있으면 그 종목 뉴스 검색 (10분 캐시)
@market_bp.route('/api/news')
def stock_news():
    q = request.args.get('q', '').strip()
    if len(q) > 30:
        return jsonify({"status": "error", "message": "검색어는 30자 이내로 입력해 주세요."}), 400
    try:
        if q:
            return jsonify({"status": "success",
                            "stocks": [{"symbol": "", "name": q, "items": search_news(q, limit=10)}]})
        return jsonify({"status": "success", "stocks": get_stock_news()})
    except NewsConfigError as e:
        return jsonify({"status": "error", "message": str(e)}), 503
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

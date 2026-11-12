"""종목 비교 API"""
from flask import Blueprint, jsonify, request

from services.compare import compare, parse_request

compare_bp = Blueprint('compare', __name__)


# 두 종목에 같은 금액을 같은 기간 투자했을 때의 수익
@compare_bp.route('/api/compare')
def compare_stocks():
    args = request.args
    try:
        params = parse_request(args.get('a', ''), args.get('b', ''), args.get('amount'),
                               args.get('start'), args.get('end'))
        return jsonify({"status": "success", **compare(*params)})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except LookupError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

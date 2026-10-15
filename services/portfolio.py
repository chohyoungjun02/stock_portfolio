"""보유 종목 조회 결과를 대시보드 형식으로 정규화"""


def _pick(d, *keys):
    """여러 후보 키 중 처음으로 값이 있는 것을 반환 (값이 dict면 amount/value 추출)"""
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            v = d[k]
            if isinstance(v, dict):
                v = v.get('amount', v.get('value', v.get('krw')))
            return v
    return None

def _find_list(obj):
    """토스 응답에서 보유 종목 리스트를 찾아 반환"""
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in ('holdings', 'items', 'positions', 'stocks', 'list'):
            if isinstance(obj.get(k), list):
                return obj[k]
        for k in ('data', 'result', 'body'):
            if k in obj:
                found = _find_list(obj[k])
                if found is not None:
                    return found
    return None

def _num(v):
    """문자열/None 값을 float로 변환 (변환 불가 시 None)"""
    if v is None:
        return None
    try:
        return float(str(v).replace(',', '').replace('%', ''))
    except ValueError:
        return None

def normalize_holdings(raw):
    """토스 API 원본 응답을 index2.html이 기대하는 구조로 변환"""
    items = _find_list(raw) or []
    holdings = []
    for it in items:
        qty = _num(_pick(it, 'quantity', 'qty', 'holdingQuantity', 'balanceQuantity'))
        avg = _num(_pick(it, 'avg_buy_price', 'averagePrice', 'avgPrice', 'purchasePrice', 'averagePurchasePrice'))
        cur = _num(_pick(it, 'current_price', 'currentPrice', 'price', 'lastPrice', 'marketPrice'))
        eval_amt = _num(_pick(it, 'eval_amount', 'evaluationAmount', 'marketValue', 'evaluatedAmount'))
        pnl = _num(_pick(it, 'pnl', 'profitLoss', 'profitAmount', 'unrealizedPnl', 'evaluationProfit'))
        rate = _num(_pick(it, 'pnl_rate', 'profitRate', 'profitLossRate', 'returnRate', 'yield'))

        # 응답에 없는 값은 가격·수량으로 직접 계산
        cost = avg * qty if avg is not None and qty is not None else None
        if eval_amt is None and cur is not None and qty is not None:
            eval_amt = cur * qty
        if pnl is None and eval_amt is not None and cost is not None:
            pnl = eval_amt - cost
        # 수익률은 매입단가·현재가로 계산한 값을 우선 사용 (응답 값이 없거나 0, 비율(0.05) 형태여도 정확)
        if avg and cur is not None:
            rate = (cur - avg) / avg * 100
        elif cost and pnl is not None:
            rate = pnl / cost * 100

        holdings.append({
            "name": _pick(it, 'name', 'stockName', 'productName', 'securityName'),
            "symbol": _pick(it, 'symbol', 'ticker', 'code', 'stockCode', 'productCode'),
            "quantity": qty,
            "avg_buy_price": avg,
            "current_price": cur,
            "eval_amount": eval_amt,
            "pnl": pnl,
            "pnl_rate": round(rate, 2) if rate is not None else None,
        })

    total_eval = sum(h["eval_amount"] or 0 for h in holdings)
    total_buy = sum((h["avg_buy_price"] or 0) * (h["quantity"] or 0) for h in holdings)
    total_pnl = sum(h["pnl"] or 0 for h in holdings) or (total_eval - total_buy)
    # 매입금액을 알 수 없으면 평가금액 - 손익으로 역산
    cost_basis = total_buy or (total_eval - total_pnl)
    summary = {
        "total_asset": total_eval,
        "total_buy": cost_basis,
        "deposit_krw": 0,
        "total_pnl": total_pnl,
        "total_pnl_rate": round(total_pnl / cost_basis * 100, 2) if cost_basis else 0,
    }
    return summary, holdings

"""두 종목에 같은 금액을 투자했을 때의 수익 비교"""
from datetime import date

import pandas as pd
import yfinance as yf

MAX_AMOUNT = 1_000_000_000_000  # 1조 원


def parse_request(a, b, amount, start, end):
    """요청값 검증 → (a, b, amount, start, end), 잘못되면 ValueError"""
    a, b = a.strip().upper(), b.strip().upper()
    if not a or not b:
        raise ValueError("비교할 종목 두 개를 입력해 주세요.")
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("투자 금액을 숫자로 입력해 주세요.")
    if not 0 < amount <= MAX_AMOUNT:
        raise ValueError("투자 금액은 0원보다 크고 1조 원 이하로 입력해 주세요.")
    try:
        start, end = date.fromisoformat(start), date.fromisoformat(end)
    except (TypeError, ValueError):
        raise ValueError("기간을 YYYY-MM-DD 형식으로 입력해 주세요.")
    if start >= end:
        raise ValueError("시작일은 종료일보다 앞이어야 해요.")
    return a, b, amount, start, min(end, date.today())


def summarize(close, amount):
    """종가 Series → 투자 결과 (첫 거래일 종가에 매수, 마지막 거래일 종가로 평가)"""
    close = close.dropna()
    first, last = float(close.iloc[0]), float(close.iloc[-1])
    value = close / first * amount
    return {
        "start_date": close.index[0].strftime('%Y-%m-%d'),
        "end_date": close.index[-1].strftime('%Y-%m-%d'),
        "start_price": round(first, 4),
        "end_price": round(last, 4),
        "return_pct": round((last / first - 1) * 100, 2),
        "final_value": round(float(value.iloc[-1])),
        "profit": round(float(value.iloc[-1]) - amount),
        "series": [{"time": t.strftime('%Y-%m-%d'), "value": round(float(v))} for t, v in value.items()],
    }


def compare(a, b, amount, start, end):
    # yfinance end는 그날을 포함하지 않으므로 하루 뒤까지 요청
    close = yf.download([a, b], start=start, end=end + pd.Timedelta(days=1),
                        progress=False, auto_adjust=True)['Close']
    result = []
    for sym in (a, b):
        if sym not in close or close[sym].dropna().empty:
            raise LookupError(f"{sym}의 해당 기간 시세를 찾을 수 없어요.")
        result.append({"symbol": sym, **summarize(close[sym], amount)})
    return {"amount": amount, "stocks": result}

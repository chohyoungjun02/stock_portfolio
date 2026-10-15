"""달러/원 환율 조회 (60초 캐시)"""
import time

import yfinance as yf

_fx_cache = {"rate": None, "time": 0.0}
CACHE_SECONDS = 60


def get_usd_krw():
    """(환율, 지연 여부) 반환. 조회 실패 시 마지막 환율을 지연 표시와 함께 반환, 없으면 예외 발생"""
    now = time.time()
    if _fx_cache["rate"] and now - _fx_cache["time"] < CACHE_SECONDS:
        return _fx_cache["rate"], False
    try:
        df = yf.Ticker('KRW=X').history(period='5d', interval='1d')
        if df.empty:
            raise ValueError("환율 데이터를 찾을 수 없습니다.")
        rate = round(float(df['Close'].iloc[-1]), 2)
        _fx_cache.update(rate=rate, time=now)
        return rate, False
    except Exception:
        # 조회 실패 시 마지막으로 받은 환율이라도 반환
        if _fx_cache["rate"]:
            return _fx_cache["rate"], True
        raise

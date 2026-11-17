"""모의투자용 현재가 조회 (원화 환산, 60초 캐시)"""
import re
import time

import yfinance as yf

from services.fx import get_usd_krw

CACHE_SECONDS = 60
MAX_SYMBOLS = 30
_cache = {}  # 심볼 → (시각, 현지 통화 가격)

# 국내(.KS/.KQ)는 원화, 접미사 없는 미국 종목은 달러 (BRK-B처럼 '-' 허용)
_KR_RE = re.compile(r'^[0-9A-Z]{6}\.(KS|KQ)$')
_US_RE = re.compile(r'^[A-Z][A-Z0-9-]{0,9}$')


def parse_symbols(raw):
    """'NVDA,005930.KS' → ['NVDA', '005930.KS'], 지원하지 않는 형식이면 ValueError"""
    symbols = list(dict.fromkeys(s.strip().upper() for s in (raw or '').split(',') if s.strip()))
    if not symbols:
        raise ValueError("조회할 종목을 입력해 주세요.")
    if len(symbols) > MAX_SYMBOLS:
        raise ValueError(f"한 번에 {MAX_SYMBOLS}개 종목까지 조회할 수 있어요.")
    for s in symbols:
        if not (_KR_RE.match(s) or _US_RE.match(s)):
            raise ValueError(f"{s}: 모의투자는 국내·미국 종목만 지원해요.")
    return symbols


def is_krw(symbol):
    return bool(_KR_RE.match(symbol))


def _fetch_prices(symbols):
    close = yf.download(symbols, period='5d', interval='1d', progress=False, auto_adjust=False)['Close']
    prices = {}
    for s in symbols:
        if s in close:
            series = close[s].dropna()
            if not series.empty:
                prices[s] = float(series.iloc[-1])
    return prices


def get_quotes(symbols):
    """{심볼: {"price", "currency", "price_krw"}}, 시세가 없는 종목은 빠짐 + 적용 환율"""
    now = time.time()
    missing = [s for s in symbols if s not in _cache or now - _cache[s][0] >= CACHE_SECONDS]
    if missing:
        for s, p in _fetch_prices(missing).items():
            _cache[s] = (now, p)
    usd_krw = get_usd_krw()[0] if any(not is_krw(s) for s in symbols) else None
    quotes = {}
    for s in symbols:
        if s not in _cache:
            continue
        price = _cache[s][1]
        krw = is_krw(s)
        quotes[s] = {"price": round(price, 4), "currency": "KRW" if krw else "USD",
                     "price_krw": round(price if krw else price * usd_krw, 2)}
    return {"quotes": quotes, "usd_krw": usd_krw}

"""주요 지수·자산 시세와 시장 현황 키워드 (5분 캐시)"""
import time

import pandas as pd
import yfinance as yf

# 표시 순서대로
SYMBOLS = {
    '^GSPC': 'S&P 500',
    '^IXIC': '나스닥',
    '^DJI': '다우',
    '^SOX': '필라델피아 반도체',
    '^KS11': '코스피',
    '^KQ11': '코스닥',
    '^VIX': 'VIX 공포지수',
    '^TNX': '미국 10년물 금리',
    'KRW=X': '원/달러 환율',
    'GC=F': '금',
    'CL=F': 'WTI 유가',
    'BTC-USD': '비트코인',
}

_cache = {"data": None, "time": 0.0}
CACHE_SECONDS = 300


def fetch_quotes():
    """{심볼: {"price", "change_pct", "change"}} - 최근 두 거래일 종가 기준"""
    close = yf.download(list(SYMBOLS), period='7d', interval='1d', progress=False)['Close']
    quotes = {}
    for sym in SYMBOLS:
        if sym not in close:
            continue
        s = close[sym].dropna()  # 국가별 휴장일이 달라 종목별로 결측 제거
        if len(s) < 2:
            continue
        last, prev = float(s.iloc[-1]), float(s.iloc[-2])
        quotes[sym] = {"price": round(last, 2), "change": round(last - prev, 4),
                       "change_pct": round((last / prev - 1) * 100, 2)}
    return quotes


def _kw(text, tone, desc):
    return {"text": text, "tone": tone, "desc": desc}


def build_keywords(q):
    """시세 dict로 시장 현황 키워드 목록 생성 (tone: up / down / neutral / warn)"""
    pct = lambda s: q[s]["change_pct"] if s in q else None
    kws = []

    us = [p for p in (pct('^GSPC'), pct('^IXIC')) if p is not None]
    if us:
        avg = sum(us) / len(us)
        if avg >= 0.5:
            kws.append(_kw("미국 증시 강세", "up", f"S&P 500·나스닥 평균 {avg:+.2f}%"))
        elif avg <= -0.5:
            kws.append(_kw("미국 증시 약세", "down", f"S&P 500·나스닥 평균 {avg:+.2f}%"))
        else:
            kws.append(_kw("미국 증시 보합", "neutral", f"S&P 500·나스닥 평균 {avg:+.2f}%"))

    sox = pct('^SOX')
    if sox is not None and abs(sox) >= 1.5:
        kws.append(_kw("반도체 랠리" if sox > 0 else "반도체 약세", "up" if sox > 0 else "down",
                       f"필라델피아 반도체 지수 {sox:+.2f}%"))

    kospi = pct('^KS11')
    if kospi is not None:
        if kospi >= 0.5:
            kws.append(_kw("국내 증시 상승", "up", f"코스피 {kospi:+.2f}%"))
        elif kospi <= -0.5:
            kws.append(_kw("국내 증시 하락", "down", f"코스피 {kospi:+.2f}%"))

    if '^VIX' in q:
        vix, vix_chg = q['^VIX']["price"], q['^VIX']["change_pct"]
        if vix >= 30:
            kws.append(_kw("공포 확산", "warn", f"VIX {vix:.1f} (30 이상)"))
        elif vix >= 20:
            kws.append(_kw("변동성 경계", "warn", f"VIX {vix:.1f} (20 이상)"))
        elif vix < 15:
            kws.append(_kw("시장 안정", "neutral", f"VIX {vix:.1f} (15 미만)"))
        if vix_chg >= 10:
            kws.append(_kw("변동성 급등", "warn", f"VIX 하루 {vix_chg:+.1f}%"))

    nasdaq = pct('^IXIC')
    if nasdaq is not None and '^VIX' in q:
        vix_chg = q['^VIX']["change_pct"]
        if nasdaq > 0 and vix_chg < 0:
            kws.append(_kw("위험 선호 (Risk-on)", "up", "나스닥 상승 + VIX 하락"))
        elif nasdaq < 0 and vix_chg > 0:
            kws.append(_kw("위험 회피 (Risk-off)", "down", "나스닥 하락 + VIX 상승"))

    if '^TNX' in q:
        bp = q['^TNX']["change"] * 100  # ^TNX는 금리(%) 값이라 차이 × 100 = bp
        if bp >= 5:
            kws.append(_kw("금리 상승 부담", "warn", f"미 10년물 {q['^TNX']['price']:.2f}% ({bp:+.0f}bp)"))
        elif bp <= -5:
            kws.append(_kw("금리 하락", "neutral", f"미 10년물 {q['^TNX']['price']:.2f}% ({bp:+.0f}bp)"))

    if 'KRW=X' in q:
        krw, krw_chg = q['KRW=X']["price"], q['KRW=X']["change_pct"]
        if krw >= 1400:
            kws.append(_kw("고환율", "warn", f"원/달러 {krw:,.0f}원"))
        if krw_chg >= 0.5:
            kws.append(_kw("원화 약세", "down", f"원/달러 {krw_chg:+.2f}%"))
        elif krw_chg <= -0.5:
            kws.append(_kw("원화 강세", "up", f"원/달러 {krw_chg:+.2f}%"))

    gold = pct('GC=F')
    if gold is not None and gold >= 1:
        kws.append(_kw("안전자산 선호", "warn", f"금 {gold:+.2f}%"))

    oil = pct('CL=F')
    if oil is not None and abs(oil) >= 2:
        kws.append(_kw("유가 급등" if oil > 0 else "유가 급락", "warn" if oil > 0 else "neutral", f"WTI {oil:+.2f}%"))

    btc = pct('BTC-USD')
    if btc is not None and abs(btc) >= 3:
        kws.append(_kw("코인 강세" if btc > 0 else "코인 약세", "up" if btc > 0 else "down", f"비트코인 {btc:+.2f}%"))

    return kws


def get_market_overview():
    now = time.time()
    if _cache["data"] and now - _cache["time"] < CACHE_SECONDS:
        return _cache["data"]
    quotes = fetch_quotes()
    if not quotes:
        raise LookupError("시장 시세를 불러오지 못했습니다.")
    data = {
        "indices": [{"symbol": s, "name": SYMBOLS[s], **quotes[s]} for s in SYMBOLS if s in quotes],
        "keywords": build_keywords(quotes),
        "as_of": pd.Timestamp.now(tz='Asia/Seoul').strftime('%Y-%m-%d %H:%M'),
    }
    _cache.update(data=data, time=now)
    return data

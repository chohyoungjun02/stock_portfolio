"""경제 일정: FOMC 금리 결정일 + 주요 종목 실적 발표일 (6시간 캐시)"""
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

import yfinance as yf

# 연준 발표 일정의 결정일(이틀 회의의 둘째 날, 미국 동부 14:00 = 한국 다음 날 새벽)
# shortcut: 2026년 일정만 직접 입력, 연준이 2027년 일정을 발표하면 추가
FOMC_DATES = ['2026-01-28', '2026-03-18', '2026-04-29', '2026-06-17',
              '2026-07-29', '2026-09-16', '2026-10-28', '2026-12-09']

# 실적 발표일을 보여줄 종목 (티커: 한글 이름)
EARNINGS_STOCKS = {
    'NVDA': '엔비디아', 'TSLA': '테슬라', 'AAPL': '애플', 'MSFT': '마이크로소프트',
    'GOOGL': '구글', 'AMZN': '아마존', 'META': '메타', 'AVGO': '브로드컴', 'AMD': 'AMD',
    'NFLX': '넷플릭스', 'ORCL': '오라클', 'MU': '마이크론', 'PLTR': '팔란티어', 'TSM': 'TSMC',
    'COST': '코스트코', 'WMT': '월마트', 'JPM': 'JP모건',
    '005930.KS': '삼성전자', '000660.KS': 'SK하이닉스',
}

DAYS_AHEAD = 60
CACHE_SECONDS = 6 * 3600
_cache = {"data": None, "time": 0.0}


def _earnings_date(symbol):
    try:
        dates = yf.Ticker(symbol).calendar.get('Earnings Date') or []
        return dates[0] if dates else None
    except Exception as e:
        print(f"[calendar] {symbol} 실적 발표일 조회 실패: {e}")
        return None


def build_events(earnings, today, days=DAYS_AHEAD):
    """{티커: 발표일} → 오늘부터 days일 안의 일정 목록 (날짜순)"""
    until = today + timedelta(days=days)
    events = [{"date": d, "type": "fomc", "title": "FOMC 금리 결정",
               "desc": "미국 동부 14:00 발표 (한국 다음 날 새벽)"}
              for d in FOMC_DATES if today <= date.fromisoformat(d) <= until]
    events += [{"date": d.isoformat(), "type": "earnings", "title": f"{EARNINGS_STOCKS[sym]} 실적 발표",
                "desc": sym, "symbol": sym}
               for sym, d in earnings.items() if d and today <= d <= until]
    return sorted(events, key=lambda e: (e["date"], e["type"] != "fomc", e["title"]))


def get_calendar():
    now = time.time()
    if _cache["data"] is not None and now - _cache["time"] < CACHE_SECONDS:
        return _cache["data"]
    with ThreadPoolExecutor(max_workers=8) as pool:
        dates = dict(zip(EARNINGS_STOCKS, pool.map(_earnings_date, EARNINGS_STOCKS)))
    data = build_events(dates, date.today())
    if any(dates.values()):  # 실적 조회가 전부 실패한 결과는 캐시하지 않음
        _cache.update(data=data, time=now)
    return data

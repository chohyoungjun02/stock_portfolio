"""주요 단일 종목 뉴스 + 종목 뉴스 검색 (네이버 검색 API, 10분 캐시)"""
import html
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

import requests

# 표시 순서대로 (티커: 검색에 쓰는 한글 이름)
STOCKS = {
    'NVDA': '엔비디아',
    'TSLA': '테슬라',
    'AAPL': '애플',
    'MSFT': '마이크로소프트',
    'GOOGL': '구글',
    'AMZN': '아마존',
    'META': '메타',
    '005930.KS': '삼성전자',
    '000660.KS': 'SK하이닉스',
}

PER_STOCK = 5
CACHE_SECONDS = 600
API_URL = "https://naverapihub.apigw.ntruss.com/search/v1/news"  # 2026년 NAVER API HUB로 이관된 주소
_cache = {}  # (검색어, 개수) → (시각, 기사 목록)
_TAG_RE = re.compile(r'<[^>]+>')


class NewsConfigError(Exception):
    pass


def _clean(text):
    # 네이버는 검색어를 <b>로 감싸고 HTML 엔티티로 보냄
    return html.unescape(_TAG_RE.sub('', text or '')).strip()


def parse_items(items, limit=PER_STOCK):
    """네이버 응답 items → [{"title", "source", "link", "published"}] (최신순)"""
    result = []
    for it in items:
        try:
            published = parsedate_to_datetime(it.get('pubDate')).timestamp()
        except (TypeError, ValueError):
            published = 0
        link = it.get('originallink') or it.get('link')
        result.append({"title": _clean(it.get('title')),
                       "source": urlparse(link or '').netloc.removeprefix('www.'),  # 언론사명 필드가 없어 도메인 표시
                       "link": link, "published": published})
    result.sort(key=lambda x: x["published"], reverse=True)
    return result[:limit]


def search_news(query, limit=PER_STOCK):
    """'{query} 주가' 최신 뉴스 (검색어별 10분 캐시)"""
    client_id, secret = os.environ.get('NAVER_CLIENT_ID'), os.environ.get('NAVER_CLIENT_SECRET')
    if not client_id or not secret:
        raise NewsConfigError("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수를 설정해 주세요.")
    now = time.time()
    cached = _cache.get((query, limit))
    if cached and now - cached[0] < CACHE_SECONDS:
        return cached[1]
    res = requests.get(API_URL, params={"query": f"{query} 주가", "display": limit, "sort": "date"},
                       headers={"X-NCP-APIGW-API-KEY-ID": client_id, "X-NCP-APIGW-API-KEY": secret}, timeout=8)
    res.raise_for_status()
    items = parse_items(res.json().get('items', []), limit)
    if len(_cache) > 500:  # 검색어가 끝없이 쌓이지 않도록
        _cache.clear()
    _cache[(query, limit)] = (now, items)
    return items


def _safe_search(name):
    try:
        return search_news(name)
    except NewsConfigError:
        raise
    except Exception as e:
        print(f"[news] {name} 뉴스 조회 실패: {e}")
        return []  # 한 종목 실패가 전체를 막지 않도록


def get_stock_news():
    """주요 종목별 최신 뉴스"""
    with ThreadPoolExecutor(max_workers=len(STOCKS)) as pool:
        results = list(pool.map(_safe_search, STOCKS.values()))
    return [{"symbol": sym, "name": name, "items": items}
            for (sym, name), items in zip(STOCKS.items(), results)]

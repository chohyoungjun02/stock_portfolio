"""뉴스 파싱 테스트 (네트워크 없이 실행: python tests/test_news_parse.py)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.news import NewsConfigError, parse_items, search_news  # noqa: E402

ITEMS = [
    {"title": "옛날 기사", "originallink": "https://www.hankyung.com/a", "link": "https://n.news.naver.com/a",
     "pubDate": "Mon, 09 Nov 2026 10:00:00 +0900"},
    {"title": "<b>엔비디아</b> 급등 &quot;AI&quot; &amp; 반도체", "originallink": "", "link": "https://n.news.naver.com/b",
     "pubDate": "Wed, 11 Nov 2026 10:00:00 +0900"},
    {"title": "날짜 없음", "originallink": "https://etnews.com/c"},
]

items = parse_items(ITEMS, limit=2)
# 최신순 정렬, <b> 태그·HTML 엔티티 제거, 원문 링크 없으면 네이버 링크
assert [i["title"] for i in items] == ['엔비디아 급등 "AI" & 반도체', "옛날 기사"], items
assert items[0]["link"] == "https://n.news.naver.com/b" and items[0]["source"] == "n.news.naver.com"
assert items[1]["source"] == "hankyung.com"
assert parse_items(ITEMS)[-1] == {"title": "날짜 없음", "source": "etnews.com", "link": "https://etnews.com/c", "published": 0}

# 키가 없으면 설정 오류
os.environ.pop('NAVER_CLIENT_ID', None)
try:
    search_news("엔비디아")
    raise AssertionError("키 없이 호출됨")
except NewsConfigError:
    pass
print("news parse tests OK")

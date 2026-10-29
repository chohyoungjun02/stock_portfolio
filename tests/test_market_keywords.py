"""시장 키워드 규칙 테스트 (네트워크 없이 실행: python tests/test_market_keywords.py)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.market import build_keywords  # noqa: E402


def q(price, change_pct, change=0.0):
    return {"price": price, "change_pct": change_pct, "change": change}


def texts(quotes):
    return [k["text"] for k in build_keywords(quotes)]


# 강세장: 미국 상승 + VIX 하락 + 반도체 급등 + 원화 강세
bull = texts({'^GSPC': q(6000, 1.2), '^IXIC': q(20000, 1.8), '^SOX': q(5000, 3.1),
              '^VIX': q(13.5, -8), 'KRW=X': q(1340, -0.7)})
assert bull == ["미국 증시 강세", "반도체 랠리", "시장 안정", "위험 선호 (Risk-on)", "원화 강세"], bull

# 약세장: 미국 하락 + VIX 급등 + 금리 급등 + 고환율 + 금 상승
bear = texts({'^GSPC': q(5500, -1.5), '^IXIC': q(18000, -2.4), '^VIX': q(31, 25),
              '^TNX': q(4.6, 2.0, 0.08), 'KRW=X': q(1420, 0.8), 'GC=F': q(2700, 1.4)})
assert bear == ["미국 증시 약세", "공포 확산", "변동성 급등", "위험 회피 (Risk-off)",
                "금리 상승 부담", "고환율", "원화 약세", "안전자산 선호"], bear

# 보합 + 데이터 일부 누락에도 오류 없음
assert texts({'^GSPC': q(6000, 0.1)}) == ["미국 증시 보합"]
assert texts({}) == []

print("market keyword tests OK")

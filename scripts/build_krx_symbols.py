"""KRX(KIND) 상장 법인 목록으로 한글 종목명 → 야후 티커 파일 생성
실행: python scripts/build_krx_symbols.py  (신규 상장·상장폐지 반영하려면 가끔 다시 실행)"""
import io
import json
import os

import pandas as pd
import requests

URL = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&marketType={}"
MARKETS = {"stockMkt": ".KS", "kosdaqMkt": ".KQ"}  # 코스피 / 코스닥 (야후 티커 접미사)
OUT = os.path.join(os.path.dirname(__file__), "..", "static", "data", "krx_symbols.json")


def main():
    symbols = {}
    for market, suffix in MARKETS.items():
        res = requests.get(URL.format(market), timeout=30)
        res.raise_for_status()
        df = pd.read_html(io.StringIO(res.content.decode("euc-kr")), converters={"종목코드": str})[0]
        for name, code in zip(df["회사명"], df["종목코드"]):
            symbols[str(name).strip()] = f"{code.zfill(6)}{suffix}"
    assert len(symbols) > 2000, f"종목 수가 너무 적어요: {len(symbols)}"  # 다운로드 형식이 바뀐 경우 덮어쓰기 방지
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(symbols, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    print(f"{len(symbols)}개 종목 저장 → {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()

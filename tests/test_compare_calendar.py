"""종목 비교 계산·입력 검증, 경제 일정 정리 테스트 (네트워크 없이 실행: python tests/test_compare_calendar.py)"""
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.compare import parse_request, summarize  # noqa: E402
from services.economic_calendar import build_events  # noqa: E402

# 100 → (휴장 NaN) → 150: 100만 원이 150만 원, 수익 50만 원
close = pd.Series([100.0, np.nan, 120.0, 150.0], index=pd.to_datetime(['2026-01-02', '2026-01-05', '2026-01-06', '2026-01-07']))
r = summarize(close, 1_000_000)
assert (r["return_pct"], r["final_value"], r["profit"]) == (50.0, 1_500_000, 500_000), r
assert r["start_date"] == '2026-01-02' and len(r["series"]) == 3 and r["series"][1] == {"time": '2026-01-06', "value": 1_200_000}

# 하락: 손실은 음수
r = summarize(pd.Series([200.0, 150.0], index=pd.to_datetime(['2026-01-02', '2026-01-05'])), 1_000_000)
assert (r["return_pct"], r["profit"]) == (-25.0, -250_000), r

# 입력 검증
assert parse_request(' nvda ', 'tsla', '1000000', '2026-01-01', '2026-06-01')[:3] == ('NVDA', 'TSLA', 1_000_000.0)
for bad in [('', 'TSLA', '100', '2026-01-01', '2026-02-01'), ('A', 'B', '0', '2026-01-01', '2026-02-01'),
            ('A', 'B', 'abc', '2026-01-01', '2026-02-01'), ('A', 'B', '100', '2026-03-01', '2026-02-01'),
            ('A', 'B', '100', '2026/01/01', '2026-02-01'), ('A', 'B', '1e13', '2026-01-01', '2026-02-01')]:
    try:
        parse_request(*bad)
        raise AssertionError(f"통과하면 안 됨: {bad}")
    except ValueError:
        pass

# 경제 일정: 기간 안의 FOMC·실적만, 날짜순, 같은 날이면 FOMC 먼저
events = build_events({'NVDA': date(2026, 12, 9), 'AAPL': date(2027, 3, 1), 'TSLA': None}, date(2026, 11, 12))
assert [(e["date"], e["type"]) for e in events] == [('2026-12-09', 'fomc'), ('2026-12-09', 'earnings')], events
assert events[1]["title"] == '엔비디아 실적 발표'
print("compare & calendar tests OK")

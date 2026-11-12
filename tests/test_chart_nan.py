"""장 시작 전 오늘 행(가격 NaN)이 와도 차트 응답이 올바른 JSON인지 테스트
(네트워크 없이 실행: python tests/test_chart_nan.py)"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import services.chart  # noqa: E402

idx = pd.bdate_range(end='2026-11-02', periods=300)
close = 100 + np.cumsum(np.random.default_rng(0).normal(0, 1, 300))
df = pd.DataFrame({'Open': close, 'High': close + 1, 'Low': close - 1, 'Close': close,
                   'Volume': np.full(300, 1e6)}, index=idx)
df.iloc[-1, :4] = np.nan  # 오늘 행: 가격은 NaN, 거래량만 있음


class FakeTicker:
    def __init__(self, symbol):
        pass

    def history(self, period, interval):
        return df.copy()


services.chart.yf.Ticker = FakeTicker
payload = services.chart.build_chart_payload('QLD')

json.dumps(payload, allow_nan=False)  # NaN이 남아 있으면 ValueError
assert payload['candles'][-1]['time'] == idx[-2].strftime('%Y-%m-%d')
assert len(payload['candles']) == len(payload['volume']) == 299
assert payload['summary']['close'] == round(close[-2], 2)

print("chart NaN tests OK")

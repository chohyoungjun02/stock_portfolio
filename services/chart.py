"""일봉 캔들 + 지표 + 신호 + 분석 요약 데이터 생성"""
import pandas as pd
import yfinance as yf

from services.indicators import compute_indicators, detect_signals, judge_trend, _round


def build_chart_payload(symbol):
    """차트 화면에 필요한 전체 데이터를 dict로 반환. 시세가 없으면 LookupError"""
    ticker = yf.Ticker(symbol)
    df = ticker.history(period='max', interval='1d')

    if df.empty:
        raise LookupError(f"{symbol} 시세 데이터를 찾을 수 없습니다.")

    df = compute_indicators(df)

    cols = {'rsi': 'RSI', 'ma20': 'MA20', 'ma60': 'MA60', 'ma120': 'MA120', 'bb_upper': 'BB_UPPER',
            'bb_lower': 'BB_LOWER', 'macd': 'MACD', 'macd_signal': 'MACD_SIGNAL', 'macd_hist': 'MACD_HIST'}
    candles, volume = [], []
    series = {k: [] for k in cols}

    for idx, row in df.iterrows():
        date_str = idx.strftime('%Y-%m-%d')
        candles.append({
            "time": date_str,
            "open": round(float(row['Open']), 2),
            "high": round(float(row['High']), 2),
            "low": round(float(row['Low']), 2),
            "close": round(float(row['Close']), 2)
        })
        volume.append({"time": date_str, "value": float(row['Volume']), "up": bool(row['Close'] >= row['Open'])})
        for key, col in cols.items():
            if pd.notna(row[col]):
                series[key].append({"time": date_str, "value": round(float(row[col]), 4)})

    summary = None
    signals = []
    if len(df) >= 2:
        last, prev = df.iloc[-1], df.iloc[-2]
        year = df.tail(252)
        signals = detect_signals(df)
        summary = {
            "close": _round(last['Close']),
            "change_pct": _round((last['Close'] / prev['Close'] - 1) * 100),
            "ma20": _round(last['MA20']),
            "ma60": _round(last['MA60']),
            "ma120": _round(last['MA120']),
            "rsi": _round(last['RSI']),
            "macd": _round(last['MACD'], 3),
            "macd_signal": _round(last['MACD_SIGNAL'], 3),
            "bb_upper": _round(last['BB_UPPER']),
            "bb_lower": _round(last['BB_LOWER']),
            "high_52w": _round(year['High'].max()),
            "low_52w": _round(year['Low'].min()),
            "volume_ratio": _round(last['Volume'] / last['VOL_MA20']) if last['VOL_MA20'] else None,
        }
        # 120일선이 계산될 만큼 데이터가 있을 때만 추세 판단
        if len(df) >= 122:
            score, verdict, reasons, warnings = judge_trend(df)
            summary.update(score=score, verdict=verdict, reasons=reasons, warnings=warnings)

    return {
        "candles": candles,
        "volume": volume,
        **series,
        "signals": signals,
        "summary": summary
    }

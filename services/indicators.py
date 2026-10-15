"""기술적 지표 계산, 진입/주의 신호 탐지, 강세/약세 판단"""
import pandas as pd


def compute_indicators(df):
    close = df['Close']

    # 이동평균선
    for n in (20, 60, 120):
        df[f'MA{n}'] = close.rolling(n).mean()

    # 볼린저 밴드 (20일, 2σ)
    std20 = close.rolling(20).std()
    df['BB_UPPER'] = df['MA20'] + 2 * std20
    df['BB_LOWER'] = df['MA20'] - 2 * std20

    # RSI 14 (Wilder's Smoothing)
    delta = close.diff()
    avg_gain = delta.clip(lower=0).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = (-delta.clip(upper=0)).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_SIGNAL'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_HIST'] = df['MACD'] - df['MACD_SIGNAL']

    # 거래량 20일 평균
    df['VOL_MA20'] = df['Volume'].rolling(20).mean()
    return df

def detect_signals(df):
    """진입(매수) / 주의(매도) 시점 탐지"""
    signals = []
    prev = df.shift(1)
    for idx in df.index[1:]:
        r, p = df.loc[idx], prev.loc[idx]
        if pd.isna(r['MA60']) or pd.isna(p['MA60']) or pd.isna(p['RSI']):
            continue
        date_str = idx.strftime('%Y-%m-%d')
        macd_up = p['MACD'] <= p['MACD_SIGNAL'] and r['MACD'] > r['MACD_SIGNAL']
        macd_down = p['MACD'] >= p['MACD_SIGNAL'] and r['MACD'] < r['MACD_SIGNAL']
        rsi_rebound = p['RSI'] < 30 <= r['RSI']
        rsi_overheat = p['RSI'] > 70 >= r['RSI']
        golden = p['MA20'] <= p['MA60'] and r['MA20'] > r['MA60']
        dead = p['MA20'] >= p['MA60'] and r['MA20'] < r['MA60']

        if golden:
            signals.append({"time": date_str, "type": "buy", "label": "골든크로스", "desc": "20일선이 60일선을 상향 돌파"})
        elif rsi_rebound:
            signals.append({"time": date_str, "type": "buy", "label": "과매도 탈출", "desc": "RSI가 30을 상향 돌파"})
        elif macd_up and r['Close'] > r['MA60']:
            signals.append({"time": date_str, "type": "buy", "label": "MACD 매수", "desc": "60일선 위에서 MACD 골든크로스"})
        elif dead:
            signals.append({"time": date_str, "type": "sell", "label": "데드크로스", "desc": "20일선이 60일선을 하향 돌파"})
        elif rsi_overheat:
            signals.append({"time": date_str, "type": "sell", "label": "과열 해소", "desc": "RSI가 70을 하향 이탈"})
        elif macd_down and r['Close'] < r['MA60']:
            signals.append({"time": date_str, "type": "sell", "label": "MACD 매도", "desc": "60일선 아래에서 MACD 데드크로스"})
    return signals

def judge_trend(df):
    """최신 일봉 기준 강세/약세 점수 (-6 ~ +6)"""
    r = df.iloc[-1]
    checks = [
        (r['Close'] > r['MA20'], "주가 > 20일선", "주가 < 20일선"),
        (r['MA20'] > r['MA60'], "20일선 > 60일선 (단기 정배열)", "20일선 < 60일선 (단기 역배열)"),
        (r['MA60'] > r['MA120'], "60일선 > 120일선 (중기 상승)", "60일선 < 120일선 (중기 하락)"),
        (r['MACD'] > r['MACD_SIGNAL'], "MACD > 시그널", "MACD < 시그널"),
        (r['MACD_HIST'] > df['MACD_HIST'].iloc[-2], "MACD 히스토그램 증가", "MACD 히스토그램 감소"),
        (r['RSI'] > 50, f"RSI {r['RSI']:.1f} (50 이상)", f"RSI {r['RSI']:.1f} (50 미만)"),
    ]
    score, reasons = 0, []
    for cond, good, bad in checks:
        score += 1 if cond else -1
        reasons.append({"bullish": bool(cond), "text": good if cond else bad})

    if score >= 4:
        verdict = "강한 강세"
    elif score >= 2:
        verdict = "강세"
    elif score <= -4:
        verdict = "강한 약세"
    elif score <= -2:
        verdict = "약세"
    else:
        verdict = "중립"

    warnings = []
    if r['RSI'] >= 70:
        warnings.append("RSI 과매수 구간 (70 이상) - 단기 조정 가능성")
    elif r['RSI'] <= 30:
        warnings.append("RSI 과매도 구간 (30 이하) - 반등 가능성")
    if r['Close'] > r['BB_UPPER']:
        warnings.append("볼린저 상단 돌파 - 과열 주의")
    elif r['Close'] < r['BB_LOWER']:
        warnings.append("볼린저 하단 이탈 - 과매도 주의")
    return score, verdict, reasons, warnings

def _round(v, n=2):
    return round(float(v), n) if pd.notna(v) else None

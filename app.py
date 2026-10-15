import os
import time
from flask import Flask, render_template, jsonify, request
import requests
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd

from auth import get_access_token
from holding import get_my_holdings  # 보유 종목 조회 함수

load_dotenv()

app = Flask(__name__)

# 1. 메인 대시보드 화면 렌더링
@app.route('/')
def index():
    return render_template('index2.html')

def _pick(d, *keys):
    """여러 후보 키 중 처음으로 값이 있는 것을 반환 (값이 dict면 amount/value 추출)"""
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            v = d[k]
            if isinstance(v, dict):
                v = v.get('amount', v.get('value', v.get('krw')))
            return v
    return None

def _find_list(obj):
    """토스 응답에서 보유 종목 리스트를 찾아 반환"""
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in ('holdings', 'items', 'positions', 'stocks', 'list'):
            if isinstance(obj.get(k), list):
                return obj[k]
        for k in ('data', 'result', 'body'):
            if k in obj:
                found = _find_list(obj[k])
                if found is not None:
                    return found
    return None

def _num(v):
    """문자열/None 값을 float로 변환 (변환 불가 시 None)"""
    if v is None:
        return None
    try:
        return float(str(v).replace(',', '').replace('%', ''))
    except ValueError:
        return None

def normalize_holdings(raw):
    """토스 API 원본 응답을 index2.html이 기대하는 구조로 변환"""
    items = _find_list(raw) or []
    holdings = []
    for it in items:
        qty = _num(_pick(it, 'quantity', 'qty', 'holdingQuantity', 'balanceQuantity'))
        avg = _num(_pick(it, 'avg_buy_price', 'averagePrice', 'avgPrice', 'purchasePrice', 'averagePurchasePrice'))
        cur = _num(_pick(it, 'current_price', 'currentPrice', 'price', 'lastPrice', 'marketPrice'))
        eval_amt = _num(_pick(it, 'eval_amount', 'evaluationAmount', 'marketValue', 'evaluatedAmount'))
        pnl = _num(_pick(it, 'pnl', 'profitLoss', 'profitAmount', 'unrealizedPnl', 'evaluationProfit'))
        rate = _num(_pick(it, 'pnl_rate', 'profitRate', 'profitLossRate', 'returnRate', 'yield'))

        # 응답에 없는 값은 가격·수량으로 직접 계산
        cost = avg * qty if avg is not None and qty is not None else None
        if eval_amt is None and cur is not None and qty is not None:
            eval_amt = cur * qty
        if pnl is None and eval_amt is not None and cost is not None:
            pnl = eval_amt - cost
        # 수익률은 매입단가·현재가로 계산한 값을 우선 사용 (응답 값이 없거나 0, 비율(0.05) 형태여도 정확)
        if avg and cur is not None:
            rate = (cur - avg) / avg * 100
        elif cost and pnl is not None:
            rate = pnl / cost * 100

        holdings.append({
            "name": _pick(it, 'name', 'stockName', 'productName', 'securityName'),
            "symbol": _pick(it, 'symbol', 'ticker', 'code', 'stockCode', 'productCode'),
            "quantity": qty,
            "avg_buy_price": avg,
            "current_price": cur,
            "eval_amount": eval_amt,
            "pnl": pnl,
            "pnl_rate": round(rate, 2) if rate is not None else None,
        })

    total_eval = sum(h["eval_amount"] or 0 for h in holdings)
    total_buy = sum((h["avg_buy_price"] or 0) * (h["quantity"] or 0) for h in holdings)
    total_pnl = sum(h["pnl"] or 0 for h in holdings) or (total_eval - total_buy)
    # 매입금액을 알 수 없으면 평가금액 - 손익으로 역산
    cost_basis = total_buy or (total_eval - total_pnl)
    summary = {
        "total_asset": total_eval,
        "total_buy": cost_basis,
        "deposit_krw": 0,
        "total_pnl": total_pnl,
        "total_pnl_rate": round(total_pnl / cost_basis * 100, 2) if cost_basis else 0,
    }
    return summary, holdings

# 2. 보유 종목 및 평가 데이터 조회 엔드포인트 (5초 폴링용)
@app.route('/api/holdings')
@app.route('/api/dashboard-data')
def dashboard_data():
    try:
        # holding.py 내부의 계좌 보유 종목 조회 호출
        holdings_data = get_my_holdings()
        if holdings_data:
            summary, holdings = normalize_holdings(holdings_data)
            return jsonify({
                "status": "success",
                "summary": summary,
                "holdings": holdings,
                "raw": holdings_data  # 필드 매핑 확인용 원본 응답
            })
        else:
            return jsonify({
                "status": "error",
                "message": "보유 종목 데이터를 불러올 수 없습니다."
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# 3. 달러/원 환율 조회 엔드포인트 (60초 캐시)
_fx_cache = {"rate": None, "time": 0.0}

@app.route('/api/fx')
def get_fx_rate():
    now = time.time()
    if _fx_cache["rate"] and now - _fx_cache["time"] < 60:
        return jsonify({"status": "success", "usd_krw": _fx_cache["rate"]})
    try:
        df = yf.Ticker('KRW=X').history(period='5d', interval='1d')
        if df.empty:
            raise ValueError("환율 데이터를 찾을 수 없습니다.")
        rate = round(float(df['Close'].iloc[-1]), 2)
        _fx_cache.update(rate=rate, time=now)
        return jsonify({"status": "success", "usd_krw": rate})
    except Exception as e:
        # 조회 실패 시 마지막으로 받은 환율이라도 반환
        if _fx_cache["rate"]:
            return jsonify({"status": "success", "usd_krw": _fx_cache["rate"], "stale": True})
        return jsonify({"status": "error", "message": str(e)}), 500

# 4. 기술적 지표 계산
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

# 5. 일봉 캔들 + 지표 + 신호 조회 엔드포인트
@app.route('/api/candles')
def get_candles():
    symbol = request.args.get('symbol', 'QLD').upper().strip()
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='max', interval='1d')

        if df.empty:
            return jsonify({"status": "error", "message": f"{symbol} 시세 데이터를 찾을 수 없습니다."}), 404

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

        return jsonify({
            "status": "success",
            "candles": candles,
            "volume": volume,
            **series,
            "signals": signals,
            "summary": summary
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # 개발 서버 실행
    app.run(debug=True, port=5000)
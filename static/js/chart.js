// 일봉 + RSI + MACD 차트 컴포넌트 (LightweightCharts 전역 사용)
import { parseAmount } from './utils.js';
import { renderAnalysis, renderAnalysisMessage } from './analysis.js';

let chart = null;
let candleSeries = null;
let rsiChart = null;
let rsiSeries = null;
let currentSymbol = 'QLD';

export function getCurrentSymbol() {
  return currentSymbol;
}

// 지표 라인 시리즈 & 차트 목록
let indicatorSeries = {};
let macdChart = null;
let macdSeries = {};
let allCharts = [];
let isSyncing = false;

// 차트 초기화 (상단 캔들 + RSI + MACD 동기화)
export function initChart() {
  const container = document.getElementById('chartContainer');
  const rsiContainer = document.getElementById('rsiContainer');
  const macdContainer = document.getElementById('macdContainer');
  container.innerHTML = '';
  rsiContainer.innerHTML = '';
  macdContainer.innerHTML = '';

  const commonOptions = {
    layout: { background: { color: '#1e293b' }, textColor: '#94a3b8' },
    grid: { vertLines: { color: '#334155' }, horzLines: { color: '#334155' } },
    crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
    timeScale: { timeVisible: false, secondsVisible: false, borderColor: '#334155' },
  };

  // 1. 상단 일봉 차트
  chart = LightweightCharts.createChart(container, {
    ...commonOptions,
    width: container.clientWidth || 928,
    height: 400,
  });

  candleSeries = chart.addCandlestickSeries({
    upColor: '#f87171',
    downColor: '#60a5fa',
    borderDownColor: '#60a5fa',
    borderUpColor: '#f87171',
    wickDownColor: '#60a5fa',
    wickUpColor: '#f87171',
  });

  // 거래량 (차트 하단 20% 영역)
  indicatorSeries.volume = chart.addHistogramSeries({
    priceFormat: { type: 'volume' },
    priceScaleId: 'volume',
    lastValueVisible: false,
    priceLineVisible: false,
  });
  chart.priceScale('volume').applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });
  candleSeries.priceScale().applyOptions({ scaleMargins: { top: 0.05, bottom: 0.22 } });

  // 이동평균선 & 볼린저 밴드
  const lineOpts = { lineWidth: 1, lastValueVisible: false, priceLineVisible: false, crosshairMarkerVisible: false };
  indicatorSeries.ma20 = chart.addLineSeries({ ...lineOpts, color: '#facc15', lineWidth: 2 });
  indicatorSeries.ma60 = chart.addLineSeries({ ...lineOpts, color: '#22c55e', lineWidth: 2 });
  indicatorSeries.ma120 = chart.addLineSeries({ ...lineOpts, color: '#e879f9', lineWidth: 2 });
  indicatorSeries.bb_upper = chart.addLineSeries({ ...lineOpts, color: '#64748b', lineStyle: LightweightCharts.LineStyle.Dashed });
  indicatorSeries.bb_lower = chart.addLineSeries({ ...lineOpts, color: '#64748b', lineStyle: LightweightCharts.LineStyle.Dashed });

  // 2. RSI 차트
  rsiChart = LightweightCharts.createChart(rsiContainer, {
    ...commonOptions,
    width: rsiContainer.clientWidth || 928,
    height: 130,
  });

  rsiSeries = rsiChart.addLineSeries({
    color: '#a855f7',
    lineWidth: 2,
  });

  // RSI 70/30 기준선 추가
  rsiSeries.createPriceLine({ price: 70, color: '#f87171', lineWidth: 1, lineStyle: LightweightCharts.LineStyle.Dashed, axisLabelVisible: true, title: '과매수 70' });
  rsiSeries.createPriceLine({ price: 30, color: '#60a5fa', lineWidth: 1, lineStyle: LightweightCharts.LineStyle.Dashed, axisLabelVisible: true, title: '과매도 30' });

  // 3. MACD 차트
  macdChart = LightweightCharts.createChart(macdContainer, {
    ...commonOptions,
    width: macdContainer.clientWidth || 928,
    height: 130,
  });
  macdSeries.hist = macdChart.addHistogramSeries({ lastValueVisible: false, priceLineVisible: false });
  macdSeries.macd = macdChart.addLineSeries({ color: '#38bdf8', lineWidth: 2, priceLineVisible: false });
  macdSeries.signal = macdChart.addLineSeries({ color: '#fb923c', lineWidth: 1, priceLineVisible: false });

  // 4. 세 차트의 시간축 스크롤 및 줌 동기화
  allCharts = [chart, rsiChart, macdChart];
  allCharts.forEach(src => {
    src.timeScale().subscribeVisibleLogicalRangeChange(range => {
      if (!range || isSyncing) return;
      isSyncing = true;
      allCharts.forEach(dst => { if (dst !== src) dst.timeScale().setVisibleLogicalRange(range); });
      isSyncing = false;
    });
  });

  // 반응형 크기 조절
  const resizeObserver = new ResizeObserver(entries => {
    if (entries.length === 0 || !entries[0].contentRect) return;
    const newWidth = entries[0].contentRect.width;
    allCharts.forEach(c => c.applyOptions({ width: newWidth }));
  });
  resizeObserver.observe(container);
}

function toSeries(list) {
  return (list || []).map(item => ({ time: item.time, value: parseAmount(item.value) }))
    .sort((a, b) => (a.time > b.time ? 1 : -1));
}

// 최근 3개월만 화면에 보이도록 설정 (전체 데이터는 스크롤/줌으로 확인 가능)
function showRecentMonths(candles, months = 3) {
  if (candles.length === 0) return;
  const last = new Date(candles[candles.length - 1].time);
  last.setMonth(last.getMonth() - months);
  const fromStr = last.toISOString().slice(0, 10);
  let fromIdx = candles.findIndex(c => c.time >= fromStr);
  if (fromIdx < 0) fromIdx = 0;
  chart.timeScale().setVisibleLogicalRange({ from: fromIdx, to: candles.length + 2 });
}

// 캔들, 지표, 신호 데이터 로드
export async function loadCandles(symbol) {
  currentSymbol = symbol.toUpperCase();
  document.getElementById('currentChartTicker').innerText = currentSymbol;

  try {
    const res = await fetch(`/api/candles?symbol=${encodeURIComponent(currentSymbol)}`);
    const result = await res.json();

    if (result.status !== 'success' || !result.candles || result.candles.length === 0) {
      console.warn("차트 데이터 로드 실패:", result.message);
      renderAnalysisMessage(`${currentSymbol} 데이터를 불러오지 못했습니다. ${result.message || ''}`);
      return;
    }

    // 일봉 캔들 데이터 반영
    const formattedCandles = result.candles.map(item => ({
      time: item.time,
      open: parseAmount(item.open),
      high: parseAmount(item.high),
      low: parseAmount(item.low),
      close: parseAmount(item.close),
    })).sort((a, b) => (a.time > b.time ? 1 : -1));

    candleSeries.setData(formattedCandles);

    // 거래량
    indicatorSeries.volume.setData((result.volume || []).map(v => ({
      time: v.time,
      value: v.value,
      color: v.up ? 'rgba(248,113,113,0.4)' : 'rgba(96,165,250,0.4)',
    })));

    // 이동평균선 & 볼린저 밴드
    ['ma20', 'ma60', 'ma120', 'bb_upper', 'bb_lower'].forEach(key => {
      indicatorSeries[key].setData(toSeries(result[key]));
    });

    // RSI
    // RSI는 앞쪽 14일이 비어 있으므로 빈 날짜(whitespace)로 채워 캔들 차트와 날짜 위치를 맞춤
    const rsiData = toSeries(result.rsi);
    const firstRsiTime = rsiData.length ? rsiData[0].time : null;
    const rsiPadding = formattedCandles
      .filter(c => firstRsiTime === null || c.time < firstRsiTime)
      .map(c => ({ time: c.time }));
    rsiSeries.setData([...rsiPadding, ...rsiData]);

    // MACD
    macdSeries.macd.setData(toSeries(result.macd));
    macdSeries.signal.setData(toSeries(result.macd_signal));
    macdSeries.hist.setData(toSeries(result.macd_hist).map(p => ({
      ...p,
      color: p.value >= 0 ? 'rgba(248,113,113,0.6)' : 'rgba(96,165,250,0.6)',
    })));

    // 진입(매수) / 주의(매도) 신호 마커
    const signals = result.signals || [];
    candleSeries.setMarkers(signals.map(s => ({
      time: s.time,
      position: s.type === 'buy' ? 'belowBar' : 'aboveBar',
      color: s.type === 'buy' ? '#22c55e' : '#f97316',
      shape: s.type === 'buy' ? 'arrowUp' : 'arrowDown',
      text: s.label,
    })));

    renderAnalysis(result.summary, signals);

    // 최근 3개월 일봉만 표시
    showRecentMonths(formattedCandles, 3);
  } catch (err) {
    console.error("시세 데이터 요청 오류:", err);
  }
}

// 검색창 티커 전환
function changeChartSymbol() {
  const input = document.getElementById('tickerInput');
  const symbol = input.value.trim();
  if (symbol) {
    loadCandles(symbol);
    input.value = '';
  }
}

// 검색 버튼 / 엔터키 이벤트 연결
export function initChartSearch() {
  document.getElementById('chartSearchBtn').addEventListener('click', changeChartSymbol);
  document.getElementById('tickerInput').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
      changeChartSymbol();
    }
  });
}

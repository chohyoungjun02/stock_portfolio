// 종목 비교: 같은 금액을 같은 기간 투자했을 때의 수익
import { API_BASE, formatNumber } from './utils.js';
import { resolveSymbol, displayName } from './stocks.js';

const COLORS = ['#3182f6', '#f04452'];
let chart = null;
let lines = [];

const escapeHtml = s => String(s ?? '').replace(/[&<>"']/g,
  c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const won = v => `${formatNumber(Math.abs(v))}원`;
const signed = v => `${v > 0 ? '+' : v < 0 ? '-' : ''}${won(v)}`;
const isoDate = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

function setMessage(text) {
  document.getElementById('compareResult').innerHTML = `<div class="msg">${escapeHtml(text)}</div>`;
}

// 차트는 탭이 보인 뒤 처음 비교할 때 만듦 (숨긴 상태에서 만들면 폭이 0)
function ensureChart() {
  if (chart) return;
  const el = document.getElementById('compareChart');
  el.hidden = false;
  chart = LightweightCharts.createChart(el, {
    autoSize: true,
    layout: { background: { color: '#ffffff' }, textColor: '#8b95a1', fontFamily: 'Pretendard, sans-serif' },
    grid: { vertLines: { color: '#f2f4f6' }, horzLines: { color: '#f2f4f6' } },
    timeScale: { borderColor: '#e5e8eb' },
    localization: { priceFormatter: v => `${formatNumber(v)}원` },
  });
  lines = COLORS.map(color => chart.addLineSeries({ color, lineWidth: 2 }));
}

function render(data) {
  const [a, b] = data.stocks;
  const gap = a.final_value - b.final_value;
  const winner = gap === 0 ? null : (gap > 0 ? a : b).symbol;
  const cards = data.stocks.map((s, i) => {
    const tone = s.profit > 0 ? 'up' : s.profit < 0 ? 'down' : '';
    return `
    <div class="cmp-card ${s.symbol === winner ? 'win' : ''}">
      <div class="cmp-head">
        <i style="background: ${COLORS[i]}"></i>
        <b>${escapeHtml(displayName(s.symbol))}</b><small>${escapeHtml(s.symbol)}</small>
        ${s.symbol === winner ? '<span class="badge">수익 더 높음</span>' : ''}
      </div>
      <div class="cmp-rate ${tone}">${s.return_pct > 0 ? '+' : ''}${formatNumber(s.return_pct, 2)}%</div>
      <dl class="cmp-rows">
        <div><dt>투자 금액</dt><dd>${won(data.amount)}</dd></div>
        <div><dt>평가 금액</dt><dd>${won(s.final_value)}</dd></div>
        <div><dt>수익</dt><dd class="${tone}">${signed(s.profit)}</dd></div>
        <div><dt>기간</dt><dd>${s.start_date.replaceAll('-', '.')} ~ ${s.end_date.replaceAll('-', '.')}</dd></div>
      </dl>
    </div>`;
  }).join('');
  const verdict = gap === 0
    ? '두 종목의 결과가 같아요.'
    : `${displayName((gap > 0 ? a : b).symbol)}에 투자했다면 ${won(gap)} 더 벌었어요.`;
  document.getElementById('compareResult').innerHTML = `<div class="verdict">${escapeHtml(verdict)}</div>${cards}`;

  ensureChart();
  data.stocks.forEach((s, i) => {
    lines[i].applyOptions({ title: displayName(s.symbol) });
    lines[i].setData(s.series);
  });
  chart.timeScale().fitContent();
}

async function runCompare(e) {
  e.preventDefault();
  const params = new URLSearchParams({
    a: resolveSymbol(document.getElementById('cmpA').value),
    b: resolveSymbol(document.getElementById('cmpB').value),
    amount: Number(document.getElementById('cmpAmount').value) * 10000,  // 만원 단위 입력 → 원
    start: document.getElementById('cmpStart').value,
    end: document.getElementById('cmpEnd').value,
  });
  setMessage('비교하는 중...');
  try {
    const res = await fetch(`${API_BASE}/api/compare?${params}`);
    const data = await res.json();
    if (data.status !== 'success') throw new Error(data.message);
    render(data);
  } catch (err) {
    console.error("종목 비교 오류:", err);
    setMessage(`비교하지 못했어요. ${err.message}`);
  }
}

export function initCompare() {
  const today = new Date();
  const yearAgo = new Date(today);
  yearAgo.setFullYear(today.getFullYear() - 1);
  const start = document.getElementById('cmpStart');
  const end = document.getElementById('cmpEnd');
  start.value = isoDate(yearAgo);
  end.value = isoDate(today);
  start.max = end.max = isoDate(today);
  document.getElementById('compareForm').addEventListener('submit', runCompare);
}

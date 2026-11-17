// 모의투자 화면: 주문·보유 종목·거래 내역 (계산은 paperCore.js, 저장은 localStorage)
import { API_BASE, formatNumber } from './utils.js';
import { resolveSymbol, displayName } from './stocks.js';
import { buy, sell, summarize, restore, newAccount, START_CASH } from './paperCore.js';

const KEY = 'paperAccount';
let account = newAccount();
let prices = {};  // 심볼 → { price_krw, price, currency }

const escapeHtml = s => String(s ?? '').replace(/[&<>"']/g,
  c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const won = v => `${formatNumber(Math.round(Math.abs(v)))}원`;
const signedWon = v => `${v > 0 ? '+' : v < 0 ? '-' : ''}${won(v)}`;
const pct = v => `${v > 0 ? '+' : ''}${formatNumber(v, 2)}%`;
const tone = v => (v > 0 ? 'up' : v < 0 ? 'down' : '');
const $ = id => document.getElementById(id);

function load() {
  try { account = restore(JSON.parse(localStorage.getItem(KEY))); } catch { account = newAccount(); }
}

function save() {
  try { localStorage.setItem(KEY, JSON.stringify(account)); } catch { /* 사생활 보호 모드 등: 이번 방문 동안만 유지 */ }
}

async function fetchQuotes(symbols) {
  if (!symbols.length) return {};
  const res = await fetch(`${API_BASE}/api/quote?symbols=${encodeURIComponent(symbols.join(','))}`);
  const data = await res.json();
  if (data.status !== 'success') throw new Error(data.message);
  Object.assign(prices, data.quotes);
  return data.quotes;
}

function localPrice(q) {
  return q.currency === 'USD' ? ` ($${formatNumber(q.price, 2)})` : '';
}

function render() {
  const krw = Object.fromEntries(Object.entries(prices).map(([s, q]) => [s, q.price_krw]));
  const s = summarize(account, krw);
  $('paperTotal').innerText = won(s.total);
  $('paperProfit').className = tone(s.profit);
  $('paperProfit').innerText = `${signedWon(s.profit)} (${pct(s.returnPct)})`;
  $('paperCash').innerText = won(s.cash);
  $('paperStock').innerText = won(s.stockValue);

  $('paperHoldings').innerHTML = s.rows.map(r => `
    <tr data-symbol="${escapeHtml(r.symbol)}" tabindex="0">
      <td><b>${escapeHtml(displayName(r.symbol))}</b><small>${escapeHtml(r.symbol)}</small></td>
      <td>${formatNumber(r.qty)}주</td>
      <td>${won(r.avgPrice)}</td>
      <td>${r.price ? won(r.price) : '<small>시세 없음</small>'}</td>
      <td>${won(r.value)}</td>
      <td class="${tone(r.profit)}">${signedWon(r.profit)}<small>${pct(r.returnPct)}</small></td>
    </tr>`).join('') || '<tr><td colspan="6" class="empty">아직 보유 종목이 없어요. 오른쪽 주문창에서 사 보세요.</td></tr>';

  $('paperTrades').innerHTML = account.trades.slice(0, 20).map(t => `
    <div class="paper-trade">
      <span class="tag ${t.side}">${t.side === 'buy' ? '매수' : '매도'}</span>
      <div><b>${escapeHtml(displayName(t.symbol))} ${formatNumber(t.qty)}주</b>
        <small>${new Date(t.time).toLocaleString('ko-KR', { dateStyle: 'short', timeStyle: 'short' })} · 1주 ${won(t.price)}</small></div>
      <div class="amt">${won(t.amount)}${t.profit !== undefined ? `<small class="${tone(t.profit)}">실현 ${signedWon(t.profit)}</small>` : ''}</div>
    </div>`).join('') || '<small style="color: var(--subtext);">아직 거래가 없어요.</small>';
}

// 보유 종목 시세를 새로 받아 평가
async function refresh() {
  try {
    await fetchQuotes(Object.keys(account.holdings));
  } catch (err) {
    console.error("모의투자 시세 조회 오류:", err);
  }
  render();
}

// 주문창 종목 → 현재가 표시, 심볼과 가격 반환
async function lookup() {
  const input = $('paperSymbol').value.trim();
  if (!input) return null;
  const symbol = resolveSymbol(input);
  $('paperPrice').innerText = '현재가를 불러오는 중...';
  try {
    const q = (await fetchQuotes([symbol]))[symbol];
    if (!q) throw new Error(`${symbol}의 시세를 찾을 수 없어요.`);
    const held = account.holdings[symbol]?.qty || 0;
    $('paperPrice').innerText = `${displayName(symbol)} 현재가 ${won(q.price_krw)}${localPrice(q)} · 보유 ${formatNumber(held)}주`;
    return { symbol, price: q.price_krw };
  } catch (err) {
    $('paperPrice').innerText = err.message;
    return null;
  }
}

async function order(e) {
  e.preventDefault();
  const side = e.submitter?.value || 'buy';
  const qty = Number($('paperQty').value);
  const msg = $('paperMsg');
  msg.className = 'paper-msg';
  msg.innerText = '주문하는 중...';
  const q = await lookup();  // 주문 직전 가격으로 체결
  if (!q) { msg.innerText = '시세를 불러오지 못해 주문하지 못했어요.'; return; }
  try {
    account = (side === 'buy' ? buy : sell)(account, q.symbol, qty, q.price);
    save();
    msg.className = 'paper-msg ok';
    msg.innerText = `${displayName(q.symbol)} ${formatNumber(qty)}주를 1주 ${won(q.price)}에 ${side === 'buy' ? '샀어요' : '팔았어요'}.`;
    await lookup();  // 보유 수량 갱신
    render();
  } catch (err) {
    msg.className = 'paper-msg err';
    msg.innerText = err.message;
  }
}

// confirm() 창은 토스 웹뷰·앱 내 브라우저에서 막힐 수 있어 버튼을 한 번 더 누르게 함
let resetTimer = null;
function reset() {
  const btn = $('paperReset');
  if (!resetTimer) {
    btn.innerText = '한 번 더 누르면 초기화';
    btn.classList.add('danger');
    resetTimer = setTimeout(() => {
      resetTimer = null;
      btn.innerText = '초기화';
      btn.classList.remove('danger');
    }, 3000);
    return;
  }
  clearTimeout(resetTimer);
  resetTimer = null;
  btn.innerText = '초기화';
  btn.classList.remove('danger');
  account = newAccount();
  prices = {};
  save();
  const msg = $('paperMsg');
  msg.className = 'paper-msg ok';
  msg.innerText = `초기화했어요. 현금 ${won(START_CASH)}으로 다시 시작해요.`;
  render();
}

// 차트 화면의 '모의로 사기' 등에서 종목을 채워 넣기
export function prefillOrder(symbol) {
  $('paperSymbol').value = displayName(symbol);
  $('paperQty').value = 1;
  $('paperMsg').innerText = '';
  lookup();
}

export function initPaper() {
  load();
  $('paperOrder').addEventListener('submit', order);
  $('paperSymbol').addEventListener('change', lookup);
  $('paperRefresh').addEventListener('click', refresh);
  $('paperReset').addEventListener('click', reset);
  const pick = e => {
    const row = e.target.closest('tr[data-symbol]');
    if (row && (e.type === 'click' || e.key === 'Enter')) prefillOrder(row.dataset.symbol);
  };
  $('paperHoldings').addEventListener('click', pick);
  $('paperHoldings').addEventListener('keydown', pick);
  // 탭을 열 때만 시세 조회 (처음 페이지 로딩을 가볍게)
  document.addEventListener('tabchange', e => { if (e.detail === 'investTab') refresh(); });
  render();
}

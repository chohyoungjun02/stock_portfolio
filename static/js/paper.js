// 모의투자 화면: 주문·보유 종목·거래 내역 (계산은 paperCore.js, 저장은 localStorage)
import { API_BASE, formatNumber } from './utils.js';
import { resolveSymbol, displayName } from './stocks.js';
import { buy, sell, summarize, restore, newAccount, preview, START_CASH } from './paperCore.js';

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

let view = 'value';   // 보유 종목 오른쪽 금액: price(1주 가격) | value(평가 금액)
let showUsd = false;  // 해외 종목을 달러로 보기
let side = 'buy';
let cur = null;       // 주문창 종목 { symbol, price(원) }

const AVATAR_COLORS = ['#3182f6', '#f04452', '#e8a33d', '#76b82a', '#8b5cf6', '#14b8a6', '#64748b'];
function avatar(symbol) {
  const n = [...symbol].reduce((a, c) => a + c.charCodeAt(0), 0);
  return { ch: displayName(symbol).trim().charAt(0).toUpperCase(), bg: AVATAR_COLORS[n % AVATAR_COLORS.length] };
}

// 100만 원 이상 손익은 '361.4만'처럼 줄여서
const shortWon = v => (Math.abs(v) >= 1_000_000 ? `${formatNumber(Math.abs(v) / 10_000, 1)}만` : won(v));
const sign = v => (v > 0 ? '+' : v < 0 ? '-' : '');

// 원화 금액을 보기 통화로: 해외 종목 + 달러 보기면 현재 환율로 달러 환산
function money(krw, symbol, short = false) {
  const q = prices[symbol];
  if (showUsd && q?.currency === 'USD' && q.price) return `$${formatNumber(Math.abs(krw) / (q.price_krw / q.price), 2)}`;
  return short ? shortWon(krw) : won(krw);
}

function render() {
  const krw = Object.fromEntries(Object.entries(prices).map(([s, q]) => [s, q.price_krw]));
  const s = summarize(account, krw);
  $('paperTotal').innerText = won(s.total);
  $('paperProfit').className = tone(s.profit);
  $('paperProfit').innerText = `${signedWon(s.profit)} (${pct(s.returnPct)})`;
  $('paperCash').innerText = won(s.cash);
  $('paperStock').innerText = won(s.stockValue);

  $('paperHoldings').innerHTML = s.rows.map(r => {
    const a = avatar(r.symbol);
    const main = view === 'price' ? (r.price ? money(r.price, r.symbol) : '시세 없음') : money(r.value, r.symbol);
    return `
    <li><button type="button" class="hold-row" data-symbol="${escapeHtml(r.symbol)}">
      <span class="avatar" style="background:${a.bg}" aria-hidden="true">${escapeHtml(a.ch)}</span>
      <span class="hold-name"><b>${escapeHtml(displayName(r.symbol))}</b><small>${formatNumber(r.qty)}주</small></span>
      <span class="hold-amt"><b>${main}</b>
        <small class="${tone(r.profit)}">${sign(r.profit)}${money(r.profit, r.symbol, true)} (${formatNumber(Math.abs(r.returnPct), 1)}%)</small></span>
    </button></li>`;
  }).join('') || '<li class="hold-empty">아직 보유 종목이 없어요. 주문창에서 사 보세요.</li>';

  $('paperTrades').innerHTML = account.trades.slice(0, 20).map(t => `
    <div class="paper-trade">
      <span class="tag ${t.side}">${t.side === 'buy' ? '매수' : '매도'}</span>
      <div><b>${escapeHtml(displayName(t.symbol))} ${formatNumber(t.qty)}주</b>
        <small>${new Date(t.time).toLocaleString('ko-KR', { dateStyle: 'short', timeStyle: 'short' })} · 1주 ${won(t.price)}</small></div>
      <div class="amt">${won(t.amount)}${t.profit !== undefined ? `<small class="${tone(t.profit)}">실현 ${signedWon(t.profit)}</small>` : ''}</div>
    </div>`).join('') || '<small style="color: var(--subtext);">아직 거래가 없어요.</small>';
  updateOrder();
}

// 주문창 숫자들(최대 수량, 평균, 예상, 총액) 다시 계산
function updateOrder() {
  const buying = side === 'buy';
  const qty = Number($('paperQty').value);
  const p = cur ? preview(account, cur.symbol, side, qty, cur.price) : null;
  $('orderMax').innerText = `최대 ${formatNumber(p?.max ?? 0)}주`;
  $('orderAvg').innerText = p?.avg ? won(p.avg) : '-';
  $('orderAfterLabel').innerText = buying ? '구매 후 예상 평균' : '판매 후 예상 손익';
  $('orderAfter').className = buying ? '' : tone(p?.after);
  $('orderAfter').innerText = p?.after == null ? '-' : buying ? won(p.after) : signedWon(p.after);
  $('orderCanLabel').innerText = buying ? '구매가능 금액' : '판매가능 수량';
  $('orderCan').innerText = buying ? won(account.cash) : `${formatNumber(account.holdings[cur?.symbol]?.qty || 0)}주`;
  $('orderTotal').innerText = won(p?.total ?? 0);
  const btn = $('orderSubmit');
  btn.innerText = buying ? '구매하기' : '판매하기';
  btn.classList.toggle('paper-buy', buying);
  btn.classList.toggle('paper-sell', !buying);
}

function setSide(next) {
  side = next;
  document.querySelectorAll('.order-side button').forEach(b => b.classList.toggle('active', b.dataset.side === side));
  $('paperMsg').innerText = '';
  updateOrder();
}

function setQty(n) {
  $('paperQty').value = Math.max(1, Math.floor(n) || 1);
  updateOrder();
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
  const a = avatar(symbol);
  $('orderAvatar').innerText = a.ch;
  $('orderAvatar').style.background = a.bg;
  $('orderName').innerText = displayName(symbol);
  $('orderSymbol').innerText = symbol;
  $('paperPrice').innerText = '불러오는 중...';
  try {
    const q = (await fetchQuotes([symbol]))[symbol];
    if (!q) throw new Error(`${symbol}의 시세를 찾을 수 없어요.`);
    $('paperPrice').innerHTML = `${won(q.price_krw)}${q.currency === 'USD' ? `<small>$${formatNumber(q.price, 2)}</small>` : ''}`;
    cur = { symbol, price: q.price_krw };
    updateOrder();
    return cur;
  } catch (err) {
    cur = null;
    $('paperPrice').innerText = '';
    $('paperMsg').className = 'paper-msg err';
    $('paperMsg').innerText = err.message;
    updateOrder();
    return null;
  }
}

async function order(e) {
  e.preventDefault();
  const qty = Number($('paperQty').value);
  const msg = $('paperMsg');
  msg.className = 'paper-msg';
  msg.innerText = '주문하는 중...';
  const q = await lookup();  // 주문 직전 가격으로 체결
  if (!q) {  // 시세 오류 메시지는 lookup이 이미 표시
    if (!$('paperSymbol').value.trim()) { msg.className = 'paper-msg err'; msg.innerText = '종목을 먼저 골라 주세요.'; }
    return;
  }
  try {
    account = (side === 'buy' ? buy : sell)(account, q.symbol, qty, q.price);
    save();
    msg.className = 'paper-msg ok';
    msg.innerText = `${displayName(q.symbol)} ${formatNumber(qty)}주를 1주 ${won(q.price)}에 ${side === 'buy' ? '샀어요' : '팔았어요'}.`;
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
  cur = null;
  lookup();
}

export function initPaper() {
  load();
  // 엔터(폼 제출)는 시세 조회만, 주문은 구매/판매 버튼을 눌렀을 때만
  $('paperOrder').addEventListener('submit', e => { e.preventDefault(); lookup(); });
  $('orderSubmit').addEventListener('click', order);
  $('paperSymbol').addEventListener('change', lookup);
  $('paperRefresh').addEventListener('click', refresh);
  $('paperReset').addEventListener('click', reset);
  $('paperQty').addEventListener('input', updateOrder);
  document.querySelector('.order-side').addEventListener('click', e => {
    if (e.target.dataset.side) setSide(e.target.dataset.side);
  });
  document.querySelectorAll('.qty-row .step').forEach(b => b.addEventListener('click', () =>
    setQty(Number($('paperQty').value) + Number(b.dataset.step))));
  document.querySelectorAll('.qty-pcts button').forEach(b => b.addEventListener('click', () => {
    const max = cur ? preview(account, cur.symbol, side, 0, cur.price).max : 0;
    setQty(max * Number(b.dataset.pct) / 100);
  }));
  // 보유 종목 보기 전환 (주가/자산, 달러/원)
  document.querySelectorAll('[data-view]').forEach(b => b.addEventListener('click', () => {
    view = b.dataset.view;
    document.querySelectorAll('[data-view]').forEach(x => x.classList.toggle('active', x === b));
    render();
  }));
  document.querySelectorAll('[data-cur]').forEach(b => b.addEventListener('click', () => {
    showUsd = b.dataset.cur === 'usd';
    document.querySelectorAll('[data-cur]').forEach(x => x.classList.toggle('active', x === b));
    render();
  }));
  $('paperHoldings').addEventListener('click', e => {
    const row = e.target.closest('[data-symbol]');
    if (row) prefillOrder(row.dataset.symbol);
  });
  // 탭을 열 때만 시세 조회 (처음 페이지 로딩을 가볍게)
  document.addEventListener('tabchange', e => { if (e.detail === 'investTab') refresh(); });
  render();
}

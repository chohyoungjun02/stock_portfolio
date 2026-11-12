// 관심 종목: 브라우저(localStorage)에 저장, 차트·뉴스 탭에서 바로 불러오기
import { displayName } from './stocks.js';

const KEY = 'watchlist';
let symbols = [];
let current = null;

function load() {
  try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch { return []; }
}

function save() {
  try { localStorage.setItem(KEY, JSON.stringify(symbols)); } catch { /* 사생활 보호 모드 등: 이번 방문 동안만 유지 */ }
}

const escapeHtml = s => String(s).replace(/[&<>"']/g,
  c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function render() {
  const chips = symbols.map(sym => `<button type="button" class="watch-chip" data-symbol="${escapeHtml(sym)}">${escapeHtml(displayName(sym))}</button>`).join('');
  const empty = '<small>☆를 누르면 관심 종목에 추가돼요.</small>';
  document.getElementById('chartWatchlist').innerHTML = chips ? `<small>관심 종목</small>${chips}` : empty;
  document.getElementById('newsWatchlist').innerHTML = chips ? `<small>관심 종목 뉴스</small>${chips}` : '';

  const on = symbols.includes(current);
  const btn = document.getElementById('watchToggle');
  btn.innerText = on ? '★' : '☆';
  btn.setAttribute('aria-pressed', on);
  btn.setAttribute('aria-label', on ? '관심 종목에서 빼기' : '관심 종목에 추가');
}

// onSelectChart(symbol): 차트 전환, onSelectNews(name): 뉴스 검색
export function initWatchlist({ onSelectChart, onSelectNews }) {
  symbols = load();
  document.addEventListener('symbolchange', e => { current = e.detail; render(); });
  document.getElementById('watchToggle').addEventListener('click', () => {
    symbols = symbols.includes(current) ? symbols.filter(s => s !== current) : [...symbols, current];
    save();
    render();
  });
  document.getElementById('chartWatchlist').addEventListener('click', e => {
    const sym = e.target.dataset?.symbol;
    if (sym) onSelectChart(sym);
  });
  document.getElementById('newsWatchlist').addEventListener('click', e => {
    const sym = e.target.dataset?.symbol;
    if (sym) onSelectNews(displayName(sym));
  });
  render();
}

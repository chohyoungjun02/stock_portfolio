// 종목별 주요 뉴스 컴포넌트
import { findSymbol } from './stocks.js';
import { API_BASE } from './utils.js';

const escapeHtml = s => String(s ?? '').replace(/[&<>"']/g,
  c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// "3시간 전" 형태 (published: 초 단위 timestamp)
function timeAgo(published) {
  if (!published) return '';
  const min = Math.floor((Date.now() / 1000 - published) / 60);
  if (min < 60) return `${Math.max(min, 1)}분 전`;
  if (min < 60 * 24) return `${Math.floor(min / 60)}시간 전`;
  return `${Math.floor(min / 60 / 24)}일 전`;
}

let currentQuery = '';  // 비어 있으면 주요 종목 뉴스
let onSelectChart = () => {};

function renderStock(s) {
  const symbol = s.symbol || findSymbol(s.name);
  // 티커를 아는 종목은 이름을 누르면 차트로 이동
  const title = symbol
    ? `<button type="button" class="news-stock-link" data-symbol="${escapeHtml(symbol)}" title="차트 보기">${escapeHtml(s.name)}<small>${escapeHtml(symbol)} · 차트 ›</small></button>`
    : escapeHtml(s.name);
  return `
      <div class="news-stock">
        <h3>${title}</h3>
        ${s.items.map(n => `
          <a class="news-item" href="${escapeHtml(n.link)}" target="_blank" rel="noopener noreferrer">
            <b>${escapeHtml(n.title)}</b>
            <small>${escapeHtml(n.source)} · ${timeAgo(n.published)}</small>
          </a>`).join('') || '<small style="color: var(--subtext);">최근 뉴스가 없어요.</small>'}
      </div>`;
}

async function fetchNews() {
  const box = document.getElementById('stockNews');
  const query = currentQuery;
  document.getElementById('newsTitle').innerText = query ? `'${query}' 뉴스` : '종목별 주요 뉴스';
  document.getElementById('newsReset').hidden = !query;
  box.innerHTML = '<span style="color: var(--subtext);">뉴스를 불러오는 중입니다...</span>';
  try {
    const res = await fetch(API_BASE + '/api/news' + (query ? `?q=${encodeURIComponent(query)}` : ''));
    const data = await res.json();
    if (query !== currentQuery) return;  // 그사이 다른 검색을 했으면 버림
    if (data.status !== 'success') throw new Error(data.message);
    box.innerHTML = data.stocks.map(renderStock).join('');
  } catch (err) {
    console.error("뉴스 조회 오류:", err);
    box.innerHTML = `<span style="color: var(--subtext);">뉴스를 불러오지 못했어요. ${escapeHtml(err.message)}</span>`;
  }
}

// 관심 종목 등 다른 곳에서 뉴스 검색
export function searchNews(query) {
  currentQuery = query;
  document.getElementById('newsQuery').value = query;
  fetchNews();
}

export function initNews({ onSelectChart: selectChart }) {
  onSelectChart = selectChart;
  document.getElementById('stockNews').addEventListener('click', e => {
    const link = e.target.closest('.news-stock-link');
    if (link) onSelectChart(link.dataset.symbol);
  });
  document.getElementById('newsSearchForm').addEventListener('submit', e => {
    e.preventDefault();
    currentQuery = document.getElementById('newsQuery').value.trim();
    fetchNews();
  });
  document.getElementById('newsReset').addEventListener('click', () => {
    currentQuery = '';
    document.getElementById('newsQuery').value = '';
    fetchNews();
  });
  fetchNews();
  setInterval(fetchNews, 10 * 60 * 1000); // 서버 캐시 주기(10분)에 맞춰 갱신
}

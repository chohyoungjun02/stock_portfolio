// 요약 카드 + 보유 자산 테이블 컴포넌트
import { parseAmount, formatQuantity } from './utils.js';
import { formatMoney, formatKrwMoney } from './currency.js';

let lastDashboardData = null;

// 토스증권 포트폴리오 데이터 갱신
export async function fetchHoldings() {
  try {
    const res = await fetch('/api/holdings');
    const data = await res.json();

    if (data.status === 'success') {
      console.debug("토스 원본 응답:", data.raw);
      renderDashboard(data);
    } else {
      console.error("포트폴리오 조회 실패:", data.message);
    }
  } catch (err) {
    console.error("포트폴리오 조회 오류:", err);
  }
}

// 통화 전환 시 마지막 데이터로 다시 그리기
export function rerenderDashboard() {
  if (lastDashboardData) renderDashboard(lastDashboardData);
}

// 요약 카드 렌더링
function renderSummary(summary) {
  document.getElementById('totalAsset').innerText = formatMoney(summary.total_asset);
  document.getElementById('totalBuy').innerText = formatMoney(summary.total_buy);
  document.getElementById('depositKrw').innerText = formatKrwMoney(summary.deposit_krw);

  const pnl = parseAmount(summary.total_pnl);
  const pnlRate = parseAmount(summary.total_pnl_rate);
  const pnlElem = document.getElementById('totalPnl');
  pnlElem.innerText = `${formatMoney(pnl, true)} (${pnlRate.toFixed(2)}%)`;
  pnlElem.className = `sub-value ${pnl >= 0 ? 'up' : 'down'}`;
}

// 보유 종목 테이블 한 행
function holdingRow(item) {
  const itemPnl = parseAmount(item.pnl);
  const itemRate = parseAmount(item.pnl_rate);
  const pnlClass = itemPnl >= 0 ? 'up' : 'down';
  const ticker = item.symbol || item.code || '';

  return `
    <tr data-ticker="${ticker}" title="클릭하여 차트 확인">
      <td>
        <div style="font-weight: 600;">${item.name}</div>
        <div style="font-size: 0.8rem; color: var(--subtext);">${ticker}</div>
      </td>
      <td>${formatQuantity(item.quantity)} 주</td>
      <td>${formatMoney(item.avg_buy_price)}</td>
      <td>${formatMoney(item.current_price)}</td>
      <td>${formatMoney(item.eval_amount)}</td>
      <td class="${pnlClass}" style="font-weight: 600;">
        ${formatMoney(itemPnl, true)}<br>
        <span style="font-size: 0.8rem;">(${itemRate.toFixed(2)}%)</span>
      </td>
    </tr>
  `;
}

// 대시보드 렌더링
function renderDashboard(data) {
  lastDashboardData = data;
  const summary = data.summary || {};
  const holdings = data.holdings || [];

  renderSummary(summary);

  const tbody = document.getElementById('holdingBody');
  if (holdings.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 20px; color: var(--subtext);">보유 중인 주식이 없습니다.</td></tr>';
    return;
  }

  tbody.innerHTML = holdings.map(holdingRow).join('');

  const now = new Date();
  document.getElementById('updateTime').innerText = `최근 갱신: ${now.toLocaleTimeString()}`;
}

// onSelectTicker: 보유 종목 행 클릭 시 호출 (차트 연동)
export function initPortfolio({ onSelectTicker }) {
  document.getElementById('refreshHoldings').addEventListener('click', fetchHoldings);
  document.getElementById('holdingBody').addEventListener('click', e => {
    const row = e.target.closest('tr[data-ticker]');
    if (row && row.dataset.ticker) onSelectTicker(row.dataset.ticker);
  });

  fetchHoldings();
  setInterval(fetchHoldings, 5000); // 5초 주기 보유자산 자동 갱신
}

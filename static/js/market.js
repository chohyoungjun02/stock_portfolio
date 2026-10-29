// 오늘의 시장 키워드 + 주요 지수 컴포넌트
import { formatNumber } from './utils.js';

async function fetchMarket() {
  try {
    const res = await fetch('/api/market');
    const data = await res.json();
    if (data.status !== 'success') throw new Error(data.message);
    renderMarket(data);
  } catch (err) {
    console.error("시장 현황 조회 오류:", err);
    document.getElementById('marketKeywords').innerHTML =
      '<span style="color: var(--subtext);">시장 데이터를 불러오지 못했어요.</span>';
  }
}

function renderMarket(data) {
  document.getElementById('marketAsOf').innerText = `${data.as_of} 기준`;

  document.getElementById('marketKeywords').innerHTML = data.keywords.map(k => `
    <div class="keyword ${k.tone}">
      <b>#${k.text}</b>
      <small>${k.desc}</small>
    </div>`).join('') || '<span style="color: var(--subtext);">특별한 변화가 없어요.</span>';

  document.getElementById('marketIndices').innerHTML = data.indices.map(i => {
    const cls = i.change_pct > 0 ? 'up' : i.change_pct < 0 ? 'down' : '';
    return `
      <div class="index-tile">
        <div class="name">${i.name}</div>
        <div class="price">${formatNumber(i.price, 2)}</div>
        <div class="chg ${cls}">${i.change_pct > 0 ? '+' : ''}${formatNumber(i.change_pct, 2)}%</div>
      </div>`;
  }).join('');
}

export function initMarket() {
  fetchMarket();
  setInterval(fetchMarket, 5 * 60 * 1000); // 서버 캐시 주기(5분)에 맞춰 갱신
}

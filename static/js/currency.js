// 달러 ↔ 원화 표시 전환 컴포넌트
import { parseAmount, formatNumber } from './utils.js';

// 통화 표시 상태 (기본값: 달러)
let displayCurrency = 'USD';
let usdKrwRate = null;

// 달러 금액을 현재 선택된 통화로 표시 (signed: +/- 부호 표시)
export function formatMoney(usdVal, signed = false) {
  let v = parseAmount(usdVal);
  let text;
  if (displayCurrency === 'KRW' && usdKrwRate) {
    v = v * usdKrwRate;
    text = `${formatNumber(Math.abs(v))} 원`;
  } else {
    text = `$${formatNumber(Math.abs(v), 2)}`;
  }
  const sign = v < 0 ? '-' : (signed ? '+' : '');
  return sign + text;
}

// 원화 금액(예수금 등)을 현재 선택된 통화로 표시
export function formatKrwMoney(krwVal) {
  const v = parseAmount(krwVal);
  if (displayCurrency === 'USD' && usdKrwRate) {
    return `$${formatNumber(v / usdKrwRate, 2)}`;
  }
  return `${formatNumber(v)} 원`;
}

// 달러/원 환율 조회
export async function fetchFxRate() {
  try {
    const res = await fetch('/api/fx');
    const data = await res.json();
    if (data.status === 'success') {
      usdKrwRate = data.usd_krw;
      document.getElementById('fxRateText').innerText =
        `환율 1$ = ${formatNumber(usdKrwRate, 2)}원${data.stale ? ' (지연)' : ''}`;
    }
  } catch (err) {
    console.error("환율 조회 오류:", err);
  }
}

// 달러 ↔ 원화 전환 (전환 후 onChange 호출로 화면 다시 그림)
async function toggleCurrency(onChange) {
  if (displayCurrency === 'USD') {
    if (!usdKrwRate) await fetchFxRate();
    if (!usdKrwRate) {
      alert('환율 정보를 불러오지 못해 원화로 전환할 수 없습니다.');
      return;
    }
    displayCurrency = 'KRW';
  } else {
    displayCurrency = 'USD';
  }
  document.getElementById('currencyToggle').innerText =
    displayCurrency === 'USD' ? '원화로 보기 (₩)' : '달러로 보기 ($)';
  onChange();
}

export function initCurrency({ onChange }) {
  document.getElementById('currencyToggle').addEventListener('click', () => toggleCurrency(onChange));
  fetchFxRate();
  setInterval(fetchFxRate, 60000); // 1분 주기 환율 갱신
}

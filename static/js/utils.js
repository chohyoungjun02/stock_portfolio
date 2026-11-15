// 공통 숫자 변환 / 포맷 유틸

export function parseAmount(val) {
  if (!val) return 0;
  return parseFloat(String(val).replace(/,/g, '')) || 0;
}

export function formatNumber(val, decimals = 0) {
  return Number(val).toLocaleString('ko-KR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

// 소수점 주식 수량 표시 (최대 소수점 6자리)
export function formatQuantity(val) {
  return Number(parseAmount(val).toFixed(6)).toLocaleString('ko-KR', { maximumFractionDigits: 6 });
}

// API 서버 주소: 같은 서버면 '' (Flask), 앱인토스 미니앱 번들은 index.html에서 window.API_BASE로 지정
export const API_BASE = window.API_BASE || '';

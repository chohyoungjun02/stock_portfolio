// 한글 종목명 ↔ 티커 변환
// shortcut: 자주 찾는 종목만 담은 고정 목록, 종목이 늘면 서버의 종목 검색 API로 교체
const NAME_TO_SYMBOL = {
  '엔비디아': 'NVDA', '테슬라': 'TSLA', '애플': 'AAPL', '마이크로소프트': 'MSFT', '마소': 'MSFT',
  '구글': 'GOOGL', '알파벳': 'GOOGL', '아마존': 'AMZN', '메타': 'META', '넷플릭스': 'NFLX',
  'AMD': 'AMD', '브로드컴': 'AVGO', '인텔': 'INTC', '퀄컴': 'QCOM', 'TSMC': 'TSM', '마이크론': 'MU',
  '팔란티어': 'PLTR', '코인베이스': 'COIN', '마이크로스트래티지': 'MSTR', '스트래티지': 'MSTR',
  '아이온큐': 'IONQ', '리게티': 'RGTI', '오라클': 'ORCL', '세일즈포스': 'CRM', '어도비': 'ADBE',
  '우버': 'UBER', '쇼피파이': 'SHOP', '버크셔': 'BRK-B', '코카콜라': 'KO', '디즈니': 'DIS',
  '나스닥100': 'QQQ', 'S&P500': 'SPY', '나스닥2배': 'QLD', '나스닥3배': 'TQQQ',
  '반도체3배': 'SOXL', '반도체인버스3배': 'SOXS',
  '삼성전자': '005930.KS', 'SK하이닉스': '000660.KS', '하이닉스': '000660.KS',
  'LG에너지솔루션': '373220.KS', '삼성바이오로직스': '207940.KS', '현대차': '005380.KS',
  '기아': '000270.KS', '셀트리온': '068270.KS', 'NAVER': '035420.KS', '네이버': '035420.KS',
  '카카오': '035720.KS', 'KB금융': '105560.KS', 'POSCO홀딩스': '005490.KS', '포스코홀딩스': '005490.KS',
  'LG화학': '051910.KS', '삼성SDI': '006400.KS', '한화에어로스페이스': '012450.KS',
  '두산에너빌리티': '034020.KS', 'HD현대중공업': '329180.KS', '에코프로': '086520.KQ',
  '에코프로비엠': '247540.KQ', '알테오젠': '196170.KQ',
};

// 공백 제거 + 대문자로 맞춰 비교 ("sk 하이닉스" → "SK하이닉스")
const norm = s => s.replace(/\s+/g, '').toUpperCase();
const LOOKUP = Object.fromEntries(Object.entries(NAME_TO_SYMBOL).map(([k, v]) => [norm(k), v]));
const SYMBOL_TO_NAME = {};
Object.entries(NAME_TO_SYMBOL).forEach(([k, v]) => { SYMBOL_TO_NAME[v] ??= k; });  // 먼저 나온 이름이 대표명

// 한글 이름이면 티커로, 아니면 입력 그대로(티커로 간주)
export function resolveSymbol(input) {
  return LOOKUP[norm(input)] || input.trim().toUpperCase();
}

// 이름 → 티커, 모르는 이름이면 null
export function findSymbol(name) {
  return LOOKUP[norm(name)] || null;
}

// 티커 → 대표 한글 이름, 없으면 티커
export function displayName(symbol) {
  return SYMBOL_TO_NAME[symbol] || symbol;
}

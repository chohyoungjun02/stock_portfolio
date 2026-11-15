// 한글 종목명 ↔ 티커 변환
// 국내: KRX 전체 상장사 목록(static/data/krx_symbols.json, scripts/build_krx_symbols.py로 생성)
// 해외: 아래 직접 정리한 목록 (해외 종목 한글명은 공식 자료가 없음)
// shortcut: 해외는 주요 종목만 지원, 목록에 없는 종목은 티커로 검색
const US_NAMES = {
  // 빅테크·반도체
  '엔비디아': 'NVDA', '테슬라': 'TSLA', '애플': 'AAPL', '마이크로소프트': 'MSFT', '마소': 'MSFT',
  '구글': 'GOOGL', '알파벳': 'GOOGL', '아마존': 'AMZN', '메타': 'META', '페이스북': 'META', '넷플릭스': 'NFLX',
  'AMD': 'AMD', '브로드컴': 'AVGO', '인텔': 'INTC', '퀄컴': 'QCOM', 'TSMC': 'TSM', '마이크론': 'MU',
  'ASML': 'ASML', 'ARM': 'ARM', '암홀딩스': 'ARM', '어플라이드머티리얼즈': 'AMAT', '램리서치': 'LRCX',
  'KLA': 'KLAC', '텍사스인스트루먼트': 'TXN', '마벨': 'MRVL', '마벨테크놀로지': 'MRVL',
  '슈퍼마이크로컴퓨터': 'SMCI', '슈마컴': 'SMCI', '온세미': 'ON', '아날로그디바이스': 'ADI',
  '시놉시스': 'SNPS', '케이던스': 'CDNS', '글로벌파운드리스': 'GFS', '웨스턴디지털': 'WDC', '샌디스크': 'SNDK',
  '시게이트': 'STX', '델': 'DELL', 'HP': 'HPQ', '휴렛팩커드엔터프라이즈': 'HPE', 'IBM': 'IBM', '시스코': 'CSCO',
  '아리스타네트웍스': 'ANET', '버티브': 'VRT', '코어위브': 'CRWV', '네비우스': 'NBIS',
  // 소프트웨어·인터넷
  '팔란티어': 'PLTR', '오라클': 'ORCL', '세일즈포스': 'CRM', '어도비': 'ADBE', '서비스나우': 'NOW',
  '스노우플레이크': 'SNOW', '크라우드스트라이크': 'CRWD', '팔로알토': 'PANW', '팔로알토네트웍스': 'PANW',
  '데이터독': 'DDOG', '몽고DB': 'MDB', '유니티': 'U', '로블록스': 'RBLX', '쇼피파이': 'SHOP',
  '우버': 'UBER', '에어비앤비': 'ABNB', '도어대시': 'DASH', '스포티파이': 'SPOT', '줌': 'ZM',
  '페이팔': 'PYPL', '블록': 'XYZ', '로빈후드': 'HOOD', '소파이': 'SOFI', '쿠팡': 'CPNG', '앱러빈': 'APP',
  '레딧': 'RDDT', '핀터레스트': 'PINS', '스냅': 'SNAP', '인튜이트': 'INTU', '오토데스크': 'ADSK',
  '템퍼스AI': 'TEM', '사운드하운드': 'SOUN', '빅베어AI': 'BBAI', '듀오링고': 'DUOL',
  // 가상자산·양자·우주·원전
  '코인베이스': 'COIN', '마이크로스트래티지': 'MSTR', '스트래티지': 'MSTR', '마라홀딩스': 'MARA',
  '라이엇플랫폼': 'RIOT', '서클': 'CRCL', '아이온큐': 'IONQ', '리게티': 'RGTI', '리게티컴퓨팅': 'RGTI',
  '디웨이브': 'QBTS', '디웨이브퀀텀': 'QBTS', '퀀텀컴퓨팅': 'QUBT', '로켓랩': 'RKLB', 'AST스페이스모바일': 'ASTS',
  '오클로': 'OKLO', '뉴스케일파워': 'SMR', '센트러스에너지': 'LEU', '컨스텔레이션에너지': 'CEG', '비스트라': 'VST',
  // 소비재·헬스케어·금융·산업
  '버크셔': 'BRK-B', '버크셔해서웨이': 'BRK-B', 'JP모건': 'JPM', '골드만삭스': 'GS', '모건스탠리': 'MS',
  '뱅크오브아메리카': 'BAC', '웰스파고': 'WFC', '비자': 'V', '마스터카드': 'MA', '아메리칸익스프레스': 'AXP',
  '블랙록': 'BLK', '코카콜라': 'KO', '펩시': 'PEP', '펩시코': 'PEP', '맥도날드': 'MCD', '스타벅스': 'SBUX',
  '나이키': 'NKE', '월마트': 'WMT', '코스트코': 'COST', '타깃': 'TGT', '홈디포': 'HD', '디즈니': 'DIS',
  '프록터앤드갬블': 'PG', 'P&G': 'PG', '존슨앤드존슨': 'JNJ', '일라이릴리': 'LLY', '릴리': 'LLY',
  '노보노디스크': 'NVO', '화이자': 'PFE', '머크': 'MRK', '애브비': 'ABBV', '유나이티드헬스': 'UNH',
  '모더나': 'MRNA', '인튜이티브서지컬': 'ISRG', '히모스헬스': 'HIMS', '보잉': 'BA', '록히드마틴': 'LMT',
  '캐터필러': 'CAT', 'GE에어로스페이스': 'GE', 'GE버노바': 'GEV', '엑손모빌': 'XOM', '셰브론': 'CVX',
  '포드': 'F', 'GM': 'GM', '제너럴모터스': 'GM', '리비안': 'RIVN', '루시드': 'LCID', '니오': 'NIO',
  '알리바바': 'BABA', '바이두': 'BIDU', 'PDD': 'PDD', '테무': 'PDD', 'AT&T': 'T', '버라이즌': 'VZ',
  // ETF
  '나스닥100': 'QQQ', 'S&P500': 'SPY', '다우존스': 'DIA', '러셀2000': 'IWM', '나스닥2배': 'QLD',
  '나스닥3배': 'TQQQ', '나스닥인버스3배': 'SQQQ', 'S&P500 3배': 'UPRO', '반도체': 'SOXX',
  '반도체3배': 'SOXL', '반도체인버스3배': 'SOXS', '테슬라2배': 'TSLL', '엔비디아2배': 'NVDL',
  '미국채20년': 'TLT', '미국채20년3배': 'TMF', '금ETF': 'GLD', '은ETF': 'SLV', '배당다우존스': 'SCHD',
  '슈드': 'SCHD', '제피': 'JEPI', '제피큐': 'JEPQ', '비트코인ETF': 'IBIT', '아크': 'ARKK',
};

// 국내 종목의 흔한 줄임말·옛 이름 (KRX 목록에는 정식 이름만 있음)
const KR_ALIASES = {
  '현대차': '005380.KS', '하이닉스': '000660.KS', '네이버': '035420.KS', '포스코홀딩스': '005490.KS',
  '삼바': '207940.KS', '엘지에너지솔루션': '373220.KS', '엘지화학': '051910.KS', '엘지전자': '066570.KS',
  '한화에어로': '012450.KS', '현대모비스': '012330.KS', '삼성바이오': '207940.KS', '카뱅': '323410.KS',
};

// 공백 제거 + 대문자로 맞춰 비교 ("sk 하이닉스" → "SK하이닉스")
const norm = s => s.replace(/\s+/g, '').toUpperCase();

let krx = {};
try {
  // 이 파일 기준 상대 경로라 Flask와 미니앱 번들 양쪽에서 맞음
  krx = await (await fetch(new URL('../data/krx_symbols.json', import.meta.url))).json();
} catch (err) {
  console.error('국내 종목 목록 로드 실패 (해외 목록만 사용):', err);
}

// 직접 정리한 이름이 KRX 이름과 겹치면 직접 정리한 쪽 우선
const ALL = { ...krx, ...KR_ALIASES, ...US_NAMES };
const LOOKUP = Object.fromEntries(Object.entries(ALL).map(([k, v]) => [norm(k), v]));
const SYMBOL_TO_NAME = {};
// 대표명: 해외는 먼저 나온 이름, 국내는 KRX 정식 이름
[...Object.entries(US_NAMES), ...Object.entries(krx)].forEach(([k, v]) => { SYMBOL_TO_NAME[v] ??= k; });

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

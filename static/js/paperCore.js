// 모의투자 계산 (화면·저장과 분리된 순수 함수, tests/paper_core.test.mjs로 검증)
// 금액은 모두 원 단위 정수, 해외 종목은 거래 시점 환율로 원화 환산해 기록
export const START_CASH = 30_000_000;
const MAX_TRADES = 200;  // 거래 내역은 최근 것만 보관 (localStorage 용량 보호)

export function newAccount() {
  return { cash: START_CASH, holdings: {}, trades: [] };
}

function checkOrder(qty, priceKrw) {
  if (!Number.isInteger(qty) || qty <= 0) throw new Error('수량은 1주 이상의 정수로 입력해 주세요.');
  if (!(priceKrw > 0)) throw new Error('현재가를 불러오지 못했어요.');
}

function record(acc, trade) {
  return [trade, ...acc.trades].slice(0, MAX_TRADES);
}

// 새 계좌 객체를 반환 (원래 계좌는 그대로), 불가능하면 Error
export function buy(acc, symbol, qty, priceKrw, time = Date.now()) {
  checkOrder(qty, priceKrw);
  const cost = Math.round(qty * priceKrw);
  if (cost > acc.cash) throw new Error(`현금이 부족해요. (필요 ${cost.toLocaleString('ko-KR')}원)`);
  const h = acc.holdings[symbol] || { qty: 0, cost: 0 };
  return {
    cash: acc.cash - cost,
    holdings: { ...acc.holdings, [symbol]: { qty: h.qty + qty, cost: h.cost + cost } },
    trades: record(acc, { time, side: 'buy', symbol, qty, price: priceKrw, amount: cost }),
  };
}

export function sell(acc, symbol, qty, priceKrw, time = Date.now()) {
  checkOrder(qty, priceKrw);
  const h = acc.holdings[symbol];
  if (!h || qty > h.qty) throw new Error(`보유 수량(${h ? h.qty : 0}주)보다 많이 팔 수 없어요.`);
  const amount = Math.round(qty * priceKrw);
  const soldCost = Math.round(h.cost * qty / h.qty);  // 평균 단가 기준으로 원가를 덜어냄
  const holdings = { ...acc.holdings };
  if (qty === h.qty) delete holdings[symbol];
  else holdings[symbol] = { qty: h.qty - qty, cost: h.cost - soldCost };
  return {
    cash: acc.cash + amount,
    holdings,
    trades: record(acc, { time, side: 'sell', symbol, qty, price: priceKrw, amount, profit: amount - soldCost }),
  };
}

// prices: {심볼: 원화 현재가}, 시세가 없는 종목은 원가로 평가
export function summarize(acc, prices) {
  const rows = Object.entries(acc.holdings).map(([symbol, h]) => {
    const price = prices[symbol];
    const value = price ? Math.round(h.qty * price) : h.cost;
    return {
      symbol, qty: h.qty, avgPrice: h.cost / h.qty, price: price ?? null,
      value, profit: value - h.cost, returnPct: (value / h.cost - 1) * 100,
    };
  });
  const stockValue = rows.reduce((sum, r) => sum + r.value, 0);
  const total = acc.cash + stockValue;
  return {
    cash: acc.cash, stockValue, total,
    profit: total - START_CASH, returnPct: (total / START_CASH - 1) * 100, rows,
  };
}

// 저장된 값이 깨졌거나 형식이 다르면 새 계좌
export function restore(saved) {
  const ok = saved && Number.isFinite(saved.cash) && saved.holdings && typeof saved.holdings === 'object'
    && Array.isArray(saved.trades)
    && Object.values(saved.holdings).every(h => Number.isInteger(h.qty) && h.qty > 0 && Number.isFinite(h.cost));
  return ok ? saved : newAccount();
}

// 주문창 미리보기: 최대 수량, 평균 단가, 주문 후 예상(구매: 새 평균 / 판매: 실현 손익)
export function preview(acc, symbol, side, qty, priceKrw) {
  const h = acc.holdings[symbol] || { qty: 0, cost: 0 };
  const max = side === 'buy' ? (priceKrw > 0 ? Math.floor(acc.cash / priceKrw) : 0) : h.qty;
  const q = Math.max(0, Math.min(qty || 0, max));
  const total = Math.round(q * priceKrw) || 0;
  const avg = h.qty ? h.cost / h.qty : null;
  const after = side === 'buy'
    ? (h.qty + q ? (h.cost + total) / (h.qty + q) : null)
    : (q ? total - Math.round(h.cost * q / h.qty) : null);
  return { max, avg, after, total: Math.round((qty || 0) * priceKrw) || 0 };
}

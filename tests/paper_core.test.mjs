// 모의투자 계산 테스트 (실행: node tests/paper_core.test.mjs)
import assert from 'node:assert/strict';
import { START_CASH, newAccount, buy, sell, summarize, restore } from '../static/js/paperCore.js';

const throwsMsg = (fn, re) => assert.throws(fn, err => re.test(err.message));

// 매수: 현금 차감, 원가 누적, 원본 계좌는 그대로
let a = newAccount();
assert.equal(a.cash, 30_000_000);
const b = buy(a, 'NVDA', 10, 200_000.4, 1);
assert.equal(a.cash, START_CASH);
assert.equal(b.cash, START_CASH - 2_000_004);
assert.deepEqual(b.holdings.NVDA, { qty: 10, cost: 2_000_004 });

// 추가 매수 → 평균 단가
a = buy(b, 'NVDA', 10, 100_000, 2);
assert.deepEqual(a.holdings.NVDA, { qty: 20, cost: 3_000_004 });

// 평가: 현재가 150,000원 → 3,000,000원, 원가 대비 -4원
let s = summarize(a, { NVDA: 150_000 });
assert.equal(s.stockValue, 3_000_000);
assert.equal(s.total, START_CASH - 4);
assert.equal(s.rows[0].profit, -4);

// 일부 매도: 평균 단가만큼 원가를 덜고 실현 손익 기록
a = sell(a, 'NVDA', 5, 200_000, 3);
assert.deepEqual(a.holdings.NVDA, { qty: 15, cost: 3_000_004 - 750_001 });
assert.equal(a.trades[0].profit, 1_000_000 - 750_001);

// 전량 매도 → 보유에서 사라짐, 총자산 = 현금
a = sell(a, 'NVDA', 15, 100_000, 4);
assert.equal(a.holdings.NVDA, undefined);
s = summarize(a, {});
assert.equal(s.total, a.cash);
assert.equal(a.trades.length, 4);
assert.equal(a.trades[0].side, 'sell');

// 잘못된 주문
throwsMsg(() => buy(newAccount(), 'NVDA', 0, 1000), /1주 이상/);
throwsMsg(() => buy(newAccount(), 'NVDA', 1.5, 1000), /정수/);
throwsMsg(() => buy(newAccount(), 'NVDA', 1, 0), /현재가/);
throwsMsg(() => buy(newAccount(), 'NVDA', 1, 30_000_001), /현금이 부족/);
throwsMsg(() => sell(newAccount(), 'NVDA', 1, 1000), /보유 수량\(0주\)/);
throwsMsg(() => sell(buy(newAccount(), 'NVDA', 2, 1000), 'NVDA', 3, 1000), /보유 수량\(2주\)/);

// 시세 없는 종목은 원가로 평가
s = summarize(buy(newAccount(), 'AAPL', 2, 1000), {});
assert.equal(s.rows[0].value, 2000);
assert.equal(s.rows[0].price, null);

// 저장값 복구: 깨진 값은 새 계좌
assert.deepEqual(restore(null), newAccount());
assert.deepEqual(restore({ cash: 'x', holdings: {}, trades: [] }), newAccount());
assert.deepEqual(restore({ cash: 1, holdings: { A: { qty: -1, cost: 1 } }, trades: [] }), newAccount());
const saved = buy(newAccount(), 'NVDA', 1, 1000);
assert.equal(restore(saved), saved);

console.log('paper core tests OK');

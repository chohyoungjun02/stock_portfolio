// 기술적 분석 요약 패널 컴포넌트
import { formatNumber } from './utils.js';

// 패널에 안내/오류 문구만 표시
export function renderAnalysisMessage(message) {
  document.getElementById('analysisPanel').innerHTML =
    `<div style="color: var(--subtext);">${message}</div>`;
}

// 지표 요약 & 강세/약세 판단 패널
export function renderAnalysis(s, signals) {
  const panel = document.getElementById('analysisPanel');
  if (!s) {
    panel.innerHTML = '<div style="color: var(--subtext);">지표를 계산할 데이터가 부족합니다.</div>';
    return;
  }

  const fmt = (v, d = 2) => (v === null || v === undefined) ? '-' : formatNumber(v, d);
  const verdictClass = !s.verdict ? 'neutral'
    : s.verdict.includes('강세') ? 'bull'
    : s.verdict.includes('약세') ? 'bear' : 'neutral';
  const changeClass = s.change_pct >= 0 ? 'up' : 'down';

  // 최근 신호 5개 (최신순)
  const recent = signals.slice(-5).reverse();
  const lastBuy = [...signals].reverse().find(x => x.type === 'buy');

  panel.innerHTML = `
    <div class="analysis-top">
      <div>
        <div class="verdict-badge ${verdictClass}">${s.verdict || '판단 불가'}</div>
        <div style="font-size: 0.85rem; color: var(--subtext); margin-top: 6px;">
          추세 점수 ${s.score !== undefined ? (s.score > 0 ? '+' : '') + s.score : '-'} / ±6
        </div>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 1.4rem; font-weight: 700;">$${fmt(s.close)}</div>
        <div class="${changeClass}" style="font-size: 0.9rem;">${s.change_pct >= 0 ? '+' : ''}${fmt(s.change_pct)}%</div>
      </div>
    </div>

    <div class="metric-grid">
      <div class="metric"><span>MA20</span><b style="color:#facc15;">${fmt(s.ma20)}</b></div>
      <div class="metric"><span>MA60</span><b style="color:#22c55e;">${fmt(s.ma60)}</b></div>
      <div class="metric"><span>MA120</span><b style="color:#e879f9;">${fmt(s.ma120)}</b></div>
      <div class="metric"><span>RSI (14)</span><b>${fmt(s.rsi)}</b></div>
      <div class="metric"><span>MACD / 시그널</span><b>${fmt(s.macd, 3)} / ${fmt(s.macd_signal, 3)}</b></div>
      <div class="metric"><span>볼린저 상단 / 하단</span><b>${fmt(s.bb_upper)} / ${fmt(s.bb_lower)}</b></div>
      <div class="metric"><span>52주 최고 / 최저</span><b>${fmt(s.high_52w)} / ${fmt(s.low_52w)}</b></div>
      <div class="metric"><span>거래량 (20일 평균 대비)</span><b>${s.volume_ratio ? fmt(s.volume_ratio) + '배' : '-'}</b></div>
    </div>

    <div class="analysis-cols">
      <div>
        <div class="analysis-sub">판단 근거</div>
        <ul class="reason-list">
          ${(s.reasons || []).map(r => `<li class="${r.bullish ? 'bull' : 'bear'}">${r.bullish ? '▲' : '▼'} ${r.text}</li>`).join('') || '<li>-</li>'}
          ${(s.warnings || []).map(w => `<li class="warn">⚠ ${w}</li>`).join('')}
        </ul>
      </div>
      <div>
        <div class="analysis-sub">최근 진입 / 주의 신호</div>
        <ul class="reason-list">
          ${recent.map(x => `
            <li class="${x.type === 'buy' ? 'bull' : 'bear'}">
              ${x.time} · <b>${x.type === 'buy' ? '진입' : '주의'}</b> ${x.label}
              <div style="font-size: 0.75rem; color: var(--subtext);">${x.desc}</div>
            </li>`).join('') || '<li>최근 신호 없음</li>'}
        </ul>
        ${lastBuy ? `<div style="font-size: 0.8rem; color: var(--subtext); margin-top: 6px;">마지막 진입 신호: ${lastBuy.time} (${lastBuy.label})</div>` : ''}
      </div>
    </div>
    <div class="disclaimer">※ 기술적 지표를 기계적으로 계산한 참고용 정보이며, 투자 권유나 수익을 보장하지 않습니다.</div>
  `;
}

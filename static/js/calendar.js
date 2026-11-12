// 경제 일정 (뉴스 탭 오른쪽 패널)
const escapeHtml = s => String(s ?? '').replace(/[&<>"']/g,
  c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토'];

// "2026-11-18" → { label: "11월 18일 (수)", dday: "D-6" } (브라우저 현지 날짜 기준)
function dayInfo(iso) {
  const [y, m, d] = iso.split('-').map(Number);
  const day = new Date(y, m - 1, d);
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const diff = Math.round((day - today) / 86400000);
  return { label: `${m}월 ${d}일 (${WEEKDAYS[day.getDay()]})`, dday: diff === 0 ? '오늘' : `D-${diff}`, isToday: diff === 0 };
}

function renderEvent(e) {
  const tag = e.type === 'fomc' ? '금리' : '실적';
  const body = `<b>${escapeHtml(e.title)}</b><small>${escapeHtml(e.desc)}</small>`;
  // 실적 일정은 누르면 그 종목 차트로 이동
  const content = e.symbol
    ? `<button type="button" data-symbol="${escapeHtml(e.symbol)}" title="차트 보기">${body}</button>`
    : `<div>${body}</div>`;
  return `<div class="cal-event ${e.type}"><span class="tag">${tag}</span>${content}</div>`;
}

async function fetchCalendar() {
  const box = document.getElementById('calendarList');
  try {
    const res = await fetch('/api/calendar');
    const data = await res.json();
    if (data.status !== 'success') throw new Error(data.message);
    const byDate = {};
    data.events.forEach(e => (byDate[e.date] ??= []).push(e));
    box.innerHTML = Object.entries(byDate).map(([iso, events]) => {
      const info = dayInfo(iso);
      return `
        <div class="cal-day ${info.isToday ? 'today' : ''}">
          <h4>${info.label}<small>${info.dday}</small></h4>
          ${events.map(renderEvent).join('')}
        </div>`;
    }).join('') || '<span style="color: var(--subtext);">앞으로 60일 안의 일정이 없어요.</span>';
  } catch (err) {
    console.error("경제 일정 조회 오류:", err);
    box.innerHTML = '<span style="color: var(--subtext);">일정을 불러오지 못했어요.</span>';
  }
}

export function initCalendar({ onSelectChart }) {
  document.getElementById('calendarList').addEventListener('click', e => {
    const btn = e.target.closest('button[data-symbol]');
    if (btn) onSelectChart(btn.dataset.symbol);
  });
  fetchCalendar();
}

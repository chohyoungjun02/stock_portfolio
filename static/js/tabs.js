// 차트 분석 / 뉴스 탭 전환
export function showTab(id) {
  document.querySelectorAll('.tab').forEach(t => {
    const active = t.dataset.tab === id;
    t.classList.toggle('active', active);
    t.setAttribute('aria-selected', active);
    document.getElementById(t.dataset.tab).hidden = !active;
  });
}

export function initTabs() {
  document.querySelectorAll('.tab').forEach(tab =>
    tab.addEventListener('click', () => showTab(tab.dataset.tab)));
}

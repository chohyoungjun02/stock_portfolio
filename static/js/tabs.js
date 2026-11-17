// 상단 탭(차트 분석 / 뉴스 / 모의투자) + 모의투자 안의 하위 탭 전환
export function showTab(id) {
  document.querySelectorAll('.tab').forEach(t => {
    const active = t.dataset.tab === id;
    t.classList.toggle('active', active);
    t.setAttribute('aria-selected', active);
    document.getElementById(t.dataset.tab).hidden = !active;
  });
  document.dispatchEvent(new CustomEvent('tabchange', { detail: id }));  // 탭을 열 때 데이터 갱신용
}

export function showSubTab(id) {
  document.querySelectorAll('.subtab').forEach(t => {
    const active = t.dataset.sub === id;
    t.classList.toggle('active', active);
    t.setAttribute('aria-selected', active);
    document.getElementById(t.dataset.sub).hidden = !active;
  });
}

export function initTabs() {
  document.querySelectorAll('.tab').forEach(tab =>
    tab.addEventListener('click', () => showTab(tab.dataset.tab)));
  document.querySelectorAll('.subtab').forEach(tab =>
    tab.addEventListener('click', () => showSubTab(tab.dataset.sub)));
}

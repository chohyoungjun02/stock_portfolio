// 대시보드 진입점: 각 컴포넌트 초기화 및 연결
import { initCalendar } from './calendar.js';
import { initChart, initChartSearch, loadCandles, getCurrentSymbol } from './chart.js';
import { initCompare } from './compare.js';
import { initMarket } from './market.js';
import { initNews, searchNews } from './news.js';
import { initPaper, prefillOrder } from './paper.js';
import { initTabs, showTab, showSubTab } from './tabs.js';
import { initWatchlist } from './watchlist.js';

// 뉴스·관심 종목·경제 일정에서 종목을 고르면 차트 탭으로 이동
function openChart(symbol) {
  showTab('chartTab');
  loadCandles(symbol);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// type="module" 스크립트는 DOM 파싱 후 실행됨
initTabs();
initWatchlist({ onSelectChart: openChart, onSelectNews: searchNews });  // 첫 차트 로드 전에 별표 이벤트 연결
initChart();
initChartSearch();
loadCandles(getCurrentSymbol());

initMarket();
initNews({ onSelectChart: openChart });
initCalendar({ onSelectChart: openChart });
initCompare();
initPaper();

// 차트 화면의 '모의로 사기' → 모의투자 탭 주문창에 현재 종목 채우기
document.getElementById('paperBuyBtn').addEventListener('click', () => {
  showTab('investTab');
  showSubTab('paperPanel');
  prefillOrder(getCurrentSymbol());
});

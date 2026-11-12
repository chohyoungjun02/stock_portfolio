// 대시보드 진입점: 각 컴포넌트 초기화 및 연결
import { initChart, initChartSearch, loadCandles, getCurrentSymbol } from './chart.js';
import { initMarket } from './market.js';
import { initNews, searchNews } from './news.js';
import { initTabs, showTab } from './tabs.js';
import { initWatchlist } from './watchlist.js';

// 뉴스·관심 종목에서 종목을 고르면 차트 탭으로 이동
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

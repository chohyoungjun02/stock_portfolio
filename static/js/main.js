// 대시보드 진입점: 각 컴포넌트 초기화 및 연결
import { initChart, initChartSearch, loadCandles, getCurrentSymbol } from './chart.js';
import { initCurrency } from './currency.js';
import { initPortfolio, rerenderDashboard } from './portfolio.js';

// type="module" 스크립트는 DOM 파싱 후 실행됨
initChart();
initChartSearch();
loadCandles(getCurrentSymbol());

initCurrency({ onChange: rerenderDashboard });
initPortfolio({ onSelectTicker: loadCandles });

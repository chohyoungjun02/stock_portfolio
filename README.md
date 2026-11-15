# 📈 주식 대시보드 — 기술적 분석 & 시장 뉴스

Yahoo Finance와 네이버 뉴스 검색 API를 연동해 **종목별 일봉 차트와 기술적 지표**, **오늘의 시장 키워드**, **종목별 주요 뉴스·경제 일정**, **종목 수익 비교**를 토스 스타일의 세 탭으로 보여주는 웹 대시보드입니다.

🔗 **데모**: https://stock-portfolio-delta.vercel.app

---

## 🚀 주요 기능

화면은 **차트 분석** / **뉴스** / **종목 비교** 세 탭으로 나뉩니다.

### 📊 차트 분석 탭
![일봉 차트 & 기술적 분석 요약](docs/images/chart_analysis.png)

* **한글 종목명 검색**: `엔비디아`, `한미반도체`, `나스닥3배`처럼 이름으로도 검색 (티커 `NVDA`, `005930.KS`도 그대로 가능)
  * 국내: KRX 상장사 목록으로 **코스피·코스닥 전 종목** (+ `현대차`, `하이닉스` 같은 줄임말)
  * 해외: 직접 정리한 **주요 종목·ETF 약 170개**, 목록에 없으면 티커로 검색
* 상장 이후 전체 일봉을 불러오고 화면에는 **최근 3개월**을 표시 (드래그로 이전 기간 확인)
* 지표: **MA20 / MA60 / MA120**, **볼린저 밴드**(20일, 2σ), **거래량**, **RSI(14)**, **MACD(12, 26, 9)**
* 일봉 · RSI · MACD 세 차트의 스크롤·줌 동기화
* 차트 위 **진입(▲) / 주의(▼) 신호**

  | 구분 | 신호 | 조건 |
  |---|---|---|
  | ▲ 진입 | 골든크로스 | 20일선이 60일선을 상향 돌파 |
  | ▲ 진입 | 과매도 탈출 | RSI가 30을 상향 돌파 |
  | ▲ 진입 | MACD 매수 | 60일선 위에서 MACD 골든크로스 |
  | ▼ 주의 | 데드크로스 | 20일선이 60일선을 하향 돌파 |
  | ▼ 주의 | 과열 해소 | RSI가 70을 하향 이탈 |
  | ▼ 주의 | MACD 매도 | 60일선 아래에서 MACD 데드크로스 |

* 오른쪽 **기술적 분석 요약**: 6가지 조건으로 추세 점수(-6 ~ +6)를 매겨 `강한 강세 / 강세 / 중립 / 약세 / 강한 약세` 판정, 판단 근거·경고·최근 신호 표시

### ⭐ 관심 종목
* 차트 제목 옆 **☆**를 누르면 관심 종목에 추가 (다시 누르면 빼기)
* 차트 탭의 관심 종목을 누르면 그 종목 차트로, 뉴스 탭의 관심 종목을 누르면 그 종목 뉴스로 이동
* 로그인 없이 **브라우저(localStorage)에 저장**되어 같은 브라우저에서 다시 열어도 유지

### 🗞 뉴스 탭
![오늘의 시장 키워드](docs/images/market_keywords.png)

* **오늘의 시장 키워드**: S&P 500, 나스닥, 다우, 필라델피아 반도체, 코스피, 코스닥, VIX, 미국 10년물 금리, 원/달러 환율, 금, WTI 유가, 비트코인의 전일 대비 변화로 `#미국 증시 강세`, `#반도체 랠리`, `#위험 선호 (Risk-on)` 같은 키워드 생성 (5분 캐시)
* **종목별 주요 뉴스**: 엔비디아, 테슬라, 애플, 마이크로소프트, 구글, 아마존, 메타, 삼성전자, SK하이닉스의 최신 뉴스 5개씩 (네이버 뉴스 검색, 10분 캐시)
* **종목 뉴스 검색**: 원하는 종목명을 검색하면 그 종목 최신 뉴스 10개
* 뉴스 카드의 **종목명을 누르면 차트 분석 탭**에서 그 종목 차트가 열림
* 오른쪽 **경제 일정** 패널: 앞으로 60일의 **FOMC 금리 결정일**과 주요 19개 종목의 **실적 발표일**을 날짜별 D-day와 함께 표시 (실적 일정을 누르면 차트로 이동, 6시간 캐시)

### ⚖️ 종목 비교 탭
* 종목 2개, 투자 금액(만원 단위), 기간을 넣으면 **같은 금액을 투자했을 때의 수익** 비교
* 종목별 수익률, 평가 금액, 수익(원)과 **수익이 더 높은 종목** 표시, 투자 금액 변화를 두 선으로 겹친 차트
* 시작일 첫 거래일 종가에 사서 종료일 마지막 거래일 종가로 평가
  * **수정주가** 기준이라 주식 분할·병합과 배당(재투자)이 반영됨
  * 해외 종목은 환율 변동 없이 주가 수익률만 반영

> ⚠️ 신호, 강세/약세 판단, 시장 키워드는 지표를 기계적으로 계산한 **참고용 정보**이며 투자 권유나 수익을 보장하지 않습니다.

---

## 🛠 기술 스택
* **Backend**: Python 3, Flask (Blueprint), pandas, yfinance, requests, python-dotenv
* **Frontend**: Jinja2 템플릿 컴포넌트, CSS, JavaScript ES 모듈, TradingView Lightweight Charts v4.1.1, Pretendard 폰트
* **Data Sources**: Yahoo Finance (일봉 시세, 환율, 주요 지수), NAVER API HUB 뉴스 검색
* **Deploy**: Vercel (Python 런타임)

---

## 🔌 API 엔드포인트

| 엔드포인트 | 설명 |
|---|---|
| `GET /` | 대시보드 화면 |
| `GET /api/candles?symbol=QLD` | 일봉, 거래량, 지표, 신호, 분석 요약 |
| `GET /api/market` | 주요 지수 시세 + 시장 키워드 (5분 캐시) |
| `GET /api/news` | 주요 종목별 최신 뉴스 (10분 캐시) |
| `GET /api/news?q=현대차` | 종목 뉴스 검색 (최대 10개) |
| `GET /api/calendar` | FOMC + 주요 종목 실적 발표 일정 (6시간 캐시) |
| `GET /api/compare?a=QQQ&b=QLD&amount=1000000&start=2025-11-12&end=2026-11-12` | 두 종목 수익 비교 (금액은 원) |
| `GET /api/fx` | 달러/원 환율 (60초 캐시) |

> 회원가입·토스증권 계좌 연동 API(`/signup`, `/login`, `/account`, `/api/holdings`)는 코드에 남아 있지만 화면에서는 쓰지 않습니다. 토스 Open API가 등록된 IP에서만 호출되어 Vercel 배포본에서는 보유 주식을 조회할 수 없기 때문입니다.

---

## ⚙️ 실행 방법

### 1. 저장소 클론 및 패키지 설치
```bash
git clone https://github.com/chohyoungjun02/stock_portfolio.git
cd stock_portfolio
python -m venv venv
venv/Scripts/activate        # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

### 2. 네이버 뉴스 API 키 설정
1. [NAVER API HUB](https://console.ncloud.com/naver-api-hub)에서 Application을 등록하고 **검색 > 뉴스** API를 추가합니다.
2. 인증 정보의 Client ID / Client Secret을 `.env`에 넣습니다 (`env_example.env` 참고).
   ```
   NAVER_CLIENT_ID=발급받은 Client ID
   NAVER_CLIENT_SECRET=발급받은 Client Secret
   ```
   키가 없으면 뉴스 영역에만 설정 안내가 표시되고, 차트·시장 키워드는 정상 동작합니다.

### 3. 서버 구동
```bash
python app.py
```
브라우저에서 `http://127.0.0.1:5000` 접속

### 4. Vercel 배포
* `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`을 Vercel 프로젝트 환경변수에 등록한 뒤 `vercel deploy --prod`
* `.env`, `instance/` 등은 `.vercelignore`로 업로드에서 제외됩니다.

### 5. 앱인토스 미니앱 (.ait) 빌드
미니앱은 화면(HTML·JS·CSS)만 `.ait` 파일로 묶고, 데이터는 배포된 서버(`https://stock-portfolio-delta.vercel.app`)의 `/api/`를 호출합니다.
```bash
cd miniapp
npm install
npm run build        # dist/ 생성 후 ait build → miniapp/<appName>.ait
```
* `miniapp/apps-in-toss.config.ts`의 `appName`을 **앱인토스 콘솔에 등록한 이름**으로 맞춰야 업로드됩니다.
* 생성된 `.ait` 파일을 콘솔에 업로드하거나 `npx ait deploy`로 올립니다.
* API 서버 주소는 `MINIAPP_API_BASE` 환경변수로 바꿀 수 있습니다 (https만 가능).
* 서버는 토스 미니앱 도메인(`*.apps.tossmini.com`, `*.private-apps.tossmini.com` 등)에서 오는 `/api/` 요청만 CORS로 허용합니다.

### 6. 국내 종목 목록 갱신
신규 상장·상장폐지를 반영하려면 가끔 다시 생성합니다.
```bash
python scripts/build_krx_symbols.py   # static/data/krx_symbols.json 갱신
```

### 7. 테스트
```bash
python tests/test_news_parse.py       # 뉴스 응답 정리·정렬, 키 미설정 처리
python tests/test_compare_calendar.py # 종목 비교 계산·입력 검증, 경제 일정 정리
python tests/test_cors.py             # 토스 미니앱 출처만 CORS 허용
python tests/test_chart_nan.py        # 장 시작 전 NaN 행이 있어도 차트 응답이 올바른 JSON인지
python tests/test_market_keywords.py  # 시장 키워드 규칙
python tests/test_auth_flow.py        # 회원가입 → 계좌 연동 흐름 (화면 미사용 기능)
```

---

## 📁 디렉터리 구조
```text
├── app.py                    # Flask 앱 생성, 설정, 블루프린트 등록
├── routes/                   # 화면·API 라우트 (Flask Blueprint)
│   ├── pages.py              #   GET /  대시보드 화면
│   ├── chart.py              #   GET /api/candles  일봉·지표·신호
│   ├── market.py             #   /api/market 시장 키워드, /api/news 뉴스, /api/calendar 경제 일정
│   ├── compare.py            #   GET /api/compare  종목 비교
│   ├── fx.py                 #   GET /api/fx  환율
│   ├── auth.py, portfolio.py #   회원·계좌 연동 (화면 미사용)
├── services/                 # 비즈니스 로직
│   ├── indicators.py         #   MA·볼린저·RSI·MACD, 신호, 강세/약세 판단
│   ├── chart.py              #   차트 응답 데이터 생성
│   ├── market.py             #   주요 지수 시세, 시장 키워드 규칙
│   ├── news.py               #   네이버 뉴스 검색, 종목별 뉴스
│   ├── economic_calendar.py  #   FOMC 일정, 실적 발표일
│   ├── compare.py            #   종목 비교 수익 계산
│   ├── fx.py                 #   달러/원 환율
│   ├── users.py, portfolio.py#   회원 DB, 토스 응답 정규화 (화면 미사용)
├── templates/
│   ├── index2.html           # 대시보드 레이아웃 (탭 2개, 컴포넌트 include)
│   └── components/           # header(탭), chart_panel, analysis_panel,
│                             # market_keywords, stock_news, economic_calendar, compare_panel
├── static/
│   ├── css/                  # base, chart, analysis, market, compare
│   ├── data/krx_symbols.json # 국내 전 종목 한글명 → 티커
│   └── js/                   # main(진입점), tabs, chart, analysis, market, news,
│                             # stocks(한글 종목명↔티커), watchlist(관심 종목), calendar, compare, utils
├── scripts/build_krx_symbols.py # KRX 상장사 목록으로 krx_symbols.json 생성
├── scripts/build_miniapp_web.py # 미니앱용 정적 웹 번들(miniapp/dist) 생성
├── miniapp/                  # 앱인토스 미니앱 프로젝트 (apps-in-toss.config.ts, package.json)
├── tests/                    # 뉴스·차트·비교·일정·시장 키워드·회원 흐름 테스트
├── docs/images/              # README 스크린샷
├── requirements.txt          # Python 패키지 목록
├── .vercelignore             # Vercel 업로드 제외 (.env, instance 등)
└── env_example.env           # 환경 변수 예시
```

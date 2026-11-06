# Discord 스타일 Yahoo Finance 마켓 대시보드

## 1. 설치

```bash
conda create -n market_yf python=3.11 -y
conda activate market_yf
pip install -r requirements.txt
```

## 2. 실행

```bash
python main.py
```

최초 실행 시 Yahoo Finance에서 1분봉과 최근 1년 일봉을 내려받는다.
기본 갱신 주기는 60초다. 네트워크 상태나 Yahoo 응답 속도에 따라 갱신 시점은 달라질 수 있다.

## 3. 구조

```text
discord_yfinance_market/
├── main.py
├── config.py
├── requirements.txt
├── data/
│   └── yahoo_finance_manager.py
├── workers/
│   └── market_worker.py
└── ui/
    └── main_window.py
```

- `config.py`: 화면 종목, 채널, Yahoo 티커 매핑
- `data/yahoo_finance_manager.py`: Yahoo Finance 데이터 다운로드와 지표 계산
- `workers/market_worker.py`: 별도 QThread에서 주기적 수집
- `ui/main_window.py`: Discord 스타일 화면과 데이터 표시
- `main.py`: UI/Worker 생성 및 Signal 연결

## 4. 수집 대상

| 화면 항목 | Yahoo Finance 티커 |
|---|---|
| USD/KRW | USDKRW=X |
| JPY/KRW | JPYKRW=X |
| NASDAQ-100 | ^NDX |
| WTI 원유 선물 | CL=F |
| 금 선물 | GC=F |
| TQQQ, QLD, QQQ 등 | 각 종목 티커 |
| NVDA, AAPL, GOOGL, AMZN | 각 종목 티커 |

주의: NASDAQ 카드는 나스닥 종합지수가 아니라 NASDAQ-100 지수(^NDX)로 연결했다.
원하는 지수가 나스닥 종합지수라면 `config.py`에서 `^IXIC`로 바꾼다.

## 5. 주간/야간 KOSPI200 선물

Yahoo Finance에서 국내 주간/야간 KOSPI200 선물의 안정적인 실시간 심볼을 확인하지 못했으므로
이 프로젝트에서는 해당 카드에 가짜 실시간 값을 넣지 않고 `--`로 표시한다.

`^KS200`은 KOSPI200 지수 심볼로 조회 가능 여부를 별도 테스트할 수 있지만,
KOSPI200 선물과 동일하지 않다. 기존 mkospi/eSignal 수집기를 별도 Worker로 연결하는 것을 권장한다.

## 6. 실시간성 및 데이터 제한

- yfinance는 Yahoo Finance 데이터를 조회하는 비공식 Python 라이브러리다.
- 거래소/상품별로 지연 시세 또는 데이터 누락이 발생할 수 있다.
- 1분봉은 체결 틱 스트리밍이 아니다. 이 프로젝트는 60초마다 최신 1분봉을 다시 조회한다.
- Yahoo의 1분봉은 장기간 과거 조회에 제한이 있다. 장기 차트는 `1d` 일봉을 별도로 사용한다.
- 호출을 과도하게 반복하면 일시적인 rate limit이 발생할 수 있다. 기본 갱신 간격 60초를 유지하고,
  문제가 생기면 120~300초로 늘린다.
- 투자/주문 체결용 데이터로 사용하기 전에 데이터 지연과 정확성을 별도로 검증한다.

## 7. 기존 프로젝트에 연결

기존 `TickerEngine`을 유지하려면 `MarketWorker`를 그대로 사용하지 않아도 된다.
기존 엔진의 Qt Signal을 다음 UI 메서드에 연결하면 된다.

```python
window.update_market_data(market_data_dict)
window.update_ticker_data("TQQQ", ticker_data_dict)
```

UI를 다른 스레드에서 직접 변경하지 말고 반드시 Qt Signal/Slot을 통해 메인 스레드에서 갱신한다.

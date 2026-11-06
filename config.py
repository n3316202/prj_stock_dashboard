"""마켓 모니터링 종목 및 채널 설정"""

MARKET_DATA = {
    "USD/KRW": {"price": None, "change": None, "unit": "원"},
    "JPY/KRW": {"price": None, "change": None, "unit": "원"},
    "NASDAQ": {"price": None, "change": None, "unit": ""},
    "OIL": {"price": None, "change": None, "unit": ""},
    "GOLD": {"price": None, "change": None, "unit": ""},
    "코스피200": {"price": None, "change": None, "unit": ""},
    "야간선물": {"price": None, "change": None, "unit": ""},
}

TICKER_DATA = {
    "TQQQ": {
        "name": "ProShares UltraPro QQQ",
        "price": 60.90, "change": 1.44, "change_pct": 2.41,
        "high": 88.09, "previous_close": 59.46, "volume": "32.5M",
        "category": "레버리지",
    },
    "QLD": {
        "name": "ProShares Ultra QQQ",
        "price": 81.64, "change": 1.33, "change_pct": 1.66,
        "high": 101.62, "previous_close": 80.31, "volume": "4.2M",
        "category": "레버리지",
    },
    "QQQ": {
        "name": "Invesco QQQ Trust",
        "price": 686.83, "change": 5.74, "change_pct": 0.84,
        "high": 762.86, "previous_close": 681.09, "volume": "28.1M",
        "category": "나스닥100",
    },
    "SPY": {
        "name": "SPDR S&P 500 ETF Trust",
        "price": 755.25, "change": 3.15, "change_pct": 0.42,
        "high": 781.62, "previous_close": 752.10, "volume": "41.8M",
        "category": "S&P500",
    },
    "SSO": {
        "name": "ProShares Ultra S&P500",
        "price": 67.57, "change": 0.56, "change_pct": 0.83,
        "high": 72.80, "previous_close": 67.01, "volume": "2.1M",
        "category": "레버리지",
    },
    "SPXL": {
        "name": "Direxion Daily S&P500 Bull 3X",
        "price": 269.57, "change": 3.25, "change_pct": 1.22,
        "high": 303.18, "previous_close": 266.32, "volume": "1.9M",
        "category": "레버리지",
    },
    "UPRO": {
        "name": "ProShares UltraPro S&P500",
        "price": 140.90, "change": 1.76, "change_pct": 1.26,
        "high": 158.63, "previous_close": 139.14, "volume": "1.4M",
        "category": "레버리지",
    },
    "SCHD": {
        "name": "Schwab US Dividend Equity ETF",
        "price": 35.65, "change": -0.25, "change_pct": -0.68,
        "high": 36.10, "previous_close": 35.90, "volume": "8.3M",
        "category": "배당",
    },
    "DIA": {
        "name": "SPDR Dow Jones Industrial Average ETF",
        "price": 517.32, "change": -2.02, "change_pct": -0.39,
        "high": 546.75, "previous_close": 519.34, "volume": "2.0M",
        "category": "다우",
    },
    "DDM": {
        "name": "ProShares Ultra Dow30",
        "price": 62.88, "change": -0.67, "change_pct": -1.05,
        "high": 71.25, "previous_close": 63.55, "volume": "0.4M",
        "category": "레버리지",
    },
    "UDOW": {
        "name": "ProShares UltraPro Dow30",
        "price": 65.48, "change": -0.78, "change_pct": -1.18,
        "high": 79.26, "previous_close": 66.26, "volume": "0.7M",
        "category": "레버리지",
    },
    "MOAT": {
        "name": "VanEck Morningstar Wide Moat ETF",
        "price": 114.41, "change": 0.33, "change_pct": 0.29,
        "high": 115.58, "previous_close": 114.08, "volume": "0.3M",
        "category": "가치투자",
    },
    "SOXL": {
        "name": "Direxion Daily Semiconductor Bull 3X",
        "price": 75.70, "change": 7.53, "change_pct": 11.05,
        "high": 302.00, "previous_close": 68.17, "volume": "45.2M",
        "category": "반도체",
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "price": 207.85, "change": 5.79, "change_pct": 2.86,
        "high": 243.37, "previous_close": 202.06, "volume": "122.0M",
        "category": "빅테크",
    },
    "AAPL": {
        "name": "Apple Inc.",
        "price": 329.48, "change": -8.84, "change_pct": -2.61,
        "high": 351.73, "previous_close": 338.32, "volume": "52.1M",
        "category": "빅테크",
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "price": 277.69, "change": -1.30, "change_pct": -0.47,
        "high": 408.61, "previous_close": 278.99, "volume": "18.4M",
        "category": "빅테크",
    },
    "AMZN": {
        "name": "Amazon.com Inc.",
        "price": 246.47, "change": 0.84, "change_pct": 0.34,
        "high": 287.20, "previous_close": 245.63, "volume": "29.7M",
        "category": "빅테크",
    },
    "SPCX": {
        "name": "Sample Portfolio Asset",
        "price": 141.92, "change": 5.55, "change_pct": 4.07,
        "high": 225.64, "previous_close": 136.37, "volume": "0.2M",
        "category": "관심종목",
    },
}

# 서버별 채널과 채널별 종목 목록
SERVER_CHANNELS = {
    "M": {
        "title": "MARKET",
        "channels": {
            "시장 개요": ["TQQQ", "QQQ", "SPY", "NVDA"],
            "환율": [],
            "원자재": [],
            "선물": [],
        },
    },
    "E": {
        "title": "ETF",
        "channels": {
            "전체 ETF": list(TICKER_DATA.keys()),
            "레버리지": [k for k, v in TICKER_DATA.items() if v["category"] == "레버리지"],
            "나스닥100": ["TQQQ", "QLD", "QQQ"],
            "S&P500": ["SPY", "SSO", "SPXL", "UPRO"],
            "배당": ["SCHD"],
            "반도체": ["SOXL"],
            "가치투자": ["MOAT"],
            "다우": ["DIA", "DDM", "UDOW"],
        },
    },
    "S": {
        "title": "US STOCK",
        "channels": {
            "빅테크": ["NVDA", "AAPL", "GOOGL", "AMZN"],
            "반도체": ["NVDA"],
            "관심종목": [],
        },
    },
    "F": {
        "title": "FUTURES",
        "channels": {
            "주간선물": [],
            "야간선물": [],
        },
    },
    "C": {
        "title": "COMMODITIES",
        "channels": {
            "원유": [],
            "금": [],
        },
    },
}


# Yahoo Finance 티커 매핑
# 환율: USDKRW=X / JPYKRW=X
# 나스닥: ^NDX (NASDAQ-100 지수)
# 원유: CL=F (WTI 선물), 금: GC=F (금 선물)
MARKET_YAHOO_SYMBOLS = {
    "USD/KRW": "USDKRW=X",
    "JPY/KRW": "JPYKRW=X",
    #"NASDAQ": "^NDX",
    # 코스피200 지수
    "코스피200": "^KS200",
    "NASDAQ": "NQ=F",
    "OIL": "CL=F",
    "GOLD": "GC=F",
}

# 화면에 등록된 종목 중 Yahoo Finance에서 조회할 종목
TICKER_YAHOO_SYMBOLS = {
    symbol: symbol
    for symbol in TICKER_DATA
    if symbol != "SPCX"  # 예제용 가상 티커이므로 실시간 조회 제외
}

# Yahoo Finance에서 KOSPI200 지수는 별도 심볼(^KS200) 조회를 시도할 수 있지만,
# 주간/야간 KOSPI200 선물 시세와 동일한 상품이 아니다.
# 주간/야간 선물은 기존 mkospi/eSignal 등 별도 수집기를 유지한다.

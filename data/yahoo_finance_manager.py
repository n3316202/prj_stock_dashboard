
"""
Yahoo Finance 데이터 수집기 + 실시간 갱신 디버깅

기능
1. 1분봉: 최근 가격 조회
2. 전체 기간 일봉: 전일 종가, 역사적 신고가, 거래량 조회
3. 여러 티커를 묶어서 다운로드
4. 15분 일봉 캐시
5. ETF 가격 갱신 여부 추적
6. 데이터 기준 시각 및 지연 시간 확인
7. API 요청 및 응답 소요 시간 기록
8. 종목별 가격 변화 및 업데이트 상태 기록
"""

from datetime import datetime
import logging
import time

import pandas as pd
import yfinance as yf

from config import MARKET_YAHOO_SYMBOLS, TICKER_YAHOO_SYMBOLS


log = logging.getLogger(__name__)


class YahooFinanceManager:

    def __init__(self):

        self.symbol_map = {}

        self.symbol_map.update(MARKET_YAHOO_SYMBOLS)
        self.symbol_map.update(TICKER_YAHOO_SYMBOLS)

        # ----------------------------------------
        # 일봉 캐시
        # ----------------------------------------

        self._daily_cache = {}
        self._daily_cache_time = 0.0

        self.daily_refresh_seconds = 900

        # ----------------------------------------
        # 디버깅용 이전 가격 저장
        # ----------------------------------------

        self._last_quote_state = {}

        # 마지막 조회 결과 저장
        self._last_fetch_time = None

        log.info("=" * 70)
        log.info("YahooFinanceManager 초기화")
        log.info("등록된 종목 수: %d", len(self.symbol_map))
        log.info("등록 종목: %s", list(self.symbol_map.keys()))
        log.info("=" * 70)

    # ====================================================
    # 티커별 데이터 추출
    # ====================================================

    @staticmethod
    def _extract_ticker_frame(download_df, yahoo_symbol):

        if download_df is None or download_df.empty:
            return pd.DataFrame()

        if isinstance(download_df.columns, pd.MultiIndex):

            level0 = download_df.columns.get_level_values(0)
            level1 = download_df.columns.get_level_values(1)

            if yahoo_symbol in level0:

                frame = download_df[yahoo_symbol].copy()

            elif yahoo_symbol in level1:

                frame = download_df.xs(
                    yahoo_symbol,
                    axis=1,
                    level=1
                ).copy()

            else:

                return pd.DataFrame()

        else:

            frame = download_df.copy()

        return frame.dropna(how="all")

    # ====================================================
    # 안전한 숫자 변환
    # ====================================================

    @staticmethod
    def _safe_float(value):

        try:

            number = float(value)

            if pd.isna(number):
                return None

            return number

        except (TypeError, ValueError):

            return None

    # ====================================================
    # 전일 종가 계산
    # ====================================================

    @staticmethod
    def _previous_close(daily_frame, latest_intraday_timestamp):

        if daily_frame.empty or "Close" not in daily_frame:
            return None

        closes = daily_frame["Close"].dropna()

        if closes.empty:
            return None

        try:

            daily_date = pd.Timestamp(
                daily_frame.dropna(subset=["Close"]).index[-1]
            ).date()

            intraday_date = pd.Timestamp(
                latest_intraday_timestamp
            ).date()

            if daily_date == intraday_date and len(closes) >= 2:

                return float(closes.iloc[-2])

        except Exception:

            log.exception("전일 종가 계산 중 오류")

        return float(closes.iloc[-1])

    # ====================================================
    # 데이터 시각 지연 계산
    # ====================================================

    @staticmethod
    def _get_data_age(timestamp):

        try:

            ts = pd.Timestamp(timestamp)

            if ts.tzinfo is not None:

                now = pd.Timestamp.now(tz=ts.tz)

            else:

                now = pd.Timestamp.now()

            age = (now - ts).total_seconds()

            return round(age, 1)

        except Exception:

            return None

    # ====================================================
    # 종목별 디버깅 로그
    # ====================================================

    def _debug_quote(self, display_name, yahoo_symbol, item):

        price = item["price"]
        quote_time = item["quote_time"]

        previous_state = self._last_quote_state.get(display_name)

        # ----------------------------------------
        # 최초 수신
        # ----------------------------------------

        if previous_state is None:

            status = "FIRST"

            poll_change = None

            price_changed = True

        else:

            old_price = previous_state["price"]
            old_quote_time = previous_state["quote_time"]

            poll_change = price - old_price

            # ------------------------------------
            # 가격과 데이터 시각 비교
            # ------------------------------------

            if quote_time != old_quote_time:

                status = "NEW_BAR"

                price_changed = price != old_price

            elif price != old_price:

                status = "PRICE_CHANGED_SAME_BAR"

                price_changed = True

            else:

                status = "UNCHANGED"

                price_changed = False

        # ----------------------------------------
        # 데이터 지연 시간
        # ----------------------------------------

        age = self._get_data_age(quote_time)

        # ----------------------------------------
        # 다음 조회를 위한 상태 저장
        # ----------------------------------------

        self._last_quote_state[display_name] = {

            "price": price,

            "quote_time": quote_time,

            "received_at": datetime.now().isoformat(
                timespec="seconds"
            )
        }

        # ----------------------------------------
        # 로그 출력
        # ----------------------------------------

        log.info(
            "[YAHOO] %-12s | "
            "SYMBOL=%-12s | "
            "PRICE=%10.4f | "
            "POLL_CHANGE=%s | "
            "CHANGE=%+.4f | "
            "CHANGE_PCT=%+.3f%% | "
            "DATA_TIME=%s | "
            "AGE=%ss | "
            "STATUS=%s",
            display_name,
            yahoo_symbol,
            price,
            "-" if poll_change is None else f"{poll_change:+.4f}",
            item["change"],
            item["change_pct"],
            quote_time,
            age,
            status
        )

        # ----------------------------------------
        # 상세 디버깅
        # ----------------------------------------

        log.debug(
            "[DETAIL] %s | previous_close=%s | "
            "all_time_high=%s | volume=%s | "
            "price_changed=%s",
            display_name,
            item["previous_close"],
            item["high"],
            item["volume"],
            price_changed
        )

    # ====================================================
    # 전체 데이터 수집
    # ====================================================

    def fetch_snapshot(self):

        fetch_start = time.perf_counter()

        request_time = datetime.now()

        symbols = list(
            dict.fromkeys(self.symbol_map.values())
        )

        result = {

            "market": {},

            "tickers": {},

            "timestamp": request_time.isoformat(
                timespec="seconds"
            ),

            "errors": []
        }

        log.info("")
        log.info("=" * 80)
        log.info(
            "[YAHOO FETCH START] %s",
            request_time.strftime("%Y-%m-%d %H:%M:%S")
        )

        log.info("조회 종목 수: %d", len(symbols))

        log.debug("조회 티커 목록: %s", symbols)

        # ====================================================
        # 1. 1분봉 다운로드
        # ====================================================

        intraday_start = time.perf_counter()

        try:

            intraday_all = yf.download(
                tickers=symbols,
                period="1d",
                interval="1m",
                group_by="ticker",
                auto_adjust=False,
                prepost=True,
                threads=True,
                progress=False,
                timeout=20,
                multi_level_index=True
            )

            intraday_elapsed = (
                time.perf_counter() - intraday_start
            )

            log.info(
                "[INTRADAY] 다운로드 완료 | "
                "소요시간=%.2f초 | "
                "행=%d",
                intraday_elapsed,
                0 if intraday_all is None else len(intraday_all)
            )

            if intraday_all is None or intraday_all.empty:

                log.warning(
                    "[INTRADAY] 수신된 데이터가 없음"
                )

        except Exception as exc:

            log.exception(
                "[INTRADAY ERROR] 1분봉 다운로드 실패"
            )

            result["errors"].append(
                f"1분봉 조회 실패: {exc}"
            )

            intraday_all = pd.DataFrame()

        # ====================================================
        # 2. 전체 기간 일봉 다운로드 및 캐시
        # ====================================================

        now_monotonic = time.monotonic()

        cache_age = (
            now_monotonic - self._daily_cache_time
        )

        if (
            not self._daily_cache
            or cache_age >= self.daily_refresh_seconds
        ):

            daily_start = time.perf_counter()

            try:

                daily_all = yf.download(
                    tickers=symbols,
                    period="max",
                    interval="1d",
                    group_by="ticker",
                    auto_adjust=False,
                    prepost=False,
                    threads=True,
                    progress=False,
                    timeout=25,
                    multi_level_index=True
                )

                if daily_all is not None and not daily_all.empty:
                    self._daily_cache = {

                        ticker: self._extract_ticker_frame(
                            daily_all,
                            ticker
                        )

                        for ticker in symbols
                    }

                    self._daily_cache_time = time.monotonic()

                    log.info(
                        "[DAILY] 전체 기간 일봉 갱신 완료 | "
                        "소요시간=%.2f초",
                        time.perf_counter() - daily_start
                    )

                else:

                    log.warning(
                        "[DAILY] 일봉 데이터가 비어 있음"
                    )

            except Exception as exc:

                log.exception(
                    "[DAILY ERROR] 일봉 다운로드 실패"
                )

                result["errors"].append(
                    f"일봉 조회 실패: {exc}"
                )

        else:

            log.debug(
                "[DAILY CACHE] 기존 일봉 사용 | "
                "캐시 경과시간=%.1f초",
                cache_age
            )

        # ====================================================
        # 3. 종목별 데이터 분리
        # ====================================================

        frames = {}

        for yahoo_symbol in symbols:

            intraday = self._extract_ticker_frame(
                intraday_all,
                yahoo_symbol
            )

            daily = self._daily_cache.get(
                yahoo_symbol,
                pd.DataFrame()
            )

            frames[yahoo_symbol] = (
                intraday,
                daily
            )

            log.debug(
                "[FRAME] %s | 1분봉=%d | 일봉=%d",
                yahoo_symbol,
                len(intraday),
                len(daily)
            )

        # ====================================================
        # 4. 시장 지표 처리
        # ====================================================

        for display_name, yahoo_symbol in MARKET_YAHOO_SYMBOLS.items():

            intraday, daily = frames.get(

                yahoo_symbol,

                (pd.DataFrame(), pd.DataFrame())
            )

            item = self._make_quote(
                intraday,
                daily
            )

            if item:

                item["unit"] = (
                    "원"
                    if display_name in ("USD/KRW", "JPY/KRW")
                    else ""
                )

                result["market"][display_name] = item

                self._debug_quote(
                    display_name,
                    yahoo_symbol,
                    item
                )

            else:

                error = (
                    f"{display_name}({yahoo_symbol}) "
                    "시세 데이터 없음"
                )

                log.warning("[NO DATA] %s", error)

                result["errors"].append(error)

        # ====================================================
        # 5. ETF 처리
        # ====================================================

        for display_name, yahoo_symbol in TICKER_YAHOO_SYMBOLS.items():

            intraday, daily = frames.get(

                yahoo_symbol,

                (pd.DataFrame(), pd.DataFrame())
            )

            item = self._make_quote(
                intraday,
                daily
            )

            if item:

                result["tickers"][display_name] = item

                self._debug_quote(
                    display_name,
                    yahoo_symbol,
                    item
                )

            else:

                error = (
                    f"{display_name}({yahoo_symbol}) "
                    "시세 데이터 없음"
                )

                log.warning("[NO DATA] %s", error)

                result["errors"].append(error)

        # ====================================================
        # 6. 전체 수집 결과
        # ====================================================

        total_elapsed = (
            time.perf_counter() - fetch_start
        )

        success_count = (
            len(result["market"])
            + len(result["tickers"])
        )

        total_count = (
            len(MARKET_YAHOO_SYMBOLS)
            + len(TICKER_YAHOO_SYMBOLS)
        )

        log.info("-" * 80)

        log.info(
            "[YAHOO FETCH END] "
            "성공=%d/%d | "
            "오류=%d | "
            "총 소요시간=%.2f초",
            success_count,
            total_count,
            len(result["errors"]),
            total_elapsed
        )

        if result["errors"]:

            for error in result["errors"]:

                log.warning("[ERROR LIST] %s", error)

        log.info("=" * 80)

        self._last_fetch_time = datetime.now()

        return result

    # ====================================================
    # 종목별 현재가 및 지표 생성
    # ====================================================

    def _make_quote(self, intraday, daily):

        if intraday.empty or "Close" not in intraday:

            return None

        close_series = intraday["Close"].dropna()

        if close_series.empty:

            return None

        price = self._safe_float(
            close_series.iloc[-1]
        )

        timestamp = close_series.index[-1]

        if price is None:

            return None

        previous_close = self._previous_close(
            daily,
            timestamp
        )

        if previous_close in (None, 0):

            change = 0.0

            change_pct = 0.0

        else:

            change = price - previous_close

            change_pct = (
                change / previous_close
            ) * 100

        # ----------------------------------------
        # 역사적 신고가(상장 이후 전체 거래일의 고가 중 최댓값)
        # ----------------------------------------

        historical_high = None

        volume = "-"

        if not daily.empty:

            if "High" in daily:

                high_values = daily["High"].dropna()

                if not high_values.empty:

                    historical_high = float(
                        high_values.max()
                    )

            if "Volume" in daily:

                volumes = daily["Volume"].dropna()

                if not volumes.empty:

                    volume = f"{int(volumes.iloc[-1]):,}"

        if historical_high is None and "High" in intraday:

            high_values = intraday["High"].dropna()

            historical_high = (
                float(high_values.max())
                if not high_values.empty
                else price
            )

        return {

            "price": price,

            "change": change,

            "change_pct": change_pct,

            "previous_close": (
                previous_close
                if previous_close is not None
                else 0.0
            ),

            "high": (
                historical_high
                if historical_high is not None
                else price
            ),

            "volume": volume,

            "quote_time": str(timestamp)
        }

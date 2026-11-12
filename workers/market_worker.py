"""
Yahoo Finance와 네이버 환율 데이터를 UI 스레드와 분리해 수집하는 QThread Worker

- YahooFinanceManager: 주식 및 시장 지표 수집
- NaverExchangeManager: USD/KRW, JPY/KRW 환율 수집
- 한쪽 데이터 수집에 실패해도 다른 쪽 데이터는 전달
"""

import logging
import threading

from PyQt6.QtCore import QThread, pyqtSignal

from data.yahoo_finance_manager import YahooFinanceManager
from data.naver_exchange_manager import NaverExchangeManager


log = logging.getLogger(__name__)


class MarketWorker(QThread):
    # 전체 시장 스냅샷 전달
    snapshot_ready = pyqtSignal(dict)

    # 상태 메시지, 연결 성공 여부
    status_changed = pyqtSignal(str, bool)

    def __init__(self, interval_seconds=60, parent=None):
        super().__init__(parent)

        self.interval_seconds = max(30, int(interval_seconds))
        self._stop_event = threading.Event()

        self.manager = YahooFinanceManager()
        self.naver_exchange = NaverExchangeManager()

    # =========================================================
    # Yahoo Finance 데이터 수집
    # =========================================================
    def _fetch_yahoo_snapshot(self):
        """
        Yahoo Finance 데이터를 수집한다.

        반환 데이터는 기존 YahooFinanceManager의 구조를 유지한다.
        """
        snapshot = self.manager.fetch_snapshot()

        if not isinstance(snapshot, dict):
            raise TypeError(
                "YahooFinanceManager.fetch_snapshot()은 dict를 반환해야 한다."
            )

        # market / tickers 키가 누락된 경우에도 후속 처리 가능하도록 보정
        snapshot.setdefault("market", {})
        snapshot.setdefault("tickers", {})

        if not isinstance(snapshot["market"], dict):
            raise TypeError("snapshot['market']은 dict 형식이어야 한다.")

        if not isinstance(snapshot["tickers"], dict):
            raise TypeError("snapshot['tickers']는 dict 형식이어야 한다.")

        return snapshot

    # =========================================================
    # 네이버 환율 데이터 수집
    # =========================================================
    def _fetch_naver_rates(self):
        """
        네이버 환율 데이터를 수집한다.

        예상 반환 구조:
        {
            "USD/KRW": {
                "price": 1335.40,
                "change": -76.8,
                "change_pct": -5.43,
                "change_label": "하락"
            },
            "JPY/KRW": {
                "price": 8.95,
                "change": 0.03,
                "change_pct": 0.34,
                "change_label": "상승"
            }
        }

        네이버 수집에 실패하면 빈 dict를 반환한다.
        """
        try:
            rates = self.naver_exchange.fetch_all()

            if not isinstance(rates, dict):
                log.warning("네이버 환율 데이터 형식이 dict가 아니다.")
                return {}

            valid_rates = {}

            for symbol, data in rates.items():
                if not isinstance(data, dict):
                    log.warning(
                        "네이버 환율 데이터 형식 오류: %s / %s",
                        symbol,
                        type(data).__name__,
                    )
                    continue

                # 가격이 없는 데이터는 시장 데이터에 반영하지 않는다.
                if data.get("price") is None:
                    continue

                # 기존 반환 필드를 유지하면서 필요한 필드만 전달한다.
                valid_rates[symbol] = {
                    "price": data.get("price"),
                    "change": data.get("change"),
                    "change_pct": data.get("change_pct"),
                }

                # 새 NaverExchangeManager가 제공하는 경우에만 추가
                if data.get("change_label") is not None:
                    valid_rates[symbol]["change_label"] = data["change_label"]

            return valid_rates

        except Exception:
            log.exception("네이버 환율 수집 실패")
            return {}

    # =========================================================
    # Worker 실행
    # =========================================================
    def run(self):
        self.status_changed.emit("MARKET DATA 연결 중", True)

        while not self._stop_event.is_set():

            try:
                # -------------------------------------------------
                # 1. Yahoo Finance 수집
                # -------------------------------------------------
                try:
                    snapshot = self._fetch_yahoo_snapshot()
                    yahoo_success = True

                except Exception:
                    log.exception("Yahoo Finance 데이터 수집 실패")
                    snapshot = {
                        "market": {},
                        "tickers": {},
                    }
                    yahoo_success = False

                # -------------------------------------------------
                # 2. 네이버 환율 수집
                # -------------------------------------------------
                naver_rates = self._fetch_naver_rates()

                # -------------------------------------------------
                # 3. 데이터 병합
                # -------------------------------------------------
                # 네이버에서 정상 수집한 환율은 Yahoo 데이터보다 우선한다.
                # 네이버 수집 실패 시 기존 Yahoo 시장 데이터는 유지한다.
                snapshot["market"].update(naver_rates)

                # -------------------------------------------------
                # 4. UI로 스냅샷 전달
                # -------------------------------------------------
                self.snapshot_ready.emit(snapshot)

                # -------------------------------------------------
                # 5. 연결 상태 표시
                # -------------------------------------------------
                has_market_data = bool(snapshot.get("market"))
                has_ticker_data = bool(snapshot.get("tickers"))

                if yahoo_success or naver_rates:
                    if has_market_data or has_ticker_data:
                        if yahoo_success and naver_rates:
                            message = "YAHOO FINANCE / NAVER 연결 정상"
                        elif yahoo_success:
                            message = "YAHOO FINANCE 연결 정상 (NAVER 환율 확인 필요)"
                        else:
                            message = "NAVER 환율 연결 정상 (YAHOO FINANCE 확인 필요)"

                        self.status_changed.emit(message, True)
                    else:
                        self.status_changed.emit("시세 데이터 수신 실패", False)
                else:
                    self.status_changed.emit("시장 데이터 수집 실패", False)

            except Exception as exc:
                # 예상하지 못한 오류가 발생해도 Worker 반복 실행을 유지한다.
                log.exception("Market worker error")
                self.status_changed.emit(f"수집 오류: {exc}", False)

            # QThread 내부에서 대기하므로 GUI 이벤트 루프를 막지 않는다.
            self._stop_event.wait(self.interval_seconds)

        self.status_changed.emit("MARKET DATA 수집 중지", False)

    # =========================================================
    # Worker 종료
    # =========================================================
    def stop(self):
        """
        Worker 종료 요청.

        wait()를 통해 스레드가 종료될 때까지 기다린다.
        """
        self._stop_event.set()

        if self.isRunning():
            self.wait(60000)

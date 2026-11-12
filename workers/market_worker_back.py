"""Yahoo Finance 수집을 UI 스레드와 분리하는 QThread Worker"""
import logging
import threading
from PyQt6.QtCore import QThread, pyqtSignal

from data.yahoo_finance_manager import YahooFinanceManager
from data.naver_exchange_manager import NaverExchangeManager

log = logging.getLogger(__name__)


class MarketWorker(QThread):
    snapshot_ready = pyqtSignal(dict)
    status_changed = pyqtSignal(str, bool)

    def __init__(self, interval_seconds=60, parent=None):
        super().__init__(parent)
        self.interval_seconds = max(30, int(interval_seconds))
        self._stop_event = threading.Event()
        self.manager = YahooFinanceManager()
        
        self.naver_exchange = NaverExchangeManager()

    def run(self):
        self.status_changed.emit("YAHOO FINANCE 연결 중", True)

        while not self._stop_event.is_set():
            try:
                snapshot = self.manager.fetch_snapshot()

                # 네이버 환율 데이터 수집
                naver_rates = self.naver_exchange.fetch_all()

                # Yahoo Finance 결과에 네이버 환율 반영
                snapshot["market"].update(naver_rates)

                self.snapshot_ready.emit(snapshot)


                if snapshot["market"] or snapshot["tickers"]:
                    self.status_changed.emit("YAHOO FINANCE 연결 정상", True)
                else:
                    self.status_changed.emit("시세 데이터 수신 실패", False)

            except Exception as exc:
                log.exception("Market worker error")
                self.status_changed.emit(f"수집 오류: {exc}", False)

            # QThread 내부에서 대기하므로 GUI 이벤트 루프를 막지 않는다.
            self._stop_event.wait(self.interval_seconds)

    def stop(self):
        self._stop_event.set()
        self.wait(60000)

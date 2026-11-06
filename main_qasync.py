"""기존 PyQt6 + qasync 프로젝트에서 사용하는 실행 예제"""
import sys
import asyncio
import logging

from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop

from ui.main_window import MainWindow
from workers.market_worker import MarketWorker

logging.basicConfig(level=logging.INFO)


def apply_snapshot(window, snapshot):
    if snapshot.get("market"):
        window.update_market_data(snapshot["market"])

    for symbol, quote in snapshot.get("tickers", {}).items():
        window.update_ticker_data(symbol, quote)

    window.update_last_update()


def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    worker = MarketWorker(interval_seconds=60)
    worker.snapshot_ready.connect(lambda data: apply_snapshot(window, data))
    worker.status_changed.connect(window.set_connection_status)

    window.show()
    worker.start()
    app.aboutToQuit.connect(worker.stop)

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()

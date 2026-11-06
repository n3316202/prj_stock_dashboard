
"""
Discord 스타일 Yahoo Finance 마켓 대시보드 실행 파일

기능
1. PyQt6 대시보드 실행
2. Yahoo Finance 데이터 수집 Worker 실행
3. 실시간 가격 갱신 로그 확인
4. API 수집 오류 확인
5. UI 업데이트 확인
"""

import sys
import logging

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from workers.market_worker import MarketWorker


# =====================================================
# 1. 로그 설정
# =====================================================

logging.basicConfig(

    level=logging.DEBUG,

    format=(
        "%(asctime)s "
        "[%(levelname)-8s] "
        "%(name)s: "
        "%(message)s"
    ),

    handlers=[

        # # 일반 대시보드 로그
        # logging.FileHandler(
        #     "market_dashboard.log",
        #     encoding="utf-8"
        # ),

        # # Yahoo Finance 상세 디버깅 로그
        # logging.FileHandler(
        #     "yahoo_debug.log",
        #     encoding="utf-8"
        # ),

        # 콘솔 출력
        logging.StreamHandler()

    ]
)


# ====================================================
# 2. 로거 생성
# ====================================================

log = logging.getLogger(__name__)


# ====================================================
# 3. 메인 실행 함수
# ====================================================

def main():

    log.info("=" * 70)
    log.info("Yahoo Finance Market Dashboard 시작")
    log.info("=" * 70)

    # ----------------------------------------
    # QApplication
    # ----------------------------------------

    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    # ----------------------------------------
    # MainWindow
    # ----------------------------------------

    window = MainWindow()

    # ----------------------------------------
    # MarketWorker
    # ----------------------------------------

    worker = MarketWorker(

        interval_seconds = 30 #30

    )

    log.info(
        "MarketWorker 생성 완료 | 조회 주기=60초"
    )

    # ----------------------------------------
    # Worker -> UI 연결
    # ----------------------------------------

    worker.snapshot_ready.connect(

        lambda snapshot: apply_snapshot(
            window,
            snapshot
        )

    )

    worker.status_changed.connect(

        window.set_connection_status

    )

    # ----------------------------------------
    # UI 실행
    # ----------------------------------------

    window.show()

    # ----------------------------------------
    # 데이터 수집 시작
    # ----------------------------------------

    log.info("Yahoo Finance 데이터 수집 시작")

    worker.start()

    # ----------------------------------------
    # 프로그램 종료 처리
    # ----------------------------------------

    def shutdown():

        log.info("대시보드 종료 요청")

        worker.stop()

        log.info("MarketWorker 종료 요청 완료")

    app.aboutToQuit.connect(shutdown)

    sys.exit(app.exec())


# ====================================================
# 4. 데이터 수신 후 UI 업데이트
# ====================================================

def apply_snapshot(window, snapshot):

    market = snapshot.get("market", {})
    tickers = snapshot.get("tickers", {})
    errors = snapshot.get("errors", [])

    log.info("-" * 70)

    log.info(
        "[UI UPDATE] 시장지표=%d개 | ETF=%d개 | 오류=%d개",
        len(market),
        len(tickers),
        len(errors)
    )

    # ----------------------------------------
    # 시장 지표 업데이트
    # ----------------------------------------

    if market:

        window.update_market_data(market)

        log.debug(
            "[UI] 시장 지표 업데이트 완료"
        )

    # ----------------------------------------
    # ETF 업데이트
    # ----------------------------------------

    for symbol, quote in tickers.items():

        window.update_ticker_data(
            symbol,
            quote
        )

        log.debug(
            "[UI ETF] %s | 가격=%.4f | 등락률=%+.3f%%",
            symbol,
            quote.get("price", 0),
            quote.get("change_pct", 0)
        )

    # ----------------------------------------
    # 데이터 수집 오류
    # ----------------------------------------

    if errors:

        for error in errors:

            log.warning(
                "[YAHOO DATA ERROR] %s",
                error
            )

    # ----------------------------------------
    # 최종 업데이트 시각
    # ----------------------------------------

    window.update_last_update()

    log.info("[UI UPDATE] 화면 업데이트 완료")

    log.info("-" * 70)


# ====================================================
# 5. 프로그램 시작
# ====================================================

if __name__ == "__main__":

    main()

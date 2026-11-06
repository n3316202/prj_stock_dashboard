"""Discord 스타일 마켓 대시보드 UI"""
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea,
    QVBoxLayout, QWidget, QGridLayout
)
from config import MARKET_DATA, TICKER_DATA, SERVER_CHANNELS

APP_STYLE = """
QMainWindow {
    background-color: #313338;
    color: #DBDEE1;
}
QWidget {
    color: #DBDEE1;
    font-family: "Malgun Gothic";
    font-size: 12pt;
}
QScrollArea {
    background-color: transparent;
    border: none;
}
QScrollArea QWidget {
    background-color: transparent;
}
QLabel {
    background-color: transparent;
}
QFrame#ServerSidebar {
    background-color: #1E1F22;
    border: none;
}
QFrame#ChannelSidebar, QFrame#DetailPanel {
    background-color: #2B2D31;
    border: none;
}
QFrame#MainPanel {
    background-color: #313338;
    border: none;
}
QLabel#Muted {
    color: #949BA4;
}
QLabel#SectionTitle {
    color: #F2F3F5;
    font-size: 11pt;
    font-weight: bold;
}
QPushButton {
    border: none;
    border-radius: 6px;
    padding: 8px;
    text-align: left;
    color: #B5BAC1;
    background-color: transparent;
}
QPushButton:hover {
    background-color: #35373C;
    color: #FFFFFF;
}
QPushButton:checked {
    background-color: #404249;
    color: #FFFFFF;
}
QPushButton#ServerButton {
    background-color: #313338;
    border-radius: 18px;
    min-width: 42px;
    max-width: 42px;
    min-height: 42px;
    max-height: 42px;
    font-weight: bold;
    font-size: 12pt;
}
QPushButton#ServerButton:checked {
    background-color: #5865F2;
    border-radius: 14px;
    color: white;
}
QPushButton#ChannelButton {
    padding: 7px 9px;
    text-align: left;
}
QPushButton#ChannelButton:checked {
    background-color: #404249;
    color: white;
}
QFrame#MarketCard {
    background-color: #2B2D31;
    border: 1px solid #3F4147;
    border-radius: 8px;
}
QFrame#TickerRow {
    background-color: #2B2D31;
    border: 1px solid #383A40;
    border-radius: 6px;
}
QFrame#TickerRow[selected="true"] {
    background-color: #3B3F8F;
    border: 1px solid #5865F2;
}
QLabel#TickerSymbol {
    color: #F2F3F5;
    font-size: 11pt;
    font-weight: bold;
}
QLabel#Price {
    color: #F2F3F5;
    font-size: 11pt;
    font-weight: bold;
}
QLabel#DetailSymbol {
    color: #FFFFFF;
    font-size: 22pt;
    font-weight: bold;
}
QLabel#DetailPrice {
    color: #FFFFFF;
    font-size: 25pt;
    font-weight: bold;
}
QLabel[detailChange="true"] {
    font-size: 12pt;
    font-weight: bold;
}
QLabel#Positive {
    color: #23D18B;
    font-weight: bold;
}
QLabel#Negative {
    color: #F23F43;
    font-weight: bold;
}
QFrame#Divider {
    background-color: #3F4147;
    max-height: 1px;
    min-height: 1px;
}

/* 마켓카드 관련 */
QLabel#MarketCardTitle {
    font-size: 10pt;
}

QLabel#MarketCardValue {
    font-size: 17pt;
    font-weight:bold;
    color:#ffffff;
}

QLabel#MarketCardChange {
    font-size: 10pt;
}

/* 카드 내부 구분선 */
QFrame#cardDivider {
    background-color: #666666;
    border: none;
    max-height: 1px;
}

/* 카드 마우스 오버 */
QFrame#card:hover {
    border: 1px solid #b48cff;
}

/* 카드 외곽  #4a4a4a #1E1F22 */
QFrame#MarketCard {
    background-color: #4a4a4a; 
    border: 1px solid #5a5a5a;
    border-radius: 10px;
}
"""


# ============================================================
# 3. 재사용 위젯
# ============================================================

# ============================================================
# Market Card
# ============================================================
class MarketCard(QFrame):
    """
    상단 시장 카드 위젯

    구성:
    - 제목
    - 구분선
    - 현재 가격
    - 구분선
    - 등락 정보
    - 외곽 테두리 및 가격 변동 플래시 효과
    """

    def __init__(self, title, value, change, unit=""):
        super().__init__()

        self.setObjectName("MarketCard")
        self.setMinimumHeight(92)
        self.setMaximumHeight(112)

        self.last_price = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        # 카드 제목
        self.title_label = QLabel(title)
        self.title_label.setObjectName("MarketCardTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ----------------------------------------------------
        # First Divider
        # 제목과 가격 사이 구분선
        # ----------------------------------------------------

        self.title_divider = QFrame()
        self.title_divider.setObjectName("cardDivider")
        self.title_divider.setFrameShape(QFrame.Shape.HLine)
        self.title_divider.setFixedHeight(1)

        # 현재 가격
        self.value_label = QLabel("--")
        self.value_label.setObjectName("MarketCardValue")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ----------------------------------------------------
        # Second Divider
        # 가격과 등락 정보 사이 구분선
        # ----------------------------------------------------

        self.value_divider = QFrame()
        self.value_divider.setObjectName("cardDivider")
        self.value_divider.setFrameShape(QFrame.Shape.HLine)
        self.value_divider.setFixedHeight(1)

        # 등락률
        self.change_label = QLabel("--")
        self.change_label.setObjectName("MarketCardChange")
        self.change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title_label)
        layout.addWidget(self.title_divider)
        layout.addWidget(self.value_label)
        layout.addWidget(self.value_divider)
        layout.addWidget(self.change_label)

        # 가격 변동 테두리 자동 복구 타이머
        self.flash_timer = QTimer(self)
        self.flash_timer.setSingleShot(True)
        self.flash_timer.timeout.connect(self.reset_flash)

        # 최초 데이터 설정 시에는 플래시를 실행하지 않는다.
        self.set_values(value, change, unit, flash=False)

    def set_values(self, value, change, unit="", flash=True):
        """현재가 + 전일 종가 대비 변동폭 및 변동률 표시"""

        print("나와라 뿅", value, change, unit, flash)

        try:
            price_float = (
                float(str(value).replace(",", ""))
                if value is not None else None
            )
        except (ValueError, TypeError):
            price_float = None

        # 가격 표시
        if price_float is None:
            self.value_label.setText("--")
        else:
            self.value_label.setText(f"{price_float:,.2f}{unit}")

        # 전일 종가 대비 변동폭 및 변동률
        if change is None or price_float is None:
            self.change_label.setText("--")
            self.change_label.setStyleSheet("color: #949BA4;")

        else:
            try:
                change_float = float(
                    str(change).replace(",", "").replace("%", "")
                )

                # 전일 종가 계산
                previous_close = price_float - change_float

                # 변동률 계산
                if previous_close != 0:
                    change_rate = (change_float / previous_close) * 100
                else:
                    change_rate = 0

                # 부호 표시
                sign1 = "+" if change_float > 0 else ""
                sign2 = "+" if change_rate > 0 else ""

                # 화면 표시
                self.change_label.setText(
                    f"{sign1}{change_float:.2f} / "
                    f"({sign2}{change_rate:.2f}%)"
                )

                # 상승 / 하락 색상
                if change_float > 0:
                    color = "#00FF9C"
                elif change_float < 0:
                    color = "#FF4D4D"
                else:
                    color = "#B48CFF"

                self.change_label.setStyleSheet(
                    f"color: {color}; font-weight: bold;"
                )

            except (ValueError, TypeError, ZeroDivisionError):
                self.change_label.setText("--")
                self.change_label.setStyleSheet("color: #949BA4;")

        # 직전 가격과 비교하여 테두리 강조
        direction = None

        if flash and self.last_price is not None and price_float is not None:
            if price_float > self.last_price:
                direction = "up"
            elif price_float < self.last_price:
                direction = "down"

        if price_float is not None:
            self.last_price = price_float

        if direction is not None:
            self.flash(direction)

    # def set_values(self, value, change, unit="", flash=True):
    #     """가격, 등락률을 갱신하고 가격 방향에 따라 테두리를 강조한다."""
        
    #     print("나와라 뿅", value, change,unit, flash)
        
    #     try:
    #         price_float = (
    #             float(str(value).replace(",", ""))
    #             if value is not None else None
    #         )
    #     except (ValueError, TypeError):
    #         price_float = None

    #     # 가격 표시
    #     if price_float is None:
    #         self.value_label.setText("--")
    #     else:
    #         self.value_label.setText(f"{price_float:,.2f}{unit}")

    #     # 등락률 표시 및 색상
    #     if change is None:
    #         self.change_label.setText("--")
    #         self.change_label.setStyleSheet("color: #949BA4;")
    #     else:
    #         try:
    #             change_float = float(
    #                 str(change).replace("%", "").replace(",", "")
    #             )
    #             sign = "+" if change_float > 0 else ""
    #             self.change_label.setText(f"{sign}{change_float:.2f}%")

    #             if change_float > 0:
    #                 color = "#00FF9C"
    #             elif change_float < 0:
    #                 color = "#FF4D4D"
    #             else:
    #                 color = "#B48CFF"

    #             self.change_label.setStyleSheet(
    #                 f"color: {color}; font-weight: bold;"
    #             )
    #         except (ValueError, TypeError):
    #             self.change_label.setText(str(change))
    #             self.change_label.setStyleSheet("color: #B48CFF;")

    #     # 직전 가격과 비교
    #     direction = None

    #     if flash and self.last_price is not None and price_float is not None:
    #         if price_float > self.last_price:
    #             direction = "up"
    #         elif price_float < self.last_price:
    #             direction = "down"

    #     if price_float is not None:
    #         self.last_price = price_float

    #     if direction is not None:
    #         self.flash(direction)

    def flash(self, direction):
        """상승은 초록색, 하락은 빨간색 테두리로 표시한다."""

        if direction == "up":
            color = "#00FF9C"
        elif direction == "down":
            color = "#FF4D4D"
        else:
            color = "#B48CFF"

        self.setStyleSheet(
            f"""
            QFrame#MarketCard {{
                background-color: #3A3C42;
                border: 2px solid {color};
                border-radius: 10px;
            }}
            """
        )

        self.flash_timer.start(700)

    def reset_flash(self):
        """강조 효과를 제거하고 기본 APP_STYLE로 복귀한다."""
        self.setStyleSheet("")


# class MarketCard(QFrame):
#     """상단 시장 지표 카드"""

#     def __init__(self, title, value, change, unit=""):
#         super().__init__()
#         self.setObjectName("MarketCard")
#         self.setMinimumHeight(78)

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(10, 8, 10, 8)
#         layout.setSpacing(3)

#         self.title_label = QLabel(title)
#         self.title_label.setObjectName("Muted")
#         self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

#         self.value_label = QLabel("--" if value is None else f"{value:,.2f}{unit}")
#         self.value_label.setObjectName("Price")
#         self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

#         self.change_label = QLabel()
#         self.change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.set_values(value, change, unit)

#         layout.addWidget(self.title_label)
#         layout.addWidget(self.value_label)
#         layout.addWidget(self.change_label)

#     def set_values(self, value, change, unit=""):
#         self.value_label.setText("--" if value is None else f"{value:,.2f}{unit}")
#         if change is None:
#             self.change_label.setText("--")
#             self.change_label.setObjectName("Muted")
#         else:
#             sign = "+" if change >= 0 else ""
#             self.change_label.setText(f"{sign}{change:.2f}%")
#             self.change_label.setObjectName(
#                 "Positive" if change >= 0 else "Negative"
#             )
#         self.change_label.style().unpolish(self.change_label)
#         self.change_label.style().polish(self.change_label)


class TickerRow(QFrame):
    """중앙 시세 목록의 한 행"""

    clicked = pyqtSignal(str)

    def __init__(self, symbol, data, selected=False):
        super().__init__()
        self.symbol = symbol
        self.data = data
        self.setObjectName("TickerRow")
        self.setProperty("selected", selected)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(54)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 7, 12, 7)
        layout.setSpacing(8)

        left = QVBoxLayout()
        left.setSpacing(2)

        self.symbol_label = QLabel(symbol)
        self.symbol_label.setObjectName("TickerSymbol")

        self.name_label = QLabel(data.get("name", data.get("category", "")))
        self.name_label.setObjectName("Muted")
        self.name_label.setStyleSheet("font-size: 8pt;")

        left.addWidget(self.symbol_label)
        left.addWidget(self.name_label)

        # 상장 이후 역사적 신고가(ATH)
        self.high_label = QLabel()
        self.high_label.setObjectName("Muted")
        self.high_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.high_label.setStyleSheet("font-size: 9pt; color: #B48CFF;")
        self.set_high(data.get("high"))

        price = data.get("price")
        self.price_label = QLabel("--" if price is None else f"${price:,.2f}")
        self.price_label.setObjectName("Price")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.change_label = QLabel()
        self.change_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.set_change(data["change"], data["change_pct"])

        layout.addLayout(left, 3)
        layout.addWidget(self.high_label, 2)
        layout.addWidget(self.price_label, 2)
        layout.addWidget(self.change_label, 2)

    def set_high(self, high):
        """상장 이후 역사적 신고가(ATH)를 표시한다."""
        try:
            high_value = float(str(high).replace(",", "")) if high is not None else None
        except (TypeError, ValueError):
            high_value = None

        self.high_label.setText(
            "--" if high_value is None or high_value <= 0
            else f"${high_value:,.2f}"
        )

    def set_change(self, change, pct):
        if change is None or pct is None:
            self.change_label.setText("--")
            self.change_label.setObjectName("Muted")
        else:
            sign = "+" if change >= 0 else ""
            self.change_label.setText(
                f"{sign}{change:.2f}  ({sign}{pct:.2f}%)"
            )
            self.change_label.setObjectName(
                "Positive" if change >= 0 else "Negative"
            )

        self.change_label.style().unpolish(self.change_label)
        self.change_label.style().polish(self.change_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.symbol)
        super().mousePressEvent(event)

    def set_selected(self, selected):
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class InfoValue(QFrame):
    """상세 패널의 라벨-값 표시"""

    def __init__(self, title, value):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("Muted")

        self.value_label = QLabel(value)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.value_label.setStyleSheet("font-weight: bold;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(value)


# ============================================================
# 4. 메인 윈도우
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self, engine=None):
        super().__init__()

        # 공통 스타일시트를 실제 메인 윈도우에 적용한다.
        self.setStyleSheet(APP_STYLE)

        self.engine = engine
        self.current_server = "E"
        self.current_channel = "전체 ETF"
        self.selected_ticker = "TQQQ"
        self.ticker_rows = {}
        self.market_cards = {}

        self.setWindowTitle("Market Monitor")
        self.resize(1500, 900)
        self.setMinimumSize(1100, 650)

        self.build_ui()
        self.select_server("E")
        self.select_ticker("TQQQ")

        # 예제 화면의 갱신 시각 표시용 타이머
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

    # --------------------------------------------------------
    # 전체 UI 조립
    # --------------------------------------------------------

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. 서버 메뉴
        self.server_sidebar = self.create_server_sidebar()
        root_layout.addWidget(self.server_sidebar)

        # 2. 채널 메뉴
        self.channel_sidebar = self.create_channel_sidebar()
        root_layout.addWidget(self.channel_sidebar)

        # 3. 중앙 시세 영역
        self.main_panel = self.create_main_panel()
        root_layout.addWidget(self.main_panel, 1)

        # 4. 우측 상세 패널
        self.detail_panel = self.create_detail_panel()
        root_layout.addWidget(self.detail_panel)

    # --------------------------------------------------------
    # 서버 메뉴
    # --------------------------------------------------------

    def create_server_sidebar(self):
        panel = QFrame()
        panel.setObjectName("ServerSidebar")
        panel.setFixedWidth(68)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(9, 12, 9, 12)
        layout.setSpacing(10)

        logo = QPushButton("M")
        logo.setObjectName("ServerButton")
        logo.setCheckable(True)
        logo.setChecked(True)
        logo.setToolTip("Market Monitor")
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)

        divider = QFrame()
        divider.setObjectName("Divider")
        layout.addWidget(divider)

        self.server_buttons = {}

        server_items = [
            ("M", "시장 개요"),
            ("E", "ETF"),
            ("S", "미국 주식"),
            ("F", "선물"),
            ("C", "원자재"),
        ]

        for key, tooltip in server_items:
            button = QPushButton(key)
            button.setObjectName("ServerButton")
            button.setCheckable(True)
            button.setToolTip(tooltip)
            button.clicked.connect(lambda checked, k=key: self.select_server(k))
            layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)
            self.server_buttons[key] = button

        layout.addStretch()

        settings = QPushButton("⚙")
        settings.setObjectName("ServerButton")
        settings.setToolTip("설정")
        layout.addWidget(settings, alignment=Qt.AlignmentFlag.AlignHCenter)

        return panel

    def select_server(self, server_key):
        if server_key not in SERVER_CHANNELS:
            return

        self.current_server = server_key

        for key, button in self.server_buttons.items():
            button.setChecked(key == server_key)

        self.populate_channels()

    # --------------------------------------------------------
    # 채널 메뉴
    # --------------------------------------------------------

    def create_channel_sidebar(self):
        panel = QFrame()
        panel.setObjectName("ChannelSidebar")
        panel.setFixedWidth(210)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(8)

        self.channel_header = QLabel("MARKET")
        self.channel_header.setObjectName("SectionTitle")
        layout.addWidget(self.channel_header)

        self.channel_subtitle = QLabel("실시간 금융정보")
        self.channel_subtitle.setObjectName("Muted")
        layout.addWidget(self.channel_subtitle)

        divider = QFrame()
        divider.setObjectName("Divider")
        layout.addWidget(divider)

        self.channel_list_layout = QVBoxLayout()
        self.channel_list_layout.setSpacing(3)
        self.channel_list_layout.setContentsMargins(0, 5, 0, 0)

        self.channel_container = QWidget()
        self.channel_container.setLayout(self.channel_list_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self.channel_container)
        layout.addWidget(scroll, 1)

        # 하단 사용자/상태 영역
        divider2 = QFrame()
        divider2.setObjectName("Divider")
        layout.addWidget(divider2)

        self.connection_label = QLabel("●  DATA CONNECTED")
        self.connection_label.setStyleSheet("color: #23D18B; font-size: 8pt;")
        layout.addWidget(self.connection_label)

        self.clock_label = QLabel("--:--:--")
        self.clock_label.setObjectName("Muted")
        layout.addWidget(self.clock_label)

        return panel

    def populate_channels(self):
        server = SERVER_CHANNELS[self.current_server]
        self.channel_header.setText(server["title"])

        while self.channel_list_layout.count():
            item = self.channel_list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.channel_buttons = {}

        for channel_name in server["channels"]:
            button = QPushButton(f"#  {channel_name}")
            button.setObjectName("ChannelButton")
            button.setCheckable(True)
            button.clicked.connect(
                lambda checked, name=channel_name: self.select_channel(name)
            )
            self.channel_list_layout.addWidget(button)
            self.channel_buttons[channel_name] = button

        self.channel_list_layout.addStretch()

        first_channel = next(iter(server["channels"]))
        self.select_channel(first_channel)

    def select_channel(self, channel_name):
        self.current_channel = channel_name

        for name, button in self.channel_buttons.items():
            button.setChecked(name == channel_name)

        self.channel_subtitle.setText(f"# {channel_name}")
        self.populate_ticker_list()

    # --------------------------------------------------------
    # 중앙 시세 영역
    # --------------------------------------------------------

    def create_main_panel(self):
        panel = QFrame()
        panel.setObjectName("MainPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(22, 18, 22, 15)
        layout.setSpacing(14)

        # 상단 제목
        header = QHBoxLayout()

        title_box = QVBoxLayout()
        self.main_title = QLabel("ETF WATCHLIST")
        self.main_title.setObjectName("SectionTitle")

        self.main_description = QLabel("관심 ETF의 실시간 가격과 등락률")
        self.main_description.setObjectName("Muted")

        title_box.addWidget(self.main_title)
        title_box.addWidget(self.main_description)

        header.addLayout(title_box)
        header.addStretch()

        self.last_update_label = QLabel("마지막 갱신: --:--:--")
        self.last_update_label.setObjectName("Muted")
        header.addWidget(self.last_update_label)

        layout.addLayout(header)

        # 시장 지표 카드
        market_title = QLabel("MARKET OVERVIEW")
        market_title.setObjectName("Muted")
        layout.addWidget(market_title)

        card_grid = QGridLayout()
        card_grid.setSpacing(8)

        for index, (name, data) in enumerate(MARKET_DATA.items()):
            card = MarketCard(name, data["price"], data["change"], data["unit"])
            self.market_cards[name] = card
            card_grid.addWidget(card, index // 4, index % 4)

        layout.addLayout(card_grid)

        # 시세 목록 제목
        list_header = QHBoxLayout()

        list_title = QLabel("MARKET WATCHLIST")
        list_title.setObjectName("SectionTitle")
        list_header.addWidget(list_title)
        list_header.addStretch()

        self.item_count_label = QLabel("0 assets")
        self.item_count_label.setObjectName("Muted")
        list_header.addWidget(self.item_count_label)

        layout.addLayout(list_header)

        # 컬럼 제목
        column_header = QHBoxLayout()
        column_header.setContentsMargins(12, 0, 12, 0)

        for text, stretch in [
            ("종목 / 상품명", 3),
            ("역사적 최고가", 2),
            ("현재가", 2),
            ("등락 / 등락률", 2),
        ]:
            label = QLabel(text)
            label.setObjectName("Muted")
            if text != "종목 / 상품명":
                label.setAlignment(Qt.AlignmentFlag.AlignRight)
            column_header.addWidget(label, stretch)

        layout.addLayout(column_header)

        self.ticker_list_layout = QVBoxLayout()
        self.ticker_list_layout.setSpacing(6)
        self.ticker_list_layout.setContentsMargins(0, 0, 0, 0)

        self.ticker_container = QWidget()
        self.ticker_container.setLayout(self.ticker_list_layout)

        ticker_scroll = QScrollArea()
        ticker_scroll.setWidgetResizable(True)
        ticker_scroll.setFrameShape(QFrame.Shape.NoFrame)
        ticker_scroll.setWidget(self.ticker_container)

        layout.addWidget(ticker_scroll, 1)

        # 하단 상태 바
        footer = QHBoxLayout()
        self.market_status_label = QLabel("미국 시장 데이터 모니터링")
        self.market_status_label.setObjectName("Muted")

        self.footer_status_label = QLabel("UI READY")
        self.footer_status_label.setStyleSheet("color: #23D18B;")

        footer.addWidget(self.market_status_label)
        footer.addStretch()
        footer.addWidget(self.footer_status_label)

        layout.addLayout(footer)

        return panel

    def populate_ticker_list(self):
        # 기존 행 제거
        while self.ticker_list_layout.count():
            item = self.ticker_list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.ticker_rows.clear()

        channel_map = SERVER_CHANNELS[self.current_server]["channels"]
        symbols = channel_map.get(self.current_channel, [])

        # 시장/선물/원자재 채널은 별도 안내 표시
        if not symbols:
            self.main_title.setText(self.current_channel.upper())
            self.main_description.setText("시장 지표 영역")
            self.item_count_label.setText("0 assets")
            message = QLabel(
                "해당 채널의 데이터는 상단 MARKET OVERVIEW에서 확인할 수 있다.\n"
                "실제 데이터 연결 시 이 영역에 상세 시세를 배치할 수 있다."
            )
            message.setObjectName("Muted")
            message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ticker_list_layout.addWidget(message)
            return

        self.main_title.setText(self.current_channel.upper())
        self.main_description.setText("종목을 선택하면 우측 상세 패널이 변경된다.")
        self.item_count_label.setText(f"{len(symbols)} assets")

        for symbol in symbols:
            if symbol not in TICKER_DATA:
                continue

            row = TickerRow(
                symbol,
                TICKER_DATA[symbol],
                selected=(symbol == self.selected_ticker),
            )
            row.clicked.connect(self.select_ticker)
            self.ticker_list_layout.addWidget(row)
            self.ticker_rows[symbol] = row

        self.ticker_list_layout.addStretch()

        if symbols and symbols[0] in TICKER_DATA:
            self.select_ticker(
                self.selected_ticker if self.selected_ticker in symbols else symbols[0]
            )

    # --------------------------------------------------------
    # 우측 종목 상세 패널
    # --------------------------------------------------------

    def create_detail_panel(self):
        panel = QFrame()
        panel.setObjectName("DetailPanel")
        panel.setFixedWidth(300)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 20, 18, 16)
        layout.setSpacing(12)

        heading = QLabel("ASSET DETAILS")
        heading.setObjectName("SectionTitle")
        layout.addWidget(heading)

        divider = QFrame()
        divider.setObjectName("Divider")
        layout.addWidget(divider)

        self.detail_symbol = QLabel("TQQQ")
        self.detail_symbol.setObjectName("DetailSymbol")
        layout.addWidget(self.detail_symbol)

        self.detail_name = QLabel("ProShares UltraPro QQQ")
        self.detail_name.setObjectName("Muted")
        self.detail_name.setWordWrap(True)
        layout.addWidget(self.detail_name)

        self.detail_price = QLabel("$60.90")
        self.detail_price.setObjectName("DetailPrice")
        layout.addWidget(self.detail_price)

        self.detail_change = QLabel("+1.44 (+2.41%)")
        self.detail_change.setObjectName("Positive")
        self.detail_change.setProperty("detailChange", True)
        layout.addWidget(self.detail_change)

        divider2 = QFrame()
        divider2.setObjectName("Divider")
        layout.addWidget(divider2)

        # 간단한 차트 플레이스홀더
        chart_frame = QFrame()
        chart_frame.setStyleSheet(
            "background-color: #1E1F22; border: 1px solid #3F4147; border-radius: 8px;"
        )
        chart_frame.setMinimumHeight(150)

        chart_layout = QVBoxLayout(chart_frame)
        chart_label = QLabel("PRICE CHART")
        chart_label.setObjectName("Muted")
        chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        chart_hint = QLabel("PyQtGraph 연동 영역")
        chart_hint.setStyleSheet("color: #5865F2; font-size: 10pt;")
        chart_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        chart_layout.addStretch()
        chart_layout.addWidget(chart_label)
        chart_layout.addWidget(chart_hint)
        chart_layout.addStretch()

        layout.addWidget(chart_frame)

        metrics_title = QLabel("PRICE METRICS")
        metrics_title.setObjectName("SectionTitle")
        layout.addWidget(metrics_title)

        self.info_high = InfoValue("최고가", "-")
        self.info_drawdown = InfoValue("고점 대비 하락률", "-")
        self.info_recovery = InfoValue("고점 회복 필요 상승률", "-")
        self.info_previous = InfoValue("전일 종가", "-")
        self.info_volume = InfoValue("거래량", "-")

        for widget in [
            self.info_high,
            self.info_drawdown,
            self.info_recovery,
            self.info_previous,
            self.info_volume,
        ]:
            layout.addWidget(widget)

        layout.addStretch()

        self.detail_category = QLabel("CATEGORY: ETF")
        self.detail_category.setObjectName("Muted")
        layout.addWidget(self.detail_category)

        return panel

    def select_ticker(self, symbol):
        if symbol not in TICKER_DATA:
            return

        self.selected_ticker = symbol
        data = TICKER_DATA[symbol]

        for row_symbol, row in self.ticker_rows.items():
            row.set_selected(row_symbol == symbol)

        price = data.get("price")
        high = data.get("high")
        change = data.get("change")
        change_pct = data.get("change_pct")

        price_value = float(price) if price is not None else None
        high_value = float(high) if high is not None else None

        drawdown = (
            ((price_value / high_value) - 1) * 100
            if price_value is not None and high_value not in (None, 0)
            else None
        )
        recovery = (
            ((high_value / price_value) - 1) * 100
            if high_value is not None and price_value not in (None, 0)
            else None
        )

        self.detail_symbol.setText(symbol)
        self.detail_name.setText(data.get("name", symbol))
        self.detail_price.setText(
            "--" if price_value is None else f"${price_value:,.2f}"
        )

        if change is None or change_pct is None:
            self.detail_change.setText("--")
            self.detail_change.setObjectName("Muted")
        else:
            sign = "+" if change >= 0 else ""
            self.detail_change.setText(
                f"{sign}{change:.2f} ({sign}{change_pct:.2f}%)"
            )
            self.detail_change.setObjectName(
                "Positive" if change >= 0 else "Negative"
            )

        self.detail_change.style().unpolish(self.detail_change)
        self.detail_change.style().polish(self.detail_change)

        self.info_high.set_value(
            "--" if high_value is None else f"${high_value:,.2f}"
        )
        self.info_drawdown.set_value(
            "--" if drawdown is None else f"{drawdown:.2f}%"
        )
        self.info_recovery.set_value(
            "--" if recovery is None else f"+{recovery:.2f}%"
        )

        previous_close = data.get("previous_close")
        self.info_previous.set_value(
            "--" if previous_close is None else f"${previous_close:,.2f}"
        )
        self.info_volume.set_value(str(data.get("volume", "--")))
        self.detail_category.setText(
            f"CATEGORY: {data.get('category', '관심종목')}"
        )

    # 외부 데이터 엔진 연동 인터페이스
    # --------------------------------------------------------

    def update_ticker_data(self, symbol, data):
        """
        외부 TickerEngine에서 종목 데이터를 전달할 때 호출한다.

        예:
            window.update_ticker_data("TQQQ", {
                "price": 61.20,
                "change": 1.74,
                "change_pct": 2.93,
                "high": 88.09,
                "previous_close": 59.46,
                "volume": "33.1M",
            })

        전달하지 않은 필드는 기존 값을 유지한다.
        """
        if symbol not in TICKER_DATA:
            TICKER_DATA[symbol] = {
                "name": symbol,
                "price": 0.0,
                "change": 0.0,
                "change_pct": 0.0,
                "high": 0.0,
                "previous_close": 0.0,
                "volume": "-",
                "category": "관심종목",
            }

        TICKER_DATA[symbol].update(data)

        if symbol in self.ticker_rows:
            old_row = self.ticker_rows[symbol]
            old_row.data = TICKER_DATA[symbol]
            current_price = TICKER_DATA[symbol].get("price")
            old_row.price_label.setText(
                "--" if current_price is None else f"${current_price:,.2f}"
            )
            old_row.set_high(TICKER_DATA[symbol].get("high"))
            old_row.set_change(
                TICKER_DATA[symbol]["change"],
                TICKER_DATA[symbol]["change_pct"],
            )

        if self.selected_ticker == symbol:
            self.select_ticker(symbol)

        self.update_last_update()

    def update_market_data(self, market_data):
        """
        시장 지표 카드 갱신 인터페이스.

        예:
            window.update_market_data({
                "NASDAQ": {"price": 28350.0, "change": 0.15, "unit": ""}
            })
        """
        for name, data in market_data.items():
            if name not in MARKET_DATA:
                continue

            MARKET_DATA[name].update(data)

            if name in self.market_cards:
                item = MARKET_DATA[name]
                self.market_cards[name].set_values(
                    item["price"],
                    item["change"],
                    item.get("unit", ""),
                )

        self.update_last_update()

    def update_last_update(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.last_update_label.setText(f"마지막 갱신: {now}")

    def set_connection_status(self, message, connected=True):
        self.connection_label.setText(("●  " if connected else "●  ") + message)
        self.connection_label.setStyleSheet(
            "color: #23D18B;" if connected else "color: #F23F43;"
        )
        self.footer_status_label.setText("CONNECTED" if connected else "DATA ERROR")
        self.footer_status_label.setStyleSheet(
            "color: #23D18B;" if connected else "color: #F23F43;"
        )

    def update_clock(self):
        self.clock_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

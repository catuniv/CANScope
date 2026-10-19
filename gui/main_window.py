import threading
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QPalette
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QCheckBox,
    QComboBox,
    QLineEdit,
    QStackedWidget
)
from core.receiver import run_receiver
from simulator.ecu_simulator import run_simulator


class MainWindow(QMainWindow):

    def paintEvent(self, event):
        painter = QPainter(self)

        scaled_background = self.background.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        x = (self.width() - scaled_background.width()) // 2
        y = (self.height() - scaled_background.height()) // 2

        painter.drawPixmap(x, y, scaled_background)
        super().paintEvent(event)
        painter.fillRect(
            self.rect(),
            QColor(0, 0, 0, 170)
        )

    message_received = Signal(
        float,
        str,
        int,
        str,
        str
    )

    def __init__(self):
        super().__init__()

        self.background = QPixmap("assets/can3.jpg")

        self.setWindowTitle("CANScope")
        self.resize(1000, 600)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            [
                "Time",
                "ID",
                "DLC",
                "DATA",
                "Decoded"
            ]
        )
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.Stretch
        )


        ######### Table ##########
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setRowCount(3)
        self.stats_table.setMaximumHeight(150)
        stats_header = self.stats_table.horizontalHeader()

        self.stats_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        stats_header.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.stats_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Count",
                "Period",
                "Frequency"
            ]
        )

        self.stats_table.setRowCount(3)
        self.stats_table.verticalHeader().setVisible(False)

        self.stats_table.setItem(
            0,
            0,
            QTableWidgetItem("0x100")
        )

        self.stats_table.setItem(
            1,
            0,
            QTableWidgetItem("0x101")
        )

        self.stats_table.setItem(
            2,
            0,
            QTableWidgetItem("0x102")
        )



        central_widget = QWidget()
        central_widget.setStyleSheet(
            "background: transparent;"
        )
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        control_layout = QHBoxLayout()
        dashboard_layout = QHBoxLayout()

        # Start, Stop, Clear Button init
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.clear_button = QPushButton("Clear")

        # Menu Button #
        self.analyzer_button = QPushButton("Analyzer")
        self.dashboard_button = QPushButton("Dashboard")
        self.statistics_button = QPushButton("Statistics")

        self.analyzer_button.setCheckable(True)
        self.dashboard_button.setCheckable(True)
        self.statistics_button.setCheckable(True)

        self.analyzer_button.setChecked(True)

        self.analyzer_button.setObjectName("menuButton")
        self.dashboard_button.setObjectName("menuButton")
        self.statistics_button.setObjectName("menuButton")

        # Auto Scroll init
        self.auto_scroll_checkbox = QCheckBox("Auto Scroll")

        # CAN Filter init
        self.id_filter = QComboBox()
        self.id_filter.setMinimumWidth(110)
        self.id_filter.view().setStyleSheet(
        """
        QListView {
            background-color: #111111;
            color: #FFFFFF;
            border: 1px solid #FFFFFF;
            selection-background-color: #444444;
            selection-color: #FFFFFF;
        }
        """
    )

        # Search init
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search ID / DATA / Decoded"
        )

        ############ Label ##############
        #message_count
        self.message_count = 0
        self.total_label = QLabel("Total: 0")
        self.visible_label = QLabel("Visible: 0")

        # Dashboard Title / Value
        self.rpm_title = QLabel("RPM")
        self.rpm_value = QLabel("0 rpm")

        self.speed_title = QLabel("SPEED")
        self.speed_value = QLabel("0 km/h")

        self.battery_title = QLabel("BATTERY")
        self.battery_value = QLabel("0 %")


        # Dashboard Card
        self.rpm_card = QWidget()
        self.speed_card = QWidget()
        self.battery_card = QWidget()

        self.rpm_card.setObjectName("dashboardCard")
        self.speed_card.setObjectName("dashboardCard")
        self.battery_card.setObjectName("dashboardCard")


        # Dashboard Card 내부 Layout
        rpm_card_layout = QVBoxLayout()
        speed_card_layout = QVBoxLayout()
        battery_card_layout = QVBoxLayout()

        self.rpm_card.setLayout(rpm_card_layout)
        self.speed_card.setLayout(speed_card_layout)
        self.battery_card.setLayout(battery_card_layout)


        # Card 안에 Title / Value 넣기
        rpm_card_layout.addWidget(self.rpm_title)
        rpm_card_layout.addWidget(self.rpm_value)

        speed_card_layout.addWidget(self.speed_title)
        speed_card_layout.addWidget(self.speed_value)

        battery_card_layout.addWidget(self.battery_title)
        battery_card_layout.addWidget(self.battery_value)


        # 가운데 정렬
        self.rpm_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.rpm_value.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.speed_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.speed_value.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.battery_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.battery_value.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )


        # 값 Label 스타일 이름
        self.rpm_value.setObjectName("dashboardValue")
        self.speed_value.setObjectName("dashboardValue")
        self.battery_value.setObjectName("dashboardValue")


        # 카드 높이
        self.rpm_card.setMinimumHeight(220)
        self.speed_card.setMinimumHeight(220)
        self.battery_card.setMinimumHeight(220)


        # CAN_id counts
        self.id_counts = {}

        # periods, frequency
        self.last_timestamp = {} # ID가 마지막으로 들어온 시간
        self.id_periods = {}    # ID 최근 주기

        # period, frequency avg
        self.period_sum = {}
        self.period_count = {}

        # message running
        self.is_running = True

        # start, stop button enabled
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Auto scroll
        self.auto_scroll_checkbox.setChecked(True)

        
        ######## Layout ########
        # Control Layout
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.clear_button)
        control_layout.addWidget(self.id_filter)
        control_layout.addWidget(self.search_input)
        control_layout.addWidget(self.auto_scroll_checkbox)
        control_layout.addStretch()
        control_layout.addWidget(self.total_label)
        control_layout.addWidget(self.visible_label)

        # Dashboard Layout
        dashboard_layout.addWidget(self.rpm_card, 1)
        dashboard_layout.addWidget(self.speed_card, 1)
        dashboard_layout.addWidget(self.battery_card, 1)

        # sidebar Layout
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setFixedWidth(160)


        sidebar_layout = QVBoxLayout()
        sidebar_widget.setLayout(sidebar_layout)


        title_label = QLabel("CANScope")
        title_label.setObjectName("sidebarTitle")

        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        sidebar_layout.addWidget(
            title_label
        )

        sidebar_layout.addWidget(
            self.analyzer_button
        )

        sidebar_layout.addWidget(
            self.dashboard_button
        )

        sidebar_layout.addWidget(
            self.statistics_button
        )

        sidebar_layout.addWidget(title_label)

        # Stacked Widget 생성
        self.stacked_widget = QStackedWidget()
        self.analyzer_page = QWidget()
        self.dashboard_page = QWidget()
        self.statistics_page = QWidget()

        # 각 페이지 Layout 생성
        analyzer_layout = QVBoxLayout()
        dashboard_page_layout = QVBoxLayout()
        statistics_layout = QVBoxLayout()

        # 페이지에 Layout 연결
        self.analyzer_page.setLayout(
            analyzer_layout
        )

        self.dashboard_page.setLayout(
            dashboard_page_layout
        )

        self.statistics_page.setLayout(
            statistics_layout
        )

        # 각 페이지에 기존 위젯 배치
        # Analyzer Page
        analyzer_layout.addLayout(
            control_layout
        )

        analyzer_layout.addWidget(
            self.table
        )

        # Dashboard Page
        dashboard_page_layout.addStretch()
        dashboard_page_layout.addLayout(dashboard_layout)
        dashboard_page_layout.addStretch()

        # Statistics Page
        statistics_layout.addWidget(
            self.stats_table
        )

        # Stacked Widget에 페이지 등록
        self.stacked_widget.addWidget(
            self.analyzer_page
        )

        self.stacked_widget.addWidget(
            self.dashboard_page
        )

        self.stacked_widget.addWidget(
            self.statistics_page
        )

        # Main Layout에는 메뉴 + Stacked Widget만
        main_layout.addWidget(
            sidebar_widget
        )

        main_layout.addWidget(
            self.stacked_widget,
            1
        )

        # 처음 실행 시 Analyzer 화면
        self.stacked_widget.setCurrentIndex(0)


        ### Signal ###
        # clear Signal
        self.clear_button.clicked.connect(
            self.clear_table
        )

        # stop Signal
        self.stop_button.clicked.connect(
            self.stop_receiving
        )

        # start Signal
        self.start_button.clicked.connect(
            self.start_receiving
        )

        # Search Signal
        self.id_filter.currentTextChanged.connect(
            self.apply_filter
        )
        self.search_input.textChanged.connect(
            self.apply_filter
        )

        self.analyzer_button.clicked.connect(
            lambda: self.change_page(0)
        )

        self.dashboard_button.clicked.connect(
            lambda: self.change_page(1)
        )

        self.statistics_button.clicked.connect(
            lambda: self.change_page(2)
        )


        self.id_filter.addItems(
            [
                "All IDs",
                "0x100",
                "0x101",
                "0x102"
            ]
        )




        self.setStyleSheet(
            """
            QTableWidget {
                background-color: rgba(0, 0, 0, 252);
                alternate-background-color: rgba(10, 10, 10, 230);
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
                gridline-color: #666666;
                selection-background-color: rgba(70, 70, 70, 255);
                selection-color: #FFFFFF;
            }

            QHeaderView::section {
                background-color: rgba(5, 5, 5, 252);
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
                padding: 8px;
                font-weight: bold;
            }

            QTableCornerButton::section {
                background-color: rgba(5, 5, 5, 210);
                border: 1px solid #FFFFFF;
            }

            QLabel {
                color: #FFFFFF;
                background-color: transparent;
                font-weight: bold;
            }

            QLineEdit {
                background-color: rgba(0, 0, 0, 180);
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
                border-radius: 4px;
                padding: 5px;
            }

            QLineEdit::placeholder {
                color: #AAAAAA;
            }

            QLineEdit:focus {
                border: 2px solid #FFFFFF;
            }

            QPushButton {
                background-color: rgba(0, 0, 0, 200);
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
                border-radius: 4px;
                padding: 5px 12px;
            }

            QPushButton:hover {
                background-color: rgba(60, 60, 60, 220);
            }

            QPushButton:disabled {
                color: #888888;
                border: 1px solid #666666;
            }

            QComboBox {
                background-color: rgba(0, 0, 0, 220);
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
                border-radius: 4px;
                padding: 5px 30px 5px 10px;
                min-width: 80px;
            }

            QComboBox::drop-down {
                border: none;
                width: 30px;
            }

            QComboBox QAbstractItemView {
                background-color: #111111;
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
                selection-background-color: #444444;
                selection-color: #FFFFFF;
                padding: 4px;
            }

            QWidget#dashboardCard {
                background-color: rgba(0, 0, 0, 210);
                border: 1px solid #FFFFFF;
                border-radius: 8px;
            }

            QLabel#dashboardValue {
                color: #FFFFFF;
                font-size: 28px;
                font-weight: bold;
            }

            QWidget#sidebar {
                background-color: rgba(0, 0, 0, 220);
                border-right: 1px solid #FFFFFF;
            }

            QLabel#sidebarTitle {
                color: #FFFFFF;
                font-size: 22px;
                font-weight: bold;
                padding: 20px 5px;
            }

            QPushButton#menuButton {
                background-color: transparent;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
            }

            QPushButton#menuButton:hover {
                background-color: rgba(255, 255, 255, 40);
            }
            
            QPushButton#menuButton:checked {
                background-color: rgba(255, 255, 255, 60);
                border-left: 3px solid #FFFFFF;
                font-weight: bold;
            }

            """
        )

        self.message_received.connect(
            self.add_message
        )
        receiver_thread = threading.Thread(
            target=run_receiver,
            args=(self.message_received.emit,),
            daemon=True
        )

        simulator_thread = threading.Thread(
            target=run_simulator,
            daemon=True
        )

        receiver_thread.start()
        simulator_thread.start()





    def add_message(
        self,
        timestamp,
        can_id,
        dlc,
        data,
        decoded,
    ):

        # Start / Stop / Clear default
        if not self.is_running:
            return

        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(
            row,
            0,
            QTableWidgetItem(f"{timestamp:.3f}")
        )

        self.table.setItem(
            row,
            1,
            QTableWidgetItem(can_id)
        )

        self.table.setItem(
            row,
            2,
            QTableWidgetItem(str(dlc))
        )

        self.table.setItem(
            row,
            3,
            QTableWidgetItem(data)
        )

        self.table.setItem(
            row,
            4,
            QTableWidgetItem(decoded)
        )


        ### message ###
        self.message_count += 1
        
        self.total_label.setText(
            f"Total: {self.message_count}"
        )

        ### can_id_counts ###
        if can_id not in self.id_counts:
            self.id_counts[can_id] = 1
        else:
            self.id_counts[can_id] += 1

        ### period ###
        if can_id in self.last_timestamp:
            period = timestamp - self.last_timestamp[can_id]

            if can_id not in self.period_sum:
                self.period_sum[can_id] = 0
                self.period_count[can_id] = 0

            self.period_sum[can_id] += period
            self.period_count[can_id] += 1

            average_period = (
                self.period_sum[can_id]
                / self.period_count[can_id]
            )
            self.id_periods[can_id] = average_period

        self.last_timestamp[can_id] = timestamp

        self.update_statistics()

        if can_id == "0x100":
            value = decoded.replace("RPM=", "")
            self.rpm_value.setText(value)

        elif can_id == "0x101":
            value = decoded.replace("Speed=", "")
            self.speed_value.setText(value)

        elif can_id == "0x102":
            value = decoded.replace("Battery=", "")
            self.battery_value.setText(value)




        self.apply_filter_to_row(row)

        self.update_visible_count()


        if self.auto_scroll_checkbox.isChecked():
            self.table.scrollToBottom()


    def apply_filter_to_row(self, row):
        selected_id = self.id_filter.currentText()
        search_text = self.search_input.text().lower()
        id_item = self.table.item(row, 1)

        data_item = self.table.item(row, 3)
        decoded_item = self.table.item(row, 4)

        can_id = id_item.text()
        data = data_item.text()
        decoded = decoded_item.text()

        id_match = (
            selected_id == "All IDs"
            or can_id == selected_id
        )

        search_target = (
            f"{can_id} {data} {decoded}"
        ).lower()

        search_match = (
            search_text == ""
            or search_text in search_target
        )

        show_row = id_match and search_match

        self.table.setRowHidden(
            row,
            not show_row
        )



    def apply_filter(self):
        for row in range(self.table.rowCount()):
            self.apply_filter_to_row(row)

        self.update_visible_count()


    def update_visible_count(self):
        visible_count = 0

        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                visible_count += 1

        self.visible_label.setText(
            f"Visible: {visible_count}"
        )

    ### start, stop, clear button function ###
    # clear
    def clear_table(self):
        self.table.setRowCount(0)
        self.message_count = 0
        self.id_counts.clear()
        self.last_timestamp.clear()
        self.id_periods.clear()
        self.period_sum.clear()
        self.period_count.clear()

        self.total_label.setText(
            "Total: 0"
        )
        self.visible_label.setText(
            "Visible: 0"
        )
        self.rpm_value.setText("0 rpm")
        self.speed_value.setText("0 km/h")
        self.battery_value.setText("0 %")

        self.update_statistics()

    # stop
    def stop_receiving(self):
        self.is_running = False

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    # start
    def start_receiving(self):
        self.is_running = True

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def update_statistics(self):
        ids = [
            "0x100",
            "0x101",
            "0x102"
        ]

        for row, can_id in enumerate(ids):

            count = self.id_counts.get(
                can_id,
                0
            )
            period = self.id_periods.get(
                can_id,
                0
            )
            frequency = (
                1 / period
                if period > 0
                else 0
            )
            self.stats_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(count)
                )
            )
            self.stats_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    f"{period:.3f}s"
                )
            )
            self.stats_table.setItem(
                row,
                3,
                QTableWidgetItem(
                    f"{frequency:.1f}Hz"
                )
            )

    def change_page(self, index):
        self.stacked_widget.setCurrentIndex(index)

        self.analyzer_button.setChecked(
            index == 0
        )

        self.dashboard_button.setChecked(
            index == 1
        )

        self.statistics_button.setChecked(
            index == 2
        )

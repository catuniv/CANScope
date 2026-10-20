import threading
import csv
import os
from datetime import datetime
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QPalette
from PySide6.QtCore import Qt
import pyqtgraph as pg
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
    QStackedWidget,
    QListWidget,
    QMessageBox
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
        self.graph_button = QPushButton("Graph")
        self.logger_button = QPushButton("Logger")

        self.analyzer_button.setCheckable(True)
        self.dashboard_button.setCheckable(True)
        self.statistics_button.setCheckable(True)
        self.graph_button.setCheckable(True)
        self.logger_button.setCheckable(True)

        self.analyzer_button.setChecked(True)

        self.analyzer_button.setObjectName("menuButton")
        self.dashboard_button.setObjectName("menuButton")
        self.statistics_button.setObjectName("menuButton")
        self.graph_button.setObjectName("menuButton")
        self.logger_button.setObjectName("menuButton")

        # Logger Button 
        self.start_log_button = QPushButton("Start Logging")
        self.stop_log_button = QPushButton("Stop Logging")

        self.log_status_label = QLabel(
            "Logging: OFF"
        )

        self.stop_log_button.setEnabled(False)

        # Logger File List
        self.refresh_log_button = QPushButton(
            "Refresh Logs"
        )
        self.log_list = QListWidget()

        self.delete_log_button = QPushButton(
            "Delete Selected Log"
        )

        self.selected_log_label = QLabel(
            "Selected: None"
        )

        self.log_list.setStyleSheet(
            """
            QListWidget {
                background-color: rgba(0, 0, 0, 220);
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
            }

            QListWidget::item {
                color: #FFFFFF;
                padding: 6px;
            }

            QListWidget::item:selected {
                background-color: #444444;
                color: #FFFFFF;
            }

            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 30);
            }
            """
        )

        # Logger Preview Table
        self.log_preview_table = QTableWidget()
        self.log_preview_table.setColumnCount(5)

        self.log_preview_table.setHorizontalHeaderLabels(
            [
                "Time",
                "ID",
                "DLC",
                "DATA",
                "Decoded"
            ]
        )

        self.log_preview_table.verticalHeader().setVisible(False)

        self.log_preview_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
            )

        preview_header = self.log_preview_table.horizontalHeader()

        preview_header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        preview_header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )

        preview_header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        preview_header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Stretch
        )

        preview_header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.Stretch
        )
        

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

        # RPM Graph Data
        self.rpm_times = []
        self.rpm_values = []

        # Speed Graph Data
        self.speed_times = []
        self.speed_values = []

        # Battery Graph Data
        self.battery_times = []
        self.battery_values = []

        # Logger
        self.is_logging = False
        self.log_file = None
        self.csv_writer = None

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
            self.analyzer_button
        )

        sidebar_layout.addWidget(
            self.dashboard_button
        )

        sidebar_layout.addWidget(
            self.statistics_button
        )

        sidebar_layout.addWidget(
            self.graph_button
        )

        sidebar_layout.addWidget(
            self.logger_button
        )

        sidebar_layout.addStretch()

        sidebar_layout.addWidget(
            title_label
        )

        # Stacked Widget 생성
        self.stacked_widget = QStackedWidget()
        self.analyzer_page = QWidget()
        self.dashboard_page = QWidget()
        self.statistics_page = QWidget()
        self.graph_page = QWidget()
        self.logger_page = QWidget()

        # Graph Widget 생성
        self.rpm_graph = pg.PlotWidget()
        self.rpm_graph.setBackground(
            (10, 10, 10)
        )

        self.rpm_graph.setTitle(
            "RPM Real-Time Graph"
        )
        self.rpm_graph.setLabel(
            "left",
            "RPM"
        )
        self.rpm_graph.setLabel(
            "bottom",
            "Time"
        )
        self.rpm_graph.showGrid(
            x=True,
            y=True,
            alpha=0.3
        )

        axis_pen = pg.mkPen(
            color=(220, 220, 220)
        )

        self.rpm_graph.getAxis("left").setPen(
            axis_pen
        )

        self.rpm_graph.getAxis("bottom").setPen(
            axis_pen
        )

        self.rpm_graph.getAxis("left").setTextPen(
            axis_pen
        )

        self.rpm_graph.getAxis("bottom").setTextPen(
            axis_pen
        )

        self.rpm_curve = self.rpm_graph.plot(
            [],
            [],
            pen=pg.mkPen(
                color=(0, 255, 255),
                width=3
            ),
            symbol="o",
            symbolSize=5
        )

        # Speed Graph
        self.speed_graph = pg.PlotWidget()

        self.speed_graph.setBackground(
            (10, 10, 10)
        )

        self.speed_graph.setTitle(
            "Speed Real-time Graph"
        )

        self.speed_graph.setLabel(
            "left",
            "Speed",
            units="km/h"
        )

        self.speed_graph.setLabel(
            "bottom",
            "Time"
        )

        self.speed_graph.showGrid(
            x=True,
            y=True,
            alpha=0.3
        )

        self.speed_graph.getAxis("left").setPen(
            axis_pen
        )

        self.speed_graph.getAxis("bottom").setPen(
            axis_pen
        )

        self.speed_graph.getAxis("left").setTextPen(
            axis_pen
        )

        self.speed_graph.getAxis("bottom").setTextPen(
            axis_pen
        )

        self.speed_curve = self.speed_graph.plot(
            [],
            [],
            pen=pg.mkPen(
                color=(255, 180, 0),
                width=3
            ),
            symbol="o",
            symbolSize=5
        )

        # Battery Graph
        self.battery_graph = pg.PlotWidget()

        self.battery_graph.setBackground(
            (10, 10, 10)
        )

        self.battery_graph.setTitle(
            "Battery Real-time Graph"
        )

        self.battery_graph.setLabel(
            "left",
            "Battery",
            units="%"
        )

        self.battery_graph.setLabel(
            "bottom",
            "Time"
        )

        self.battery_graph.showGrid(
            x=True,
            y=True,
            alpha=0.3
        )

        self.battery_graph.getAxis("left").setPen(
            axis_pen
        )

        self.battery_graph.getAxis("bottom").setPen(
            axis_pen
        )

        self.battery_graph.getAxis("left").setTextPen(
            axis_pen
        )

        self.battery_graph.getAxis("bottom").setTextPen(
            axis_pen
        )

        self.battery_curve = self.battery_graph.plot(
            [],
            [],
            pen=pg.mkPen(
                color=(120, 255, 120),
                width=3
            ),
            symbol="o",
            symbolSize=5
        )



        # 각 페이지 Layout 생성
        analyzer_layout = QVBoxLayout()
        dashboard_page_layout = QVBoxLayout()
        statistics_layout = QVBoxLayout()
        graph_layout = QVBoxLayout()
        logger_layout = QVBoxLayout()

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

        self.graph_page.setLayout(
            graph_layout
        )

        self.logger_page.setLayout(
            logger_layout
        )

        # 각 페이지에 기존 위젯 배치
        # Analyzer Page
        analyzer_layout.addLayout(
            control_layout
        )

        analyzer_layout.addWidget(
            self.table
        )

        graph_layout.addWidget(
            self.rpm_graph
        )

        graph_layout.addWidget(
            self.speed_graph
        )

        graph_layout.addWidget(
            self.battery_graph
        )

        # Logger Page
        logger_layout.addWidget(
            self.log_status_label
        )
        logger_layout.addWidget(
            self.start_log_button
        )
        logger_layout.addWidget(
            self.stop_log_button
        )
        logger_layout.addWidget(
            self.refresh_log_button
        )
        logger_layout.addWidget(
            self.log_list
        )
        logger_layout.addWidget(
            self.log_preview_table
        )
        logger_layout.addWidget(
            self.delete_log_button
        )
        logger_layout.addWidget(
            self.selected_log_label
        )

        logger_layout.addStretch

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

        self.stacked_widget.addWidget(
            self.graph_page
        )

        self.stacked_widget.addWidget(
            self.logger_page
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

        self.graph_button.clicked.connect(
            lambda: self.change_page(3)
        )

        self.logger_button.clicked.connect(
            lambda: self.change_page(4)
        )

        self.start_log_button.clicked.connect(
            self.start_logging
        )
        self.stop_log_button.clicked.connect(
            self.stop_logging
        )

        self.refresh_log_button.clicked.connect(
            self.refresh_log_list
        )

        self.log_list.itemDoubleClicked.connect(
            self.load_log_file
        )
        self.log_list.itemClicked.connect(
            self.select_log_file
        )
        self.delete_log_button.clicked.connect(
            self.delete_selected_log
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
            QMessageBox {
                background-color: #2B2B2B;
            }

            QMessageBox QLabel {
                color: #FFFFFF;
                background-color: transparent;
                font-size: 14px;
            }

            QMessageBox QPushButton {
                background-color: #444444;
                color: #FFFFFF;
                border: 1px solid #888888;
                border-radius: 5px;
                padding: 7px 20px;
                min-width: 80px;
            }

            QMessageBox QPushButton:hover {
                background-color: #5A5A5A;
            }

            QMessageBox QPushButton:pressed {
                background-color: #666666;
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

        self.refresh_log_list()
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

        # CAN Logger
        if self.is_logging:
            self.csv_writer.writerow(
                [
                    f"{timestamp:.3f}",
                    can_id,
                    dlc,
                    data,
                    decoded
                ]
            )
            self.log_file.flush()


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

            rpm_text = (
                decoded
                .replace("RPM=", "")
                .replace(" rpm", "")
            )
            rpm = float(rpm_text)

            self.rpm_times.append(timestamp)
            self.rpm_values.append(rpm)

            if len(self.rpm_times) > 100:
                self.rpm_times.pop(0)
                self.rpm_values.pop(0)

            self.rpm_curve.setData(
                self.rpm_times,
                self.rpm_values
            )

        elif can_id == "0x101":
            value = decoded.replace("Speed=", "")
            self.speed_value.setText(value)

            speed_text = (
                decoded
                .replace("Speed=", "")
                .replace(" km/h", "")
            )
            speed = float(speed_text)

            self.speed_times.append(timestamp)
            self.speed_values.append(speed)

            if len(self.speed_times) > 100:
                self.speed_times.pop(0)
                self.speed_values.pop(0)

            self.speed_curve.setData(
                self.speed_times,
                self.speed_values
            )

        elif can_id == "0x102":
            value = decoded.replace("Battery=", "")
            self.battery_value.setText(value)

            battery_text = (
                decoded
                .replace("Battery=", "")
                .replace(" %", "")
            )

            battery = float(battery_text)

            self.battery_times.append(timestamp)
            self.battery_values.append(battery)

            if len(self.battery_times) > 100:
                self.battery_times.pop(0)
                self.battery_values.pop(0)

            self.battery_curve.setData(
                self.battery_times,
                self.battery_values
    )




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

        self.rpm_times.clear()
        self.rpm_values.clear()
        self.speed_times.clear()
        self.speed_values.clear()
        self.battery_times.clear()
        self.battery_values.clear()


        self.rpm_curve.setData([], [])
        self.speed_curve.setData([], [])
        self.battery_curve.setData([], [])

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
        self.refresh_log_list()

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

        self.graph_button.setChecked(
            index == 3
        )

        self.logger_button.setChecked(
            index == 4
        )

    def start_logging(self):
        os.makedirs(
            "logs",
            exist_ok=True
        )

        current_time = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )
        file_name = (
            f"logs/can_log_{current_time}.csv"
        )
        self.log_file = open(
            file_name,
            "w",
            newline=""
        )
        self.csv_writer = csv.writer(
            self.log_file
        )
        self.csv_writer.writerow(
            [
                "Time",
                "ID",
                "DLC",
                "DATA",
                "Decoded"
            ]
        )

        self.is_logging = True
        self.log_status_label.setText(
            f"Logging: ON\n{file_name}"
        )
        self.start_log_button.setEnabled(False)
        self.stop_log_button.setEnabled(True)

    def stop_logging(self):
        self.is_logging = False
        if self.log_file is not None:
            self.log_file.close()

        self.log_file = None
        self.csv_writer = None

        self.log_status_label.setText(
            "Logging: OFF"
        )

        self.start_log_button.setEnabled(True)
        self.stop_log_button.setEnabled(False)


    def refresh_log_list(self):
        self.log_list.clear()
        if not os.path.exists("logs"):
            return

        files = os.listdir("logs")

        csv_files = []

        for file_name in files:
            if file_name.endswith(".csv"):
                csv_files.append(file_name)

        csv_files.sort(
            reverse=True
        )

        for file_name in csv_files:
            self.log_list.addItem(
                file_name
            )

    def load_log_file(self, item):

        file_name = item.text()

        file_path = os.path.join(
            "logs",
            file_name
        )

        self.log_preview_table.setRowCount(0)

        with open(
            file_path,
            "r",
            newline=""
        ) as file:

            reader = csv.reader(file)

            next(reader, None)

            for row_data in reader:

                row = self.log_preview_table.rowCount()
                self.log_preview_table.insertRow(row)

                for column, value in enumerate(row_data):

                    self.log_preview_table.setItem(
                        row,
                        column,
                        QTableWidgetItem(value)
                    )

    def select_log_file(self, item):
        file_name = item.text()

        self.selected_log_label.setText(
            f"Selected: {file_name}"
        )

    def delete_selected_log(self):

        item = self.log_list.currentItem()

        if item is None:
            QMessageBox.information(
                self,
                "No Selection",
                "삭제할 로그 파일을 먼저 선택하세요."
            )
            return

        file_name = item.text()

        message_box = QMessageBox(self)

        message_box.setWindowTitle(
            "Delete Log"
        )

        message_box.setText(
            f"{file_name}\n\n"
            "정말 삭제하시겠습니까?\n"
            "Are you sure you want to delete this log?"
        )

        message_box.setIcon(
            QMessageBox.Icon.NoIcon
        )

        message_box.setStandardButtons(
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        message_box.setDefaultButton(
            QMessageBox.StandardButton.No
        )

        result = message_box.exec()

        if result != QMessageBox.StandardButton.Yes:
            return

        file_path = os.path.join(
            "logs",
            file_name
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        self.log_preview_table.setRowCount(0)

        self.selected_log_label.setText(
            "Selected: None"
        )

        self.refresh_log_list()
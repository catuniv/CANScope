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
    QLineEdit
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
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        control_layout = QHBoxLayout()

        # Start, Stop, Clear Button init
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.clear_button = QPushButton("Clear")

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

        #message_count
        self.message_count = 0
        self.total_label = QLabel("Total: 0")
        self.visible_label = QLabel("Visible: 0")


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
        

        # 시작, 중지, 초기화 버튼
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.clear_button)

        #Filter Box
        control_layout.addWidget(self.id_filter)

        # Search Line
        control_layout.addWidget(self.search_input)

        # Auto Scroll CheckBox
        control_layout.addWidget(self.auto_scroll_checkbox)



        control_layout.addStretch()
        control_layout.addWidget(self.total_label)
        control_layout.addWidget(self.visible_label)

        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.stats_table)
        main_layout.addWidget(self.table)

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

import threading
from PySide6.QtCore import Signal
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

    message_received = Signal(
        float,
        str,
        int,
        str,
        str
    )

    def __init__(self):
        super().__init__()

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


        central_widget = QWidget()
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

        # Search init
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search ID / DATA / Decoded"
        )

        #message_count
        self.message_count = 0
        self.total_label = QLabel("Total: 0")
        self.visible_label = QLabel("Visibel: 0")

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
            QMainWindow {
                background-color: #000000;
            }

            QTableWidget {
                    background-color: #000000;
                    alternate-background-color: #0A0A0A;
                    color: #00FF00; /* 테이블 내부 글자색: 형광 초록 */
                    border: 1px solid #1A1A1A;
                    gridline-color: #1A331A; /* 격자선: 어두운 초록 */
                    selection-background-color: #004400; /* 선택 영역 배경: 진한 초록 */
                    selection-color: #FFFFFF;
                }

            QHeaderView::section {
                    background-color: #050505;
                    color: #00FF00; /* 테이블 헤더 글자색: 형광 초록 */
                    border: 1px solid #1A1A1A;
                    padding: 8px;
                    font-weight: bold;
                }

            QTableCornerButton::section {
                background-color: #050505;
                border: 1px solid #1A1A1A;
                }

            QLabel {
                color: #00FF00;
                background-color: transparent;
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
        
        self.total_label.setText(
            "Total: 0"
        )
        self.visible_label.setText(
            "Visible: 0"
        )

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


    

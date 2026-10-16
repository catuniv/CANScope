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
    QCheckBox
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

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.clear_button = QPushButton("Clear")
        self.auto_scroll_checkbox = QCheckBox("Auto Scroll")

        #message_count
        self.message_count = 0
        self.message_label = QLabel("Message: 0")

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
        control_layout.addWidget(self.auto_scroll_checkbox)

        control_layout.addStretch()
        control_layout.addWidget(self.message_label)

        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.table)


        # clear button
        self.clear_button.clicked.connect(
            self.clear_table
        )

        # stop button
        self.stop_button.clicked.connect(
            self.stop_receiving
        )

        # start button
        self.start_button.clicked.connect(
            self.start_receiving
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
        self.message_label.setText(
            f"Messages: {self.message_count}"
        )

        if self.auto_scroll_checkbox.isChecked():
            self.table.scrollToBottom()



    ### start, stop, clear button function ###
    # clear
    def clear_table(self):
        self.table.setRowCount(0)
        self.message_count = 0
        self.message_label.setText(
            "Messages: 0"
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


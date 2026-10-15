import threading
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
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
        self.setCentralWidget(self.table)

        

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
        decoded
    ):

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
        self.table.scrollToBottom()
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QPushButton, QTableWidget,
    QTableWidgetItem
)
from PySide6.QtCore import Qt
from database.db_connection import get_connection


class ReportsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Reports")
        self.setGeometry(300, 150, 900, 550)

        layout = QVBoxLayout()

        title = QLabel("Subscription & Payment Report")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
            color:#2c3e50;
            margin:15px;
        """)
        layout.addWidget(title)

        self.load_btn = QPushButton("Load Report")
        self.load_btn.setStyleSheet("""
            QPushButton{
                background:#3498db;
                color:white;
                padding:10px;
                font-size:14px;
                border-radius:8px;
            }
            QPushButton:hover{
                background:#2980b9;
            }
        """)
        self.load_btn.clicked.connect(self.load_report)

        layout.addWidget(self.load_btn)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Member Name",
            "Plan Name",
            "Amount",
            "Start Date",
            "End Date",
            "Payment Date",
            "Payment Method"
        ])

        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_report(self):

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT m.name,
               p.plan_name,
               pay.amount,
               s.start_date,
               s.end_date,
               pay.payment_date,
               pay.payment_method
        FROM subscriptions s
        JOIN members m ON s.member_id = m.member_id
        JOIN plans p ON s.plan_id = p.plan_id
        LEFT JOIN payments pay ON s.subscription_id = pay.subscription_id
        """

        cursor.execute(query)
        records = cursor.fetchall()

        self.table.setRowCount(len(records))

        for row_index, row_data in enumerate(records):
            for col_index, data in enumerate(row_data):
                self.table.setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(str(data))
                )

        cursor.close()
        conn.close()
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt
from datetime import datetime, timedelta
from database.db_connection import get_connection


class SubscriptionsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Manage Subscriptions")
        self.setGeometry(250, 120, 900, 600)

        main_layout = QVBoxLayout()

        title = QLabel("Subscriptions Management")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px; font-weight:bold; color:#2c3e50;")
        main_layout.addWidget(title)

        form_layout = QFormLayout()

        self.id_input = QLineEdit()
        self.member_id_input = QLineEdit()
        self.plan_id_input = QLineEdit()
        self.start_date_input = QLineEdit()

        self.id_input.setPlaceholderText("Subscription ID (for Update/Delete)")
        self.member_id_input.setPlaceholderText("Member ID")
        self.plan_id_input.setPlaceholderText("Plan ID")
        self.start_date_input.setPlaceholderText("YYYY-MM-DD")

        form_layout.addRow("Subscription ID:", self.id_input)
        form_layout.addRow("Member ID:", self.member_id_input)
        form_layout.addRow("Plan ID:", self.plan_id_input)
        form_layout.addRow("Start Date:", self.start_date_input)

        main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Create Subscription")
        self.delete_btn = QPushButton("Delete")
        self.view_btn = QPushButton("View All")
        self.clear_btn = QPushButton("Clear")

        self.add_btn.setStyleSheet("background:#27ae60; color:white; padding:8px;")
        self.delete_btn.setStyleSheet("background:#c0392b; color:white; padding:8px;")
        self.view_btn.setStyleSheet("background:#2980b9; color:white; padding:8px;")
        self.clear_btn.setStyleSheet("background:#7f8c8d; color:white; padding:8px;")

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.view_btn)
        button_layout.addWidget(self.clear_btn)

        main_layout.addLayout(button_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Member ID", "Plan ID", "Start Date", "End Date", "Status"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

        # Connections
        self.add_btn.clicked.connect(self.create_subscription)
        self.delete_btn.clicked.connect(self.delete_subscription)
        self.view_btn.clicked.connect(self.view_subscriptions)
        self.clear_btn.clicked.connect(self.clear_fields)
        self.table.cellClicked.connect(self.load_selected_row)

    # CREATE
    def create_subscription(self):
        conn = get_connection()
        cursor = conn.cursor()

        # Get plan duration
        cursor.execute("SELECT duration_months FROM plans WHERE plan_id=%s",
                       (self.plan_id_input.text(),))
        result = cursor.fetchone()

        if not result:
            QMessageBox.warning(self, "Error", "Invalid Plan ID")
            return

        duration = result[0]

        start_date = datetime.strptime(self.start_date_input.text(), "%Y-%m-%d")
        end_date = start_date + timedelta(days=30 * duration)

        today = datetime.today()
        status = "Active" if today <= end_date else "Expired"

        query = """
        INSERT INTO subscriptions (member_id, plan_id, start_date, end_date, status)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            self.member_id_input.text(),
            self.plan_id_input.text(),
            self.start_date_input.text(),
            end_date.strftime("%Y-%m-%d"),
            status
        )

        cursor.execute(query, values)
        conn.commit()

        QMessageBox.information(self, "Success", "Subscription Created")

        cursor.close()
        conn.close()

        self.view_subscriptions()
        self.clear_fields()

    # DELETE
    def delete_subscription(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM subscriptions WHERE subscription_id=%s",
                       (self.id_input.text(),))
        conn.commit()

        QMessageBox.information(self, "Deleted", "Subscription Deleted")

        cursor.close()
        conn.close()

        self.view_subscriptions()

    # VIEW
    def view_subscriptions(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM subscriptions")
        records = cursor.fetchall()

        self.table.setRowCount(len(records))

        for row_index, row_data in enumerate(records):
            for col_index, data in enumerate(row_data):
                self.table.setItem(row_index, col_index,
                                   QTableWidgetItem(str(data)))

        cursor.close()
        conn.close()

    # LOAD ROW
    def load_selected_row(self):
        row = self.table.currentRow()

        self.id_input.setText(self.table.item(row, 0).text())
        self.member_id_input.setText(self.table.item(row, 1).text())
        self.plan_id_input.setText(self.table.item(row, 2).text())
        self.start_date_input.setText(self.table.item(row, 3).text())

    # CLEAR
    def clear_fields(self):
        self.id_input.clear()
        self.member_id_input.clear()
        self.plan_id_input.clear()
        self.start_date_input.clear()
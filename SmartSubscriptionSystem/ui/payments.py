from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QDialog
)
from PySide6.QtCore import Qt
from database.db_connection import get_connection


class PaymentsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Payments Management")
        self.setGeometry(250, 120, 950, 650)

        main_layout = QVBoxLayout()

        # ===== TITLE =====
        title = QLabel("PAYMENTS MANAGEMENT")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
            color:#2c3e50;
            padding:10px;
        """)
        main_layout.addWidget(title)

        # ===== FORM =====
        form_layout = QFormLayout()

        self.subscription_id_input = QLineEdit()
        self.subscription_id_input.setPlaceholderText("Enter Subscription ID")

        self.amount_display = QLineEdit()
        self.amount_display.setReadOnly(True)

        self.payment_date_input = QLineEdit()
        self.payment_date_input.setPlaceholderText("YYYY-MM-DD")

        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["Cash", "Card", "UPI", "Online"])

        form_layout.addRow("Subscription ID:", self.subscription_id_input)
        form_layout.addRow("Amount (Auto):", self.amount_display)
        form_layout.addRow("Payment Date:", self.payment_date_input)
        form_layout.addRow("Payment Method:", self.payment_method_combo)

        main_layout.addLayout(form_layout)

        # ===== BUTTONS =====
        button_layout = QHBoxLayout()

        self.fetch_btn = QPushButton("Fetch Amount")
        self.add_btn = QPushButton("Record Payment")
        self.view_btn = QPushButton("View Payments")
        self.bill_btn = QPushButton("Generate Bill")
        self.clear_btn = QPushButton("Clear")

        self.fetch_btn.setStyleSheet("background:#2980b9;color:white;padding:8px;")
        self.add_btn.setStyleSheet("background:#27ae60;color:white;padding:8px;")
        self.view_btn.setStyleSheet("background:#8e44ad;color:white;padding:8px;")
        self.bill_btn.setStyleSheet("background:#e67e22;color:white;padding:8px;")
        self.clear_btn.setStyleSheet("background:#7f8c8d;color:white;padding:8px;")

        button_layout.addWidget(self.fetch_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.view_btn)
        button_layout.addWidget(self.bill_btn)
        button_layout.addWidget(self.clear_btn)

        main_layout.addLayout(button_layout)

        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Payment ID", "Subscription ID", "Amount", "Date", "Method"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        # ===== CONNECTIONS =====
        self.fetch_btn.clicked.connect(self.fetch_amount)
        self.add_btn.clicked.connect(self.record_payment)
        self.view_btn.clicked.connect(self.view_payments)
        self.bill_btn.clicked.connect(self.generate_bill)
        self.clear_btn.clicked.connect(self.clear_fields)

    # ===== FETCH AMOUNT =====
    def fetch_amount(self):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT p.price
        FROM subscriptions s
        JOIN plans p ON s.plan_id = p.plan_id
        WHERE s.subscription_id=%s
        """

        cursor.execute(query, (self.subscription_id_input.text(),))
        result = cursor.fetchone()

        if result:
            self.amount_display.setText(str(result[0]))
        else:
            QMessageBox.warning(self, "Error", "Invalid Subscription ID")

        conn.close()

    # ===== RECORD PAYMENT =====
    def record_payment(self):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO payments (subscription_id, amount, payment_date, payment_method)
        VALUES (%s, %s, %s, %s)
        """

        values = (
            self.subscription_id_input.text(),
            self.amount_display.text(),
            self.payment_date_input.text(),
            self.payment_method_combo.currentText()
        )

        cursor.execute(query, values)
        conn.commit()

        QMessageBox.information(self, "Success", "Payment Recorded Successfully")

        conn.close()

        self.view_payments()
        self.clear_fields()

    # ===== VIEW PAYMENTS =====
    def view_payments(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM payments")
        records = cursor.fetchall()

        self.table.setRowCount(len(records))

        for row_index, row_data in enumerate(records):
            for col_index, data in enumerate(row_data):
                self.table.setItem(row_index, col_index,
                                   QTableWidgetItem(str(data)))

        conn.close()

    # ===== GENERATE RECEIPT (FIXED) =====
    def generate_bill(self):
        row = self.table.currentRow()

        if row == -1:
            QMessageBox.warning(self, "Warning", "Select a payment first")
            return

        payment_id = self.table.item(row, 0).text()

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT m.name, m.email, m.phone,
               p.plan_name,
               pay.amount, pay.payment_method, pay.payment_date
        FROM payments pay
        LEFT JOIN subscriptions s ON pay.subscription_id = s.subscription_id
        LEFT JOIN members m ON s.member_id = m.member_id
        LEFT JOIN plans p ON s.plan_id = p.plan_id
        WHERE pay.payment_id = %s
        """

        cursor.execute(query, (payment_id,))
        data = cursor.fetchone()

        conn.close()

        if not data:
            QMessageBox.warning(self, "Error", "No data found")
            return

        name, email, phone, plan, amount, method, date = data

        receipt = f"""
------------------------------------------
        PAYMENT RECEIPT
------------------------------------------

Member Name : {name}
Email       : {email}
Phone       : {phone}

Plan Name   : {plan}

Amount Paid : ₹{amount}
Payment Mode: {method}
Payment Date: {date}

------------------------------------------
      THANK YOU FOR YOUR PAYMENT
------------------------------------------
"""

        dialog = QDialog(self)
        dialog.setWindowTitle("Payment Receipt")
        dialog.setGeometry(400, 200, 420, 450)

        layout = QVBoxLayout()

        label = QLabel(receipt)
        label.setAlignment(Qt.AlignLeft)

        # ✅ FIXED DARK THEME (VISIBLE TEXT)
        label.setStyleSheet("""
            font-size:15px;
            font-family:Courier;
            padding:20px;
            border:2px solid #ffffff;
            border-radius:10px;
            background:#1e1e1e;
            color:#ffffff;
        """)

        layout.addWidget(label)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background:#e74c3c;
                color:white;
                padding:10px;
                border-radius:8px;
                font-size:14px;
            }
            QPushButton:hover {
                background:#c0392b;
            }
        """)
        close_btn.clicked.connect(dialog.close)

        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def clear_fields(self):
        self.subscription_id_input.clear()
        self.amount_display.clear()
        self.payment_date_input.clear()
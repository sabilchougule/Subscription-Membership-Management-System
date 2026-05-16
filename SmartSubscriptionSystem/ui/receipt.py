from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from database.db_connection import get_connection


class ReceiptWindow(QWidget):
    def __init__(self, payment_id):
        super().__init__()

        self.setWindowTitle("Payment Receipt")
        self.setGeometry(400, 200, 420, 450)

        layout = QVBoxLayout()

        # ===== FETCH DATA =====
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

        # ===== IF NO DATA =====
        if not data:
            label = QLabel("No data found for this payment")
            label.setStyleSheet("color:white; font-size:16px;")
            layout.addWidget(label)

        else:
            name, email, phone, plan, amount, method, date = data

            receipt_text = f"""
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

            label = QLabel(receipt_text)
            label.setAlignment(Qt.AlignLeft)

            # ===== PERFECT DARK THEME STYLE =====
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

        # ===== CLOSE BUTTON =====
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
        close_btn.clicked.connect(self.close)

        layout.addWidget(close_btn)

        self.setLayout(layout)
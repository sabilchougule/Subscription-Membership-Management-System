from PySide6.QtWidgets import (
    QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QLabel, QGridLayout
)
from PySide6.QtCore import Qt
from database.db_connection import get_connection


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Subscription System - Dashboard")
        self.setGeometry(200, 80, 1100, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e3f2fd,
                    stop:1 #ffffff
                );
            }
        """)

        main_layout = QVBoxLayout()

        title = QLabel("Smart Subscription & Membership Management System")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:30px;
            font-weight:bold;
            color:#2c3e50;
            margin:20px;
        """)
        main_layout.addWidget(title)

        # ===== STATISTICS =====
        stats_layout = QGridLayout()
        stats_layout.setSpacing(25)

        card_style = """
            QLabel {
                background-color:white;
                font-size:20px;
                padding:30px;
                border-radius:18px;
                border:2px solid #dcdde1;
                font-weight:bold;
                color:#2c3e50;
            }
        """

        self.total_members_label = QLabel()
        self.total_plans_label = QLabel()
        self.total_subs_label = QLabel()
        self.total_revenue_label = QLabel()

        for label in [
            self.total_members_label,
            self.total_plans_label,
            self.total_subs_label,
            self.total_revenue_label
        ]:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(card_style)

        stats_layout.addWidget(self.total_members_label, 0, 0)
        stats_layout.addWidget(self.total_plans_label, 0, 1)
        stats_layout.addWidget(self.total_subs_label, 1, 0)
        stats_layout.addWidget(self.total_revenue_label, 1, 1)

        main_layout.addLayout(stats_layout)
        main_layout.addSpacing(40)

        # ===== MODULE BUTTONS =====
        button_layout = QGridLayout()
        button_layout.setSpacing(30)

        self.members_btn = QPushButton("👥 Manage Members")
        self.plans_btn = QPushButton("📦 Manage Plans")
        self.subscriptions_btn = QPushButton("📋 Manage Subscriptions")
        self.payments_btn = QPushButton("💳 Manage Payments")
        self.reports_btn = QPushButton("📊 Reports")
        self.logout_btn = QPushButton("🚪 Logout")

        button_style = """
            QPushButton {
                background-color:#3498db;
                color:white;
                font-size:18px;
                padding:25px;
                border-radius:18px;
            }
            QPushButton:hover {
                background-color:#2980b9;
            }
        """

        for btn in [
            self.members_btn,
            self.plans_btn,
            self.subscriptions_btn,
            self.payments_btn,
            self.reports_btn
        ]:
            btn.setStyleSheet(button_style)

        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color:#e74c3c;
                color:white;
                font-size:16px;
                padding:15px;
                border-radius:15px;
            }
            QPushButton:hover {
                background-color:#c0392b;
            }
        """)

        button_layout.addWidget(self.members_btn, 0, 0)
        button_layout.addWidget(self.plans_btn, 0, 1)
        button_layout.addWidget(self.subscriptions_btn, 1, 0)
        button_layout.addWidget(self.payments_btn, 1, 1)
        button_layout.addWidget(self.reports_btn, 2, 0, 1, 2)

        main_layout.addLayout(button_layout)
        main_layout.addSpacing(30)
        main_layout.addWidget(self.logout_btn, alignment=Qt.AlignCenter)

        central_widget.setLayout(main_layout)

        # ===== BUTTON CONNECTIONS =====
        self.members_btn.clicked.connect(self.open_members)
        self.plans_btn.clicked.connect(self.open_plans)
        self.subscriptions_btn.clicked.connect(self.open_subscriptions)
        self.payments_btn.clicked.connect(self.open_payments)
        self.reports_btn.clicked.connect(self.open_reports)
        self.logout_btn.clicked.connect(self.logout)

        self.load_statistics()

    def load_statistics(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM members")
        total_members = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM plans")
        total_plans = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM subscriptions")
        total_subs = cursor.fetchone()[0]

        cursor.execute("SELECT IFNULL(SUM(amount),0) FROM payments")
        total_revenue = cursor.fetchone()[0]

        self.total_members_label.setText(f"👥 Total Members\n{total_members}")
        self.total_plans_label.setText(f"📦 Total Plans\n{total_plans}")
        self.total_subs_label.setText(f"📋 Total Subscriptions\n{total_subs}")
        self.total_revenue_label.setText(f"💰 Total Revenue\n₹ {total_revenue}")

        cursor.close()
        conn.close()

    def open_members(self):
        from ui.members import MembersWindow
        self.members_window = MembersWindow()
        self.members_window.show()

    def open_plans(self):
        from ui.plans import PlansWindow
        self.plans_window = PlansWindow()
        self.plans_window.show()

    def open_subscriptions(self):
        from ui.subscriptions import SubscriptionsWindow
        self.sub_window = SubscriptionsWindow()
        self.sub_window.show()

    def open_payments(self):
        from ui.payments import PaymentsWindow
        self.payments_window = PaymentsWindow()
        self.payments_window.show()

    def open_reports(self):
        from ui.reports import ReportsWindow
        self.reports_window = ReportsWindow()
        self.reports_window.show()

    def logout(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
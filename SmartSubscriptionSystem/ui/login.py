from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QFrame
)
from PySide6.QtCore import Qt
from database.db_connection import get_connection
from PySide6.QtWidgets import QMessageBox


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login - Smart Subscription System")
        self.setGeometry(500, 200, 400, 400)

        # ===== Background Gradient =====
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2980b9,
                    stop:1 #6dd5fa
                );
            }
        """)

        main_layout = QVBoxLayout()

        # ===== Card Frame =====
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 20px;
            }
        """)

        card_layout = QVBoxLayout()

        title = QLabel("Admin Login")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px; font-weight:bold; color:#2c3e50;")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Login")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color:#3498db;
                color:white;
                padding:10px;
                border-radius:10px;
                font-size:16px;
            }
            QPushButton:hover {
                background-color:#2980b9;
            }
        """)

        self.login_btn.clicked.connect(self.authenticate)

        card_layout.addWidget(title)
        card_layout.addSpacing(15)
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.password)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_btn)

        card.setLayout(card_layout)

        main_layout.addStretch()
        main_layout.addWidget(card)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def authenticate(self):
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        cursor.execute(query, (self.username.text(), self.password.text()))
        result = cursor.fetchone()

        if result:
            self.open_dashboard()
        else:
            QMessageBox.warning(self, "Error", "Invalid Credentials")

        cursor.close()
        conn.close()

    def open_dashboard(self):
        from ui.dashboard import Dashboard
        self.dashboard = Dashboard()
        self.dashboard.show()
        self.close()
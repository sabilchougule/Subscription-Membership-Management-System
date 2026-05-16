from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt
from database.db_connection import get_connection


class MembersWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Manage Members")
        self.setGeometry(250, 150, 850, 600)

        main_layout = QVBoxLayout()

        # ===== Title =====
        title = QLabel("Members Management")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px; font-weight:bold; color:#2c3e50;")
        main_layout.addWidget(title)

        # ===== Form Layout =====
        form_layout = QFormLayout()

        self.id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.date_input = QLineEdit()

        self.id_input.setPlaceholderText("Enter Member ID for Update/Delete")
        self.name_input.setPlaceholderText("Enter Name")
        self.email_input.setPlaceholderText("Enter Email")
        self.phone_input.setPlaceholderText("Enter Phone")
        self.date_input.setPlaceholderText("YYYY-MM-DD")

        form_layout.addRow("Member ID:", self.id_input)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Join Date:", self.date_input)

        main_layout.addLayout(form_layout)

        # ===== Buttons =====
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add")
        self.update_btn = QPushButton("Update")
        self.delete_btn = QPushButton("Delete")
        self.search_btn = QPushButton("Search")
        self.view_btn = QPushButton("View All")
        self.clear_btn = QPushButton("Clear")

        # Button Styling
        self.add_btn.setStyleSheet("background-color:#27ae60; color:white; padding:8px;")
        self.update_btn.setStyleSheet("background-color:#2980b9; color:white; padding:8px;")
        self.delete_btn.setStyleSheet("background-color:#c0392b; color:white; padding:8px;")
        self.search_btn.setStyleSheet("background-color:#8e44ad; color:white; padding:8px;")
        self.view_btn.setStyleSheet("background-color:#f39c12; color:white; padding:8px;")
        self.clear_btn.setStyleSheet("background-color:#7f8c8d; color:white; padding:8px;")

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.search_btn)
        button_layout.addWidget(self.view_btn)
        button_layout.addWidget(self.clear_btn)

        main_layout.addLayout(button_layout)

        # ===== Table =====
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Email", "Phone", "Join Date"]
        )
        self.table.setStyleSheet("""
            QTableWidget {
                background-color:#ecf0f1;
                gridline-color:#bdc3c7;
                font-size:14px;
            }
            QHeaderView::section {
                background-color:#34495e;
                color:white;
                padding:5px;
            }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        # ===== Connections =====
        self.add_btn.clicked.connect(self.add_member)
        self.update_btn.clicked.connect(self.update_member)
        self.delete_btn.clicked.connect(self.delete_member)
        self.search_btn.clicked.connect(self.search_member)
        self.view_btn.clicked.connect(self.view_members)
        self.clear_btn.clicked.connect(self.clear_fields)
        self.table.cellClicked.connect(self.load_selected_row)

    # ================= ADD =================
    def add_member(self):
        if not self.name_input.text() or not self.date_input.text():
            QMessageBox.warning(self, "Error", "Name and Join Date are required!")
            return

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO members (name, email, phone, join_date)
        VALUES (%s, %s, %s, %s)
        """

        values = (
            self.name_input.text(),
            self.email_input.text(),
            self.phone_input.text(),
            self.date_input.text()
        )

        try:
            cursor.execute(query, values)
            conn.commit()
            QMessageBox.information(self, "Success", "Member Added Successfully")
            self.view_members()
            self.clear_fields()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

        cursor.close()
        conn.close()

    # ================= UPDATE =================
    def update_member(self):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE members
        SET name=%s, email=%s, phone=%s, join_date=%s
        WHERE member_id=%s
        """

        values = (
            self.name_input.text(),
            self.email_input.text(),
            self.phone_input.text(),
            self.date_input.text(),
            self.id_input.text()
        )

        cursor.execute(query, values)
        conn.commit()
        QMessageBox.information(self, "Success", "Member Updated Successfully")
        self.view_members()

        cursor.close()
        conn.close()

    # ================= DELETE =================
    def delete_member(self):
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this member?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.No:
            return

        conn = get_connection()
        cursor = conn.cursor()

        query = "DELETE FROM members WHERE member_id=%s"
        cursor.execute(query, (self.id_input.text(),))
        conn.commit()

        QMessageBox.information(self, "Success", "Member Deleted Successfully")
        self.view_members()
        self.clear_fields()

        cursor.close()
        conn.close()

    # ================= SEARCH =================
    def search_member(self):
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM members WHERE member_id=%s"
        cursor.execute(query, (self.id_input.text(),))
        record = cursor.fetchone()

        if record:
            self.id_input.setText(str(record[0]))
            self.name_input.setText(record[1])
            self.email_input.setText(record[2])
            self.phone_input.setText(record[3])
            self.date_input.setText(str(record[4]))
        else:
            QMessageBox.warning(self, "Error", "Member Not Found")

        cursor.close()
        conn.close()

    # ================= VIEW =================
    def view_members(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM members")
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

    # ================= LOAD ROW =================
    def load_selected_row(self):
        selected_row = self.table.currentRow()

        self.id_input.setText(self.table.item(selected_row, 0).text())
        self.name_input.setText(self.table.item(selected_row, 1).text())
        self.email_input.setText(self.table.item(selected_row, 2).text())
        self.phone_input.setText(self.table.item(selected_row, 3).text())
        self.date_input.setText(self.table.item(selected_row, 4).text())

    # ================= CLEAR =================
    def clear_fields(self):
        self.id_input.clear()
        self.name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.date_input.clear()
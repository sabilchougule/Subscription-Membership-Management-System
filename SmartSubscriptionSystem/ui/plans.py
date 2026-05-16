from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt
from database.db_connection import get_connection


class PlansWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Manage Plans")
        self.setGeometry(250, 150, 850, 600)

        main_layout = QVBoxLayout()

        # ===== Title =====
        title = QLabel("Plans Management")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px; font-weight:bold; color:#2c3e50;")
        main_layout.addWidget(title)

        # ===== Form Layout =====
        form_layout = QFormLayout()

        self.id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.duration_input = QLineEdit()
        self.price_input = QLineEdit()

        self.id_input.setPlaceholderText("Enter Plan ID for Update/Delete")
        self.name_input.setPlaceholderText("Plan Name")
        self.duration_input.setPlaceholderText("Duration in Months")
        self.price_input.setPlaceholderText("Price")

        form_layout.addRow("Plan ID:", self.id_input)
        form_layout.addRow("Plan Name:", self.name_input)
        form_layout.addRow("Duration (Months):", self.duration_input)
        form_layout.addRow("Price:", self.price_input)

        main_layout.addLayout(form_layout)

        # ===== Buttons =====
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add")
        self.update_btn = QPushButton("Update")
        self.delete_btn = QPushButton("Delete")
        self.search_btn = QPushButton("Search")
        self.view_btn = QPushButton("View All")
        self.clear_btn = QPushButton("Clear")

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
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Plan Name", "Duration", "Price"]
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
        self.add_btn.clicked.connect(self.add_plan)
        self.update_btn.clicked.connect(self.update_plan)
        self.delete_btn.clicked.connect(self.delete_plan)
        self.search_btn.clicked.connect(self.search_plan)
        self.view_btn.clicked.connect(self.view_plans)
        self.clear_btn.clicked.connect(self.clear_fields)
        self.table.cellClicked.connect(self.load_selected_row)

    # ================= ADD =================
    def add_plan(self):
        if not self.name_input.text() or not self.duration_input.text() or not self.price_input.text():
            QMessageBox.warning(self, "Error", "All fields are required!")
            return

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO plans (plan_name, duration_months, price)
        VALUES (%s, %s, %s)
        """

        values = (
            self.name_input.text(),
            self.duration_input.text(),
            self.price_input.text()
        )

        try:
            cursor.execute(query, values)
            conn.commit()
            QMessageBox.information(self, "Success", "Plan Added Successfully")
            self.view_plans()
            self.clear_fields()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

        cursor.close()
        conn.close()

    # ================= UPDATE =================
    def update_plan(self):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE plans
        SET plan_name=%s, duration_months=%s, price=%s
        WHERE plan_id=%s
        """

        values = (
            self.name_input.text(),
            self.duration_input.text(),
            self.price_input.text(),
            self.id_input.text()
        )

        cursor.execute(query, values)
        conn.commit()

        QMessageBox.information(self, "Success", "Plan Updated Successfully")
        self.view_plans()

        cursor.close()
        conn.close()

    # ================= DELETE =================
    def delete_plan(self):
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this plan?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.No:
            return

        conn = get_connection()
        cursor = conn.cursor()

        query = "DELETE FROM plans WHERE plan_id=%s"
        cursor.execute(query, (self.id_input.text(),))
        conn.commit()

        QMessageBox.information(self, "Success", "Plan Deleted Successfully")
        self.view_plans()
        self.clear_fields()

        cursor.close()
        conn.close()

    # ================= SEARCH =================
    def search_plan(self):
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM plans WHERE plan_id=%s"
        cursor.execute(query, (self.id_input.text(),))
        record = cursor.fetchone()

        if record:
            self.id_input.setText(str(record[0]))
            self.name_input.setText(record[1])
            self.duration_input.setText(str(record[2]))
            self.price_input.setText(str(record[3]))
        else:
            QMessageBox.warning(self, "Error", "Plan Not Found")

        cursor.close()
        conn.close()

    # ================= VIEW =================
    def view_plans(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM plans")
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
        self.duration_input.setText(self.table.item(selected_row, 2).text())
        self.price_input.setText(self.table.item(selected_row, 3).text())

    # ================= CLEAR =================
    def clear_fields(self):
        self.id_input.clear()
        self.name_input.clear()
        self.duration_input.clear()
        self.price_input.clear()
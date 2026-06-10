"""
Local Database Browser for Desktop App
متصفح قواعد البيانات المحلية
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QComboBox
)
from PySide6.QtCore import Qt
from database.db_manager import get_db_manager
from sqlalchemy.orm import Session

class DatabaseBrowser(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = get_db_manager()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("عرض البيانات المحلية:"))
        
        self.table_selector = QComboBox()
        self.table_selector.addItems(["البيانات المالية", "الملاحظات", "المخاطر", "القيود"])
        header.addWidget(self.table_selector)
        
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.clicked.connect(self.load_data)
        header.addWidget(refresh_btn)
        
        layout.addLayout(header)
        
        # Table
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        self.load_data()
        
    def load_data(self):
        # In a real app, this would query SQLAlchemy models
        # For now, we show a professional placeholder with real logic structure
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["المعرف", "النوع", "القيمة", "التاريخ"])
        self.table.setRowCount(5)
        
        data = [
            ("1", "إيرادات", "15,000,000", "2024-01-01"),
            ("2", "مصروفات", "9,000,000", "2024-01-02"),
            ("3", "أصول", "45,000,000", "2024-01-03"),
            ("4", "خصوم", "18,000,000", "2024-01-04"),
            ("5", "حقوق ملكية", "27,000,000", "2024-01-05")
        ]
        
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(val))
        
        self.table.resizeColumnsToContents()

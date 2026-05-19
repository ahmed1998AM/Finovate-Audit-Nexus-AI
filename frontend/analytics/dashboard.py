"""
Finovate Audit Nexus AI - Analytics Dashboard Widget
Enterprise AI Financial Audit & Intelligence Platform
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame
from PySide6.QtCore import Qt
import sys

class AnalyticsDashboard(QWidget):
    """Main Analytics Dashboard for Financial Intelligence"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analytics Dashboard")
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the dashboard UI"""
        main_layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Financial Analytics Dashboard")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E86AB;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # KPI Grid
        grid = QGridLayout()
        
        # Sample KPI Cards
        kpis = [
            ("Total Revenue", "$1,234,567", "+12.5%"),
            ("Net Profit", "$456,789", "+8.3%"),
            ("Risk Score", "Medium", "-2.1%"),
            ("Fraud Alerts", "3", "0%"),
            ("Compliance Rate", "98.5%", "+1.2%"),
            ("Audit Progress", "75%", "+15%"),
        ]
        
        for i, (title, value, change) in enumerate(kpis):
            card = self.create_kpi_card(title, value, change)
            row = i // 3
            col = i % 3
            grid.addWidget(card, row, col)
        
        main_layout.addLayout(grid)
    
    def create_kpi_card(self, title, value, change):
        """Create a KPI information card"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        card.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2E86AB;")
        layout.addWidget(value_label)
        
        change_label = QLabel(change)
        change_color = "#28A745" if change.startswith('+') else "#DC3545"
        change_label.setStyleSheet(f"font-size: 14px; color: {change_color};")
        layout.addWidget(change_label)
        
        return card


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dashboard = AnalyticsDashboard()
    dashboard.show()
    sys.exit(app.exec())

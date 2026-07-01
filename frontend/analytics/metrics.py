"""
Finovate Audit Nexus AI - KPI Metrics Widget
Enterprise AI Financial Audit & Intelligence Platform
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame, QProgressBar
from PySide6.QtCore import Qt
from frontend.api_client import get_client

class KPIMetricsWidget(QWidget):
    """Widget for displaying Key Performance Indicators"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()
    
    def load_data(self):
        try:
            report = get_client().get_summary_report()
            fh = report.get("financial_highlights", {})
            rev = fh.get("total_revenue", 0)
            profit = fh.get("net_profit", 0)
            assets = fh.get("total_assets", 0)
            equity = fh.get("equity", 1)
            roi = round(profit / max(assets, 1) * 100, 1) if assets else 0
            kpis = [
                ("Total Revenue", rev, max(rev * 1.1, 1)),
                ("Net Profit", profit, max(profit * 1.15, 1)),
                ("Total Assets", assets, max(assets * 1.05, 1)),
                ("Equity", equity, max(equity * 1.1, 1)),
                ("ROI", roi, 20.0),
                ("Debt to Equity", round((assets - equity) / max(equity, 1), 2), 1.0),
            ]
        except Exception:
            kpis = [
                ("Total Revenue", 0, 1),
                ("Net Profit", 0, 1),
                ("Total Assets", 0, 1),
                ("Equity", 0, 1),
                ("ROI", 0, 20.0),
                ("Debt to Equity", 0, 1.0),
            ]
        for i, (name, value, target) in enumerate(kpis):
            widget = self.create_kpi_widget(name, value, target)
            row = i // 2
            col = i % 2
            self.grid.addWidget(widget, row, col)
    
    def setup_ui(self):
        """Initialize the KPI metrics UI"""
        layout = QVBoxLayout(self)
        
        header = QLabel("Key Performance Indicators")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E86AB;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # KPI Grid
        self.grid = QGridLayout()
        layout.addLayout(self.grid)
    
    def create_kpi_widget(self, name, value, target):
        """Create individual KPI widget with progress bar"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 8px;
                padding: 10px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Name
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 12px; color: #666; font-weight: bold;")
        layout.addWidget(name_label)
        
        # Value
        value_label = QLabel(f"{value:.2f}")
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E86AB;")
        layout.addWidget(value_label)
        
        # Target
        target_label = QLabel(f"Target: {target:.2f}")
        target_label.setStyleSheet("font-size: 10px; color: #999;")
        layout.addWidget(target_label)
        
        # Progress Bar
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setValue(int((value / target) * 100) if target > 0 else 0)
        progress.setStyleSheet("""
            QProgressBar {
                border-radius: 5px;
                background-color: #E0E0E0;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2E86AB;
                border-radius: 5px;
            }
        """)
        layout.addWidget(progress)
        
        return frame

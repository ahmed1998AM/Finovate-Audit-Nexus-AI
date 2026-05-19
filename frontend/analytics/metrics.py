"""
Finovate Audit Nexus AI - KPI Metrics Widget
Enterprise AI Financial Audit & Intelligence Platform
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame, QProgressBar
from PySide6.QtCore import Qt

class KPIMetricsWidget(QWidget):
    """Widget for displaying Key Performance Indicators"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the KPI metrics UI"""
        layout = QVBoxLayout(self)
        
        header = QLabel("Key Performance Indicators")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E86AB;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # KPI Grid
        grid = QGridLayout()
        
        kpis = [
            ("Liquidity Ratio", 1.85, 2.0),
            ("Debt to Equity", 0.45, 1.0),
            ("ROI", 15.5, 20.0),
            ("Gross Margin", 42.3, 50.0),
            ("Operating Margin", 18.7, 25.0),
            ("Current Ratio", 2.1, 2.5),
        ]
        
        for i, (name, value, target) in enumerate(kpis):
            widget = self.create_kpi_widget(name, value, target)
            row = i // 2
            col = i % 2
            grid.addWidget(widget, row, col)
        
        layout.addLayout(grid)
    
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

"""
Finovate Audit Nexus AI - AI Models Manager Component
مكون إدارة نماذج الذكاء الاصطناعي

Provides interface for managing AI models.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QScrollArea,
    QComboBox, QLineEdit, QProgressBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class AIModelsManager(QWidget):
    """AI Models Manager Component"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إدارة نماذج الذكاء الاصطناعي")
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Models Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        models_widget = self.create_models_grid()
        scroll.setWidget(models_widget)
        main_layout.addWidget(scroll)
        
    def create_header(self) -> QWidget:
        """Create header"""
        header = QWidget()
        layout = QHBoxLayout(header)
        
        title = QLabel("🧠 إدارة نماذج الذكاء الاصطناعي")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        layout.addWidget(title)
        layout.addStretch()
        
        return header
    
    def create_models_grid(self) -> QWidget:
        """Create models grid"""
        grid_widget = QWidget()
        layout = QGridLayout(grid_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 10, 0, 10)
        
        models = [
            ("GPT-4", "OpenAI", "98%", "#27ae60"),
            ("Claude-3", "Anthropic", "97%", "#27ae60"),
            ("Llama-3", "Meta", "95%", "#27ae60"),
            ("Gemini Pro", "Google", "96%", "#27ae60"),
        ]
        
        row = 0
        col = 0
        
        for name, provider, accuracy, color in models:
            card = self.create_model_card(name, provider, accuracy, color)
            layout.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        return grid_widget
    
    def create_model_card(self, name: str, provider: str, accuracy: str, color: str) -> QFrame:
        """Create model card"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 4px solid {color};
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        name_label = QLabel(f"🤖 {name}")
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        provider_label = QLabel(f"المزود: {provider}")
        provider_label.setFont(QFont("Arial", 10))
        provider_label.setStyleSheet("color: #7f8c8d;")
        
        accuracy_label = QLabel(f"الدقة: {accuracy}")
        accuracy_label.setFont(QFont("Arial", 11, QFont.Bold))
        accuracy_label.setStyleSheet(f"color: {color};")
        
        progress = QProgressBar()
        progress.setValue(int(accuracy.replace('%', '')))
        progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        
        layout.addWidget(name_label)
        layout.addWidget(provider_label)
        layout.addWidget(accuracy_label)
        layout.addWidget(progress)
        
        return card
    
    def setup_styles(self):
        """Apply styles"""
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
            }
        """)

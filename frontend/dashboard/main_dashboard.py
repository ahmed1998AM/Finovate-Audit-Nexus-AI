"""
Finovate Audit Nexus AI - Main Dashboard Widget
لوحة التحكم الرئيسية للتطبيق
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class MainDashboard(QWidget):
    """لوحة التحكم الرئيسية"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainDashboard")
        self._setup_ui()
        
    def _setup_ui(self):
        """إعداد الواجهة"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # العنوان الرئيسي
        title_label = QLabel("📊 لوحة التحكم الرئيسية")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        main_layout.addWidget(title_label)
        
        # منطقة المحتوى
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        content_layout = QGridLayout(content_widget)
        content_layout.setSpacing(20)
        
        # بطاقات الإحصائيات
        self._create_stat_cards(content_layout)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
    def _create_stat_cards(self, layout):
        """إنشاء بطاقات الإحصائيات"""
        cards = [
            ("🏢 الشركات", "15", "شركة نشطة"),
            ("🤖 الوكلاء الذكية", "22", "وكيل جاهز"),
            ("📁 مشاريع المراجعة", "8", "مشروع قيد التنفيذ"),
            ("⚠️ المخاطر المكتشفة", "3", "تتطلب مراجعة"),
            ("✅ المهام المكتملة", "156", "هذا الشهر"),
            ("📈 نسبة الدقة", "98.5%", "في التحليل"),
        ]
        
        positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
        
        for i, (title, value, subtitle) in enumerate(cards):
            card = self._create_stat_card(title, value, subtitle)
            row, col = positions[i]
            layout.addWidget(card, row, col)
    
    def _create_stat_card(self, title, value, subtitle):
        """إنشاء بطاقة إحصائية واحدة"""
        card = QFrame()
        card.setObjectName("StatCard")
        card.setStyleSheet("""
            QFrame#StatCard {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #e0e0e0;
            }
            QFrame#StatCard:hover {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        title_label.setStyleSheet("color: #7f8c8d;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 28, QFont.Bold))
        value_label.setStyleSheet("color: #2c3e50;")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #95a5a6;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)
        layout.addStretch()
        
        return card

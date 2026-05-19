"""
Finovate Audit Nexus AI - Analytics Dashboard Component
مكون لوحة التحليلات الرئيسية

Provides comprehensive financial analytics dashboard with interactive charts and metrics.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QScrollArea, QFrame, QSpacerItem,
    QSizePolicy, QPushButton, QComboBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor, QPainter, QPixmap


class AnalyticsDashboard(QWidget):
    """
    Main Analytics Dashboard Component
    Provides comprehensive financial analytics visualization
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("لوحة التحليلات المالية")
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Initialize the dashboard UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Section
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Filters Section
        filters = self.create_filters()
        main_layout.addWidget(filters)
        
        # KPI Cards Section
        kpi_section = self.create_kpi_section()
        main_layout.addWidget(kpi_section)
        
        # Charts Section
        charts_section = self.create_charts_section()
        main_layout.addWidget(charts_section)
        
        # Recent Activity Section
        activity_section = self.create_activity_section()
        main_layout.addWidget(activity_section)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(main_layout)
        
        main_container = QVBoxLayout(self)
        main_container.addWidget(scroll)
        
    def create_header(self) -> QWidget:
        """Create dashboard header"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 10)
        
        title = QLabel("📊 لوحة التحليلات المالية الشاملة")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(refresh_btn)
        
        return header
    
    def create_filters(self) -> QWidget:
        """Create filter controls"""
        filters = QWidget()
        layout = QHBoxLayout(filters)
        layout.setContentsMargins(0, 0, 0, 10)
        
        # Period Filter
        period_label = QLabel("الفترة:")
        period_combo = QComboBox()
        period_combo.addItems(["آخر 7 أيام", "آخر 30 يوم", "آخر 3 أشهر", "آخر سنة", "مخصص"])
        
        # Date Range
        from_label = QLabel("من:")
        from_date = QDateEdit(QDate.currentDate().addMonths(-1))
        from_date.setCalendarPopup(True)
        
        to_label = QLabel("إلى:")
        to_date = QDateEdit(QDate.currentDate())
        to_date.setCalendarPopup(True)
        
        # Apply Button
        apply_btn = QPushButton("تطبيق الفلتر")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        layout.addWidget(period_label)
        layout.addWidget(period_combo)
        layout.addWidget(from_label)
        layout.addWidget(from_date)
        layout.addWidget(to_label)
        layout.addWidget(to_date)
        layout.addWidget(apply_btn)
        layout.addStretch()
        
        return filters
    
    def create_kpi_section(self) -> QWidget:
        """Create KPI cards section"""
        kpi_widget = QWidget()
        layout = QGridLayout(kpi_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 10, 0, 20)
        
        kpis = [
            ("💰 إجمالي الإيرادات", "2,450,000 ر.س", "+12.5%", "#27ae60"),
            ("📉 المصروفات", "1,680,000 ر.س", "-3.2%", "#e74c3c"),
            ("📊 صافي الربح", "770,000 ر.س", "+18.7%", "#3498db"),
            ("⚠️ المخاطر المكتشفة", "23", "-5", "#f39c12"),
        ]
        
        for i, (title, value, change, color) in enumerate(kpis):
            card = self.create_kpi_card(title, value, change, color)
            row = i // 2
            col = i % 2
            layout.addWidget(card, row, col)
        
        return kpi_widget
    
    def create_kpi_card(self, title: str, value: str, change: str, color: str) -> QFrame:
        """Create individual KPI card"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 4px solid {color};
                padding: 15px;
            }}
            QFrame:hover {{
                background-color: #f8f9fa;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11))
        title_label.setStyleSheet("color: #7f8c8d;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        
        change_label = QLabel(change)
        is_positive = change.startswith('+') or change.startswith('-')
        change_color = "#27ae60" if '+' in change else "#e74c3c" if '-' in change else "#95a5a6"
        change_label.setFont(QFont("Arial", 10, QFont.Bold))
        change_label.setStyleSheet(f"color: {change_color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(change_label)
        
        return card
    
    def create_charts_section(self) -> QWidget:
        """Create charts section placeholder"""
        charts_widget = QWidget()
        layout = QGridLayout(charts_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 10, 0, 20)
        
        # Revenue Trend Chart Placeholder
        revenue_chart = self.create_chart_placeholder(
            "📈 اتجاه الإيرادات",
            "رسم بياني لاتجاه الإيرادات خلال الفترة المحددة"
        )
        
        # Expense Breakdown Chart Placeholder
        expense_chart = self.create_chart_placeholder(
            "📊 توزيع المصروفات",
            "رسم دائري يوضح توزيع المصروفات حسب الفئة"
        )
        
        # Risk Heatmap Placeholder
        risk_chart = self.create_chart_placeholder(
            "🔥 خريطة الحرارة للمخاطر",
            "تصور بصري لمستويات المخاطر عبر الأقسام"
        )
        
        # Performance Metrics Placeholder
        performance_chart = self.create_chart_placeholder(
            "⚡ مؤشرات الأداء",
            "مقاييس الأداء الرئيسية والاتجاهات"
        )
        
        layout.addWidget(revenue_chart, 0, 0)
        layout.addWidget(expense_chart, 0, 1)
        layout.addWidget(risk_chart, 1, 0)
        layout.addWidget(performance_chart, 1, 1)
        
        return charts_widget
    
    def create_chart_placeholder(self, title: str, description: str) -> QFrame:
        """Create chart placeholder widget"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 20px;
                min-height: 250px;
            }
            QFrame:hover {
                border-color: #3498db;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        title_label.setAlignment(Qt.AlignCenter)
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #95a5a6;")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        
        # Placeholder icon
        icon_label = QLabel("📊")
        icon_label.setFont(QFont("Arial", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        
        return frame
    
    def create_activity_section(self) -> QWidget:
        """Create recent activity section"""
        activity_widget = QWidget()
        layout = QVBoxLayout(activity_widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        title = QLabel("🕐 النشاط الأخير")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px 0;")
        
        activity_list = QFrame()
        activity_list.setFrameStyle(QFrame.StyledPanel)
        activity_list.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """)
        
        list_layout = QVBoxLayout(activity_list)
        list_layout.setSpacing(10)
        
        activities = [
            ("✅ تم إكمال تحليل القوائم المالية", "منذ 5 دقائق", "#27ae60"),
            ("⚠️ تم اكتشاف شذوذ في المعاملات", "منذ 15 دقيقة", "#f39c12"),
            ("📄 تم إنشاء تقرير التدقيق الشهري", "منذ ساعة", "#3498db"),
            ("🔍 أكمل وكيل المخاطر تقييمه", "منذ ساعتين", "#9b59b6"),
        ]
        
        for activity_text, time, color in activities:
            item = QWidget()
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(10, 10, 10, 10)
            
            indicator = QLabel("●")
            indicator.setStyleSheet(f"color: {color}; font-size: 16px;")
            
            text = QLabel(activity_text)
            text.setFont(QFont("Arial", 10))
            
            timestamp = QLabel(time)
            timestamp.setFont(QFont("Arial", 9))
            timestamp.setStyleSheet("color: #95a5a6;")
            
            item_layout.addWidget(indicator)
            item_layout.addWidget(text)
            item_layout.addStretch()
            item_layout.addWidget(timestamp)
            
            list_layout.addWidget(item)
        
        layout.addWidget(title)
        layout.addWidget(activity_list)
        
        return activity_widget
    
    def setup_styles(self):
        """Apply global styles"""
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QDateEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
        """)
    
    def update_data(self, data: dict):
        """Update dashboard with new data"""
        # TODO: Implement data update logic
        print("Updating dashboard with new data...")
        pass
    
    def export_report(self):
        """Export dashboard report"""
        # TODO: Implement export functionality
        print("Exporting dashboard report...")
        pass

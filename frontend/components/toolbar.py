"""
Finovate Audit Nexus AI - Top Toolbar Component
شريط الأدوات العلوي للتطبيق
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QSpacerItem, QSizePolicy, QLineEdit,
    QComboBox, QToolButton
)
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QFont, QIcon


class TopToolbar(QWidget):
    """شريط الأدوات العلوي يحتوي على أدوات الإجراءات السريعة والبحث"""
    
    # إشارات
    quick_action_requested = Signal(str)
    search_requested = Signal(str)
    filter_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TopToolbar")
        self.setFixedHeight(70)
        self._setup_ui()
        
    def _setup_ui(self):
        """إعداد الواجهة"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(15)
        
        # مجموعة الأزرار السريعة
        self._create_quick_actions(main_layout)
        
        # فاصل مرن
        main_layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        
        # حقل البحث
        self._create_search_box(main_layout)
        
        # قائمة الفلترة
        self._create_filter_combo(main_layout)
        
        # زر الإشعارات
        self._create_notification_button(main_layout)
        
    def _create_quick_actions(self, layout):
        """إنشاء أزرار الإجراءات السريعة"""
        # زر مراجعة جديدة
        self.btn_new_audit = QToolButton()
        self.btn_new_audit.setText("📊 مراجعة جديدة")
        self.btn_new_audit.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btn_new_audit.clicked.connect(lambda: self.quick_action_requested.emit("new_audit"))
        self.btn_new_audit.setStyleSheet(self._get_button_style("#2196F3"))
        layout.addWidget(self.btn_new_audit)
        
        # زر استيراد ملف
        self.btn_import = QToolButton()
        self.btn_import.setText("📁 استيراد")
        self.btn_import.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btn_import.clicked.connect(lambda: self.quick_action_requested.emit("import_file"))
        self.btn_import.setStyleSheet(self._get_button_style("#4CAF50"))
        layout.addWidget(self.btn_import)
        
        # زر تشغيل الوكلاء
        self.btn_run_agents = QToolButton()
        self.btn_run_agents.setText("🤖 تشغيل الوكلاء")
        self.btn_run_agents.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btn_run_agents.clicked.connect(lambda: self.quick_action_requested.emit("run_agents"))
        self.btn_run_agents.setStyleSheet(self._get_button_style("#FF9800"))
        layout.addWidget(self.btn_run_agents)
        
    def _create_search_box(self, layout):
        """إنشاء صندوق البحث"""
        search_container = QFrame()
        search_container.setObjectName("SearchContainer")
        search_container.setStyleSheet("""
            #SearchContainer {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 5px;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 5, 10, 5)
        search_layout.setSpacing(10)
        
        # أيقونة البحث
        search_icon = QLabel("🔍")
        search_icon.setFont(QFont("Arial", 14))
        search_layout.addWidget(search_icon)
        
        # حقل البحث
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث...")
        self.search_input.setMinimumWidth(250)
        self.search_input.returnPressed.connect(self._on_search)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        search_layout.addWidget(self.search_input)
        
        layout.addWidget(search_container)
        
    def _create_filter_combo(self, layout):
        """إنشاء قائمة الفلترة"""
        filter_label = QLabel("تصفية:")
        filter_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("الكل", "all")
        self.filter_combo.addItem("مراجعات نشطة", "active_audits")
        self.filter_combo.addItem("مخاطر عالية", "high_risks")
        self.filter_combo.addItem("وكلاء نشطين", "active_agents")
        self.filter_combo.addItem("تقارير حديثة", "recent_reports")
        self.filter_combo.setMinimumWidth(150)
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 5px 10px;
                color: white;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                border: 1px solid rgba(255, 255, 255, 0.2);
                selection-background-color: #2196F3;
                color: white;
            }
        """)
        layout.addWidget(self.filter_combo)
        
    def _create_notification_button(self, layout):
        """إنشاء زر الإشعارات"""
        self.btn_notifications = QToolButton()
        self.btn_notifications.setText("🔔")
        self.btn_notifications.setFixedSize(40, 40)
        self.btn_notifications.clicked.connect(self._show_notifications)
        self.btn_notifications.setStyleSheet("""
            QToolButton {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                font-size: 18px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        layout.addWidget(self.btn_notifications)
        
    def _get_button_style(self, color):
        """الحصول على نمط الزر"""
        return f"""
            QToolButton {{
                background-color: {color};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
                font-size: 13px;
            }}
            QToolButton:hover {{
                background-color: {color}DD;
            }}
            QToolButton:pressed {{
                background-color: {color}BB;
            }}
        """
        
    @Slot()
    def _on_search(self):
        """عند تنفيذ البحث"""
        query = self.search_input.text().strip()
        if query:
            self.search_requested.emit(query)
            
    @Slot(int)
    def _on_filter_changed(self, index):
        """عند تغيير الفلتر"""
        filter_value = self.filter_combo.itemData(index)
        if filter_value:
            self.filter_changed.emit(filter_value)
            
    @Slot()
    def _show_notifications(self):
        """عرض الإشعارات"""
        # سيتم تنفيذ هذا لاحقاً
        print("عرض الإشعارات")
        
    def set_search_text(self, text):
        """تعيين نص البحث"""
        self.search_input.setText(text)
        
    def clear_search(self):
        """مسح البحث"""
        self.search_input.clear()
        
    def set_filter(self, filter_type):
        """تعيين الفلتر"""
        for i in range(self.filter_combo.count()):
            if self.filter_combo.itemData(i) == filter_type:
                self.filter_combo.setCurrentIndex(i)
                break

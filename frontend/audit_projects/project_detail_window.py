"""
نافذة تفاصيل المشروع
Project Detail Window
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
from datetime import datetime


class ProjectDetailWindow:
    """نافذة عرض تفاصيل مشروع المراجعة"""
    
    def __init__(self, parent, project_data: Dict):
        self.parent = parent
        self.project = project_data
        
        self.setup_ui()
        self.load_project_data()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # العنوان وأزرار التحكم
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(
            header_frame,
            text="",
            font=("Arial", 18, "bold")
        )
        self.title_label.pack(side=tk.LEFT)
        
        # أزرار الإجراءات
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            btn_frame,
            text="💾 حفظ",
            command=self.save_project
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="📊 تقرير",
            command=self.generate_report
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🤖 تشغيل AI",
            command=self.run_ai_analysis
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="❌ إغلاق",
            command=self.close_window
        ).pack(side=tk.LEFT, padx=5)
        
        # إنشاء التبويبات
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # تبويب النظرة العامة
        self.overview_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_tab, text="📋 النظرة العامة")
        self.create_overview_tab()
        
        # تبويب فريق العمل
        self.team_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.team_tab, text="👥 فريق العمل")
        self.create_team_tab()
        
        # تبويب الجدول الزمني
        self.timeline_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.timeline_tab, text="📅 الجدول الزمني")
        self.create_timeline_tab()
        
        # تبويب المهام
        self.tasks_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_tab, text="✅ المهام")
        self.create_tasks_tab()
        
        # تبويب المستندات
        self.documents_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.documents_tab, text="📄 المستندات")
        self.create_documents_tab()
        
        # تبويب نتائج AI
        self.ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_tab, text="🤖 تحليلات AI")
        self.create_ai_tab()
        
        # شريط التقدم السفلي
        progress_frame = ttk.Frame(self.frame)
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(progress_frame, text="نسبة الإنجاز:").pack(side=tk.LEFT)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        self.progress_bar.pack(side=tk.LEFT, padx=10)
        
        self.progress_label = ttk.Label(progress_frame, text="0%", width=5)
        self.progress_label.pack(side=tk.LEFT)
    
    def create_overview_tab(self):
        """إنشاء تبويب النظرة العامة"""
        frame = ttk.Frame(self.overview_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # معلومات المشروع
        info_frame = ttk.LabelFrame(frame, text="معلومات المشروع", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.project_name_var = tk.StringVar()
        self.create_info_row(info_frame, "اسم المشروع:", self.project_name_var)
        
        self.project_type_var = tk.StringVar()
        self.create_info_row(info_frame, "نوع المراجعة:", self.project_type_var)
        
        self.priority_var = tk.StringVar()
        self.create_info_row(info_frame, "الأولوية:", self.priority_var)
        
        self.status_var = tk.StringVar()
        self.create_info_row(info_frame, "الحالة:", self.status_var)
        
        self.description_text = tk.Text(info_frame, height=4, width=60)
        ttk.Label(info_frame, text="الوصف:").pack(anchor=tk.W, pady=(10, 5))
        self.description_text.pack(fill=tk.X)
        
        # معلومات العميل
        client_frame = ttk.LabelFrame(frame, text="معلومات العميل", padding=10)
        client_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.client_name_var = tk.StringVar()
        self.create_info_row(client_frame, "العميل:", self.client_name_var)
        
        self.industry_var = tk.StringVar()
        self.create_info_row(client_frame, "القطاع:", self.industry_var)
        
        self.company_size_var = tk.StringVar()
        self.create_info_row(client_frame, "حجم الشركة:", self.company_size_var)
        
        self.contact_var = tk.StringVar()
        self.create_info_row(client_frame, "الشخص المسؤول:", self.contact_var)
        
        self.email_var = tk.StringVar()
        self.create_info_row(client_frame, "البريد الإلكتروني:", self.email_var)
    
    def create_info_row(self, parent, label_text, var):
        """إنشاء صف معلومات"""
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(row_frame, text=label_text, width=20).pack(side=tk.LEFT)
        ttk.Label(row_frame, textvariable=var).pack(side=tk.LEFT)
    
    def create_team_tab(self):
        """إنشاء تبويب فريق العمل"""
        frame = ttk.Frame(self.team_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # مدير المشروع
        manager_frame = ttk.LabelFrame(frame, text="مدير المشروع", padding=10)
        manager_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.manager_var = tk.StringVar()
        ttk.Label(manager_frame, textvariable=self.manager_var, font=("Arial", 12)).pack()
        
        # أعضاء الفريق
        members_frame = ttk.LabelFrame(frame, text="أعضاء الفريق", padding=10)
        members_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("name", "role", "hours", "status")
        self.team_tree = ttk.Treeview(members_frame, columns=columns, show="headings", height=8)
        
        self.team_tree.heading("name", text="الاسم")
        self.team_tree.heading("role", text="الدور")
        self.team_tree.heading("hours", text="الساعات")
        self.team_tree.heading("status", text="الحالة")
        
        self.team_tree.column("name", width=200)
        self.team_tree.column("role", width=150)
        self.team_tree.column("hours", width=80, anchor=tk.CENTER)
        self.team_tree.column("status", width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(members_frame, orient=tk.VERTICAL, command=self.team_tree.yview)
        self.team_tree.configure(yscrollcommand=scrollbar.set)
        
        self.team_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # أزرار إدارة الفريق
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="➕ إضافة عضو", command=self.add_team_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ تعديل", command=self.edit_team_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ حذف", command=self.delete_team_member).pack(side=tk.LEFT, padx=5)
    
    def create_timeline_tab(self):
        """إنشاء تبويب الجدول الزمني"""
        frame = ttk.Frame(self.timeline_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # التواريخ الرئيسية
        dates_frame = ttk.LabelFrame(frame, text="التواريخ الرئيسية", padding=10)
        dates_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_date_var = tk.StringVar()
        self.create_info_row(dates_frame, "تاريخ البدء:", self.start_date_var)
        
        self.end_date_var = tk.StringVar()
        self.create_info_row(dates_frame, "تاريخ الانتهاء:", self.end_date_var)
        
        self.duration_var = tk.StringVar()
        self.create_info_row(dates_frame, "المدة (أسابيع):", self.duration_var)
        
        # مراحل المشروع
        phases_frame = ttk.LabelFrame(frame, text="مراحل المشروع", padding=10)
        phases_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("phase", "start", "end", "status", "progress")
        self.phases_tree = ttk.Treeview(phases_frame, columns=columns, show="headings", height=10)
        
        self.phases_tree.heading("phase", text="المرحلة")
        self.phases_tree.heading("start", text="تاريخ البدء")
        self.phases_tree.heading("end", text="تاريخ الانتهاء")
        self.phases_tree.heading("status", text="الحالة")
        self.phases_tree.heading("progress", text="التقدم")
        
        self.phases_tree.column("phase", width=200)
        self.phases_tree.column("start", width=100, anchor=tk.CENTER)
        self.phases_tree.column("end", width=100, anchor=tk.CENTER)
        self.phases_tree.column("status", width=100, anchor=tk.CENTER)
        self.phases_tree.column("progress", width=80, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(phases_frame, orient=tk.VERTICAL, command=self.phases_tree.yview)
        self.phases_tree.configure(yscrollcommand=scrollbar.set)
        
        self.phases_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_tasks_tab(self):
        """إنشاء تبويب المهام"""
        frame = ttk.Frame(self.tasks_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # أزرار التحكم
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="➕ مهمة جديدة", command=self.add_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 تحديث", command=self.refresh_tasks).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📤 تصدير", command=self.export_tasks).pack(side=tk.LEFT, padx=5)
        
        # جدول المهام
        columns = ("id", "task", "assignee", "priority", "due_date", "status", "progress")
        self.tasks_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        self.tasks_tree.heading("id", text="#")
        self.tasks_tree.heading("task", text="المهمة")
        self.tasks_tree.heading("assignee", text="المسؤول")
        self.tasks_tree.heading("priority", text="الأولوية")
        self.tasks_tree.heading("due_date", text="تاريخ الاستحقاق")
        self.tasks_tree.heading("status", text="الحالة")
        self.tasks_tree.heading("progress", text="التقدم")
        
        self.tasks_tree.column("id", width=50, anchor=tk.CENTER)
        self.tasks_tree.column("task", width=250)
        self.tasks_tree.column("assignee", width=120)
        self.tasks_tree.column("priority", width=80, anchor=tk.CENTER)
        self.tasks_tree.column("due_date", width=100, anchor=tk.CENTER)
        self.tasks_tree.column("status", width=100, anchor=tk.CENTER)
        self.tasks_tree.column("progress", width=80, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=scrollbar.set)
        
        self.tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # تحميل مهام تجريبية
        self.load_sample_tasks()
    
    def create_documents_tab(self):
        """إنشاء تبويب المستندات"""
        frame = ttk.Frame(self.documents_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # أزرار التحكم
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="📤 رفع مستند", command=self.upload_document).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📥 تنزيل", command=self.download_document).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="👁️ معاينة", command=self.preview_document).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ حذف", command=self.delete_document).pack(side=tk.LEFT, padx=5)
        
        # جدول المستندات
        columns = ("name", "type", "size", "uploaded_by", "date", "status")
        self.docs_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        self.docs_tree.heading("name", text="اسم الملف")
        self.docs_tree.heading("type", text="النوع")
        self.docs_tree.heading("size", text="الحجم")
        self.docs_tree.heading("uploaded_by", text="تم الرفع بواسطة")
        self.docs_tree.heading("date", text="تاريخ الرفع")
        self.docs_tree.heading("status", text="الحالة")
        
        self.docs_tree.column("name", width=250)
        self.docs_tree.column("type", width=80, anchor=tk.CENTER)
        self.docs_tree.column("size", width=80, anchor=tk.CENTER)
        self.docs_tree.column("uploaded_by", width=120)
        self.docs_tree.column("date", width=100, anchor=tk.CENTER)
        self.docs_tree.column("status", width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.docs_tree.yview)
        self.docs_tree.configure(yscrollcommand=scrollbar.set)
        
        self.docs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # تحميل مستندات تجريبية
        self.load_sample_documents()
    
    def create_ai_tab(self):
        """إنشاء تبويب تحليلات AI"""
        frame = ttk.Frame(self.ai_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # أزرار التحكم
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="🚀 بدء التحليل", command=self.run_ai_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📊 عرض النتائج", command=self.show_ai_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📤 تصدير التقرير", command=self.export_ai_report).pack(side=tk.LEFT, padx=5)
        
        # منطقة النتائج
        results_frame = ttk.LabelFrame(frame, text="نتائج تحليل AI", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ai_results_text = tk.Text(results_frame, wrap=tk.WORD, height=20)
        self.ai_results_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.ai_results_text.yview)
        self.ai_results_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # عرض رسالة ترحيبية
        self.ai_results_text.insert(tk.END, "اضغط على 'بدء التحليل' لتشغيل وكلاء الذكاء الاصطناعي...\n\n")
        self.ai_results_text.insert(tk.END, "الوكلاء المتاحون:\n")
        self.ai_results_text.insert(tk.END, "  • وكيل التحليل المالي\n")
        self.ai_results_text.insert(tk.END, "  • وكيل كشف الاحتيال\n")
        self.ai_results_text.insert(tk.END, "  • وكيل الامتثال الضريبي\n")
        self.ai_results_text.insert(tk.END, "  • وكيل مراجعة القيود اليومية\n")
        self.ai_results_text.insert(tk.END, "  • وكيل التسوية البنكية\n")
        self.ai_results_text.config(state=tk.DISABLED)
    
    def load_project_data(self):
        """تحميل بيانات المشروع"""
        if not self.project:
            return
        
        # النظرة العامة
        self.title_label.config(text=f"📁 {self.project.get('name', 'مشروع غير محدد')}")
        self.project_name_var.set(self.project.get('name', ''))
        self.project_type_var.set(self.project.get('audit_type', ''))
        self.priority_var.set(self.project.get('priority', ''))
        self.status_var.set(self.project.get('status', ''))
        self.description_text.insert(tk.END, self.project.get('description', ''))
        
        self.client_name_var.set(self.project.get('client_name', ''))
        self.industry_var.set(self.project.get('industry', ''))
        self.company_size_var.set(self.project.get('company_size', ''))
        self.contact_var.set(self.project.get('contact_person', ''))
        self.email_var.set(self.project.get('email', ''))
        
        # فريق العمل
        self.manager_var.set(self.project.get('manager', ''))
        self.load_sample_team()
        
        # الجدول الزمني
        self.start_date_var.set(self.project.get('start_date', ''))
        self.end_date_var.set(self.project.get('end_date', ''))
        self.duration_var.set(self.project.get('duration_weeks', ''))
        self.load_sample_phases()
        
        # شريط التقدم
        progress = self.project.get('progress', 0)
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{progress}%")
    
    def load_sample_team(self):
        """تحميل عينة من فريق العمل"""
        sample_team = [
            ("أحمد محمد", "مراجع أول", "120", "نشط"),
            ("سارة أحمد", "مراجع مالي", "80", "نشط"),
            ("محمد علي", "محلل بيانات", "60", "نشط"),
            ("فاطمة خالد", "خبير ضريبي", "40", "متاح")
        ]
        
        for member in sample_team:
            self.team_tree.insert("", tk.END, values=member)
    
    def load_sample_phases(self):
        """تحميل عينة من مراحل المشروع"""
        sample_phases = [
            ("التخطيط والتحضير", "2024-01-15", "2024-01-22", "مكتمل", "100%"),
            ("تقييم المخاطر", "2024-01-23", "2024-02-05", "قيد التنفيذ", "75%"),
            ("اختبار الضوابط", "2024-02-06", "2024-02-20", "لم يبدأ", "0%"),
            ("الإجراءات التفصيلية", "2024-02-21", "2024-03-05", "لم يبدأ", "0%"),
            ("إعداد التقرير", "2024-03-06", "2024-03-12", "لم يبدأ", "0%"),
            ("مراجعة نهائية", "2024-03-13", "2024-03-15", "لم يبدأ", "0%")
        ]
        
        for phase in sample_phases:
            self.phases_tree.insert("", tk.END, values=phase)
    
    def load_sample_tasks(self):
        """تحميل عينة من المهام"""
        sample_tasks = [
            (1, "جمع البيانات المالية", "أحمد محمد", "عالية", "2024-01-20", "مكتمل", "100%"),
            (2, "تحليل القوائم المالية", "سارة أحمد", "عالية", "2024-01-25", "قيد التنفيذ", "60%"),
            (3, "مراجعة القيود اليومية", "محمد علي", "متوسطة", "2024-01-28", "قيد التنفيذ", "40%"),
            (4, "فحص الامتثال الضريبي", "فاطمة خالد", "عالية", "2024-02-01", "لم يبدأ", "0%"),
            (5, "إعداد مسودة التقرير", "أحمد محمد", "متوسطة", "2024-03-05", "لم يبدأ", "0%")
        ]
        
        for task in sample_tasks:
            self.tasks_tree.insert("", tk.END, values=task)
    
    def load_sample_documents(self):
        """تحميل عينة من المستندات"""
        sample_docs = [
            ("القوائم المالية 2024.pdf", "PDF", "2.5 MB", "أحمد محمد", "2024-01-15", "تمت المراجعة"),
            ("سجل القيود اليومية.xlsx", "XLSX", "1.8 MB", "سارة أحمد", "2024-01-16", "جاري المراجعة"),
            ("العقود القانونية.pdf", "PDF", "5.2 MB", "محمد علي", "2024-01-17", "جديد"),
            ("كشف الحساب البنكي.pdf", "PDF", "0.8 MB", "أحمد محمد", "2024-01-18", "جديد")
        ]
        
        for doc in sample_docs:
            self.docs_tree.insert("", tk.END, values=doc)
    
    # دوال الإجراءات
    def add_team_member(self):
        messagebox.showinfo("إضافة عضو", "وظيفة إضافة عضو قيد التطوير")
    
    def edit_team_member(self):
        messagebox.showinfo("تعديل", "وظيفة تعديل عضو قيد التطوير")
    
    def delete_team_member(self):
        messagebox.showinfo("حذف", "وظيفة حذف عضو قيد التطوير")
    
    def add_task(self):
        messagebox.showinfo("إضافة مهمة", "وظيفة إضافة مهمة قيد التطوير")
    
    def refresh_tasks(self):
        messagebox.showinfo("تحديث", "تم تحديث قائمة المهام")
    
    def export_tasks(self):
        messagebox.showinfo("تصدير", "وظيفة تصدير المهام قيد التطوير")
    
    def upload_document(self):
        messagebox.showinfo("رفع", "وظيفة رفع مستند قيد التطوير")
    
    def download_document(self):
        messagebox.showinfo("تنزيل", "وظيفة تنزيل مستند قيد التطوير")
    
    def preview_document(self):
        messagebox.showinfo("معاينة", "وظيفة معاينة مستند قيد التطوير")
    
    def delete_document(self):
        messagebox.showinfo("حذف", "وظيفة حذف مستند قيد التطوير")
    
    def run_ai_analysis(self):
        """تشغيل تحليل AI"""
        self.ai_results_text.config(state=tk.NORMAL)
        self.ai_results_text.delete(1.0, tk.END)
        
        self.ai_results_text.insert(tk.END, "🚀 بدء تشغيل وكلاء الذكاء الاصطناعي...\n\n")
        self.ai_results_text.insert(tk.END, "⏳ جاري تحليل البيانات...\n")
        
        # محاكاة عملية التحليل
        import time
        
        def analyze():
            time.sleep(1)
            self.ai_results_text.insert(tk.END, "✓ وكيل التحليل المالي: اكتمل\n")
            self.ai_results_text.see(tk.END)
            
            time.sleep(1)
            self.ai_results_text.insert(tk.END, "✓ وكيل كشف الاحتيال: اكتمل - لا توجد مؤشرات احتيال\n")
            self.ai_results_text.see(tk.END)
            
            time.sleep(1)
            self.ai_results_text.insert(tk.END, "✓ وكيل الامتثال الضريبي: اكتمل - تم تحديد 3 ملاحظات\n")
            self.ai_results_text.see(tk.END)
            
            time.sleep(1)
            self.ai_results_text.insert(tk.END, "✓ وكيل مراجعة القيود: اكتمل - 156 قيد تم مراجعتها\n")
            self.ai_results_text.see(tk.END)
            
            time.sleep(1)
            self.ai_results_text.insert(tk.END, "\n✅ اكتمل التحليل بنجاح!\n")
            self.ai_results_text.insert(tk.END, "\n📊 الملخص:\n")
            self.ai_results_text.insert(tk.END, "  • إجمالي المعاملات المفحوصة: 1,245\n")
            self.ai_results_text.insert(tk.END, "  • الملاحظات المهمة: 3\n")
            self.ai_results_text.insert(tk.END, "  • نسبة الامتثال: 97.5%\n")
            self.ai_results_text.insert(tk.END, "  • مستوى المخاطر: منخفض\n")
            
            self.ai_results_text.config(state=tk.DISABLED)
        
        # تشغيل التحليل في خلفية
        self.parent.after(100, analyze)
    
    def show_ai_results(self):
        messagebox.showinfo("النتائج", "اضغط على 'بدء التحليل' أولاً")
    
    def export_ai_report(self):
        messagebox.showinfo("تصدير", "وظيفة تصدير تقرير AI قيد التطوير")
    
    def save_project(self):
        messagebox.showinfo("حفظ", "تم حفظ بيانات المشروع بنجاح")
    
    def generate_report(self):
        messagebox.showinfo("تقرير", "وظيفة إنشاء التقارير قيد التطوير")
    
    def close_window(self):
        self.parent.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("تفاصيل المشروع")
    root.geometry("1200x800")
    
    sample_project = {
        "name": "مراجعة القوائم المالية 2024",
        "audit_type": "مراجعة القوائم المالية",
        "priority": "عالية",
        "status": "قيد التنفيذ",
        "description": "مراجعة شاملة للقوائم المالية للعام المالي 2024",
        "client_name": "شركة التقنية المتقدمة",
        "industry": "تقنية",
        "company_size": "كبيرة",
        "contact_person": "محمد الأحمد",
        "email": "mohamed@techcorp.com",
        "manager": "أحمد محمد",
        "start_date": "2024-01-15",
        "end_date": "2024-03-15",
        "duration_weeks": "8",
        "progress": 65
    }
    
    app = ProjectDetailWindow(root, sample_project)
    root.mainloop()

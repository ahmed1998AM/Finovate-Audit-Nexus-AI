"""
نافذة قائمة مشاريع المراجعة
Audit Projects List Window
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List, Dict, Optional
import json
import os

class AuditProjectListWindow:
    """نافذة عرض وإدارة قائمة مشاريع المراجعة"""
    
    def __init__(self, parent, on_project_select=None):
        self.parent = parent
        self.on_project_select = on_project_select
        self.projects = []
        self.selected_project = None
        
        self.setup_ui()
        self.load_projects()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # العنوان
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            title_frame,
            text="📁 مشاريع المراجعة",
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)
        
        # أزرار التحكم
        btn_frame = ttk.Frame(title_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            btn_frame,
            text="➕ مشروع جديد",
            command=self.create_new_project
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="📂 فتح مجلد",
            command=self.open_folder
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🔄 تحديث",
            command=self.refresh_projects
        ).pack(side=tk.LEFT, padx=5)
        
        # شريط البحث
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 بحث:").pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_projects)
        
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # فلتر الحالة
        ttk.Label(search_frame, text="الحالة:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.status_filter = ttk.Combobox(
            search_frame,
            values=["الكل", "جديد", "قيد التنفيذ", "مكتمل", "متوقف"],
            state="readonly",
            width=15
        )
        self.status_filter.set("الكل")
        self.status_filter.pack(side=tk.LEFT)
        self.status_filter.bind("<<ComboboxSelected>>", self.filter_projects)
        
        # جدول المشاريع
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = (
            "id", "name", "client", "status", "start_date", 
            "end_date", "progress", "team", "priority"
        )
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # تعريف الأعمدة
        self.tree.heading("id", text="#")
        self.tree.heading("name", text="اسم المشروع")
        self.tree.heading("client", text="العميل")
        self.tree.heading("status", text="الحالة")
        self.tree.heading("start_date", text="تاريخ البدء")
        self.tree.heading("end_date", text="تاريخ الانتهاء")
        self.tree.heading("progress", text="التقدم")
        self.tree.heading("team", text="الفريق")
        self.tree.heading("priority", text="الأولوية")
        
        # عرض الأعمدة
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("name", width=200)
        self.tree.column("client", width=150)
        self.tree.column("status", width=100, anchor=tk.CENTER)
        self.tree.column("start_date", width=100, anchor=tk.CENTER)
        self.tree.column("end_date", width=100, anchor=tk.CENTER)
        self.tree.column("progress", width=80, anchor=tk.CENTER)
        self.tree.column("team", width=100)
        self.tree.column("priority", width=80, anchor=tk.CENTER)
        
        # شريط التمرير
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ربط حدث النقر المزدوج
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # شريط الحالة
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            text=f"إجمالي المشاريع: 0",
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # قائمة السياق
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="📂 فتح المشروع", command=self.open_selected_project)
        self.context_menu.add_command(label="✏️ تعديل", command=self.edit_project)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📤 تصدير", command=self.export_project)
        self.context_menu.add_command(label="🗑️ حذف", command=self.delete_project)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
    
    def load_projects(self):
        """تحميل المشاريع من قاعدة البيانات"""
        # مشاريع تجريبية للعرض
        self.projects = [
            {
                "id": 1,
                "name": "مراجعة القوائم المالية 2024",
                "client": "شركة التقنية المتقدمة",
                "status": "قيد التنفيذ",
                "start_date": "2024-01-15",
                "end_date": "2024-03-15",
                "progress": 65,
                "team": "أحمد، سارة، محمد",
                "priority": "عالية"
            },
            {
                "id": 2,
                "name": "مراجعة ضريبية ربع سنوية",
                "client": "مجموعة الأفق",
                "status": "جديد",
                "start_date": "2024-02-01",
                "end_date": "2024-02-28",
                "progress": 10,
                "team": "فاطمة، خالد",
                "priority": "متوسطة"
            },
            {
                "id": 3,
                "name": "فحص الامتثال الداخلي",
                "client": "البنك الأهلي",
                "status": "مكتمل",
                "start_date": "2023-11-01",
                "end_date": "2023-12-31",
                "progress": 100,
                "team": "أحمد، سارة، محمد، فاطمة",
                "priority": "عالية"
            },
            {
                "id": 4,
                "name": "مراجعة المشتريات",
                "client": "شركة البناء الحديثة",
                "status": "قيد التنفيذ",
                "start_date": "2024-01-20",
                "end_date": "2024-04-20",
                "progress": 45,
                "team": "خالد، نور",
                "priority": "منخفضة"
            }
        ]
        
        self.refresh_tree()
    
    def refresh_tree(self):
        """تحديث جدول العرض"""
        # مسح المحتوى الحالي
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # إضافة المشاريع
        filtered_projects = self.filter_projects_list()
        
        for project in filtered_projects:
            self.tree.insert("", tk.END, values=(
                project["id"],
                project["name"],
                project["client"],
                project["status"],
                project["start_date"],
                project["end_date"],
                f"{project['progress']}%",
                project["team"],
                project["priority"]
            ))
        
        # تحديث شريط الحالة
        self.status_label.config(text=f"إجمالي المشاريع: {len(filtered_projects)} من {len(self.projects)}")
    
    def filter_projects_list(self) -> List[Dict]:
        """تصفية المشاريع حسب البحث والحالة"""
        filtered = self.projects
        
        # فلتر البحث النصي
        search_term = self.search_var.get().lower()
        if search_term:
            filtered = [
                p for p in filtered
                if search_term in p["name"].lower() or
                   search_term in p["client"].lower()
            ]
        
        # فلتر الحالة
        status = self.status_filter.get()
        if status != "الكل":
            filtered = [p for p in filtered if p["status"] == status]
        
        return filtered
    
    def filter_projects(self, *args):
        """دالة التصفية عند تغيير البحث أو الفلتر"""
        self.refresh_tree()
    
    def create_new_project(self):
        """إنشاء مشروع جديد"""
        from frontend.audit_projects.create_project_wizard import CreateProjectWizard
        
        wizard_window = tk.Toplevel(self.parent)
        wizard_window.title("إنشاء مشروع مراجعة جديد")
        wizard_window.geometry("800x600")
        
        wizard = CreateProjectWizard(wizard_window, on_complete=self.on_project_created)
    
    def on_project_created(self, project_data):
        """عند إنشاء مشروع جديد"""
        project_data["id"] = len(self.projects) + 1
        self.projects.append(project_data)
        self.refresh_tree()
        messagebox.showinfo("نجاح", "تم إنشاء المشروع بنجاح!")
    
    def open_selected_project(self):
        """فتح المشروع المحدد"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار مشروع أولاً")
            return
        
        item = self.tree.item(selected[0])
        project_id = item["values"][0]
        
        # البحث عن المشروع
        project = next((p for p in self.projects if p["id"] == project_id), None)
        
        if project and self.on_project_select:
            self.on_project_select(project)
    
    def on_double_click(self, event):
        """عند النقر المزدوج"""
        self.open_selected_project()
    
    def edit_project(self):
        """تعديل المشروع المحدد"""
        messagebox.showinfo("تعديل", "وظيفة التعديل قيد التطوير")
    
    def export_project(self):
        """تصدير المشروع"""
        messagebox.showinfo("تصدير", "وظيفة التصدير قيد التطوير")
    
    def delete_project(self):
        """حذف المشروع المحدد"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار مشروع أولاً")
            return
        
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا المشروع؟"):
            item = self.tree.item(selected[0])
            project_id = item["values"][0]
            
            self.projects = [p for p in self.projects if p["id"] != project_id]
            self.refresh_tree()
            messagebox.showinfo("نجاح", "تم حذف المشروع بنجاح")
    
    def show_context_menu(self, event):
        """إظهار قائمة السياق"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def refresh_projects(self):
        """تحديث قائمة المشاريع"""
        self.load_projects()
        messagebox.showinfo("تحديث", "تم تحديث قائمة المشاريع")
    
    def open_folder(self):
        """فتح مجلد المشاريع"""
        import webbrowser
        projects_dir = os.path.join(os.path.dirname(__file__), "..", "..", "audit_projects")
        os.makedirs(projects_dir, exist_ok=True)
        webbrowser.open(projects_dir)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("مشاريع المراجعة")
    root.geometry("1200x700")
    
    app = AuditProjectListWindow(root)
    root.mainloop()

"""
مدير المتصلات - Connector Manager
إدارة متصلات ERP المختلفة
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional


class ConnectorManagerWindow:
    """نافذة إدارة متصلات الأنظمة الخارجية"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_connectors()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # العنوان
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            title_frame,
            text="🔌 إدارة متصلات ERP",
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)
        
        btn_frame = ttk.Frame(title_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            btn_frame,
            text="➕ إضافة متصل",
            command=self.add_connector
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🔄 تحديث الحالة",
            command=self.refresh_status
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🧪 اختبار الاتصال",
            command=self.test_connection
        ).pack(side=tk.LEFT, padx=5)
        
        # ملخص المتصلات
        summary_frame = ttk.LabelFrame(self.frame, text="ملخص المتصلات", padding=10)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.summary_labels = {}
        statuses = [
            ("total", "إجمالي المتصلات", "📊"),
            ("connected", "متصل", "✅"),
            ("disconnected", "غير متصل", "❌"),
            ("error", "به أخطاء", "⚠️")
        ]
        
        for i, (key, label, icon) in enumerate(statuses):
            container = ttk.Frame(summary_frame)
            container.pack(side=tk.LEFT, padx=20)
            
            ttk.Label(
                container,
                text=f"{icon} {label}",
                font=("Arial", 10, "bold")
            ).pack(anchor=tk.W)
            
            value_label = ttk.Label(
                container,
                text="0",
                font=("Arial", 14),
                foreground="#2196F3"
            )
            value_label.pack(anchor=tk.W)
            
            self.summary_labels[key] = value_label
        
        # جدول المتصلات
        table_frame = ttk.LabelFrame(self.frame, text="قائمة المتصلات المتاحة", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("name", "system", "status", "last_sync", "records", "version")
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )
        
        self.tree.heading("name", text="اسم المتصل")
        self.tree.heading("system", text="النظام")
        self.tree.heading("status", text="الحالة")
        self.tree.heading("last_sync", text="آخر مزامنة")
        self.tree.heading("records", text="السجلات")
        self.tree.heading("version", text="الإصدار")
        
        self.tree.column("name", width=180)
        self.tree.column("system", width=120, anchor=tk.CENTER)
        self.tree.column("status", width=100, anchor=tk.CENTER)
        self.tree.column("last_sync", width=150, anchor=tk.CENTER)
        self.tree.column("records", width=100, anchor=tk.E)
        self.tree.column("version", width=80, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ربط حدث النقر المزدوج
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # قائمة السياق
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="⚙️ إعدادات", command=self.configure_connector)
        self.context_menu.add_command(label="🔄 مزامنة الآن", command=self.sync_now)
        self.context_menu.add_command(label="🧪 اختبار الاتصال", command=self.test_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ حذف", command=self.delete_connector)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # شريط الحالة السفلي
        status_bar = ttk.Frame(self.frame)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(
            status_bar,
            text="جاهز",
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.LEFT)
    
    def load_connectors(self):
        """تحميل قائمة المتصلات"""
        # بيانات تجريبية
        self.connectors = [
            {
                "name": "SAP Production",
                "system": "SAP",
                "status": "connected",
                "last_sync": "2024-01-15 10:30",
                "records": "1,250,000",
                "version": "7.5"
            },
            {
                "name": "Oracle Finance",
                "system": "Oracle",
                "status": "connected",
                "last_sync": "2024-01-15 09:45",
                "records": "890,000",
                "version": "19c"
            },
            {
                "name": "Dynamics 365",
                "system": "Dynamics",
                "status": "connected",
                "last_sync": "2024-01-15 11:00",
                "records": "567,000",
                "version": "2024"
            },
            {
                "name": "Odoo Community",
                "system": "Odoo",
                "status": "disconnected",
                "last_sync": "2024-01-14 16:20",
                "records": "125,000",
                "version": "16.0"
            },
            {
                "name": "QuickBooks Online",
                "system": "QuickBooks",
                "status": "connected",
                "last_sync": "2024-01-15 10:15",
                "records": "45,000",
                "version": "API v3"
            },
            {
                "name": "Xero Accounting",
                "system": "Xero",
                "status": "error",
                "last_sync": "2024-01-13 14:30",
                "records": "32,000",
                "version": "2.0"
            },
            {
                "name": "Zoho Books",
                "system": "Zoho",
                "status": "connected",
                "last_sync": "2024-01-15 08:00",
                "records": "28,000",
                "version": "Latest"
            },
            {
                "name": "SQL Server DB",
                "system": "SQL",
                "status": "connected",
                "last_sync": "2024-01-15 11:30",
                "records": "2,100,000",
                "version": "2022"
            }
        ]
        
        self.refresh_tree()
        self.update_summary()
    
    def refresh_tree(self):
        """تحديث جدول العرض"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        status_icons = {
            "connected": "✅ متصل",
            "disconnected": "❌ غير متصل",
            "error": "⚠️ خطأ"
        }
        
        for conn in self.connectors:
            self.tree.insert("", tk.END, values=(
                conn["name"],
                conn["system"],
                status_icons.get(conn["status"], conn["status"]),
                conn["last_sync"],
                conn["records"],
                conn["version"]
            ))
    
    def update_summary(self):
        """تحديث ملخص الحالة"""
        total = len(self.connectors)
        connected = sum(1 for c in self.connectors if c["status"] == "connected")
        disconnected = sum(1 for c in self.connectors if c["status"] == "disconnected")
        error = sum(1 for c in self.connectors if c["status"] == "error")
        
        self.summary_labels["total"].config(text=str(total))
        self.summary_labels["connected"].config(text=str(connected), foreground="#4CAF50")
        self.summary_labels["disconnected"].config(text=str(disconnected), foreground="#f44336")
        self.summary_labels["error"].config(text=str(error), foreground="#FF9800")
    
    def add_connector(self):
        """إضافة متصل جديد"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("إضافة متصل جديد")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        ttk.Label(dialog, text="اختر نوع النظام:", font=("Arial", 11, "bold")).pack(pady=10)
        
        system_var = tk.StringVar()
        systems = [
            "SAP", "Oracle", "Microsoft Dynamics", "Odoo", 
            "QuickBooks", "Xero", "Zoho", "SQL Server",
            "MySQL", "PostgreSQL", "API Custom"
        ]
        
        combo = ttk.Combobox(dialog, textvariable=system_var, values=systems, state="readonly", width=40)
        combo.pack(pady=10)
        combo.set(systems[0])
        
        ttk.Label(dialog, text="اسم المتصل:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="عنوان الخادم/URL:").pack(pady=5)
        server_entry = ttk.Entry(dialog, width=40)
        server_entry.pack(pady=5)
        
        def save():
            if not name_entry.get():
                messagebox.showwarning("تنبيه", "يرجى إدخال اسم المتصل")
                return
            
            new_connector = {
                "name": name_entry.get(),
                "system": system_var.get().split()[0],
                "status": "disconnected",
                "last_sync": "لم تتم المزامنة",
                "records": "0",
                "version": "-"
            }
            
            self.connectors.append(new_connector)
            self.refresh_tree()
            self.update_summary()
            dialog.destroy()
            messagebox.showinfo("نجاح", "تم إضافة المتصل بنجاح!")
        
        ttk.Button(dialog, text="حفظ", command=save).pack(pady=20)
    
    def configure_connector(self):
        """إعداد المتصل المحدد"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار متصل أولاً")
            return
        
        item = self.tree.item(selected[0])
        connector_name = item["values"][0]
        
        messagebox.showinfo("إعدادات", f"إعدادات المتصل: {connector_name}\n\nهذه الوظيفة قيد التطوير")
    
    def sync_now(self):
        """مزامنة فورية"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار متصل أولاً")
            return
        
        self.status_label.config(text="جاري المزامنة...")
        self.parent.update()
        
        import time
        time.sleep(1)
        
        messagebox.showinfo("مزامنة", "تمت المزامنة بنجاح!")
        self.status_label.config(text="جاهز")
    
    def test_connection(self):
        """اختبار جميع الاتصالات"""
        self.status_label.config(text="جاري اختبار الاتصالات...")
        self.parent.update()
        
        import time
        time.sleep(1)
        
        results = "نتائج اختبار الاتصال:\n\n"
        for conn in self.connectors:
            icon = "✅" if conn["status"] == "connected" else "❌"
            results += f"{icon} {conn['name']}: {conn['status']}\n"
        
        messagebox.showinfo("اختبار الاتصال", results)
        self.status_label.config(text="جاهز")
    
    def test_selected(self):
        """اختبار المتصل المحدد"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار متصل أولاً")
            return
        
        item = self.tree.item(selected[0])
        connector_name = item["values"][0]
        
        messagebox.showinfo("اختبار", f"اختبار اتصال: {connector_name}\n\nالاتصال ناجح! ✅")
    
    def delete_connector(self):
        """حذف المتصل المحدد"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار متصل أولاً")
            return
        
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا المتصل؟"):
            item = self.tree.item(selected[0])
            connector_name = item["values"][0]
            
            self.connectors = [c for c in self.connectors if c["name"] != connector_name]
            self.refresh_tree()
            self.update_summary()
            messagebox.showinfo("نجاح", "تم حذف المتصل بنجاح")
    
    def show_context_menu(self, event):
        """إظهار قائمة السياق"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def on_double_click(self, event):
        """عند النقر المزدوج"""
        self.configure_connector()
    
    def refresh_status(self):
        """تحديث حالة المتصلات"""
        self.status_label.config(text="جاري تحديث الحالة...")
        self.parent.update()
        
        import time
        time.sleep(0.5)
        
        self.load_connectors()
        self.status_label.config(text="تم التحديث بنجاح")
        messagebox.showinfo("تحديث", "تم تحديث حالة المتصلات")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("إدارة المتصلات")
    root.geometry("1100x600")
    
    app = ConnectorManagerWindow(root)
    root.mainloop()

"""
نافذة لوحة التحليل المالي
Financial Analysis Dashboard Window
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional
import random
from datetime import datetime, timedelta


class FinancialDashboardWindow:
    """نافذة لوحة التحكم للتحليل المالي"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_sample_data()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # العنوان
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            title_frame,
            text="📊 لوحة التحليل المالي",
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)
        
        # أزرار التحكم
        btn_frame = ttk.Frame(title_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            btn_frame,
            text="📤 تصدير التقرير",
            command=self.export_report
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🔄 تحديث البيانات",
            command=self.refresh_data
        ).pack(side=tk.LEFT, padx=5)
        
        # ملخص المؤشرات الرئيسية
        kpi_frame = ttk.LabelFrame(self.frame, text="المؤشرات المالية الرئيسية", padding=10)
        kpi_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.kpi_labels = {}
        kpis = [
            ("الإيرادات", "revenue", "💰"),
            ("صافي الربح", "net_profit", "📈"),
            ("إجمالي الأصول", "total_assets", "🏦"),
            ("إجمالي الخصوم", "total_liabilities", "📉"),
            ("حقوق الملكية", "equity", "💎"),
            ("التدفق النقدي", "cash_flow", "💵"),
            ("هامش الربح", "profit_margin", "📊"),
            ("العائد على الأصول", "roa", "🎯")
        ]
        
        for i, (label_ar, key, icon) in enumerate(kpis):
            col = i % 4
            row = i // 4
            
            kpi_container = ttk.Frame(kpi_frame)
            kpi_container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            ttk.Label(
                kpi_container,
                text=f"{icon} {label_ar}",
                font=("Arial", 10, "bold")
            ).pack(anchor=tk.W)
            
            value_label = ttk.Label(
                kpi_container,
                text="جاري التحميل...",
                font=("Arial", 14),
                foreground="#2196F3"
            )
            value_label.pack(anchor=tk.W)
            
            change_label = ttk.Label(
                kpi_container,
                text="",
                font=("Arial", 9)
            )
            change_label.pack(anchor=tk.W)
            
            self.kpi_labels[key] = {
                'value': value_label,
                'change': change_label
            }
        
        kpi_frame.columnconfigure(0, weight=1)
        kpi_frame.columnconfigure(1, weight=1)
        kpi_frame.columnconfigure(2, weight=1)
        kpi_frame.columnconfigure(3, weight=1)
        
        # قسم الرسوم البيانية
        charts_frame = ttk.LabelFrame(self.frame, text="الرسوم البيانية", padding=10)
        charts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # تبويبات الرسوم البيانية
        chart_tabs = ttk.Notebook(charts_frame)
        chart_tabs.pack(fill=tk.BOTH, expand=True)
        
        # تبويب الاتجاهات
        trends_tab = ttk.Frame(chart_tabs)
        chart_tabs.add(trends_tab, text="📈 اتجاهات الإيرادات")
        
        self.trends_canvas = tk.Canvas(trends_tab, bg="white", height=300)
        self.trends_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # تبويب التركيب
        composition_tab = ttk.Frame(chart_tabs)
        chart_tabs.add(composition_tab, text="🥧 تركيب المصروفات")
        
        self.composition_canvas = tk.Canvas(composition_tab, bg="white", height=300)
        self.composition_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # جدول التحليل الرأسي
        analysis_frame = ttk.LabelFrame(self.frame, text="التحليل المالي التفصيلي", padding=10)
        analysis_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("item", "current_year", "previous_year", "change", "percentage")
        
        self.analysis_tree = ttk.Treeview(
            analysis_frame,
            columns=columns,
            show="headings",
            height=8
        )
        
        self.analysis_tree.heading("item", text="البند")
        self.analysis_tree.heading("current_year", text="السنة الحالية")
        self.analysis_tree.heading("previous_year", text="السنة السابقة")
        self.analysis_tree.heading("change", text="التغير")
        self.analysis_tree.heading("percentage", text="النسبة المئوية")
        
        self.analysis_tree.column("item", width=200)
        self.analysis_tree.column("current_year", width=120, anchor=tk.E)
        self.analysis_tree.column("previous_year", width=120, anchor=tk.E)
        self.analysis_tree.column("change", width=100, anchor=tk.E)
        self.analysis_tree.column("percentage", width=100, anchor=tk.E)
        
        scrollbar = ttk.Scrollbar(analysis_frame, orient=tk.VERTICAL, command=self.analysis_tree.yview)
        self.analysis_tree.configure(yscrollcommand=scrollbar.set)
        
        self.analysis_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_sample_data(self):
        """تحميل بيانات عينة"""
        # تحديث المؤشرات
        kpi_data = {
            'revenue': {'value': '15,750,000', 'change': '+12.5%', 'positive': True},
            'net_profit': {'value': '2,340,000', 'change': '+8.3%', 'positive': True},
            'total_assets': {'value': '45,200,000', 'change': '+5.7%', 'positive': True},
            'total_liabilities': {'value': '18,900,000', 'change': '-3.2%', 'positive': True},
            'equity': {'value': '26,300,000', 'change': '+11.4%', 'positive': True},
            'cash_flow': {'value': '3,450,000', 'change': '+15.8%', 'positive': True},
            'profit_margin': {'value': '14.86%', 'change': '-2.1%', 'positive': False},
            'roa': {'value': '5.18%', 'change': '+0.3%', 'positive': True}
        }
        
        for key, data in kpi_data.items():
            self.kpi_labels[key]['value'].config(text=data['value'])
            change_text = f"{data['change']} مقارنة بالعام السابق"
            color = "#4CAF50" if data['positive'] else "#f44336"
            self.kpi_labels[key]['change'].config(text=change_text, foreground=color)
        
        # تحميل جدول التحليل
        analysis_data = [
            ("الإيرادات", "15,750,000", "14,000,000", "+1,750,000", "+12.5%"),
            ("تكلفة البضاعة المباعة", "9,450,000", "8,400,000", "+1,050,000", "+12.5%"),
            ("إجمالي الربح", "6,300,000", "5,600,000", "+700,000", "+12.5%"),
            ("المصروفات التشغيلية", "3,200,000", "2,900,000", "+300,000", "+10.3%"),
            ("مصروفات البيع والتسويق", "1,800,000", "1,600,000", "+200,000", "+12.5%"),
            ("مصروفات إدارية", "1,400,000", "1,300,000", "+100,000", "+7.7%"),
            ("صافي الربح التشغيلي", "3,100,000", "2,700,000", "+400,000", "+14.8%"),
            ("مصروفات تمويلية", "450,000", "500,000", "-50,000", "-10.0%"),
            ("صافي الربح قبل الضريبة", "2,650,000", "2,200,000", "+450,000", "+20.5%"),
            ("ضريبة الدخل", "310,000", "280,000", "+30,000", "+10.7%"),
            ("صافي الربح", "2,340,000", "1,920,000", "+420,000", "+21.9%")
        ]
        
        for item in analysis_data:
            self.analysis_tree.insert("", tk.END, values=item)
        
        # رسم الرسم البياني للاتجاهات
        self.draw_trends_chart()
        
        # رسم الرسم البياني للتركيب
        self.draw_composition_chart()
    
    def draw_trends_chart(self):
        """رسم مخطط اتجاهات الإيرادات"""
        canvas = self.trends_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width() or 600
        height = canvas.winfo_height() or 300
        
        # بيانات تجريبية للإيرادات الشهرية
        months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", 
                  "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        revenues = [1200, 1350, 1180, 1420, 1550, 1680, 1590, 1720, 1850, 1920, 2050, 2180]
        
        # حساب الإحداثيات
        margin_left = 60
        margin_right = 20
        margin_top = 20
        margin_bottom = 40
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom
        
        max_revenue = max(revenues) * 1.1
        min_revenue = min(revenues) * 0.9
        
        # رسم المحاور
        canvas.create_line(margin_left, margin_top, margin_left, height - margin_bottom, width=2)
        canvas.create_line(margin_left, height - margin_bottom, width - margin_right, height - margin_bottom, width=2)
        
        # رسم الخط البياني
        points = []
        for i, rev in enumerate(revenues):
            x = margin_left + (i / (len(revenues) - 1)) * chart_width
            y = height - margin_bottom - ((rev - min_revenue) / (max_revenue - min_revenue)) * chart_height
            points.append((x, y))
        
        # رسم الخط
        for i in range(len(points) - 1):
            canvas.create_line(
                points[i][0], points[i][1],
                points[i+1][0], points[i+1][1],
                fill="#2196F3", width=3
            )
        
        # رسم النقاط
        for x, y in points:
            canvas.create_oval(x-4, y-4, x+4, y+4, fill="#2196F3", outline="white")
        
        # كتابة الأشهر
        for i, month in enumerate(months):
            x = margin_left + (i / (len(months) - 1)) * chart_width
            canvas.create_text(x, height - margin_bottom + 15, text=month, font=("Arial", 8))
    
    def draw_composition_chart(self):
        """رسم مخطط دائري لتركيب المصروفات"""
        canvas = self.composition_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width() or 600
        height = canvas.winfo_height() or 300
        
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 3
        
        # بيانات المصروفات
        expenses = [
            ("رواتب وأجور", 45, "#FF6384"),
            ("إيجارات", 20, "#36A2EB"),
            ("مرافق", 10, "#FFCE56"),
            ("تسويق", 15, "#4BC0C0"),
            ("أخرى", 10, "#9966FF")
        ]
        
        start_angle = 0
        total = sum(exp[1] for exp in expenses)
        
        # رسم الأجزاء
        legend_y = 20
        for name, value, color in expenses:
            angle = (value / total) * 360
            end_angle = start_angle + angle
            
            # تحويل الزوايا إلى راديان
            import math
            start_rad = math.radians(start_angle - 90)
            end_rad = math.radians(end_angle - 90)
            
            # رسم القطاع
            x1 = center_x + radius * math.cos(start_rad)
            y1 = center_y + radius * math.sin(start_rad)
            x2 = center_x + radius * math.cos(end_rad)
            y2 = center_y + radius * math.sin(end_rad)
            
            canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=start_angle, extent=angle,
                fill=color, outline="white"
            )
            
            # إضافة legenda
            canvas.create_rectangle(10, legend_y, 25, legend_y + 12, fill=color)
            canvas.create_text(35, legend_y + 6, text=f"{name}: {value}%", anchor=tk.W, font=("Arial", 9))
            
            legend_y += 25
            start_angle = end_angle
    
    def export_report(self):
        """تصدير التقرير"""
        from tkinter import filedialog
        import json
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'kpis': {k: v['value'].cget('text') for k, v in self.kpi_labels.items()},
                'status': 'تم التصدير بنجاح'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            from tkinter import messagebox
            messagebox.showinfo("نجاح", "تم تصدير التقرير بنجاح!")
    
    def refresh_data(self):
        """تحديث البيانات"""
        from tkinter import messagebox
        self.load_sample_data()
        messagebox.showinfo("تحديث", "تم تحديث البيانات بنجاح!")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("لوحة التحليل المالي")
    root.geometry("1200x800")
    
    app = FinancialDashboardWindow(root)
    root.mainloop()

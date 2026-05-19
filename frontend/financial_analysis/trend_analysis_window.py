"""
نافذة تحليل الاتجاهات المالية
Financial Trend Analysis Window
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List
from datetime import datetime


class TrendAnalysisWindow:
    """نافذة تحليل الاتجاهات المالية عبر الزمن"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_trend_data()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # العنوان وأزرار التحكم
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            title_frame,
            text="📈 تحليل الاتجاهات المالية",
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)
        
        control_frame = ttk.Frame(title_frame)
        control_frame.pack(side=tk.RIGHT)
        
        ttk.Label(control_frame, text="فترة التحليل:").pack(side=tk.LEFT, padx=5)
        
        self.period_var = tk.StringVar(value="5 سنوات")
        period_combo = ttk.Combobox(
            control_frame,
            textvariable=self.period_var,
            values=["سنة واحدة", "3 سنوات", "5 سنوات", "10 سنوات"],
            state="readonly",
            width=15
        )
        period_combo.pack(side=tk.LEFT, padx=5)
        period_combo.bind("<<ComboboxSelected>>", self.on_period_change)
        
        ttk.Button(
            control_frame,
            text="🔄 تحديث",
            command=self.refresh_data
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="📤 تصدير",
            command=self.export_trends
        ).pack(side=tk.LEFT, padx=5)
        
        # تبويبات التحليل
        tabs = ttk.Notebook(self.frame)
        tabs.pack(fill=tk.BOTH, expand=True)
        
        # تبويب اتجاهات الإيرادات
        revenue_tab = ttk.Frame(tabs)
        tabs.add(revenue_tab, text="💰 اتجاهات الإيرادات")
        self.setup_revenue_trend_tab(revenue_tab)
        
        # تبويب اتجاهات المصروفات
        expenses_tab = ttk.Frame(tabs)
        tabs.add(expenses_tab, text="📉 اتجاهات المصروفات")
        self.setup_expenses_trend_tab(expenses_tab)
        
        # تبويب اتجاهات الأرباح
        profits_tab = ttk.Frame(tabs)
        tabs.add(profits_tab, text="📊 اتجاهات الأرباح")
        self.setup_profits_trend_tab(profits_tab)
        
        # تبويب المؤشرات المركبة
        indicators_tab = ttk.Frame(tabs)
        tabs.add(indicators_tab, text="🎯 المؤشرات المركبة")
        self.setup_indicators_tab(indicators_tab)
    
    def setup_revenue_trend_tab(self, parent):
        """إعداد تبويب اتجاهات الإيرادات"""
        # إطار الرسم البياني
        chart_frame = ttk.LabelFrame(parent, text="الرسم البياني للإيرادات", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.revenue_canvas = tk.Canvas(chart_frame, bg="white", height=350)
        self.revenue_canvas.pack(fill=tk.BOTH, expand=True)
        
        # جدول البيانات
        table_frame = ttk.LabelFrame(parent, text="بيانات الإيرادات التفصيلية", padding=10)
        table_frame.pack(fill=tk.X, pady=(0, 10))
        
        columns = ("year", "revenue", "growth", "growth_rate", "trend")
        
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        
        tree.heading("year", text="السنة")
        tree.heading("revenue", text="الإيرادات")
        tree.heading("growth", text="النمو")
        tree.heading("growth_rate", text="معدل النمو")
        tree.heading("trend", text="الاتجاه")
        
        tree.column("year", width=100, anchor=tk.CENTER)
        tree.column("revenue", width=150, anchor=tk.E)
        tree.column("growth", width=120, anchor=tk.E)
        tree.column("growth_rate", width=100, anchor=tk.E)
        tree.column("trend", width=100, anchor=tk.CENTER)
        
        # بيانات الإيرادات
        revenue_data = [
            ("2020", "10,500,000", "+800,000", "+8.2%", "📈 صعودي"),
            ("2021", "12,200,000", "+1,700,000", "+16.2%", "📈 صعودي قوي"),
            ("2022", "14,000,000", "+1,800,000", "+14.8%", "📈 صعودي"),
            ("2023", "15,750,000", "+1,750,000", "+12.5%", "📈 صعودي"),
            ("2024", "17,500,000", "+1,750,000", "+11.1%", "📈 مستقر")
        ]
        
        for data in revenue_data:
            tree.insert("", tk.END, values=data)
        
        tree.pack(fill=tk.X)
        
        # ملخص التحليل
        summary_frame = ttk.LabelFrame(parent, text="ملخص تحليل الإيرادات", padding=10)
        summary_frame.pack(fill=tk.X)
        
        summary_text = """
        ✅ اتجاه الإيرادات: نمو مستمر ومستقر على مدى 5 سنوات
        📊 متوسط معدل النمو السنوي (CAGR): 13.7%
        🎯 أعلى سنة نمو: 2021 (+16.2%)
        ⚠️ ملاحظة: تباطؤ طفيف في معدل النمو آخر سنتين
        💡 توصية: التركيز على فتح أسواق جديدة لتعزيز النمو
        """
        
        ttk.Label(summary_frame, text=summary_text, justify=tk.RIGHT, font=("Arial", 10)).pack(anchor=tk.W)
    
    def setup_expenses_trend_tab(self, parent):
        """إعداد تبويب اتجاهات المصروفات"""
        chart_frame = ttk.LabelFrame(parent, text="الرسم البياني للمصروفات", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.expenses_canvas = tk.Canvas(chart_frame, bg="white", height=350)
        self.expenses_canvas.pack(fill=tk.BOTH, expand=True)
        
        table_frame = ttk.LabelFrame(parent, text="بيانات المصروفات التفصيلية", padding=10)
        table_frame.pack(fill=tk.X, pady=(0, 10))
        
        columns = ("year", "total_expenses", "operating_exp", "admin_exp", "trend")
        
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        
        tree.heading("year", text="السنة")
        tree.heading("total_expenses", text="إجمالي المصروفات")
        tree.heading("operating_exp", text="مصروفات تشغيلية")
        tree.heading("admin_exp", text="مصروفات إدارية")
        tree.heading("trend", text="الاتجاه")
        
        tree.column("year", width=100, anchor=tk.CENTER)
        tree.column("total_expenses", width=140, anchor=tk.E)
        tree.column("operating_exp", width=130, anchor=tk.E)
        tree.column("admin_exp", width=120, anchor=tk.E)
        tree.column("trend", width=120, anchor=tk.CENTER)
        
        expenses_data = [
            ("2020", "7,200,000", "4,800,000", "2,400,000", "📊 مستقر"),
            ("2021", "8,500,000", "5,600,000", "2,900,000", "⬆️ ارتفاع"),
            ("2022", "9,800,000", "6,500,000", "3,300,000", "⬆️ ارتفاع معتدل"),
            ("2023", "11,200,000", "7,400,000", "3,800,000", "⬆️ ارتفاع"),
            ("2024", "12,600,000", "8,300,000", "4,300,000", "📊 تباطؤ")
        ]
        
        for data in expenses_data:
            tree.insert("", tk.END, values=data)
        
        tree.pack(fill=tk.X)
        
        summary_frame = ttk.LabelFrame(parent, text="ملخص تحليل المصروفات", padding=10)
        summary_frame.pack(fill=tk.X)
        
        summary_text = """
        ⚠️ اتجاه المصروفات: ارتفاع متواصل يفوق نمو الإيرادات في بعض السنوات
        📊 متوسط معدل نمو المصروفات: 14.8%
        💡 توصية: مراجعة هيكل المصروفات وتحسين الكفاءة التشغيلية
        ✅ نقطة إيجابية: تباطؤ نمو المصروفات في آخر سنة
        """
        
        ttk.Label(summary_frame, text=summary_text, justify=tk.RIGHT, font=("Arial", 10)).pack(anchor=tk.W)
    
    def setup_profits_trend_tab(self, parent):
        """إعداد تبويب اتجاهات الأرباح"""
        chart_frame = ttk.LabelFrame(parent, text="الرسم البياني للأرباح", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.profits_canvas = tk.Canvas(chart_frame, bg="white", height=350)
        self.profits_canvas.pack(fill=tk.BOTH, expand=True)
        
        table_frame = ttk.LabelFrame(parent, text="بيانات الأرباح التفصيلية", padding=10)
        table_frame.pack(fill=tk.X, pady=(0, 10))
        
        columns = ("year", "gross_profit", "operating_profit", "net_profit", "margin")
        
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        
        tree.heading("year", text="السنة")
        tree.heading("gross_profit", text="إجمالي الربح")
        tree.heading("operating_profit", text="الربح التشغيلي")
        tree.heading("net_profit", text="صافي الربح")
        tree.heading("margin", text="هامش الصافي")
        
        tree.column("year", width=100, anchor=tk.CENTER)
        tree.column("gross_profit", width=130, anchor=tk.E)
        tree.column("operating_profit", width=130, anchor=tk.E)
        tree.column("net_profit", width=120, anchor=tk.E)
        tree.column("margin", width=100, anchor=tk.E)
        
        profits_data = [
            ("2020", "3,300,000", "1,800,000", "1,350,000", "12.9%"),
            ("2021", "3,700,000", "2,100,000", "1,620,000", "13.3%"),
            ("2022", "4,200,000", "2,450,000", "1,890,000", "13.5%"),
            ("2023", "4,550,000", "2,750,000", "2,100,000", "13.3%"),
            ("2024", "4,900,000", "3,100,000", "2,340,000", "13.4%")
        ]
        
        for data in profits_data:
            tree.insert("", tk.END, values=data)
        
        tree.pack(fill=tk.X)
        
        summary_frame = ttk.LabelFrame(parent, text="ملخص تحليل الأرباح", padding=10)
        summary_frame.pack(fill=tk.X)
        
        summary_text = """
        ✅ اتجاه الأرباح: نمو مستقر ومتوافق مع نمو الإيرادات
        📊 متوسط معدل نمو صافي الربح: 14.6%
        🎯 استقرار هامش صافي الربح: ~13.4% (كفاءة تشغيلية جيدة)
        💡 توصية: الحفاظ على مستويات الرقابة على التكاليف
        """
        
        ttk.Label(summary_frame, text=summary_text, justify=tk.RIGHT, font=("Arial", 10)).pack(anchor=tk.W)
    
    def setup_indicators_tab(self, parent):
        """إعداد تبويب المؤشرات المركبة"""
        # مؤشرات الأداء الرئيسية عبر السنوات
        kpi_frame = ttk.LabelFrame(parent, text="المؤشرات المالية المركبة", padding=10)
        kpi_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("indicator", "y2020", "y2021", "y2022", "y2023", "y2024", "trend")
        
        tree = ttk.Treeview(kpi_frame, columns=columns, show="headings", height=10)
        
        tree.heading("indicator", text="المؤشر")
        tree.heading("y2020", text="2020")
        tree.heading("y2021", text="2021")
        tree.heading("y2022", text="2022")
        tree.heading("y2023", text="2023")
        tree.heading("y2024", text="2024")
        tree.heading("trend", text="الاتجاه العام")
        
        tree.column("indicator", width=180)
        tree.column("y2020", width=80, anchor=tk.E)
        tree.column("y2021", width=80, anchor=tk.E)
        tree.column("y2022", width=80, anchor=tk.E)
        tree.column("y2023", width=80, anchor=tk.E)
        tree.column("y2024", width=80, anchor=tk.E)
        tree.column("trend", width=100, anchor=tk.CENTER)
        
        indicators_data = [
            ("هامش الربح الإجمالي %", "31.4%", "30.3%", "30.0%", "28.9%", "28.0%", "📉 تنازلي طفيف"),
            ("هامش الربح التشغيلي %", "17.1%", "17.2%", "17.5%", "17.5%", "17.7%", "📈 مستقر"),
            ("هامش صافي الربح %", "12.9%", "13.3%", "13.5%", "13.3%", "13.4%", "➡️ مستقر"),
            ("العائد على الأصول %", "4.2%", "4.6%", "4.9%", "5.1%", "5.2%", "📈 تصاعدي"),
            ("العائد على حقوق الملكية %", "7.1%", "7.6%", "8.1%", "8.5%", "8.9%", "📈 تصاعدي"),
            ("نسبة التداول", "2.2", "2.3", "2.4", "2.5", "2.5", "➡️ مستقر"),
            ("نسبة الدين للأصول %", "48.5%", "46.2%", "44.1%", "42.5%", "41.8%", "📉 تحسن"),
            ("دوران المخزون (مرات)", "9.5", "10.2", "11.0", "11.8", "12.2%", "📈 تحسن")
        ]
        
        for data in indicators_data:
            tree.insert("", tk.END, values=data)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # تقييم عام
        evaluation_frame = ttk.LabelFrame(parent, text="التقييم العام للاتجاهات", padding=10)
        evaluation_frame.pack(fill=tk.X, pady=(10, 0))
        
        evaluation_text = """
        🎯 التقييم الشامل: إيجابي
        
        ✅ نقاط القوة:
        • نمو مستمر في الإيرادات والأرباح
        • تحسين في كفاءة استخدام الأصول
        • انخفاض نسبة المديونية
        • استقرار هوامش الربح
        
        ⚠️ مجالات التحسين:
        • تراجع طفيف في هامش الربح الإجمالي
        • نمو المصروفات يحتاج مراقبة
        
        💡 التوصيات الاستراتيجية:
        • الاستمرار في سياسة النمو الحالية
        • مراجعة استراتيجية التسعير
        • تحسين الكفاءة التشغيلية
        """
        
        ttk.Label(evaluation_frame, text=evaluation_text, justify=tk.RIGHT, font=("Arial", 10)).pack(anchor=tk.W)
    
    def load_trend_data(self):
        """تحميل بيانات الاتجاهات"""
        self.draw_revenue_chart()
        self.draw_expenses_chart()
        self.draw_profits_chart()
    
    def draw_revenue_chart(self):
        """رسم مخطط الإيرادات"""
        canvas = self.revenue_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width() or 700
        height = canvas.winfo_height() or 350
        
        revenues = [10500000, 12200000, 14000000, 15750000, 17500000]
        years = ["2020", "2021", "2022", "2023", "2024"]
        
        margin_left = 80
        margin_right = 20
        margin_top = 20
        margin_bottom = 50
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom
        
        max_val = max(revenues) * 1.1
        min_val = min(revenues) * 0.9
        
        # رسم المحاور
        canvas.create_line(margin_left, margin_top, margin_left, height - margin_bottom, width=2)
        canvas.create_line(margin_left, height - margin_bottom, width - margin_right, height - margin_bottom, width=2)
        
        # رسم الخط
        points = []
        for i, rev in enumerate(revenues):
            x = margin_left + (i / (len(revenues) - 1)) * chart_width
            y = height - margin_bottom - ((rev - min_val) / (max_val - min_val)) * chart_height
            points.append((x, y))
        
        for i in range(len(points) - 1):
            canvas.create_line(
                points[i][0], points[i][1],
                points[i+1][0], points[i+1][1],
                fill="#4CAF50", width=3
            )
        
        for x, y in points:
            canvas.create_oval(x-5, y-5, x+5, y+5, fill="#4CAF50", outline="white")
            canvas.create_text(x, y - 15, text=f"{int(revenues[points.index((x,y))]/1000000)}M", font=("Arial", 9))
        
        for i, year in enumerate(years):
            x = margin_left + (i / (len(years) - 1)) * chart_width
            canvas.create_text(x, height - margin_bottom + 20, text=year, font=("Arial", 10, "bold"))
    
    def draw_expenses_chart(self):
        """رسم مخطط المصروفات"""
        canvas = self.expenses_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width() or 700
        height = canvas.winfo_height() or 350
        
        expenses = [7200000, 8500000, 9800000, 11200000, 12600000]
        years = ["2020", "2021", "2022", "2023", "2024"]
        
        margin_left = 80
        margin_right = 20
        margin_top = 20
        margin_bottom = 50
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom
        
        max_val = max(expenses) * 1.1
        
        # رسم المحاور
        canvas.create_line(margin_left, margin_top, margin_left, height - margin_bottom, width=2)
        canvas.create_line(margin_left, height - margin_bottom, width - margin_right, height - margin_bottom, width=2)
        
        points = []
        for i, exp in enumerate(expenses):
            x = margin_left + (i / (len(expenses) - 1)) * chart_width
            y = height - margin_bottom - (exp / max_val) * chart_height
            points.append((x, y))
        
        for i in range(len(points) - 1):
            canvas.create_line(
                points[i][0], points[i][1],
                points[i+1][0], points[i+1][1],
                fill="#f44336", width=3
            )
        
        for x, y in points:
            canvas.create_oval(x-5, y-5, x+5, y+5, fill="#f44336", outline="white")
        
        for i, year in enumerate(years):
            x = margin_left + (i / (len(years) - 1)) * chart_width
            canvas.create_text(x, height - margin_bottom + 20, text=year, font=("Arial", 10, "bold"))
    
    def draw_profits_chart(self):
        """رسم مخطط الأرباح"""
        canvas = self.profits_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width() or 700
        height = canvas.winfo_height() or 350
        
        profits = [1350000, 1620000, 1890000, 2100000, 2340000]
        years = ["2020", "2021", "2022", "2023", "2024"]
        
        margin_left = 80
        margin_right = 20
        margin_top = 20
        margin_bottom = 50
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom
        
        max_val = max(profits) * 1.1
        
        canvas.create_line(margin_left, margin_top, margin_left, height - margin_bottom, width=2)
        canvas.create_line(margin_left, height - margin_bottom, width - margin_right, height - margin_bottom, width=2)
        
        points = []
        for i, profit in enumerate(profits):
            x = margin_left + (i / (len(profits) - 1)) * chart_width
            y = height - margin_bottom - (profit / max_val) * chart_height
            points.append((x, y))
        
        for i in range(len(points) - 1):
            canvas.create_line(
                points[i][0], points[i][1],
                points[i+1][0], points[i+1][1],
                fill="#2196F3", width=3
            )
        
        for x, y in points:
            canvas.create_oval(x-5, y-5, x+5, y+5, fill="#2196F3", outline="white")
        
        for i, year in enumerate(years):
            x = margin_left + (i / (len(years) - 1)) * chart_width
            canvas.create_text(x, height - margin_bottom + 20, text=year, font=("Arial", 10, "bold"))
    
    def on_period_change(self, event):
        """عند تغيير فترة التحليل"""
        self.refresh_data()
    
    def refresh_data(self):
        """تحديث البيانات"""
        self.load_trend_data()
        messagebox.showinfo("تحديث", "تم تحديث بيانات الاتجاهات")
    
    def export_trends(self):
        """تصدير تحليل الاتجاهات"""
        from tkinter import filedialog
        import json
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'report_type': 'trend_analysis',
                'period': self.period_var.get(),
                'status': 'تم التصدير بنجاح'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("نجاح", "تم تصدير تحليل الاتجاهات بنجاح!")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("تحليل الاتجاهات المالية")
    root.geometry("1200x900")
    
    app = TrendAnalysisWindow(root)
    root.mainloop()

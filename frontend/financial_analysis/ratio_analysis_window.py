"""
نافذة تحليل النسب المالية
Financial Ratio Analysis Window
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List


class RatioAnalysisWindow:
    """نافذة تحليل النسب المالية"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_ratio_data()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # العنوان
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            title_frame,
            text="📊 تحليل النسب المالية",
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            title_frame,
            text="📤 تصدير التحليل",
            command=self.export_analysis
        ).pack(side=tk.RIGHT)
        
        # تبويبات أنواع النسب
        tabs = ttk.Notebook(self.frame)
        tabs.pack(fill=tk.BOTH, expand=True)
        
        # تبويب نسب السيولة
        liquidity_tab = ttk.Frame(tabs)
        tabs.add(liquidity_tab, text="💧 نسب السيولة")
        self.setup_liquidity_tab(liquidity_tab)
        
        # تبويب نسب الربحية
        profitability_tab = ttk.Frame(tabs)
        tabs.add(profitability_tab, text="💰 نسب الربحية")
        self.setup_profitability_tab(profitability_tab)
        
        # تبويب نسب الكفاءة
        efficiency_tab = ttk.Frame(tabs)
        tabs.add(efficiency_tab, text="⚡ نسب الكفاءة")
        self.setup_efficiency_tab(efficiency_tab)
        
        # تبويب نسب الملاءة
        solvency_tab = ttk.Frame(tabs)
        tabs.add(solvency_tab, text="🏛️ نسب الملاءة")
        self.setup_solvency_tab(solvency_tab)
        
        # تبويب نسب التقييم
        valuation_tab = ttk.Frame(tabs)
        tabs.add(valuation_tab, text="📈 نسب التقييم")
        self.setup_valuation_tab(valuation_tab)
    
    def setup_liquidity_tab(self, parent):
        """إعداد تبويب نسب السيولة"""
        # معلومات توضيحية
        info_label = ttk.Label(
            parent,
            text="تقيس قدرة الشركة على الوفاء بالتزاماتها قصيرة الأجل",
            font=("Arial", 10),
            foreground="#666"
        )
        info_label.pack(pady=10)
        
        # جدول النسب
        columns = ("ratio", "value", "industry_avg", "status", "interpretation")
        
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        
        tree.heading("ratio", text="النسبة")
        tree.heading("value", text="القيمة")
        tree.heading("industry_avg", text="متوسط القطاع")
        tree.heading("status", text="الحالة")
        tree.heading("interpretation", text="التفسير")
        
        tree.column("ratio", width=200)
        tree.column("value", width=100, anchor=tk.E)
        tree.column("industry_avg", width=100, anchor=tk.E)
        tree.column("status", width=80, anchor=tk.CENTER)
        tree.column("interpretation", width=300)
        
        # بيانات نسب السيولة
        liquidity_ratios = [
            ("نسبة التداول", "2.5", "2.0", "✅ جيد", "الشركة قادرة على تغطية التزاماتها 2.5 مرة"),
            ("نسبة السيولة السريعة", "1.8", "1.0", "✅ ممتاز", "سيولة عالية جداً بدون المخزون"),
            ("نسبة النقدية", "0.9", "0.5", "✅ ممتاز", "نقد كافٍ لتغطية 90% من الالتزامات"),
            ("رأس المال العامل", "4,500,000", "3,000,000", "✅ جيد", "فائض في الأصول المتداولة"),
            ("فترة التحصيل", "45 يوم", "60 يوم", "✅ جيد", "تحصيل سريع من العملاء"),
            ("فترة المخزون", "30 يوم", "45 يوم", "✅ جيد", "دوران سريع للمخزون")
        ]
        
        for ratio in liquidity_ratios:
            tree.insert("", tk.END, values=ratio)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_profitability_tab(self, parent):
        """إعداد تبويب نسب الربحية"""
        info_label = ttk.Label(
            parent,
            text="تقيس قدرة الشركة على تحقيق الأرباح",
            font=("Arial", 10),
            foreground="#666"
        )
        info_label.pack(pady=10)
        
        columns = ("ratio", "value", "industry_avg", "status", "interpretation")
        
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        
        tree.heading("ratio", text="النسبة")
        tree.heading("value", text="القيمة")
        tree.heading("industry_avg", text="متوسط القطاع")
        tree.heading("status", text="الحالة")
        tree.heading("interpretation", text="التفسير")
        
        tree.column("ratio", width=200)
        tree.column("value", width=100, anchor=tk.E)
        tree.column("industry_avg", width=100, anchor=tk.E)
        tree.column("status", width=80, anchor=tk.CENTER)
        tree.column("interpretation", width=300)
        
        profitability_ratios = [
            ("هامش الربح الإجمالي", "40.0%", "35.0%", "✅ جيد", "ربحية جيدة من العمليات الأساسية"),
            ("هامش الربح التشغيلي", "19.7%", "15.0%", "✅ ممتاز", "كفاءة تشغيلية عالية"),
            ("هامش صافي الربح", "14.9%", "12.0%", "✅ جيد", "ربحية صافية قوية"),
            ("العائد على الأصول (ROA)", "5.2%", "4.5%", "✅ جيد", "استخدام فعال للأصول"),
            ("العائد على حقوق الملكية (ROE)", "8.9%", "7.5%", "✅ جيد", "عائد جيد للمساهمين"),
            ("العائد على رأس المال المستثمر (ROIC)", "12.3%", "10.0%", "✅ ممتاز", "كفاءة في استخدام رأس المال")
        ]
        
        for ratio in profitability_ratios:
            tree.insert("", tk.END, values=ratio)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_efficiency_tab(self, parent):
        """إعداد تبويب نسب الكفاءة"""
        info_label = ttk.Label(
            parent,
            text="تقيس كفاءة استخدام الشركة لأصولها",
            font=("Arial", 10),
            foreground="#666"
        )
        info_label.pack(pady=10)
        
        columns = ("ratio", "value", "industry_avg", "status", "interpretation")
        
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        
        tree.heading("ratio", text="النسبة")
        tree.heading("value", text="القيمة")
        tree.heading("industry_avg", text="متوسط القطاع")
        tree.heading("status", text="الحالة")
        tree.heading("interpretation", text="التفسير")
        
        tree.column("ratio", width=200)
        tree.column("value", width=100, anchor=tk.E)
        tree.column("industry_avg", width=100, anchor=tk.E)
        tree.column("status", width=80, anchor=tk.CENTER)
        tree.column("interpretation", width=300)
        
        efficiency_ratios = [
            ("معدل دوران المخزون", "12.2 مرة", "8.0 مرة", "✅ ممتاز", "دوران سريع للمخزون"),
            ("معدل دوران الأصول الثابتة", "3.5 مرة", "2.5 مرة", "✅ جيد", "استخدام فعال للأصول"),
            ("معدل دوران إجمالي الأصول", "0.35 مرة", "0.30 مرة", "✅ جيد", "كفاءة في استخدام الأصول"),
            ("معدل دوران حسابات القبض", "8.1 مرة", "6.0 مرة", "✅ ممتاز", "تحصيل سريع من العملاء"),
            ("دورة تحويل النقد", "55 يوم", "75 يوم", "✅ ممتاز", "إدارة فعالة لرأس المال العامل"),
            ("أيام المبيعات معلقة", "45 يوم", "60 يوم", "✅ جيد", "فترة تحصيل معقولة")
        ]
        
        for ratio in efficiency_ratios:
            tree.insert("", tk.END, values=ratio)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_solvency_tab(self, parent):
        """إعداد تبويب نسب الملاءة"""
        info_label = ttk.Label(
            parent,
            text="تقيس قدرة الشركة على الوفاء بالتزاماتها طويلة الأجل",
            font=("Arial", 10),
            foreground="#666"
        )
        info_label.pack(pady=10)
        
        columns = ("ratio", "value", "industry_avg", "status", "interpretation")
        
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        
        tree.heading("ratio", text="النسبة")
        tree.heading("value", text="القيمة")
        tree.heading("industry_avg", text="متوسط القطاع")
        tree.heading("status", text="الحالة")
        tree.heading("interpretation", text="التفسير")
        
        tree.column("ratio", width=200)
        tree.column("value", width=100, anchor=tk.E)
        tree.column("industry_avg", width=100, anchor=tk.E)
        tree.column("status", width=80, anchor=tk.CENTER)
        tree.column("interpretation", width=300)
        
        solvency_ratios = [
            ("نسبة الدين إلى الأصول", "41.8%", "50.0%", "✅ ممتاز", "هيكل تمويلي محافظ"),
            ("نسبة الدين إلى حقوق الملكية", "71.9%", "100.0%", "✅ جيد", "اعتماد معتدل على الديون"),
            ("نسبة حقوق الملكية", "58.2%", "50.0%", "✅ ممتاز", "قاعدة رأسمال قوية"),
            ("نسبة تغطية الفائدة", "7.8 مرة", "5.0 مرة", "✅ ممتاز", "قدرة عالية على سداد الفائدة"),
            ("نسبة تغطية خدمة الدين", "4.5 مرة", "3.0 مرة", "✅ جيد", "قدرة جيدة على سداد الديون"),
            ("الرافعة المالية", "1.72", "2.0", "✅ جيد", "رافعة مالية معقولة")
        ]
        
        for ratio in solvency_ratios:
            tree.insert("", tk.END, values=ratio)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_valuation_tab(self, parent):
        """إعداد تبويب نسب التقييم"""
        info_label = ttk.Label(
            parent,
            text="تستخدم لتقييم قيمة الشركة وأسهمها",
            font=("Arial", 10),
            foreground="#666"
        )
        info_label.pack(pady=10)
        
        columns = ("ratio", "value", "industry_avg", "status", "interpretation")
        
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        
        tree.heading("ratio", text="النسبة")
        tree.heading("value", text="القيمة")
        tree.heading("industry_avg", text="متوسط القطاع")
        tree.heading("status", text="الحالة")
        tree.heading("interpretation", text="التفسير")
        
        tree.column("ratio", width=200)
        tree.column("value", width=100, anchor=tk.E)
        tree.column("industry_avg", width=100, anchor=tk.E)
        tree.column("status", width=80, anchor=tk.CENTER)
        tree.column("interpretation", width=300)
        
        valuation_ratios = [
            ("نسبة السعر إلى الربح (P/E)", "18.5", "15.0", "⚠️ مرتفع", "السهم قد يكون مقيم بأعلى من قيمته"),
            ("نسبة السعر إلى القيمة الدفترية (P/B)", "2.8", "2.0", "⚠️ مرتفع", "تقييم أعلى من القيمة الدفترية"),
            ("نسبة السعر إلى المبيعات (P/S)", "3.2", "2.5", "⚠️ مرتفع", "تقييم مرتفع بالنسبة للإيرادات"),
            ("العائد على توزيعات الأرباح", "2.5%", "3.0%", "⚠️ منخفض", "عائد توزيعات أقل من المتوسط"),
            ("نسبة السعر إلى التدفق النقدي (P/CF)", "12.3", "10.0", "✅ معقول", "تقييم معقول للتدفق النقدي"),
            ("قيمة المؤسسة إلى EBITDA", "9.5", "8.0", "⚠️ مرتفع", "تقييم مرتفع للقيمة المؤسسية")
        ]
        
        for ratio in valuation_ratios:
            tree.insert("", tk.END, values=ratio)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def load_ratio_data(self):
        """تحميل بيانات النسب (تم التحميل بالفعل في setup)"""
        pass
    
    def export_analysis(self):
        """تصدير تحليل النسب"""
        from tkinter import filedialog
        import json
        from datetime import datetime
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'report_type': 'financial_ratio_analysis',
                'status': 'تم التصدير بنجاح',
                'categories': [
                    'liquidity', 'profitability', 'efficiency', 
                    'solvency', 'valuation'
                ]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("نجاح", "تم تصدير تحليل النسب بنجاح!")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("تحليل النسب المالية")
    root.geometry("1100x700")
    
    app = RatioAnalysisWindow(root)
    root.mainloop()

"""
معالج إنشاء مشروع مراجعة جديد
Create Project Wizard
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Optional
from datetime import datetime


class CreateProjectWizard:
    """معالج خطوة بخطوة لإنشاء مشروع مراجعة جديد"""
    
    def __init__(self, parent, on_complete: Optional[Callable] = None):
        self.parent = parent
        self.on_complete = on_complete
        self.current_step = 0
        self.project_data = {}
        
        self.steps = [
            ("المعلومات الأساسية", self.create_basic_info_frame),
            ("تفاصيل العميل", self.create_client_info_frame),
            ("فريق العمل", self.create_team_frame),
            ("الإعدادات الزمنية", self.create_timeline_frame),
            ("مراجعة وتأكيد", self.create_review_frame)
        ]
        
        self.setup_ui()
        self.show_step(0)
    
    def setup_ui(self):
        """إعداد واجهة المعالج"""
        self.parent.configure(padx=20, pady=20)
        
        # شريط التقدم
        progress_frame = ttk.Frame(self.parent)
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            progress_frame,
            text="إنشاء مشروع مراجعة جديد",
            font=("Arial", 16, "bold")
        ).pack(side=tk.TOP, pady=(0, 10))
        
        # مؤشر الخطوات
        self.step_indicator_frame = ttk.Frame(progress_frame)
        self.step_indicator_frame.pack(fill=tk.X)
        
        self.step_indicators = []
        for i, (step_name, _) in enumerate(self.steps):
            indicator = ttk.Label(
                self.step_indicator_frame,
                text=f"○ {step_name}",
                font=("Arial", 10)
            )
            indicator.pack(side=tk.LEFT, padx=5)
            self.step_indicators.append(indicator)
        
        # فاصل
        ttk.Separator(progress_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # إطار المحتوى
        self.content_frame = ttk.Frame(self.parent)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # أزرار التنقل
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.back_button = ttk.Button(
            button_frame,
            text="⬅️ السابق",
            command=self.previous_step,
            state=tk.DISABLED
        )
        self.back_button.pack(side=tk.LEFT)
        
        self.next_button = ttk.Button(
            button_frame,
            text="التالي ➡️",
            command=self.next_step
        )
        self.next_button.pack(side=tk.RIGHT)
        
        # متغيرات النماذج
        self.basic_vars = {}
        self.client_vars = {}
        self.team_vars = {}
        self.timeline_vars = {}
    
    def show_step(self, step_index: int):
        """عرض خطوة محددة"""
        self.current_step = step_index
        
        # مسح المحتوى الحالي
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # إنشاء محتوى الخطوة الحالية
        _, create_func = self.steps[step_index]
        create_func()
        
        # تحديث مؤشر الخطوات
        self.update_step_indicators()
        
        # تحديث حالة الأزرار
        self.back_button.config(state=tk.NORMAL if step_index > 0 else tk.DISABLED)
        self.next_button.config(text="✅ إنشاء" if step_index == len(self.steps) - 1 else "التالي ➡️")
    
    def update_step_indicators(self):
        """تحديث مؤشرات الخطوات"""
        for i, indicator in enumerate(self.step_indicators):
            if i < self.current_step:
                indicator.config(text=f"● {self.steps[i][0]}", foreground="green")
            elif i == self.current_step:
                indicator.config(text=f"◉ {self.steps[i][0]}", foreground="blue", font=("Arial", 10, "bold"))
            else:
                indicator.config(text=f"○ {self.steps[i][0]}", foreground="gray")
    
    def create_basic_info_frame(self):
        """إنشاء إطار المعلومات الأساسية"""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(
            frame,
            text="المعلومات الأساسية للمشروع",
            font=("Arial", 14, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # اسم المشروع
        ttk.Label(frame, text="* اسم المشروع:").pack(anchor=tk.W, pady=5)
        self.basic_vars["name"] = tk.StringVar()
        name_entry = ttk.Entry(frame, textvariable=self.basic_vars["name"], width=60)
        name_entry.pack(fill=tk.X, pady=5)
        
        # وصف المشروع
        ttk.Label(frame, text="وصف المشروع:").pack(anchor=tk.W, pady=5)
        self.basic_vars["description"] = tk.StringVar()
        desc_entry = ttk.Entry(frame, textvariable=self.basic_vars["description"], width=60)
        desc_entry.pack(fill=tk.X, pady=5)
        
        # نوع المراجعة
        ttk.Label(frame, text="* نوع المراجعة:").pack(anchor=tk.W, pady=5)
        self.basic_vars["audit_type"] = tk.StringVar()
        audit_combo = ttk.Combobox(
            frame,
            textvariable=self.basic_vars["audit_type"],
            values=[
                "مراجعة القوائم المالية",
                "مراجعة ضريبية",
                "مراجعة داخلية",
                "فحص امتثال",
                "مراجعة تشغيلية",
                "مراجعة خاصة"
            ],
            state="readonly",
            width=57
        )
        audit_combo.pack(pady=5)
        
        # الأولوية
        ttk.Label(frame, text="الأولوية:").pack(anchor=tk.W, pady=5)
        self.basic_vars["priority"] = tk.StringVar(value="متوسطة")
        priority_frame = ttk.Frame(frame)
        priority_frame.pack(anchor=tk.W, pady=5)
        
        for priority in ["منخفضة", "متوسطة", "عالية", "عاجلة"]:
            ttk.Radiobutton(
                priority_frame,
                text=priority,
                variable=self.basic_vars["priority"],
                value=priority
            ).pack(side=tk.LEFT, padx=10)
    
    def create_client_info_frame(self):
        """إنشاء إطار معلومات العميل"""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(
            frame,
            text="تفاصيل العميل",
            font=("Arial", 14, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # اسم العميل
        ttk.Label(frame, text="* اسم العميل/الشركة:").pack(anchor=tk.W, pady=5)
        self.client_vars["client_name"] = tk.StringVar()
        client_entry = ttk.Entry(frame, textvariable=self.client_vars["client_name"], width=60)
        client_entry.pack(fill=tk.X, pady=5)
        
        # القطاع
        ttk.Label(frame, text="القطاع الصناعي:").pack(anchor=tk.W, pady=5)
        self.client_vars["industry"] = tk.StringVar()
        industry_combo = ttk.Combobox(
            frame,
            textvariable=self.client_vars["industry"],
            values=[
                "تقنية",
                "صناعة",
                "خدمات مالية",
                "رعاية صحية",
                "تجارة",
                "بناء وتشيد",
                "طاقة",
                "أخرى"
            ],
            state="readonly",
            width=57
        )
        industry_combo.pack(pady=5)
        
        # حجم الشركة
        ttk.Label(frame, text="حجم الشركة:").pack(anchor=tk.W, pady=5)
        self.client_vars["company_size"] = tk.StringVar()
        size_combo = ttk.Combobox(
            frame,
            textvariable=self.client_vars["company_size"],
            values=["صغيرة", "متوسطة", "كبيرة", "شركات متعددة الجنسيات"],
            state="readonly",
            width=57
        )
        size_combo.pack(pady=5)
        
        # معلومات الاتصال
        ttk.Label(frame, text="الشخص المسؤول:").pack(anchor=tk.W, pady=5)
        self.client_vars["contact_person"] = tk.StringVar()
        contact_entry = ttk.Entry(frame, textvariable=self.client_vars["contact_person"], width=60)
        contact_entry.pack(fill=tk.X, pady=5)
        
        # البريد الإلكتروني
        ttk.Label(frame, text="البريد الإلكتروني:").pack(anchor=tk.W, pady=5)
        self.client_vars["email"] = tk.StringVar()
        email_entry = ttk.Entry(frame, textvariable=self.client_vars["email"], width=60)
        email_entry.pack(fill=tk.X, pady=5)
    
    def create_team_frame(self):
        """إنشاء إطار فريق العمل"""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(
            frame,
            text="فريق العمل",
            font=("Arial", 14, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # مدير المشروع
        ttk.Label(frame, text="* مدير المشروع:").pack(anchor=tk.W, pady=5)
        self.team_vars["manager"] = tk.StringVar()
        manager_entry = ttk.Entry(frame, textvariable=self.team_vars["manager"], width=60)
        manager_entry.pack(fill=tk.X, pady=5)
        
        # أعضاء الفريق
        ttk.Label(frame, text="أعضاء الفريق (افصل بينهم بفاصلة):").pack(anchor=tk.W, pady=5)
        self.team_vars["members"] = tk.StringVar()
        members_entry = ttk.Entry(frame, textvariable=self.team_vars["members"], width=60)
        members_entry.pack(fill=tk.X, pady=5)
        
        # خبراء متخصصون
        ttk.Label(frame, text="خبراء متخصصون (إن وجد):").pack(anchor=tk.W, pady=5)
        self.team_vars["experts"] = tk.StringVar()
        experts_entry = ttk.Entry(frame, textvariable=self.team_vars["experts"], width=60)
        experts_entry.pack(fill=tk.X, pady=5)
        
        # ملاحظات إضافية
        ttk.Label(frame, text="ملاحظات حول الفريق:").pack(anchor=tk.W, pady=5)
        self.team_vars["notes"] = tk.StringVar()
        notes_entry = ttk.Entry(frame, textvariable=self.team_vars["notes"], width=60)
        notes_entry.pack(fill=tk.X, pady=5)
    
    def create_timeline_frame(self):
        """إنشاء الإطار الزمني"""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(
            frame,
            text="الإعدادات الزمنية",
            font=("Arial", 14, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # تاريخ البدء
        ttk.Label(frame, text="* تاريخ البدء المتوقع:").pack(anchor=tk.W, pady=5)
        self.timeline_vars["start_date"] = tk.StringVar()
        start_entry = ttk.Entry(frame, textvariable=self.timeline_vars["start_date"], width=60)
        start_entry.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="(الصيغة: YYYY-MM-DD)", font=("Arial", 9)).pack(anchor=tk.W)
        
        # تاريخ الانتهاء
        ttk.Label(frame, text="* تاريخ الانتهاء المتوقع:").pack(anchor=tk.W, pady=5)
        self.timeline_vars["end_date"] = tk.StringVar()
        end_entry = ttk.Entry(frame, textvariable=self.timeline_vars["end_date"], width=60)
        end_entry.pack(fill=tk.X, pady=5)
        
        # المدة المقدرة
        ttk.Label(frame, text="المدة المقدرة (بالأسابيع):").pack(anchor=tk.W, pady=5)
        self.timeline_vars["duration_weeks"] = tk.StringVar()
        duration_entry = ttk.Entry(frame, textvariable=self.timeline_vars["duration_weeks"], width=60)
        duration_entry.pack(fill=tk.X, pady=5)
        
        # مراحل المشروع
        ttk.Label(frame, text="مراحل المشروع الرئيسية:").pack(anchor=tk.W, pady=15)
        
        phases = [
            "التخطيط والتحضير",
            "تقييم المخاطر",
            "اختبار الضوابط",
            "الإجراءات التفصيلية",
            "إعداد التقرير",
            "مراجعة نهائية"
        ]
        
        self.timeline_vars["phases"] = {}
        for phase in phases:
            var = tk.BooleanVar(value=True)
            self.timeline_vars["phases"][phase] = var
            ttk.Checkbutton(frame, text=phase, variable=var).pack(anchor=tk.W, pady=2)
    
    def create_review_frame(self):
        """إنشاء إطار المراجعة والتأكيد"""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(
            frame,
            text="مراجعة وتأكيد البيانات",
            font=("Arial", 14, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # عرض ملخص البيانات
        summary_text = tk.Text(frame, height=25, width=80, wrap=tk.WORD)
        summary_text.pack(fill=tk.BOTH, expand=True)
        
        # تجميع البيانات
        self.collect_data()
        
        summary = "=== ملخص مشروع المراجعة ===\n\n"
        summary += "📋 المعلومات الأساسية:\n"
        summary += f"  • اسم المشروع: {self.project_data.get('name', 'غير محدد')}\n"
        summary += f"  • الوصف: {self.project_data.get('description', 'لا يوجد')}\n"
        summary += f"  • نوع المراجعة: {self.project_data.get('audit_type', 'غير محدد')}\n"
        summary += f"  • الأولوية: {self.project_data.get('priority', 'متوسطة')}\n\n"
        
        summary += "🏢 معلومات العميل:\n"
        summary += f"  • العميل: {self.project_data.get('client_name', 'غير محدد')}\n"
        summary += f"  • القطاع: {self.project_data.get('industry', 'غير محدد')}\n"
        summary += f"  • الحجم: {self.project_data.get('company_size', 'غير محدد')}\n"
        summary += f"  • المسؤول: {self.project_data.get('contact_person', 'غير محدد')}\n"
        summary += f"  • البريد: {self.project_data.get('email', 'غير محدد')}\n\n"
        
        summary += "👥 فريق العمل:\n"
        summary += f"  • المدير: {self.project_data.get('manager', 'غير محدد')}\n"
        summary += f"  • الأعضاء: {self.project_data.get('members', 'غير محدد')}\n"
        summary += f"  • الخبراء: {self.project_data.get('experts', 'لا يوجد')}\n\n"
        
        summary += "📅 الجدول الزمني:\n"
        summary += f"  • تاريخ البدء: {self.project_data.get('start_date', 'غير محدد')}\n"
        summary += f"  • تاريخ الانتهاء: {self.project_data.get('end_date', 'غير محدد')}\n"
        summary += f"  • المدة: {self.project_data.get('duration_weeks', 'غير محدد')} أسبوع\n"
        
        summary_text.insert(tk.END, summary)
        summary_text.config(state=tk.DISABLED)
        
        # تأكيد
        ttk.Label(
            frame,
            text="✓ تأكد من صحة جميع البيانات قبل الإنشاء",
            foreground="blue"
        ).pack(pady=10)
    
    def collect_data(self):
        """تجميع البيانات من جميع الخطوات"""
        self.project_data.update({
            "name": self.basic_vars.get("name", "").get(),
            "description": self.basic_vars.get("description", "").get(),
            "audit_type": self.basic_vars.get("audit_type", "").get(),
            "priority": self.basic_vars.get("priority", "").get(),
            
            "client_name": self.client_vars.get("client_name", "").get(),
            "industry": self.client_vars.get("industry", "").get(),
            "company_size": self.client_vars.get("company_size", "").get(),
            "contact_person": self.client_vars.get("contact_person", "").get(),
            "email": self.client_vars.get("email", "").get(),
            
            "manager": self.team_vars.get("manager", "").get(),
            "members": self.team_vars.get("members", "").get(),
            "experts": self.team_vars.get("experts", "").get(),
            "team_notes": self.team_vars.get("notes", "").get(),
            
            "start_date": self.timeline_vars.get("start_date", "").get(),
            "end_date": self.timeline_vars.get("end_date", "").get(),
            "duration_weeks": self.timeline_vars.get("duration_weeks", "").get(),
            "status": "جديد",
            "progress": 0
        })
    
    def validate_current_step(self) -> bool:
        """التحقق من صحة البيانات في الخطوة الحالية"""
        if self.current_step == 0:
            # التحقق من المعلومات الأساسية
            if not self.basic_vars.get("name", "").get().strip():
                messagebox.showerror("خطأ", "يرجى إدخال اسم المشروع")
                return False
            if not self.basic_vars.get("audit_type", "").get():
                messagebox.showerror("خطأ", "يرجى اختيار نوع المراجعة")
                return False
        
        elif self.current_step == 1:
            # التحقق من معلومات العميل
            if not self.client_vars.get("client_name", "").get().strip():
                messagebox.showerror("خطأ", "يرجى إدخال اسم العميل")
                return False
        
        elif self.current_step == 3:
            # التحقق من الجدول الزمني
            if not self.timeline_vars.get("start_date", "").get().strip():
                messagebox.showerror("خطأ", "يرجى إدخال تاريخ البدء")
                return False
            if not self.timeline_vars.get("end_date", "").get().strip():
                messagebox.showerror("خطأ", "يرجى إدخال تاريخ الانتهاء")
                return False
        
        return True
    
    def next_step(self):
        """الانتقال للخطوة التالية"""
        # التحقق من البيانات
        if not self.validate_current_step():
            return
        
        if self.current_step < len(self.steps) - 1:
            self.show_step(self.current_step + 1)
        else:
            # إنشاء المشروع
            self.create_project()
    
    def previous_step(self):
        """العودة للخطوة السابقة"""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def create_project(self):
        """إنشاء المشروع النهائي"""
        self.collect_data()
        
        # التحقق النهائي
        required_fields = ["name", "audit_type", "client_name", "start_date", "end_date"]
        missing_fields = [f for f in required_fields if not self.project_data.get(f)]
        
        if missing_fields:
            messagebox.showerror(
                "خطأ",
                f"يرجى تعبئة الحقول الإلزامية:\n{', '.join(missing_fields)}"
            )
            return
        
        # إضافة بيانات افتراضية
        self.project_data["id"] = None  # سيتم تعيينه لاحقاً
        self.project_data["created_at"] = datetime.now().isoformat()
        self.project_data["team"] = f"{self.project_data.get('manager', '')}, {self.project_data.get('members', '')}"
        
        # استدعاء دالة الإكمال
        if self.on_complete:
            self.on_complete(self.project_data)
        
        messagebox.showinfo(
            "نجاح",
            f"تم إنشاء مشروع '{self.project_data['name']}' بنجاح!\n\nسيتم نقلك لنافذة تفاصيل المشروع."
        )
        
        self.parent.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("إنشاء مشروع مراجعة جديد")
    root.geometry("900x700")
    
    def on_complete(data):
        print("تم إنشاء المشروع:", data)
    
    wizard = CreateProjectWizard(root, on_complete=on_complete)
    root.mainloop()

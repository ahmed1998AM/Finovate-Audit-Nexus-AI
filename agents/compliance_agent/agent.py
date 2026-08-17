"""
Compliance & Standards AI Agent
وكيل المعايير والقوانين - مراجعة الالتزام بالمعايير المحاسبية والقوانين

المهام:
- مراجعة الالتزام بالمعايير المصرية
- مراجعة الالتزام بـ IFRS/IAS
- مراجعة الالتزام بـ ISA
- مراجعة قوانين الضرائب المصرية
- اقتراح المعالجات الصحيحة
- إصدار التوصيات
"""

import hashlib
from datetime import datetime
from typing import Any, Dict, List


class ComplianceStandardsAgent:
    """وكيل المعايير والامتثال"""

    def __init__(self):
        self.agent_name = "Compliance & Standards Agent"
        self.agent_type = "compliance"
        self.version = "1.0.0"

        # المعايير المدعومة
        self.standards = {
            'egyptian': {
                'name': 'المعايير المحاسبية المصرية',
                'standards': [
                    'معيار المحاسبة المصري 1 - عرض القوائم المالية',
                    'معيار المحاسبة المصري 2 - المخزون',
                    'معيار المحاسبة المصري 3 - قوائم التدفقات النقدية',
                    'معيار المحاسبة المصري 4 - الآثار الضريبية',
                    'معيار المحاسبة المصري 5 - الأصول الثابتة',
                    'معيار المحاسبة المصري 6 - المعاملات المقومة بعملة أجنبية',
                    'معيار المحاسبة المصري 7 - اندماج الأعمال',
                    'معيار المحاسبة المصري 8 - الإهلاك',
                ]
            },
            'ifrs': {
                'name': 'International Financial Reporting Standards',
                'standards': [
                    'IFRS 1 - First-time Adoption',
                    'IFRS 2 - Share-based Payment',
                    'IFRS 3 - Business Combinations',
                    'IFRS 5 - Non-current Assets Held for Sale',
                    'IFRS 7 - Financial Instruments: Disclosures',
                    'IFRS 9 - Financial Instruments',
                    'IFRS 10 - Consolidated Financial Statements',
                    'IFRS 13 - Fair Value Measurement',
                    'IFRS 15 - Revenue from Contracts with Customers',
                    'IFRS 16 - Leases',
                ]
            },
            'isa': {
                'name': 'International Standards on Auditing',
                'standards': [
                    'ISA 200 - Overall Objectives',
                    'ISA 210 - Agreeing the Terms of Audit Engagements',
                    'ISA 220 - Quality Control',
                    'ISA 230 - Audit Documentation',
                    'ISA 240 - Fraud Responsibilities',
                    'ISA 250 - Consideration of Laws and Regulations',
                    'ISA 300 - Planning an Audit',
                    'ISA 315 - Identifying Risks',
                    'ISA 320 - Materiality',
                    'ISA 330 - Responses to Assessed Risks',
                    'ISA 500 - Audit Evidence',
                    'ISA 520 - Analytical Procedures',
                    'ISA 540 - Accounting Estimates',
                    'ISA 570 - Going Concern',
                    'ISA 700 - Forming an Opinion',
                ]
            },
            'tax_egypt': {
                'name': 'قوانين الضرائب المصرية',
                'laws': [
                    'قانون الضريبة على القيمة المضافة رقم 67 لسنة 2016',
                    'قانون ضريبة الدخل رقم 91 لسنة 2005',
                    'قانون الضريبة العقارية رقم 196 لسنة 2008',
                    'قانون الدمغات رقم 113 لسنة 1980',
                    'القانون الموحد للعمل رقم 12 لسنة 2003',
                ],
                'rates': {
                    'vat_standard': 14.0,
                    'vat_reduced': 0.0,
                    'vat_exempt_categories': [
                        'الخدمات الطبية',
                        'الخدمات التعليمية',
                        'النقل العام',
                        'المنتجات البترولية غير المكررة',
                    ],
                    'income_tax_brackets': [
                        {'min': 0, 'max': 15000, 'rate': 0.0},
                        {'min': 15000, 'max': 30000, 'rate': 2.5},
                        {'min': 30000, 'max': 45000, 'rate': 10.0},
                        {'min': 45000, 'max': 60000, 'rate': 15.0},
                        {'min': 60000, 'max': 200000, 'rate': 20.0},
                        {'min': 200000, 'max': 400000, 'rate': 22.5},
                        {'min': 400000, 'max': float('inf'), 'rate': 25.0},
                    ],
                    'withholding_tax': {
                        'dividends': 10.0,
                        'interest': 20.0,
                        'royalties': 20.0,
                        'services': 20.0,
                    }
                }
            }
        }

    def check_compliance(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for analyze_compliance for orchestrator compatibility"""
        return self.analyze_compliance(financial_data)

    def analyze_compliance(self, financial_data: Any) -> Dict[str, Any]:
        """تحليل الالتزام بالمعايير"""
        # تحويل DataFrame إلى dict إذا لزم الأمر
        if hasattr(financial_data, 'to_dict') and not isinstance(financial_data, dict):
            try:
                # Convert to list of dicts
                records = financial_data.to_dict(orient='records')
                # Create a dict structure the agent expects
                new_data = {'transactions': records}
                
                # Try to extract metrics if they are columns
                if hasattr(financial_data, 'columns'):
                    for col in ['current_ratio', 'working_capital', 'debt_to_assets', 'profit_margin']:
                        if col in financial_data.columns and len(financial_data) > 0:
                            new_data[col] = financial_data[col].iloc[0]
                
                financial_data = new_data
            except:
                financial_data = {'transactions': []}
        
        # Ensure it's a dict
        if not isinstance(financial_data, dict):
            financial_data = {'transactions': []}

        report = {
            'agent': self.agent_name,
            'timestamp': datetime.now().isoformat(),
            'analysis_id': hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12],
            'compliance_score': 0.0,
            'findings': [],
            'violations': [],
            'recommendations': [],
            'standards_checked': [],
            'risk_level': 'LOW'
        }

        if not financial_data:
            return report

        total_checks = 0
        passed_checks = 0

        # 1. التحقق من عرض القوائم المالية (Egyptian Standard 1 / IAS 1)
        check_result = self._check_financial_statement_presentation(financial_data)
        report['findings'].append(check_result)
        total_checks += 1
        if check_result['status'] == 'COMPLIANT':
            passed_checks += 1
        else:
            report['violations'].append({
                'standard': 'المعيار المصري 1 / IAS 1',
                'issue': check_result['issue'],
                'severity': check_result.get('severity', 'MEDIUM'),
                'recommendation': check_result.get('recommendation', '')
            })

        # 2. التحقق من المعالجة الضريبية
        check_result = self._check_tax_compliance(financial_data)
        report['findings'].append(check_result)
        total_checks += 1
        if check_result['status'] == 'COMPLIANT':
            passed_checks += 1
        else:
            report['violations'].append({
                'standard': 'قانون الضريبة على القيمة المضافة',
                'issue': check_result['issue'],
                'severity': check_result.get('severity', 'HIGH'),
                'recommendation': check_result.get('recommendation', '')
            })

        # 3. التحقق من معالجة الأصول الثابتة (Egyptian Standard 5 / IAS 16)
        check_result = self._check_fixed_assets_treatment(financial_data)
        report['findings'].append(check_result)
        total_checks += 1
        if check_result['status'] == 'COMPLIANT':
            passed_checks += 1
        else:
            report['violations'].append({
                'standard': 'المعيار المصري 5 / IAS 16',
                'issue': check_result['issue'],
                'severity': check_result.get('severity', 'MEDIUM'),
                'recommendation': check_result.get('recommendation', '')
            })

        # 4. التحقق من الاعتراف بالإيرادات (IFRS 15)
        check_result = self._check_revenue_recognition(financial_data)
        report['findings'].append(check_result)
        total_checks += 1
        if check_result['status'] == 'COMPLIANT':
            passed_checks += 1
        else:
            report['violations'].append({
                'standard': 'IFRS 15 - الإيرادات من عقود العملاء',
                'issue': check_result['issue'],
                'severity': check_result.get('severity', 'HIGH'),
                'recommendation': check_result.get('recommendation', '')
            })

        # 5. التحقق منGoing Concern (ISA 570)
        check_result = self._check_going_concern(financial_data)
        report['findings'].append(check_result)
        total_checks += 1
        if check_result['status'] == 'COMPLIANT':
            passed_checks += 1
        else:
            report['violations'].append({
                'standard': 'ISA 570 - المنشأة المستمرة',
                'issue': check_result['issue'],
                'severity': check_result.get('severity', 'CRITICAL'),
                'recommendation': check_result.get('recommendation', '')
            })

        # حساب درجة الالتزام
        if total_checks > 0:
            report['compliance_score'] = round((passed_checks / total_checks) * 100, 2)

        # تحديد مستوى الخطر
        if len(report['violations']) == 0:
            report['risk_level'] = 'LOW'
        elif len(report['violations']) <= 2:
            report['risk_level'] = 'MEDIUM'
        else:
            report['risk_level'] = 'HIGH'

        # إضافة توصيات عامة
        report['recommendations'] = self._generate_recommendations(report['violations'])

        # المعايير التي تم فحصها
        report['standards_checked'] = [
            'المعيار المحاسبي المصري 1',
            'المعيار المحاسبي المصري 5',
            'IFRS 15',
            'قانون VAT المصري',
            'ISA 570'
        ]

        return report

    def _check_financial_statement_presentation(self, data: Dict) -> Dict:
        """التحقق من عرض القوائم المالية"""

        required_statements = [
            'statement_of_financial_position',
            'statement_of_comprehensive_income',
            'statement_of_changes_in_equity',
            'statement_of_cash_flows',
            'notes_to_financial_statements'
        ]

        missing = []
        for stmt in required_statements:
            if stmt not in data:
                missing.append(stmt)

        if missing:
            return {
                'area': 'عرض القوائم المالية',
                'status': 'NON_COMPLIANT',
                'issue': f'القوائم التالية مفقودة: {", ".join(missing)}',
                'severity': 'MEDIUM',
                'recommendation': 'يجب إعداد جميع القوائم المالية الأساسية وفقاً للمعيار المصري 1 و IAS 1'
            }

        return {
            'area': 'عرض القوائم المالية',
            'status': 'COMPLIANT',
            'issue': None,
            'severity': 'NONE'
        }

    def _check_tax_compliance(self, data: Dict) -> Dict:
        """التحقق من الالتزام الضريبي"""

        issues = []

        # التحقق من ضريبة القيمة المضافة
        if 'vat_payable' in data or 'vat_receivable' in data:
            vat_rate = data.get('applied_vat_rate', 0)
            if vat_rate != 14.0 and vat_rate != 0.0:
                issues.append(f'معدل VAT المطبق {vat_rate}% لا يتوافق مع المعدل القانوني 14%')

        # التحقق من ضريبة الدخل
        if 'income_tax_expense' in data:
            tax_expense = data['income_tax_expense']
            profit_before_tax = data.get('profit_before_tax', 0)

            if profit_before_tax > 0:
                effective_rate = (tax_expense / profit_before_tax) * 100 if profit_before_tax else 0

                # التحقق من أن المعدل ضمن النطاق المعقول
                if effective_rate < 0 or effective_rate > 30:
                    issues.append(f'معدل الضريبة الفعلي {effective_rate:.1f}% خارج النطاق المتوقع')

        if issues:
            return {
                'area': 'الالتزام الضريبي',
                'status': 'NON_COMPLIANT',
                'issue': '; '.join(issues),
                'severity': 'HIGH',
                'recommendation': 'مراجعة الحسابات الضريبية والتأكد من تطبيق المعدلات القانونية الصحيحة'
            }

        return {
            'area': 'الالتزام الضريبي',
            'status': 'COMPLIANT',
            'issue': None,
            'severity': 'NONE'
        }

    def _check_fixed_assets_treatment(self, data: Dict) -> Dict:
        """التحقق من معالجة الأصول الثابتة"""

        issues = []

        if 'fixed_assets' in data:
            assets = data['fixed_assets']

            for asset in assets if isinstance(assets, list) else [assets]:
                # التحقق من وجود إهلاك
                if 'accumulated_depreciation' not in asset:
                    issues.append('أصل ثابت بدون إهلاك متراكم')

                # التحقق من العمر الإنتاجي
                if 'useful_life' in asset and asset['useful_life'] <= 0:
                    issues.append('عمر إنتاجي غير صحيح للأصل')

                # التحقق من طريقة الإهلاك
                if 'depreciation_method' not in asset:
                    issues.append('طريقة الإهلاك غير محددة')

        if issues:
            return {
                'area': 'معالجة الأصول الثابتة',
                'status': 'NON_COMPLIANT',
                'issue': '; '.join(issues),
                'severity': 'MEDIUM',
                'recommendation': 'تطبيق المعيار المصري 5 و IAS 16 في معالجة الأصول الثابتة والإهلاك'
            }

        return {
            'area': 'معالجة الأصول الثابتة',
            'status': 'COMPLIANT',
            'issue': None,
            'severity': 'NONE'
        }

    def _check_revenue_recognition(self, data: Dict) -> Dict:
        """التحقق من الاعتراف بالإيرادات"""

        issues = []

        if 'revenue' in data:
            revenue = data['revenue']

            # التحقق من فصل الإيرادات حسب نوع النشاط
            if isinstance(revenue, dict):
                if 'operating_revenue' not in revenue and 'non_operating_revenue' not in revenue:
                    issues.append('الإيرادات غير مصنفة حسب النوع')

            # التحقق من وجود إيرادات مقدمة
            if 'deferred_revenue' not in data.get('liabilities', {}):
                # تحذير فقط
                pass

        if issues:
            return {
                'area': 'الاعتراف بالإيرادات',
                'status': 'NON_COMPLIANT',
                'issue': '; '.join(issues),
                'severity': 'HIGH',
                'recommendation': 'تطبيق IFRS 15 للاعتراف بالإيرادات من عقود العملاء'
            }

        return {
            'area': 'الاعتراف بالإيرادات',
            'status': 'COMPLIANT',
            'issue': None,
            'severity': 'NONE'
        }

    def _check_going_concern(self, data: Dict) -> Dict:
        """التحقق من فرضية المنشأة المستمرة"""

        issues = []

        # التحقق من المؤشرات السلبية
        current_ratio = data.get('current_ratio', 0)
        if current_ratio < 1.0:
            issues.append(f'نسبة التداول {current_ratio:.2f} أقل من 1 - مؤشر سلبي')

        working_capital = data.get('working_capital', 0)
        if working_capital < 0:
            issues.append('رأس المال العامل سالب - مؤشر خطر')

        accumulated_losses = data.get('accumulated_losses', 0)
        equity = data.get('total_equity', 0)
        if equity < 0 or (accumulated_losses > equity * 0.5):
            issues.append('خسائر متراكمة كبيرة تهدد استمرارية المنشأة')

        debt_to_equity = data.get('debt_to_equity', 0)
        if debt_to_equity > 3.0:
            issues.append(f'نسبة الدين إلى حقوق الملكية {debt_to_equity:.2f} مرتفعة جداً')

        if issues:
            return {
                'area': 'فرضية المنشأة المستمرة',
                'status': 'CONCERN',
                'issue': '; '.join(issues),
                'severity': 'CRITICAL',
                'recommendation': 'يتطلب تقييم شامل لقدرة المنشأة على الاستمرار وإفصاحات كافية في القوائم المالية'
            }

        return {
            'area': 'فرضية المنشأة المستمرة',
            'status': 'COMPLIANT',
            'issue': None,
            'severity': 'NONE'
        }

    def _generate_recommendations(self, violations: List[Dict]) -> List[Dict]:
        """توليد التوصيات بناءً على المخالفات"""

        recommendations = []

        violation_types = set()
        for v in violations:
            if 'standard' in v:
                violation_types.add(v['standard'].split(' - ')[0] if ' - ' in v['standard'] else v['standard'])

        if any('ضريبة' in str(v) or 'VAT' in str(v) for v in violation_types):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'ضريبي',
                'recommendation': 'مراجعة الإقرارات الضريبية المقدمة والتأكد من صحة الحسابات',
                'action': 'التواصل مع مستشار ضريبي معتمد'
            })

        if any('IFRS' in str(v) or 'معيار' in str(v) for v in violation_types):
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'معايير محاسبية',
                'recommendation': 'إعادة معالجة القيود المحاسبية وفقاً للمعايير الدولية',
                'action': 'تدريب فريق المحاسبة على المعايير المحدثة'
            })

        if any('ISA' in str(v) or 'منشأة مستمرة' in str(v) for v in violation_types):
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'استمرارية المنشأة',
                'recommendation': 'إعداد خطة عمل شاملة لمعالجة مشاكل السيولة والربحية',
                'action': 'دراسة جدوى إعادة الهيكلة المالية'
            })

        if not recommendations:
            recommendations.append({
                'priority': 'LOW',
                'category': 'عام',
                'recommendation': 'الاستمرار في تطبيق أفضل الممارسات المحاسبية',
                'action': 'مراجعة دورية للعمليات'
            })

        return recommendations

    def get_standard_details(self, standard_code: str) -> Dict[str, Any]:
        """الحصول على تفاصيل معيار محدد"""

        for category, info in self.standards.items():
            if category == 'tax_egypt':
                for law in info.get('laws', []):
                    if standard_code.lower() in law.lower():
                        return {
                            'category': category,
                            'name': law,
                            'details': info.get('rates', {})
                        }
            else:
                for std in info.get('standards', []):
                    if standard_code.lower() in std.lower():
                        return {
                            'category': category,
                            'name': std,
                            'full_info': info
                        }

        return {'error': 'لم يتم العثور على المعيار المطلوب'}

    def calculate_tax_liability(self, taxable_income: float, tax_type: str = 'income') -> Dict[str, Any]:
        """حساب الالتزام الضريبي"""

        result = {
            'taxable_income': taxable_income,
            'tax_type': tax_type,
            'calculated_tax': 0.0,
            'breakdown': [],
            'effective_rate': 0.0
        }

        if tax_type == 'income':
            brackets = self.standards['tax_egypt']['rates']['income_tax_brackets']
            remaining_income = taxable_income
            total_tax = 0.0

            for bracket in brackets:
                if remaining_income <= 0:
                    break

                bracket_min = bracket['min']
                bracket_max = bracket['max']
                rate = bracket['rate']

                if taxable_income > bracket_min:
                    taxable_in_bracket = min(taxable_income, bracket_max) - bracket_min
                    if taxable_in_bracket > 0:
                        tax_in_bracket = taxable_in_bracket * (rate / 100)
                        total_tax += tax_in_bracket
                        result['breakdown'].append({
                            'bracket': f'{bracket_min:,} - {bracket_max if bracket_max != float("inf") else "∞"} EGP',
                            'rate': f'{rate}%',
                            'taxable_amount': taxable_in_bracket,
                            'tax_amount': tax_in_bracket
                        })

            result['calculated_tax'] = total_tax
            result['effective_rate'] = (total_tax / taxable_income * 100) if taxable_income > 0 else 0

        elif tax_type == 'vat':
            vat_rate = self.standards['tax_egypt']['rates']['vat_standard']
            result['calculated_tax'] = taxable_income * (vat_rate / 100)
            result['breakdown'].append({
                'base_amount': taxable_income,
                'rate': f'{vat_rate}%',
                'vat_amount': result['calculated_tax']
            })
            result['effective_rate'] = vat_rate

        return result


# مثال على الاستخدام

    def verify_compliance(self, financial_data: Dict[str, Any], standards: List[str] = None) -> Dict[str, Any]:
        """
        التحقق من الالتزام بالمعايير المحددة

        Args:
            financial_data: البيانات المالية
            standards: قائمة المعايير للتحقق منها

        Returns:
            Dict: تقرير الالتزام
        """
        if standards is None:
            standards = ['egyptian', 'ifrs', 'isa']

        report = {
            'agent': self.agent_name,
            'timestamp': datetime.now().isoformat(),
            'verification_id': hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12],
            'standards_verified': standards,
            'compliance_score': 0.0,
            'findings': [],
            'violations': [],
            'recommendations': [],
            'risk_level': 'LOW'
        }

        total_checks = 0
        passed_checks = 0

        # التحقق من كل معيار مطلوب
        if 'egyptian' in standards or 'ifrs' in standards:
            check_result = self._check_financial_statement_presentation(financial_data)
            report['findings'].append(check_result)
            total_checks += 1
            if check_result['status'] == 'COMPLIANT':
                passed_checks += 1
            else:
                report['violations'].append({
                    'standard': check_result.get('standard', 'Financial Statement Presentation'),
                    'issue': check_result['issue'],
                    'severity': check_result.get('severity', 'MEDIUM'),
                    'recommendation': check_result.get('recommendation', '')
                })

        if 'tax' in standards or 'egyptian' in standards:
            check_result = self._check_tax_compliance(financial_data)
            report['findings'].append(check_result)
            total_checks += 1
            if check_result['status'] == 'COMPLIANT':
                passed_checks += 1
            else:
                report['violations'].append({
                    'standard': 'Tax Compliance',
                    'issue': check_result['issue'],
                    'severity': check_result.get('severity', 'HIGH'),
                    'recommendation': check_result.get('recommendation', '')
                })

        # حساب درجة الالتزام
        if total_checks > 0:
            report['compliance_score'] = round((passed_checks / total_checks) * 100, 2)

        # تحديد مستوى الخطر
        score = report['compliance_score']
        if score >= 90:
            report['risk_level'] = 'LOW'
        elif score >= 70:
            report['risk_level'] = 'MEDIUM'
        elif score >= 50:
            report['risk_level'] = 'HIGH'
        else:
            report['risk_level'] = 'CRITICAL'

        return report

    def check(self, item_type: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        فحص عنصر محدد للتحقق من امتثاله

        Args:
            item_type: نوع العنصر (journal_entry, account_balance, transaction, etc.)
            item_data: بيانات العنصر

        Returns:
            Dict: نتيجة الفحص
        """
        result = {
            'item_type': item_type,
            'timestamp': datetime.now().isoformat(),
            'status': 'PASS',
            'issues': [],
            'recommendations': []
        }

        if item_type == 'journal_entry':
            # فحص القيود اليومية
            if not item_data.get('debit_account'):
                result['status'] = 'FAIL'
                result['issues'].append('Missing debit account')

            if not item_data.get('credit_account'):
                result['status'] = 'FAIL'
                result['issues'].append('Missing credit account')

            debit = item_data.get('debit_amount', 0)
            credit = item_data.get('credit_amount', 0)

            if abs(debit - credit) > 0.01:
                result['status'] = 'FAIL'
                result['issues'].append(f'Debit ({debit}) != Credit ({credit})')

            if item_data.get('description') and len(item_data['description']) < 10:
                result['status'] = 'WARNING'
                result['issues'].append('Description too short')
                result['recommendations'].append('Add detailed description for audit trail')

        elif item_type == 'account_balance':
            # فحص أرصدة الحسابات
            balance = item_data.get('balance', 0)

            if balance < 0 and item_data.get('account_type') in ['asset', 'expense']:
                result['status'] = 'WARNING'
                result['issues'].append(f'Negative balance in {item_data.get("account_type")} account')
                result['recommendations'].append('Review account classification')

        elif item_type == 'transaction':
            # فحص المعاملات
            amount = item_data.get('amount', 0)
            date = item_data.get('date')

            if amount <= 0:
                result['status'] = 'FAIL'
                result['issues'].append('Invalid transaction amount')

            if not date:
                result['status'] = 'FAIL'
                result['issues'].append('Missing transaction date')

            if amount > 1000000:  # معامل كبير
                result['status'] = 'REVIEW'
                result['recommendations'].append('Large transaction requires additional documentation')

        return result

if __name__ == '__main__':
    agent = ComplianceStandardsAgent()

    # بيانات مالية تجريبية
    sample_data = {
        'statement_of_financial_position': True,
        'statement_of_comprehensive_income': True,
        'statement_of_changes_in_equity': True,
        'statement_of_cash_flows': True,
        'notes_to_financial_statements': True,

        'vat_payable': 50000,
        'applied_vat_rate': 14.0,

        'income_tax_expense': 100000,
        'profit_before_tax': 500000,

        'fixed_assets': [
            {
                'cost': 1000000,
                'accumulated_depreciation': 200000,
                'useful_life': 10,
                'depreciation_method': 'straight_line'
            }
        ],

        'revenue': {
            'operating_revenue': 2000000,
            'other_revenue': 50000
        },

        'current_ratio': 1.5,
        'working_capital': 300000,
        'accumulated_losses': 50000,
        'total_equity': 800000,
        'debt_to_equity': 1.2,

        'liabilities': {
            'deferred_revenue': 30000
        }
    }

    print("=" * 80)
    print("تقرير الالتزام بالمعايير والقوانين")
    print("=" * 80)

    report = agent.analyze_compliance(sample_data)

    print(f"\n📊 درجة الالتزام: {report['compliance_score']}%")
    print(f"⚠️  مستوى الخطر: {report['risk_level']}")
    print(f"📋 عدد المخالفات: {len(report['violations'])}")

    if report['violations']:
        print("\n❌ المخالفات المكتشفة:")
        for i, violation in enumerate(report['violations'], 1):
            print(f"\n{i}. المعيار: {violation['standard']}")
            print(f"   المشكلة: {violation['issue']}")
            print(f"   الخطورة: {violation['severity']}")
            print(f"   التوصية: {violation['recommendation']}")

    print("\n💡 التوصيات:")
    for rec in report['recommendations']:
        print(f"\n- [{rec['priority']}] {rec['category']}")
        print(f"  {rec['recommendation']}")
        print(f"  الإجراء: {rec['action']}")

    # حساب الضريبة
    print("\n" + "=" * 80)
    print("حساب الالتزام الضريبي")
    print("=" * 80)

    tax_calc = agent.calculate_tax_liability(500000, 'income')
    print(f"\nالدخل الخاضع للضريبة: {tax_calc['taxable_income']:,.0f} جنيه")
    print(f"الضريبة المستحقة: {tax_calc['calculated_tax']:,.2f} جنيه")
    print(f"المعدل الفعلي: {tax_calc['effective_rate']:.1f}%")

    print("\nتفصيل الشرائح:")
    for item in tax_calc['breakdown']:
        print(f"  {item['bracket']} @ {item['rate']} = {item['tax_amount']:,.2f} جنيه")

    print("\n✅ اكتمل تحليل الالتزام بنجاح!")


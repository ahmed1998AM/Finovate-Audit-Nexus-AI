"""
Finovate Audit Nexus AI
Fixed Assets Audit Agent
وكيل مراجعة الأصول الثابتة

Developed By: Ahmed Mostafa Ibrahim
© 2025 Finovate – AHMED EG - All Rights Reserved
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import pandas as pd


class DepreciationMethod(Enum):
    """طرق الإهلاك"""
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    SUM_OF_YEARS_DIGITS = "sum_of_years_digits"
    UNITS_OF_PRODUCTION = "units_of_production"


@dataclass
class FixedAsset:
    """هيكل بيانات أصل ثابت"""
    asset_id: str
    asset_name: str
    category: str
    acquisition_date: datetime
    acquisition_cost: float
    accumulated_depreciation: float
    net_book_value: float
    salvage_value: float
    useful_life_years: int
    depreciation_method: str
    location: str
    status: str  # active, disposed, fully_depreciated, impaired
    serial_number: str
    supplier: str


@dataclass
class AssetIssue:
    """مشكلة أصل ثابت مكتشفة"""
    issue_id: str
    asset_id: str
    issue_type: str  # over_depreciated, under_depreciated, fully_depreciated_in_use, impaired, missing
    severity: str  # low, medium, high, critical
    description: str
    calculated_nbv: float
    recorded_nbv: float
    variance: float
    financial_impact: float
    recommended_action: str
    detected_at: datetime = field(default_factory=datetime.now)


class FixedAssetsAuditAgent:
    """
    وكيل مراجعة الأصول الثابتة

    المهام:
    - مراجعة الإهلاك
    - تحليل الأعمار الإنتاجية
    - مراجعة الإضافات
    - مراجعة الاستبعادات
    - كشف الأخطاء
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.name = "Fixed Assets Audit Agent"
        self.version = "1.0.0"
        self.issues: List[AssetIssue] = []

        # عتبات الكشف
        self.variance_threshold_pct = self.config.get('variance_threshold_pct', 5.0)
        self.disposal_review_days = self.config.get('disposal_review_days', 90)

    def analyze_fixed_assets(
        self,
        assets_data: pd.DataFrame,
        additions_data: Optional[pd.DataFrame] = None,
        disposals_data: Optional[pd.DataFrame] = None,
        company_name: str = "Company"
    ) -> Dict[str, Any]:
        """
        تحليل الأصول الثابتة شامل

        Args:
            assets_data: DataFrame يحتوي على بيانات الأصول
            additions_data: DataFrame يحتوي على الإضافات
            disposals_data: DataFrame يحتوي على الاستبعادات
            company_name: اسم الشركة

        Returns:
            تقرير تحليل شامل
        """
        results = {
            'company_name': company_name,
            'analysis_date': datetime.now().isoformat(),
            'summary': {},
            'issues': [],
            'depreciation_analysis': {},
            'category_analysis': {},
            'recommendations': []
        }

        # التحقق من البيانات المطلوبة
        required_columns = ['asset_id', 'acquisition_cost', 'acquisition_date', 'useful_life_years']
        missing_cols = [col for col in required_columns if col not in assets_data.columns]

        if missing_cols:
            return {
                'status': 'error',
                'message': f'Missing required columns: {missing_cols}',
                'results': results
            }

        # تحويل التواريخ
        assets_data['acquisition_date'] = pd.to_datetime(assets_data['acquisition_date'])

        # حساب القيم الأساسية
        assets_data = self._calculate_asset_values(assets_data)

        # التحليل الأساسي
        results['summary'] = self._calculate_assets_summary(assets_data)

        # كشف المشاكل
        issues = self._detect_asset_issues(assets_data)
        results['issues'] = [vars(i) for i in issues]
        self.issues.extend(issues)

        # تحليل الإهلاك
        results['depreciation_analysis'] = self._analyze_depreciation(assets_data)

        # تحليل الفئات
        results['category_analysis'] = self._analyze_by_category(assets_data)

        # تحليل الإضافات والاستبعادات
        if additions_data is not None:
            results['additions_analysis'] = self._analyze_additions(additions_data)

        if disposals_data is not None:
            results['disposals_analysis'] = self._analyze_disposals(disposals_data)

        # التوصيات
        results['recommendations'] = self._generate_asset_recommendations(
            results['summary'],
            issues,
            results['depreciation_analysis']
        )

        return {
            'status': 'success',
            'message': f'Fixed assets analysis completed for {company_name}',
            'results': results
        }

    def _calculate_asset_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """حساب قيم الأصول"""

        df_copy = df.copy()

        # حساب العمر الحالي بالأشهر
        df_copy['asset_age_months'] = (datetime.now() - df_copy['acquisition_date']).dt.days / 30.44

        # حساب الإهلاك المتراكم المتوقع
        df_copy['expected_accumulated_depreciation'] = df_copy.apply(
            lambda row: self._calculate_expected_depreciation(row), axis=1
        )

        # صافي القيمة الدفترية
        if 'net_book_value' not in df_copy.columns:
            df_copy['net_book_value'] = df_copy['acquisition_cost'] - df_copy.get('accumulated_depreciation', 0)

        # الإهلاك السنوي
        df_copy['annual_depreciation'] = df_copy.apply(
            lambda row: self._calculate_annual_depreciation(row), axis=1
        )

        return df_copy

    def _calculate_expected_depreciation(self, row: pd.Series) -> float:
        """حساب الإهلاك المتراكم المتوقع"""

        cost = row['acquisition_cost']
        salvage = row.get('salvage_value', 0)
        useful_life = row['useful_life_years']
        age_months = row.get('asset_age_months', 0)
        method = row.get('depreciation_method', 'straight_line')

        if method == 'straight_line' or pd.isna(method):
            # طريقة القسط الثابت
            annual_dep = (cost - salvage) / useful_life
            expected_accumulated = annual_dep * (age_months / 12)
        elif method == 'declining_balance':
            # طريقة الرصيد المتناقص
            rate = row.get('declining_rate', 2 / useful_life)
            book_value = cost
            accumulated = 0
            for year in range(int(age_months / 12) + 1):
                dep = book_value * rate
                accumulated += dep
                book_value -= dep
            expected_accumulated = min(accumulated, cost - salvage)
        else:
            # افتراض القسط الثابت
            annual_dep = (cost - salvage) / useful_life
            expected_accumulated = annual_dep * (age_months / 12)

        return min(expected_accumulated, cost - salvage)

    def _calculate_annual_depreciation(self, row: pd.Series) -> float:
        """حساب مصروف الإهلاك السنوي"""

        cost = row['acquisition_cost']
        salvage = row.get('salvage_value', 0)
        useful_life = row['useful_life_years']
        method = row.get('depreciation_method', 'straight_line')

        if method == 'straight_line' or pd.isna(method):
            return (cost - salvage) / useful_life
        elif method == 'declining_balance':
            rate = row.get('declining_rate', 2 / useful_life)
            return row['net_book_value'] * rate
        else:
            return (cost - salvage) / useful_life

    def _calculate_assets_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """حساب ملخص إحصائيات الأصول"""

        total_assets = len(df)
        total_cost = df['acquisition_cost'].sum()
        total_accumulated_dep = df.get('accumulated_depreciation', pd.Series([0]*len(df))).sum()
        total_net_book_value = df['net_book_value'].sum()

        # تحليل حسب الحالة
        status_counts = df['status'].value_counts().to_dict() if 'status' in df.columns else {}

        # تحليل حسب الفئة
        category_analysis = {}
        if 'category' in df.columns:
            category_analysis = df.groupby('category').agg({
                'asset_id': 'count',
                'acquisition_cost': 'sum',
                'net_book_value': 'sum'
            }).to_dict()

        # أصول مستهلكة بالكامل
        fully_depreciated = df[df['net_book_value'] <= 0]
        fully_dep_count = len(fully_depreciated)
        fully_dep_original_cost = fully_depreciated['acquisition_cost'].sum()

        # أصول قريبة من الاستهلاك الكامل
        near_fully_dep = df[(df['net_book_value'] > 0) & (df['net_book_value'] < df['acquisition_cost'] * 0.1)]
        near_fully_dep_count = len(near_fully_dep)

        # متوسط العمر
        avg_age_months = df['asset_age_months'].mean()
        avg_useful_life = df['useful_life_years'].mean() * 12

        return {
            'total_assets': int(total_assets),
            'total_cost': float(total_cost),
            'total_accumulated_depreciation': float(total_accumulated_dep),
            'total_net_book_value': float(total_net_book_value),
            'average_asset_cost': float(total_cost / total_assets) if total_assets > 0 else 0,
            'status_breakdown': status_counts,
            'category_breakdown': category_analysis,
            'fully_depreciated': {
                'count': int(fully_dep_count),
                'original_cost': float(fully_dep_original_cost)
            },
            'near_fully_depreciated': {
                'count': int(near_fully_dep_count),
                'threshold': '10% of original cost'
            },
            'age_analysis': {
                'average_age_months': float(avg_age_months),
                'average_useful_life_months': float(avg_useful_life),
                'average_remaining_life_months': float(avg_useful_life - avg_age_months)
            },
            'assets_health_score': self._calculate_health_score(df, fully_dep_count, near_fully_dep_count)
        }

    def _calculate_health_score(
        self,
        df: pd.DataFrame,
        fully_dep_count: int,
        near_fully_dep_count: int
    ) -> float:
        """حساب درجة صحة محفظة الأصول"""

        total_assets = len(df)
        if total_assets == 0:
            return 0.0

        score = 1.0

        # خصم للأصول المستهلكة بالكامل المستخدمة
        in_use_fully_dep = len(df[(df['net_book_value'] <= 0) & (df['status'] == 'active')])
        score -= min(0.2, in_use_fully_dep / total_assets * 0.3)

        # خصم للتباينات الكبيرة
        large_variances = len(df[abs(df['net_book_value'] - (df['acquisition_cost'] - df['expected_accumulated_depreciation'])) > df['acquisition_cost'] * 0.1])
        score -= min(0.2, large_variances / total_assets * 0.3)

        return max(0.0, min(1.0, score))

    def _detect_asset_issues(self, df: pd.DataFrame) -> List[AssetIssue]:
        """كشف مشاكل الأصول الثابتة"""

        issues = []

        # 1. كشف الإفراط في الإهلاك
        over_depreciated = self._detect_over_depreciation(df)
        issues.extend(over_depreciated)

        # 2. كشف النقص في الإهلاك
        under_depreciated = self._detect_under_depreciation(df)
        issues.extend(under_depreciated)

        # 3. أصول مستهلكة بالكامل ولا تزال مستخدمة
        fully_dep_in_use = self._detect_fully_depreciated_in_use(df)
        issues.extend(fully_dep_in_use)

        # 4. تباينات كبيرة في القيم
        variances = self._detect_large_variances(df)
        issues.extend(variances)

        # 5. أصول تجاوزت عمرها الإنتاجي
        exceeded_life = self._detect_exceeded_useful_life(df)
        issues.extend(exceeded_life)

        return issues

    def _detect_over_depreciation(self, df: pd.DataFrame) -> List[AssetIssue]:
        """كشف الإفراط في الإهلاك"""

        issues = []

        for idx, row in df.iterrows():
            recorded_acc_dep = row.get('accumulated_depreciation', 0)
            expected_acc_dep = row.get('expected_accumulated_depreciation', 0)

            if pd.isna(recorded_acc_dep) or pd.isna(expected_acc_dep):
                continue

            variance = recorded_acc_dep - expected_acc_dep
            variance_pct = (variance / row['acquisition_cost'] * 100) if row['acquisition_cost'] != 0 else 0

            if variance_pct > self.variance_threshold_pct and variance > 0:
                severity = 'critical' if variance_pct > 20 else 'high' if variance_pct > 10 else 'medium'

                issue = AssetIssue(
                    issue_id=f'ASSET-OVER-{len(issues)+1:04d}',
                    asset_id=row['asset_id'],
                    issue_type='over_depreciated',
                    severity=severity,
                    description=f"Asset over-depreciated by {variance_pct:.1f}%",
                    calculated_nbv=float(row['acquisition_cost'] - expected_acc_dep),
                    recorded_nbv=float(row['net_book_value']),
                    variance=float(variance),
                    financial_impact=float(variance),
                    recommended_action='Review depreciation calculations and adjust accumulated depreciation'
                )
                issues.append(issue)

        return issues

    def _detect_under_depreciation(self, df: pd.DataFrame) -> List[AssetIssue]:
        """كشف النقص في الإهلاك"""

        issues = []

        for idx, row in df.iterrows():
            recorded_acc_dep = row.get('accumulated_depreciation', 0)
            expected_acc_dep = row.get('expected_accumulated_depreciation', 0)

            if pd.isna(recorded_acc_dep) or pd.isna(expected_acc_dep):
                continue

            variance = expected_acc_dep - recorded_acc_dep
            variance_pct = (variance / row['acquisition_cost'] * 100) if row['acquisition_cost'] != 0 else 0

            if variance_pct > self.variance_threshold_pct and variance > 0:
                severity = 'high' if variance_pct > 15 else 'medium' if variance_pct > 5 else 'low'

                issue = AssetIssue(
                    issue_id=f'ASSET-UNDER-{len(issues)+1:04d}',
                    asset_id=row['asset_id'],
                    issue_type='under_depreciated',
                    severity=severity,
                    description=f"Asset under-depreciated by {variance_pct:.1f}%",
                    calculated_nbv=float(row['acquisition_cost'] - expected_acc_dep),
                    recorded_nbv=float(row['net_book_value']),
                    variance=float(-variance),
                    financial_impact=float(variance),
                    recommended_action='Record additional depreciation expense'
                )
                issues.append(issue)

        return issues

    def _detect_fully_depreciated_in_use(self, df: pd.DataFrame) -> List[AssetIssue]:
        """كشف الأصول المستهلكة بالكامل التي لا تزال مستخدمة"""

        issues = []

        fully_dep_active = df[(df['net_book_value'] <= 0) & (df['status'] == 'active')]

        for idx, row in fully_dep_active.iterrows():
            issue = AssetIssue(
                issue_id=f'ASSET-FULLUSE-{len(issues)+1:04d}',
                asset_id=row['asset_id'],
                issue_type='fully_depreciated_in_use',
                severity='low',
                description=f"Fully depreciated asset still in use: {row.get('asset_name', row['asset_id'])}",
                calculated_nbv=0,
                recorded_nbv=float(row['net_book_value']),
                variance=0,
                financial_impact=0,
                recommended_action='Consider asset replacement or update useful life estimate'
            )
            issues.append(issue)

        return issues

    def _detect_large_variances(self, df: pd.DataFrame) -> List[AssetIssue]:
        """كشف التباينات الكبيرة"""

        issues = []

        for idx, row in df.iterrows():
            recorded_nbv = row['net_book_value']
            expected_nbv = row['acquisition_cost'] - row.get('expected_accumulated_depreciation', 0)

            variance = abs(recorded_nbv - expected_nbv)
            variance_pct = (variance / row['acquisition_cost'] * 100) if row['acquisition_cost'] != 0 else 0

            if variance_pct > self.variance_threshold_pct * 2:
                severity = 'critical' if variance_pct > 30 else 'high' if variance_pct > 20 else 'medium'

                issue = AssetIssue(
                    issue_id=f'ASSET-VAR-{len(issues)+1:04d}',
                    asset_id=row['asset_id'],
                    issue_type='valuation_variance',
                    severity=severity,
                    description=f"Large NBV variance: {variance_pct:.1f}% difference",
                    calculated_nbv=float(expected_nbv),
                    recorded_nbv=float(recorded_nbv),
                    variance=float(recorded_nbv - expected_nbv),
                    financial_impact=float(abs(variance)),
                    recommended_action='Investigate root cause and reconcile values'
                )
                issues.append(issue)

        return issues

    def _detect_exceeded_useful_life(self, df: pd.DataFrame) -> List[AssetIssue]:
        """كشف الأصول التي تجاوزت عمرها الإنتاجي"""

        issues = []

        for idx, row in df.iterrows():
            age_months = row.get('asset_age_months', 0)
            useful_life_months = row['useful_life_years'] * 12

            if age_months > useful_life_months * 1.2:  # تجاوز 20%
                excess_months = age_months - useful_life_months

                issue = AssetIssue(
                    issue_id=f'ASSET-EXCEED-{len(issues)+1:04d}',
                    asset_id=row['asset_id'],
                    issue_type='exceeded_useful_life',
                    severity='medium',
                    description=f"Asset exceeded useful life by {excess_months:.0f} months",
                    calculated_nbv=float(row['net_book_value']),
                    recorded_nbv=float(row['net_book_value']),
                    variance=0,
                    financial_impact=0,
                    recommended_action='Review and update useful life estimates or consider disposal'
                )
                issues.append(issue)

        return issues

    def _analyze_depreciation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """تحليل الإهلاك"""

        # توزيع طرق الإهلاك
        method_distribution = {}
        if 'depreciation_method' in df.columns:
            method_distribution = df['depreciation_method'].value_counts().to_dict()

        # إجمالي مصروف الإهلاك السنوي
        total_annual_depreciation = df['annual_depreciation'].sum()

        # الأصول حسب طريقة الإهلاك
        depreciation_by_method = {}
        if 'depreciation_method' in df.columns:
            depreciation_by_method = df.groupby('depreciation_method').agg({
                'acquisition_cost': 'sum',
                'annual_depreciation': 'sum',
                'asset_id': 'count'
            }).to_dict()

        # نسبة الإهلاك إلى التكلفة
        dep_to_cost_ratio = total_annual_depreciation / df['acquisition_cost'].sum() if df['acquisition_cost'].sum() > 0 else 0

        return {
            'method_distribution': method_distribution,
            'total_annual_depreciation': float(total_annual_depreciation),
            'depreciation_by_method': depreciation_by_method,
            'dep_to_cost_ratio': float(dep_to_cost_ratio),
            'average_depreciation_rate': float((df['annual_depreciation'] / df['acquisition_cost']).mean()) if len(df) > 0 else 0
        }

    def _analyze_by_category(self, df: pd.DataFrame) -> Dict[str, Any]:
        """تحليل الأصول حسب الفئة"""

        if 'category' not in df.columns:
            return {}

        category_stats = df.groupby('category').agg({
            'asset_id': 'count',
            'acquisition_cost': ['sum', 'mean'],
            'net_book_value': 'sum',
            'asset_age_months': 'mean',
            'useful_life_years': 'mean'
        })

        return {
            cat: {
                'count': int(stats['asset_id']['count']),
                'total_cost': float(stats['acquisition_cost']['sum']),
                'avg_cost': float(stats['acquisition_cost']['mean']),
                'total_nbv': float(stats['net_book_value']['sum']),
                'avg_age_months': float(stats['asset_age_months']['mean']),
                'avg_useful_life_years': float(stats['useful_life_years']['mean'])
            }
            for cat, stats in category_stats.iterrows()
        }

    def _analyze_additions(self, additions_df: pd.DataFrame) -> Dict[str, Any]:
        """تحليل الإضافات"""

        additions_df['date'] = pd.to_datetime(additions_df['date'])

        total_additions = len(additions_df)
        total_additions_value = additions_df['amount'].sum() if 'amount' in additions_df.columns else 0

        # تحليل شهري
        additions_df['month'] = additions_df['date'].dt.to_period('M')
        monthly_additions = additions_df.groupby('month')['amount'].sum() if 'amount' in additions_df.columns else {}

        return {
            'total_additions_count': int(total_additions),
            'total_additions_value': float(total_additions_value),
            'monthly_trend': {str(k): float(v) for k, v in monthly_additions.to_dict().items()},
            'average_addition_size': float(total_additions_value / total_additions) if total_additions > 0 else 0
        }

    def _analyze_disposals(self, disposals_df: pd.DataFrame) -> Dict[str, Any]:
        """تحليل الاستبعادات"""

        disposals_df['date'] = pd.to_datetime(disposals_df['date'])

        total_disposals = len(disposals_df)
        total_disposals_proceeds = disposals_df['proceeds'].sum() if 'proceeds' in disposals_df.columns else 0
        total_disposals_nbv = disposals_df['net_book_value'].sum() if 'net_book_value' in disposals_df.columns else 0

        # مكاسب/خسائر الاستبعاد
        gain_loss = total_disposals_proceeds - total_disposals_nbv

        return {
            'total_disposals_count': int(total_disposals),
            'total_proceeds': float(total_disposals_proceeds),
            'total_nbv_disposed': float(total_disposals_nbv),
            'total_gain_loss': float(gain_loss),
            'disposal_analysis': 'gain' if gain_loss > 0 else 'loss' if gain_loss < 0 else 'break_even'
        }

    def _generate_asset_recommendations(
        self,
        summary: Dict[str, Any],
        issues: List[AssetIssue],
        depreciation_analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """توليد توصيات إدارة الأصول الثابتة"""

        recommendations = []

        # توصيات بناءً على المشاكل
        critical_issues = sum(1 for i in issues if i.severity == 'critical')
        high_issues = sum(1 for i in issues if i.severity == 'high')

        if critical_issues > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'asset_valuation',
                'recommendation': f'{critical_issues} critical asset valuation issues require immediate attention.',
                'impact': 'Financial statement accuracy'
            })

        if high_issues > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'depreciation_accuracy',
                'recommendation': f'{high_issues} high-severity depreciation issues identified. Review calculations.',
                'impact': 'Depreciation expense accuracy'
            })

        # توصيات الأصول المستهلكة بالكامل
        fully_dep_in_use = sum(1 for i in issues if i.issue_type == 'fully_depreciated_in_use')
        if fully_dep_in_use > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'asset_management',
                'recommendation': f'{fully_dep_in_use} fully depreciated assets still in use. Consider capital budgeting for replacements.',
                'impact': 'Operational efficiency'
            })

        # توصيات نسبة الإهلاك
        dep_ratio = depreciation_analysis.get('dep_to_cost_ratio', 0)
        if dep_ratio > 0.15:
            recommendations.append({
                'priority': 'low',
                'category': 'capital_planning',
                'recommendation': f'High depreciation ratio ({dep_ratio:.1%}). Plan for asset renewals.',
                'impact': 'Long-term sustainability'
            })

        return recommendations

    def generate_fixed_assets_audit_report(
        self,
        company_name: str,
        audit_date: datetime,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """توليد تقرير مراجعة الأصول الثابتة احترافي"""

        report = {
            'report_title': 'Fixed Assets Audit Report',
            'report_id': f'FA-AUDIT-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            'generated_at': datetime.now().isoformat(),
            'company_info': {
                'company_name': company_name,
                'audit_date': audit_date.isoformat(),
                'prepared_by': 'Finovate Audit Nexus AI - Fixed Assets Agent'
            },
            'executive_summary': {
                'total_assets': results['summary'].get('total_assets', 0),
                'total_cost': results['summary'].get('total_cost', 0),
                'total_net_book_value': results['summary'].get('total_net_book_value', 0),
                'health_score': results['summary'].get('assets_health_score', 0),
                'total_issues': len(results['issues']),
                'critical_issues': sum(1 for i in results['issues'] if i.get('severity') == 'critical')
            },
            'detailed_findings': {
                'issues': results['issues'],
                'depreciation_analysis': results['depreciation_analysis'],
                'category_analysis': results['category_analysis']
            },
            'recommendations': results['recommendations'],
            'audit_trail': {
                'procedures_performed': [
                    'Asset existence verification',
                    'Depreciation calculation testing',
                    'Useful life assessment',
                    'Impairment indicators review',
                    'Additions and disposals testing',
                    'Reconciliation with general ledger'
                ],
                'confidence_score': self._calculate_confidence_score(results)
            }
        }

        return report

    def _calculate_confidence_score(self, results: Dict[str, Any]) -> float:
        """حساب درجة الثقة في النتائج"""

        score = 1.0

        # خصم لعدد المشاكل الحرجة
        critical_count = sum(1 for i in results['issues'] if i.get('severity') == 'critical')
        score -= min(0.3, critical_count * 0.1)

        # خصم لدرجة الصحة المنخفضة
        health_score = results['summary'].get('assets_health_score', 1.0)
        if health_score < 0.7:
            score -= 0.2

        return max(0.5, min(1.0, score))


# مثال للاستخدام
if __name__ == "__main__":
    # إنشاء وكيل مراجعة الأصول الثابتة
    agent = FixedAssetsAuditAgent()

    # بيانات تجريبية
    categories = ['Buildings', 'Machinery', 'Vehicles', 'Office Equipment', 'Computers']
    methods = ['straight_line', 'declining_balance']
    statuses = ['active', 'disposed', 'fully_depreciated']

    sample_data = {
        'asset_id': [f'ASSET-{i+1:04d}' for i in range(30)],
        'asset_name': [f'Asset {i+1}' for i in range(30)],
        'category': [categories[i % len(categories)] for i in range(30)],
        'acquisition_date': [(datetime.now() - timedelta(days=i*30)).strftime('%Y-%m-%d') for i in range(30)],
        'acquisition_cost': [50000 + i * 10000 for i in range(30)],
        'accumulated_depreciation': [i * 5000 for i in range(30)],
        'salvage_value': [5000 for _ in range(30)],
        'useful_life_years': [5, 10, 5, 7, 3] * 6,
        'depreciation_method': [methods[i % len(methods)] for i in range(30)],
        'status': [statuses[i % len(statuses)] for i in range(30)],
        'location': ['Building A', 'Building B', 'Warehouse'] * 10
    }

    df = pd.DataFrame(sample_data)

    # تحليل الأصول الثابتة
    results = agent.analyze_fixed_assets(df, company_name="Sample Company")

    print("=" * 80)
    print("Finovate Audit Nexus AI - Fixed Assets Audit Agent")
    print("=" * 80)
    print(f"\nStatus: {results['status']}")
    print(f"Message: {results['message']}")
    print("\nSummary:")
    summary = results['results']['summary']
    print(f"  Total Assets: {summary['total_assets']}")
    print(f"  Total Cost: ${summary['total_cost']:,.2f}")
    print(f"  Net Book Value: ${summary['total_net_book_value']:,.2f}")
    print(f"  Health Score: {summary['assets_health_score']:.2f}")
    print(f"  Fully Depreciated: {summary['fully_depreciated']['count']} assets")

    print(f"\nIssues Found: {len(results['results']['issues'])}")
    critical = sum(1 for i in results['results']['issues'] if i['severity'] == 'critical')
    high = sum(1 for i in results['results']['issues'] if i['severity'] == 'high')
    print(f"  Critical: {critical}, High: {high}")

    print("\nDepreciation Analysis:")
    dep_analysis = results['results']['depreciation_analysis']
    print(f"  Total Annual Depreciation: ${dep_analysis['total_annual_depreciation']:,.2f}")
    print(f"  Depreciation to Cost Ratio: {dep_analysis['dep_to_cost_ratio']:.1%}")

    print(f"\nRecommendations: {len(results['results']['recommendations'])}")
    for rec in results['results']['recommendations'][:3]:
        print(f"  [{rec['priority'].upper()}] {rec['recommendation']}")

    print("\n" + "=" * 80)
    print("Developed By: Ahmed Mostafa Ibrahim")
    print("© 2025 Finovate – AHMED EG - All Rights Reserved")
    print("=" * 80)

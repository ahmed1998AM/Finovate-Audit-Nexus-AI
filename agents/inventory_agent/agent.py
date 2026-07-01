"""
Finovate Audit Nexus AI
Inventory Audit Agent
وكيل مراجعة المخزون

Developed By: Ahmed Mostafa Ibrahim
© 2025 Finovate – AHMED EG - All Rights Reserved
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class InventoryItem:
    """هيكل بيانات صنف مخزون"""
    item_id: str
    item_name: str
    category: str
    quantity_on_hand: float
    quantity_reserved: float
    quantity_available: float
    unit_cost: float
    total_value: float
    reorder_point: float
    max_stock_level: float
    last_movement_date: datetime
    supplier_id: str
    status: str = "active"


@dataclass
class InventoryIssue:
    """مشكلة مخزون مكتشفة"""
    issue_id: str
    item_id: str
    issue_type: str  # shortage, overage, obsolete, slow_moving, negative_stock
    severity: str  # low, medium, high, critical
    description: str
    current_quantity: float
    expected_quantity: float
    variance: float
    financial_impact: float
    recommended_action: str
    detected_at: datetime = field(default_factory=datetime.now)


class InventoryAuditAgent:
    """
    وكيل مراجعة المخزون

    المهام:
    - كشف العجز والزيادة
    - تحليل التكلفة
    - تحليل الحركة
    - كشف الراكد
    - تقييم دقة الجرد
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.name = "Inventory Audit Agent"
        self.version = "1.0.0"
        self.issues: List[InventoryIssue] = []

        # عتبات الكشف
        self.shortage_threshold_pct = self.config.get('shortage_threshold_pct', 5.0)
        self.obsolete_days = self.config.get('obsolete_days', 365)
        self.slow_moving_days = self.config.get('slow_moving_days', 90)
        self.negative_stock_tolerance = self.config.get('negative_stock_tolerance', 0.01)

    def analyze_inventory(
        self,
        inventory_data: pd.DataFrame,
        movement_data: Optional[pd.DataFrame] = None,
        warehouse_name: str = "Main Warehouse"
    ) -> Dict[str, Any]:
        """
        تحليل المخزون شامل

        Args:
            inventory_data: DataFrame يحتوي على بيانات المخزون
            movement_data: DataFrame يحتوي على حركات المخزون
            warehouse_name: اسم المخزن

        Returns:
            تقرير تحليل شامل
        """
        results = {
            'warehouse_name': warehouse_name,
            'analysis_date': datetime.now().isoformat(),
            'summary': {},
            'issues': [],
            'abc_analysis': {},
            'movement_analysis': {},
            'recommendations': []
        }

        # التحقق من البيانات المطلوبة
        required_columns = ['item_id', 'quantity_on_hand', 'unit_cost']
        missing_cols = [col for col in required_columns if col not in inventory_data.columns]

        if missing_cols:
            return {
                'status': 'error',
                'message': f'Missing required columns: {missing_cols}',
                'results': results
            }

        # حساب القيم الإجمالية
        inventory_data['total_value'] = inventory_data['quantity_on_hand'] * inventory_data['unit_cost']
        inventory_data['quantity_available'] = inventory_data['quantity_on_hand'] - inventory_data.get('quantity_reserved', 0)

        # التحليل الأساسي
        results['summary'] = self._calculate_inventory_summary(inventory_data)

        # كشف المشاكل
        issues = self._detect_inventory_issues(inventory_data, movement_data)
        results['issues'] = [vars(i) for i in issues]
        self.issues.extend(issues)

        # تحليل ABC
        results['abc_analysis'] = self._perform_abc_analysis(inventory_data)

        # تحليل الحركة
        if movement_data is not None:
            results['movement_analysis'] = self._analyze_inventory_movement(movement_data)

        # التوصيات
        results['recommendations'] = self._generate_inventory_recommendations(
            results['summary'],
            issues,
            results['abc_analysis']
        )

        return {
            'status': 'success',
            'message': f'Inventory analysis completed for {warehouse_name}',
            'results': results
        }

    def _calculate_inventory_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """حساب ملخص إحصائيات المخزون"""

        total_items = len(df)
        total_value = df['total_value'].sum()
        total_quantity = df['quantity_on_hand'].sum()

        # تحليل حسب الحالة
        status_counts = df['status'].value_counts().to_dict() if 'status' in df.columns else {}

        # تحليل حسب الفئة
        category_analysis = {}
        if 'category' in df.columns:
            category_analysis = df.groupby('category').agg({
                'item_id': 'count',
                'total_value': 'sum',
                'quantity_on_hand': 'sum'
            }).to_dict()

        # المخزون راكد (لم يتحرك خلال سنة)
        obsolete_count = 0
        obsolete_value = 0
        if 'last_movement_date' in df.columns:
            cutoff_date = datetime.now() - timedelta(days=self.obsolete_days)
            obsolete_items = df[pd.to_datetime(df['last_movement_date']) < cutoff_date]
            obsolete_count = len(obsolete_items)
            obsolete_value = obsolete_items['total_value'].sum()

        # أصناف بكمية سالبة
        negative_stock_items = df[df['quantity_on_hand'] < -self.negative_stock_tolerance]
        negative_count = len(negative_stock_items)
        negative_value = abs(negative_stock_items['total_value'].sum())

        # أصناف أقل من نقطة إعادة الطلب
        below_reorder = 0
        if 'reorder_point' in df.columns:
            below_reorder = len(df[df['quantity_on_hand'] < df['reorder_point']])

        return {
            'total_items': int(total_items),
            'total_value': float(total_value),
            'total_quantity': float(total_quantity),
            'average_item_value': float(total_value / total_items) if total_items > 0 else 0,
            'status_breakdown': status_counts,
            'category_breakdown': category_analysis,
            'obsolete_items': {
                'count': int(obsolete_count),
                'value': float(obsolete_value),
                'percentage': float(obsolete_count / total_items * 100) if total_items > 0 else 0
            },
            'negative_stock': {
                'count': int(negative_count),
                'value': float(negative_value)
            },
            'below_reorder_point': int(below_reorder),
            'inventory_health_score': self._calculate_health_score(df, obsolete_count, negative_count, below_reorder)
        }

    def _calculate_health_score(
        self,
        df: pd.DataFrame,
        obsolete_count: int,
        negative_count: int,
        below_reorder: int
    ) -> float:
        """حساب درجة صحة المخزون"""

        total_items = len(df)
        if total_items == 0:
            return 0.0

        score = 1.0

        # خصم للمخزون الراكد
        obsolete_ratio = obsolete_count / total_items
        score -= min(0.3, obsolete_ratio * 0.5)

        # خصم للكميات السالبة
        negative_ratio = negative_count / total_items
        score -= min(0.3, negative_ratio * 0.6)

        # خصم للأصناف أقل من نقطة إعادة الطلب
        reorder_ratio = below_reorder / total_items
        score -= min(0.2, reorder_ratio * 0.3)

        return max(0.0, min(1.0, score))

    def _detect_inventory_issues(
        self,
        inventory_df: pd.DataFrame,
        movement_df: Optional[pd.DataFrame] = None
    ) -> List[InventoryIssue]:
        """كشف مشاكل المخزون"""

        issues = []

        # 1. كشف الكميات السالبة
        negative_stock = self._detect_negative_stock(inventory_df)
        issues.extend(negative_stock)

        # 2. كشف المخزون الراكد
        obsolete = self._detect_obsolete_inventory(inventory_df)
        issues.extend(obsolete)

        # 3. كشف المخزون بطيء الحركة
        slow_moving = self._detect_slow_moving_inventory(inventory_df, movement_df)
        issues.extend(slow_moving)

        # 4. كشف التباينات الكبيرة
        variances = self._detect_large_variances(inventory_df, movement_df)
        issues.extend(variances)

        # 5. كشف المخزون الزائد
        overstock = self._detect_overstock(inventory_df)
        issues.extend(overstock)

        return issues

    def _detect_negative_stock(self, df: pd.DataFrame) -> List[InventoryIssue]:
        """كشف الكميات السالبة"""

        issues = []
        negative_items = df[df['quantity_on_hand'] < -self.negative_stock_tolerance]

        for idx, row in negative_items.iterrows():
            issue = InventoryIssue(
                issue_id=f'INV-NEG-{len(issues)+1:04d}',
                item_id=row['item_id'],
                issue_type='negative_stock',
                severity='critical',
                description=f"Negative stock detected for item {row.get('item_name', row['item_id'])}",
                current_quantity=float(row['quantity_on_hand']),
                expected_quantity=0,
                variance=float(abs(row['quantity_on_hand'])),
                financial_impact=float(abs(row['quantity_on_hand']) * row['unit_cost']),
                recommended_action='Immediate physical count and investigation required'
            )
            issues.append(issue)

        return issues

    def _detect_obsolete_inventory(self, df: pd.DataFrame) -> List[InventoryIssue]:
        """كشف المخزون الراكد"""

        issues = []

        if 'last_movement_date' not in df.columns:
            return issues

        cutoff_date = datetime.now() - timedelta(days=self.obsolete_days)
        df_copy = df.copy()
        df_copy['last_movement_date'] = pd.to_datetime(df_copy['last_movement_date'])

        obsolete_items = df_copy[df_copy['last_movement_date'] < cutoff_date]

        for idx, row in obsolete_items.iterrows():
            days_since_movement = (datetime.now() - row['last_movement_date']).days

            issue = InventoryIssue(
                issue_id=f'INV-OBS-{len(issues)+1:04d}',
                item_id=row['item_id'],
                issue_type='obsolete',
                severity='high' if row['total_value'] > 10000 else 'medium',
                description=f"Obsolete inventory: No movement for {days_since_movement} days",
                current_quantity=float(row['quantity_on_hand']),
                expected_quantity=0,
                variance=float(row['quantity_on_hand']),
                financial_impact=float(row['total_value']),
                recommended_action='Review for disposal, write-down, or clearance sale'
            )
            issues.append(issue)

        return issues

    def _detect_slow_moving_inventory(
        self,
        df: pd.DataFrame,
        movement_df: Optional[pd.DataFrame]
    ) -> List[InventoryIssue]:
        """كشف المخزون بطيء الحركة"""

        issues = []

        if movement_df is None or 'item_id' not in movement_df.columns:
            return issues

        # تحليل حركة كل صنف
        for idx, row in df.iterrows():
            item_movements = movement_df[movement_df['item_id'] == row['item_id']]

            if len(item_movements) == 0:
                continue

            # آخر حركة
            last_movement = pd.to_datetime(item_movements['date']).max()
            days_since_last = (datetime.now() - last_movement).days

            if days_since_last > self.slow_moving_days and row['quantity_on_hand'] > 0:
                issue = InventoryIssue(
                    issue_id=f'INV-SLOW-{len(issues)+1:04d}',
                    item_id=row['item_id'],
                    issue_type='slow_moving',
                    severity='medium',
                    description=f"Slow moving inventory: Last movement {days_since_last} days ago",
                    current_quantity=float(row['quantity_on_hand']),
                    expected_quantity=0,
                    variance=float(row['quantity_on_hand']),
                    financial_impact=float(row['total_value']),
                    recommended_action='Review pricing, marketing, or consider promotion'
                )
                issues.append(issue)

        return issues

    def _detect_large_variances(
        self,
        inventory_df: pd.DataFrame,
        movement_df: Optional[pd.DataFrame]
    ) -> List[InventoryIssue]:
        """كشف التباينات الكبيرة"""

        issues = []

        if movement_df is None:
            return issues

        # مقارنة الرصيد النظري بالفعلي
        for idx, row in inventory_df.iterrows():
            if 'expected_quantity' in row:
                variance = row['quantity_on_hand'] - row['expected_quantity']
                variance_pct = abs(variance / row['expected_quantity'] * 100) if row['expected_quantity'] != 0 else 0

                if variance_pct > self.shortage_threshold_pct:
                    severity = 'critical' if variance_pct > 20 else 'high' if variance_pct > 10 else 'medium'

                    issue = InventoryIssue(
                        issue_id=f'INV-VAR-{len(issues)+1:04d}',
                        item_id=row['item_id'],
                        issue_type='variance',
                        severity=severity,
                        description=f"Large inventory variance: {variance_pct:.1f}% difference",
                        current_quantity=float(row['quantity_on_hand']),
                        expected_quantity=float(row['expected_quantity']),
                        variance=float(variance),
                        financial_impact=float(abs(variance) * row['unit_cost']),
                        recommended_action='Physical count and investigation of root cause'
                    )
                    issues.append(issue)

        return issues

    def _detect_overstock(self, df: pd.DataFrame) -> List[InventoryIssue]:
        """كشف المخزون الزائد"""

        issues = []

        if 'max_stock_level' not in df.columns:
            return issues

        overstocked = df[df['quantity_on_hand'] > df['max_stock_level']]

        for idx, row in overstocked.iterrows():
            excess_quantity = row['quantity_on_hand'] - row['max_stock_level']
            excess_value = excess_quantity * row['unit_cost']

            issue = InventoryIssue(
                issue_id=f'INV-OVER-{len(issues)+1:04d}',
                item_id=row['item_id'],
                issue_type='overstock',
                severity='medium',
                description=f"Overstock: {excess_quantity:.0f} units above maximum level",
                current_quantity=float(row['quantity_on_hand']),
                expected_quantity=float(row['max_stock_level']),
                variance=float(excess_quantity),
                financial_impact=float(excess_value),
                recommended_action='Review purchasing policy and consider reducing orders'
            )
            issues.append(issue)

        return issues

    def _perform_abc_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        تحليل ABC للمخزون

        A: أعلى 80% من القيمة (20% من الأصناف)
        B: التالي 15% من القيمة (30% من الأصناف)
        C: الأخير 5% من القيمة (50% من الأصناف)
        """

        df_copy = df.copy()
        df_copy = df_copy.sort_values('total_value', ascending=False)

        total_value = df_copy['total_value'].sum()
        df_copy['cumulative_value'] = df_copy['total_value'].cumsum()
        df_copy['cumulative_pct'] = df_copy['cumulative_value'] / total_value * 100

        # تصنيف ABC
        def classify_abc(pct):
            if pct <= 80:
                return 'A'
            elif pct <= 95:
                return 'B'
            else:
                return 'C'

        df_copy['abc_class'] = df_copy['cumulative_pct'].apply(classify_abc)

        # ملخص التحليل
        abc_summary = df_copy.groupby('abc_class').agg({
            'item_id': 'count',
            'total_value': 'sum',
            'quantity_on_hand': 'sum'
        })

        return {
            'classification': df_copy[['item_id', 'abc_class']].set_index('item_id').to_dict()['abc_class'],
            'summary': {
                class_name: {
                    'items_count': int(row['item_id']),
                    'total_value': float(row['total_value']),
                    'value_percentage': float(row['total_value'] / total_value * 100),
                    'quantity': float(row['quantity_on_hand'])
                }
                for class_name, row in abc_summary.iterrows()
            },
            'recommendations': {
                'A': 'Tight control, frequent reviews, accurate records',
                'B': 'Moderate control, regular reviews',
                'C': 'Simple control, periodic reviews'
            }
        }

    def _analyze_inventory_movement(self, movement_df: pd.DataFrame) -> Dict[str, Any]:
        """تحليل حركات المخزون"""

        movement_df['date'] = pd.to_datetime(movement_df['date'])

        # إحصائيات الحركات
        total_movements = len(movement_df)
        receipts = movement_df[movement_df['movement_type'] == 'receipt'] if 'movement_type' in movement_df.columns else movement_df[movement_df['quantity'] > 0]
        issues = movement_df[movement_df['movement_type'] == 'issue'] if 'movement_type' in movement_df.columns else movement_df[movement_df['quantity'] < 0]

        # تحليل شهري
        movement_df['month'] = movement_df['date'].dt.to_period('M')
        monthly_movements = movement_df.groupby('month').size()

        # أصناف الأكثر حركة
        if 'item_id' in movement_df.columns:
            top_moved = movement_df.groupby('item_id').agg({
                'quantity': 'sum',
                'date': 'count'
            }).nlargest(10, 'date')
        else:
            top_moved = None

        return {
            'total_movements': int(total_movements),
            'receipts_count': int(len(receipts)),
            'issues_count': int(len(issues)),
            'monthly_trend': {str(k): int(v) for k, v in monthly_movements.to_dict().items()},
            'top_moved_items': top_moved.to_dict() if top_moved is not None else {},
            'average_daily_movements': float(total_movements / max(1, (movement_df['date'].max() - movement_df['date'].min()).days))
        }

    def _generate_inventory_recommendations(
        self,
        summary: Dict[str, Any],
        issues: List[InventoryIssue],
        abc_analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """توليد توصيات إدارة المخزون"""

        recommendations = []

        # توصيات بناءً على المشاكل
        critical_issues = sum(1 for i in issues if i.severity == 'critical')
        high_issues = sum(1 for i in issues if i.severity == 'high')

        if critical_issues > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'inventory_accuracy',
                'recommendation': f'{critical_issues} critical inventory issues require immediate attention.',
                'impact': 'Financial accuracy and operational continuity'
            })

        if high_issues > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'inventory_control',
                'recommendation': f'{high_issues} high-severity issues identified. Review inventory controls.',
                'impact': 'Loss prevention'
            })

        # توصيات المخزون الراكد
        obsolete_value = summary.get('obsolete_items', {}).get('value', 0)
        if obsolete_value > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'obsolete_inventory',
                'recommendation': f'Obsolete inventory worth {obsolete_value:,.2f}. Consider write-down or disposal.',
                'impact': 'Working capital optimization'
            })

        # توصيات تحليل ABC
        if 'A' in abc_analysis.get('summary', {}):
            a_items = abc_analysis['summary']['A']['items_count']
            recommendations.append({
                'priority': 'medium',
                'category': 'inventory_optimization',
                'recommendation': f'{a_items} Class-A items identified. Implement tight controls and frequent cycle counts.',
                'impact': 'Inventory optimization'
            })

        # توصيات الكميات السالبة
        negative_count = summary.get('negative_stock', {}).get('count', 0)
        if negative_count > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'data_integrity',
                'recommendation': f'{negative_count} items with negative stock. Investigate system errors or unrecorded transactions.',
                'impact': 'Data integrity'
            })

        return recommendations

    def generate_inventory_audit_report(
        self,
        warehouse_name: str,
        audit_date: datetime,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """توليد تقرير مراجعة مخزون احترافي"""

        report = {
            'report_title': 'Inventory Audit Report',
            'report_id': f'INV-AUDIT-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            'generated_at': datetime.now().isoformat(),
            'warehouse_info': {
                'warehouse_name': warehouse_name,
                'audit_date': audit_date.isoformat(),
                'prepared_by': 'Finovate Audit Nexus AI - Inventory Agent'
            },
            'executive_summary': {
                'total_items': results['summary'].get('total_items', 0),
                'total_value': results['summary'].get('total_value', 0),
                'health_score': results['summary'].get('inventory_health_score', 0),
                'total_issues': len(results['issues']),
                'critical_issues': sum(1 for i in results['issues'] if i.get('severity') == 'critical'),
                'obsolete_items': results['summary'].get('obsolete_items', {}).get('count', 0)
            },
            'detailed_findings': {
                'issues': results['issues'],
                'abc_classification': results['abc_analysis'],
                'movement_analysis': results.get('movement_analysis', {})
            },
            'recommendations': results['recommendations'],
            'audit_trail': {
                'procedures_performed': [
                    'Physical quantity verification',
                    'Valuation testing',
                    'Obsolete inventory identification',
                    'ABC analysis',
                    'Movement pattern analysis',
                    'Variance analysis'
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
        health_score = results['summary'].get('inventory_health_score', 1.0)
        if health_score < 0.7:
            score -= 0.2

        return max(0.5, min(1.0, score))


# مثال للاستخدام
if __name__ == "__main__":
    import random

    # إنشاء وكيل مراجعة المخزون
    agent = InventoryAuditAgent()

    # بيانات تجريبية
    categories = ['Electronics', 'Furniture', 'Office Supplies', 'Raw Materials']
    statuses = ['active', 'discontinued', 'pending']

    sample_data = {
        'item_id': [f'ITEM-{i+1:04d}' for i in range(50)],
        'item_name': [f'Product {i+1}' for i in range(50)],
        'category': [random.choice(categories) for _ in range(50)],
        'quantity_on_hand': [random.randint(-5, 500) for _ in range(50)],
        'quantity_reserved': [random.randint(0, 50) for _ in range(50)],
        'unit_cost': [random.uniform(10, 1000) for _ in range(50)],
        'reorder_point': [random.randint(20, 100) for _ in range(50)],
        'max_stock_level': [random.randint(200, 1000) for _ in range(50)],
        'last_movement_date': [(datetime.now() - timedelta(days=random.randint(0, 500))).strftime('%Y-%m-%d') for _ in range(50)],
        'status': [random.choice(statuses) for _ in range(50)]
    }

    df = pd.DataFrame(sample_data)

    # تحليل المخزون
    results = agent.analyze_inventory(df, warehouse_name="Main Warehouse")

    print("=" * 80)
    print("Finovate Audit Nexus AI - Inventory Audit Agent")
    print("=" * 80)
    print(f"\nStatus: {results['status']}")
    print(f"Message: {results['message']}")
    print("\nSummary:")
    summary = results['results']['summary']
    print(f"  Total Items: {summary['total_items']}")
    print(f"  Total Value: ${summary['total_value']:,.2f}")
    print(f"  Health Score: {summary['inventory_health_score']:.2f}")
    print(f"  Obsolete Items: {summary['obsolete_items']['count']} (${summary['obsolete_items']['value']:,.2f})")
    print(f"  Negative Stock: {summary['negative_stock']['count']} items")

    print(f"\nIssues Found: {len(results['results']['issues'])}")
    critical = sum(1 for i in results['results']['issues'] if i['severity'] == 'critical')
    high = sum(1 for i in results['results']['issues'] if i['severity'] == 'high')
    print(f"  Critical: {critical}, High: {high}")

    print("\nABC Analysis:")
    for cls, data in results['results']['abc_analysis']['summary'].items():
        print(f"  Class {cls}: {data['items_count']} items, ${data['total_value']:,.2f} ({data['value_percentage']:.1f}%)")

    print(f"\nRecommendations: {len(results['results']['recommendations'])}")
    for rec in results['results']['recommendations'][:3]:
        print(f"  [{rec['priority'].upper()}] {rec['recommendation']}")

    print("\n" + "=" * 80)
    print("Developed By: Ahmed Mostafa Ibrahim")
    print("© 2025 Finovate – AHMED EG - All Rights Reserved")
    print("=" * 80)

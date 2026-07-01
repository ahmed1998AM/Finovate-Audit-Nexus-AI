"""
Finovate Audit Nexus AI - Executive Intelligence Agent
وكيل التحليل التنفيذي الذكي

المهام:
- تحليل الأداء التنفيذي
- مؤشرات الأداء المالية KPIs
- رؤى استراتيجية
- الصحة المالية الشاملة
- التحليل التنبؤي
- توصيات للإدارة العليا

Developed By: Ahmed Mostafa Ibrahim
© 2025 Finovate – AHMED EG - All Rights Reserved
"""

from datetime import datetime
from typing import Dict, List


class ExecutiveIntelligenceAgent:
    """وكيل التحليل التنفيذي الذكي"""

    def __init__(self):
        self.agent_name = "Executive Intelligence Agent"
        self.agent_type = "executive_analysis"
        self.created_at = datetime.now()

    def analyze_executive_performance(self, financial_data: Dict) -> Dict:
        """تحليل الأداء التنفيذي"""

        results = {
            'agent': self.agent_name,
            'analysis_type': 'Executive Performance Analysis',
            'timestamp': datetime.now().isoformat(),
            'kpis': {},
            'financial_health_score': 0,
            'strategic_insights': [],
            'recommendations': [],
            'risk_alerts': []
        }

        # حساب مؤشرات الأداء الرئيسية KPIs
        kpis = self._calculate_kpis(financial_data)
        results['kpis'] = kpis

        # حساب درجة الصحة المالية
        health_score = self._calculate_financial_health_score(kpis)
        results['financial_health_score'] = health_score

        # توليد الرؤى الاستراتيجية
        insights = self._generate_strategic_insights(kpis, health_score)
        results['strategic_insights'] = insights

        # توليد التوصيات
        recommendations = self._generate_recommendations(kpis, health_score)
        results['recommendations'] = recommendations

        # كشف التنبيهات الحرجة
        alerts = self._identify_critical_alerts(kpis)
        results['risk_alerts'] = alerts

        return results

    def _calculate_kpis(self, data: Dict) -> Dict:
        """حساب مؤشرات الأداء الرئيسية"""

        kpis = {
            'profitability': {},
            'liquidity': {},
            'efficiency': {},
            'leverage': {},
            'growth': {}
        }

        # مؤشرات الربحية
        if 'revenue' in data and 'net_income' in data:
            profit_margin = (data['net_income'] / data['revenue']) * 100 if data['revenue'] > 0 else 0
            kpis['profitability']['net_profit_margin'] = round(profit_margin, 2)

        if 'total_assets' in data and 'net_income' in data:
            roa = (data['net_income'] / data['total_assets']) * 100 if data['total_assets'] > 0 else 0
            kpis['profitability']['roa'] = round(roa, 2)

        if 'equity' in data and 'net_income' in data:
            roe = (data['net_income'] / data['equity']) * 100 if data['equity'] > 0 else 0
            kpis['profitability']['roe'] = round(roe, 2)

        # مؤشرات السيولة
        if 'current_assets' in data and 'current_liabilities' in data:
            current_ratio = data['current_assets'] / data['current_liabilities'] if data['current_liabilities'] > 0 else 0
            kpis['liquidity']['current_ratio'] = round(current_ratio, 2)

        if 'quick_assets' in data and 'current_liabilities' in data:
            quick_ratio = data['quick_assets'] / data['current_liabilities'] if data['current_liabilities'] > 0 else 0
            kpis['liquidity']['quick_ratio'] = round(quick_ratio, 2)

        # مؤشرات الكفاءة
        if 'revenue' in data and 'total_assets' in data:
            asset_turnover = data['revenue'] / data['total_assets'] if data['total_assets'] > 0 else 0
            kpis['efficiency']['asset_turnover'] = round(asset_turnover, 2)

        # مؤشرات الرافعة المالية
        if 'total_debt' in data and 'total_assets' in data:
            debt_ratio = (data['total_debt'] / data['total_assets']) * 100 if data['total_assets'] > 0 else 0
            kpis['leverage']['debt_ratio'] = round(debt_ratio, 2)

        # مؤشرات النمو
        if 'revenue_current' in data and 'revenue_previous' in data:
            revenue_growth = ((data['revenue_current'] - data['revenue_previous']) / data['revenue_previous']) * 100 if data['revenue_previous'] > 0 else 0
            kpis['growth']['revenue_growth'] = round(revenue_growth, 2)

        return kpis

    def _calculate_financial_health_score(self, kpis: Dict) -> float:
        """حساب درجة الصحة المالية الشاملة (0-100)"""

        score = 0

        # تقييم الربحية (30 نقطة)
        if 'profitability' in kpis:
            if kpis['profitability'].get('net_profit_margin', 0) > 10:
                score += 30
            elif kpis['profitability'].get('net_profit_margin', 0) > 5:
                score += 20
            elif kpis['profitability'].get('net_profit_margin', 0) > 0:
                score += 10

        # تقييم السيولة (25 نقطة)
        if 'liquidity' in kpis:
            if kpis['liquidity'].get('current_ratio', 0) > 2:
                score += 25
            elif kpis['liquidity'].get('current_ratio', 0) > 1.5:
                score += 20
            elif kpis['liquidity'].get('current_ratio', 0) > 1:
                score += 10

        # تقييم الكفاءة (20 نقطة)
        if 'efficiency' in kpis:
            if kpis['efficiency'].get('asset_turnover', 0) > 1:
                score += 20
            elif kpis['efficiency'].get('asset_turnover', 0) > 0.5:
                score += 10

        # تقييم الرافعة (15 نقطة)
        if 'leverage' in kpis:
            if kpis['leverage'].get('debt_ratio', 100) < 40:
                score += 15
            elif kpis['leverage'].get('debt_ratio', 100) < 60:
                score += 10

        # تقييم النمو (10 نقاط)
        if 'growth' in kpis:
            if kpis['growth'].get('revenue_growth', 0) > 10:
                score += 10
            elif kpis['growth'].get('revenue_growth', 0) > 0:
                score += 5

        return round(score, 2)

    def _generate_strategic_insights(self, kpis: Dict, health_score: float) -> List[str]:
        """توليد الرؤى الاستراتيجية"""

        insights = []

        # رؤى عامة
        if health_score >= 80:
            insights.append("✅ الصحة المالية ممتازة - الشركة في وضع قوي جداً")
        elif health_score >= 60:
            insights.append("🟡 الصحة المالية جيدة - هناك مجال للتحسين")
        elif health_score >= 40:
            insights.append("⚠️ الصحة المالية متوسطة - تحتاج إلى تحسينات جوهرية")
        else:
            insights.append("🔴 الصحة المالية ضعيفة - تحتاج إلى تدخل عاجل")

        # رؤى الربحية
        if 'profitability' in kpis:
            roe = kpis['profitability'].get('roe', 0)
            if roe > 15:
                insights.append("📈 العائد على حقوق المساهمين ممتاز (%{})".format(round(roe, 2)))
            elif roe < 5:
                insights.append("📉 العائد على حقوق المساهمين منخفض - يحتاج تحسين")

        # رؤى السيولة
        if 'liquidity' in kpis:
            current_ratio = kpis['liquidity'].get('current_ratio', 0)
            if current_ratio < 1:
                insights.append("⚠️ نسبة التداول أقل من 1 - خطر سيولة محتمل")
            elif current_ratio > 3:
                insights.append("💰 نسبة تداول مرتفعة جداً - قد تكون هناك أموال معطلة")

        # رؤى النمو
        if 'growth' in kpis:
            growth = kpis['growth'].get('revenue_growth', 0)
            if growth > 20:
                insights.append("🚀 نمو إيرادات استثنائي (%{})".format(round(growth, 2)))
            elif growth < 0:
                insights.append("📉 انكماش في الإيرادات - يحتاج استراتيجية نمو")

        return insights

    def _generate_recommendations(self, kpis: Dict, health_score: float) -> List[Dict]:
        """توليد التوصيات الاستراتيجية"""

        recommendations = []

        # توصيات الربحية
        if 'profitability' in kpis:
            if kpis['profitability'].get('net_profit_margin', 0) < 5:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Profitability',
                    'recommendation': 'مراجعة هيكل التكاليف وزيادة الهوامش الربحية',
                    'actions': [
                        'تحليل التكاليف الثابتة والمتغيرة',
                        'إعادة التفاوض مع الموردين',
                        'رفع الأسعار بشكل استراتيجي'
                    ]
                })

        # توصيات السيولة
        if 'liquidity' in kpis:
            if kpis['liquidity'].get('current_ratio', 0) < 1.5:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'category': 'Liquidity',
                    'recommendation': 'تحسين السيولة العاجلة',
                    'actions': [
                        'تسريع تحصيل المستحقات',
                        'إعادة جدولة الديون قصيرة الأجل',
                        'تقليل المخزون الراكد'
                    ]
                })

        # توصيات الرافعة
        if 'leverage' in kpis:
            if kpis['leverage'].get('debt_ratio', 0) > 60:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Leverage',
                    'recommendation': 'خفض نسبة المديونية',
                    'actions': [
                        'إعادة هيكلة الديون',
                        'زيادة رأس المال',
                        'تحويل الديون إلى حقوق ملكية'
                    ]
                })

        return recommendations

    def _identify_critical_alerts(self, kpis: Dict) -> List[Dict]:
        """كشف التنبيهات الحرجة"""

        alerts = []

        # تنبيهات السيولة
        if 'liquidity' in kpis:
            if kpis['liquidity'].get('current_ratio', 0) < 1:
                alerts.append({
                    'severity': 'CRITICAL',
                    'type': 'Liquidity Crisis',
                    'message': 'نسبة التداول أقل من 1 - خطر عدم القدرة على سداد الالتزامات',
                    'immediate_action_required': True
                })

        # تنبيهات الربحية
        if 'profitability' in kpis:
            if kpis['profitability'].get('net_profit_margin', 0) < 0:
                alerts.append({
                    'severity': 'HIGH',
                    'type': 'Operating Loss',
                    'message': 'الشركة تحقق خسائر تشغيلية',
                    'immediate_action_required': True
                })

        # تنبيهات الرافعة
        if 'leverage' in kpis:
            if kpis['leverage'].get('debt_ratio', 0) > 80:
                alerts.append({
                    'severity': 'HIGH',
                    'type': 'Excessive Debt',
                    'message': 'نسبة المديونية خطيرة (>80%)',
                    'immediate_action_required': True
                })

        return alerts

    def generate_executive_dashboard(self, analysis_results: Dict) -> Dict:
        """إنشاء لوحة قيادة تنفيذية"""

        dashboard = {
            'title': 'Executive Intelligence Dashboard',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'financial_health_score': analysis_results.get('financial_health_score', 0),
                'total_kpis_tracked': len(analysis_results.get('kpis', {})),
                'critical_alerts': len(analysis_results.get('risk_alerts', [])),
                'strategic_insights_count': len(analysis_results.get('strategic_insights', [])),
                'recommendations_count': len(analysis_results.get('recommendations', []))
            },
            'health_status': '',
            'key_highlights': [],
            'action_items': []
        }

        # تحديد حالة الصحة
        score = dashboard['summary']['financial_health_score']
        if score >= 80:
            dashboard['health_status'] = 'EXCELLENT'
        elif score >= 60:
            dashboard['health_status'] = 'GOOD'
        elif score >= 40:
            dashboard['health_status'] = 'FAIR'
        else:
            dashboard['health_status'] = 'POOR'

        # أبرز النقاط
        dashboard['key_highlights'] = analysis_results.get('strategic_insights', [])[:5]

        # بنود العمل
        for rec in analysis_results.get('recommendations', [])[:3]:
            dashboard['action_items'].append({
                'priority': rec.get('priority', 'MEDIUM'),
                'action': rec.get('recommendation', ''),
                'category': rec.get('category', '')
            })

        return dashboard


# === مثال على الاستخدام ===
if __name__ == "__main__":
    print("=" * 70)
    print("Finovate Audit Nexus AI - Executive Intelligence Agent")
    print("=" * 70)

    agent = ExecutiveIntelligenceAgent()

    # بيانات مالية تجريبية
    sample_data = {
        'revenue': 10000000,
        'net_income': 1500000,
        'total_assets': 25000000,
        'equity': 15000000,
        'current_assets': 8000000,
        'current_liabilities': 4000000,
        'quick_assets': 5000000,
        'total_debt': 10000000,
        'revenue_current': 10000000,
        'revenue_previous': 8500000
    }

    print("\n📊 جاري تحليل الأداء التنفيذي...")
    results = agent.analyze_executive_performance(sample_data)

    print(f"\n{'='*70}")
    print("نتائج التحليل التنفيذي")
    print(f"{'='*70}")

    print(f"\n📈 درجة الصحة المالية: {results['financial_health_score']}/100")

    print("\n📊 مؤشرات الأداء الرئيسية:")
    kpis = results['kpis']
    for category, metrics in kpis.items():
        if metrics:
            print(f"\n  {category.upper()}:")
            for metric, value in metrics.items():
                print(f"    • {metric}: {value}")

    print("\n💡 الرؤى الاستراتيجية:")
    for insight in results['strategic_insights']:
        print(f"  {insight}")

    print("\n🎯 التوصيات:")
    for rec in results['recommendations']:
        print(f"\n  [{rec['priority']}] {rec['category']}")
        print(f"  → {rec['recommendation']}")
        print("  الإجراءات:")
        for action in rec['actions']:
            print(f"    • {action}")

    if results['risk_alerts']:
        print("\n⚠️ التنبيهات الحرجة:")
        for alert in results['risk_alerts']:
            print(f"\n  [{alert['severity']}] {alert['type']}")
            print(f"  → {alert['message']}")
            if alert['immediate_action_required']:
                print("  🚨 يتطلب تدخلاً عاجلاً!")

    # إنشاء لوحة القيادة
    print(f"\n{'='*70}")
    print("لوحة القيادة التنفيذية")
    print(f"{'='*70}")

    dashboard = agent.generate_executive_dashboard(results)
    print(f"\nالحالة الصحية: {dashboard['health_status']}")
    print(f"عدد مؤشرات الأداء: {dashboard['summary']['total_kpis_tracked']}")
    print(f"التنبيهات الحرجة: {dashboard['summary']['critical_alerts']}")
    print(f"الرؤى الاستراتيجية: {dashboard['summary']['strategic_insights_count']}")
    print(f"التوصيات: {dashboard['summary']['recommendations_count']}")

    print(f"\n{'='*70}")
    print("✅ اكتمل التحليل التنفيذي بنجاح!")
    print(f"{'='*70}\n")

"""
Analytics Service - خدمة التحليلات المالية والذكاء الاصطناعي
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    خدمة التحليلات المالية والذكاء الاصطناعي
    
    المسؤولة عن:
    - التحليل المالي
    - تحليل النسب
    - تحليل الاتجاهات
    - التنبؤ المالي
    - كشف الأنماط
    - تقييم المخاطر
    """
    
    def __init__(self):
        """تهيئة خدمة التحليلات"""
        self.analysis_cache = {}
        logger.info("AnalyticsService initialized")
    
    def calculate_financial_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        حساب النسب المالية
        
        Args:
            financial_data: البيانات المالية
            
        Returns:
            النسب المحسوبة
        """
        logger.info("Calculating financial ratios")
        
        ratios = {
            'liquidity_ratios': {},
            'profitability_ratios': {},
            'leverage_ratios': {},
            'efficiency_ratios': {},
            'calculated_at': datetime.now()
        }
        
        # نسب السيولة
        if 'current_assets' in financial_data and 'current_liabilities' in financial_data:
            ca = financial_data['current_assets']
            cl = financial_data['current_liabilities']
            
            ratios['liquidity_ratios']['current_ratio'] = round(ca / cl, 2) if cl > 0 else 0
            ratios['liquidity_ratios']['quick_ratio'] = round((ca - financial_data.get('inventory', 0)) / cl, 2) if cl > 0 else 0
        
        # نسب الربحية
        if 'net_income' in financial_data and 'revenue' in financial_data:
            ni = financial_data['net_income']
            rev = financial_data['revenue']
            
            ratios['profitability_ratios']['gross_profit_margin'] = round((rev - financial_data.get('cogs', 0)) / rev * 100, 2) if rev > 0 else 0
            ratios['profitability_ratios']['net_profit_margin'] = round(ni / rev * 100, 2) if rev > 0 else 0
            ratios['profitability_ratios']['roe'] = round(ni / financial_data.get('equity', 1) * 100, 2)
        
        # نسب الرافعة المالية
        if 'total_debt' in financial_data and 'total_assets' in financial_data:
            ratios['leverage_ratios']['debt_to_assets'] = round(financial_data['total_debt'] / financial_data['total_assets'], 2)
            ratios['leverage_ratios']['debt_to_equity'] = round(financial_data['total_debt'] / financial_data.get('equity', 1), 2)
        
        # نسب الكفاءة
        if 'revenue' in financial_data and 'accounts_receivable' in financial_data:
            ratios['efficiency_ratios']['receivables_turnover'] = round(financial_data['revenue'] / financial_data['accounts_receivable'], 2)
        
        return ratios
    
    def analyze_trends(self, historical_data: List[Dict[str, Any]], metric: str) -> Dict[str, Any]:
        """
        تحليل الاتجاهات
        
        Args:
            historical_data: البيانات التاريخية
            metric: المقياس المطلوب تحليله
            
        Returns:
            نتيجة التحليل
        """
        logger.info(f"Analyzing trends for {metric}")
        
        if len(historical_data) < 2:
            return {'error': 'Insufficient data'}
        
        values = [d.get(metric, 0) for d in historical_data]
        dates = [d.get('date', '') for d in historical_data]
        
        # حساب معدل النمو
        growth_rates = []
        for i in range(1, len(values)):
            if values[i-1] > 0:
                growth_rate = ((values[i] - values[i-1]) / values[i-1]) * 100
                growth_rates.append(growth_rate)
        
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0
        
        # تحديد الاتجاه
        if avg_growth > 5:
            trend = 'strong_upward'
        elif avg_growth > 0:
            trend = 'upward'
        elif avg_growth > -5:
            trend = 'stable'
        elif avg_growth > -10:
            trend = 'downward'
        else:
            trend = 'strong_downward'
        
        return {
            'metric': metric,
            'trend': trend,
            'average_growth_rate': round(avg_growth, 2),
            'min_value': min(values),
            'max_value': max(values),
            'latest_value': values[-1],
            'data_points': len(values),
            'period': f"{dates[0]} to {dates[-1]}" if dates else 'N/A'
        }
    
    def detect_anomalies(self, data: List[Dict[str, Any]], threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        كشف الشذوذ في البيانات
        
        Args:
            data: البيانات
            threshold: عتبة الكشف (عدد الانحرافات المعيارية)
            
        Returns:
            قائمة بالشذوذ المكتشف
        """
        logger.info(f"Detecting anomalies with threshold {threshold}")
        
        anomalies = []
        
        if not data:
            return anomalies
        
        # تحليل القيم
        numeric_values = []
        for item in data:
            for key, value in item.items():
                if isinstance(value, (int, float)):
                    numeric_values.append((item, key, value))
        
        if not numeric_values:
            return anomalies
        
        values = [v[2] for v in numeric_values]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # كشف القيم الشاذة
        for item, key, value in numeric_values:
            z_score = abs(value - mean) / std_dev if std_dev > 0 else 0
            
            if z_score > threshold:
                anomalies.append({
                    'item': item,
                    'field': key,
                    'value': value,
                    'z_score': round(z_score, 2),
                    'mean': round(mean, 2),
                    'std_dev': round(std_dev, 2),
                    'severity': 'high' if z_score > 3 else 'medium'
                })
        
        return anomalies
    
    def calculate_risk_score(self, risk_factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        حساب درجة المخاطرة
        
        Args:
            risk_factors: عوامل المخاطرة
            
        Returns:
            درجة المخاطرة
        """
        logger.info("Calculating risk score")
        
        weights = {
            'financial_risk': 0.25,
            'compliance_risk': 0.25,
            'fraud_risk': 0.30,
            'operational_risk': 0.20
        }
        
        total_score = 0
        
        for factor, weight in weights.items():
            factor_score = risk_factors.get(factor, 0)
            total_score += factor_score * weight
        
        risk_level = 'low'
        if total_score > 75:
            risk_level = 'critical'
        elif total_score > 50:
            risk_level = 'high'
        elif total_score > 25:
            risk_level = 'medium'
        
        return {
            'overall_score': round(total_score, 2),
            'risk_level': risk_level,
            'factor_scores': {
                'financial_risk': risk_factors.get('financial_risk', 0),
                'compliance_risk': risk_factors.get('compliance_risk', 0),
                'fraud_risk': risk_factors.get('fraud_risk', 0),
                'operational_risk': risk_factors.get('operational_risk', 0)
            },
            'weights': weights,
            'calculated_at': datetime.now()
        }
    
    def generate_insights(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        توليد رؤى ذكية
        
        Args:
            analysis_results: نتائج التحليل
            
        Returns:
            قائمة بالرؤى
        """
        insights = []
        
        # تحليل النسب
        if 'ratios' in analysis_results:
            ratios = analysis_results['ratios']
            
            if ratios.get('liquidity_ratios', {}).get('current_ratio', 0) < 1:
                insights.append({
                    'type': 'warning',
                    'category': 'liquidity',
                    'title': 'انخفاض السيولة',
                    'description': 'نسبة التداول أقل من 1، مما قد يشير إلى صعوبات في سداد الالتزامات قصيرة الأجل',
                    'recommendation': 'مراجعة إدارة رأس المال العامل'
                })
            
            if ratios.get('profitability_ratios', {}).get('net_profit_margin', 0) < 5:
                insights.append({
                    'type': 'warning',
                    'category': 'profitability',
                    'title': 'انخفاض هامش الربح',
                    'description': 'هامش صافي الربح أقل من 5%',
                    'recommendation': 'مراجعة هيكل التكاليف والأسعار'
                })
        
        # تحليل الاتجاهات
        if 'trends' in analysis_results:
            for metric, trend_data in analysis_results['trends'].items():
                if trend_data.get('trend') == 'strong_downward':
                    insights.append({
                        'type': 'alert',
                        'category': 'trend',
                        'title': f'تراجع قوي في {metric}',
                        'description': f'معدل نمو سلبي: {trend_data.get("average_growth_rate", 0)}%',
                        'recommendation': 'التحقيق في أسباب التراجع واتخاذ إجراءات تصحيحية'
                    })
        
        # كشف الشذوذ
        if 'anomalies' in analysis_results and analysis_results['anomalies']:
            high_severity = [a for a in analysis_results['anomalies'] if a.get('severity') == 'high']
            if high_severity:
                insights.append({
                    'type': 'critical',
                    'category': 'anomaly',
                    'title': f'تم اكتشاف {len(high_severity)} قيم شاذة عالية الخطورة',
                    'description': 'توجد قيم غير طبيعية تتطلب مراجعة فورية',
                    'recommendation': 'فحص القيود والمعاملات المشتبه بها'
                })
        
        return insights
    
    def get_dashboard_metrics(self, company_id: int) -> Dict[str, Any]:
        """
        الحصول على مقاييس لوحة التحكم
        
        Args:
            company_id: معرف الشركة
            
        Returns:
            المقاييس
        """
        logger.info(f"Getting dashboard metrics for company {company_id}")
        
        return {
            'company_id': company_id,
            'financial_health_score': 78,
            'risk_score': 35,
            'compliance_score': 92,
            'active_audits': 3,
            'pending_findings': 12,
            'critical_alerts': 2,
            'last_sync': datetime.now(),
            'kpi_summary': {
                'revenue_growth': 8.5,
                'profit_margin': 12.3,
                'current_ratio': 1.8,
                'debt_to_equity': 0.45
            }
        }

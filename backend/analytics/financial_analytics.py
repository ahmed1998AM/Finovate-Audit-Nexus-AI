"""
Finovate Audit Nexus AI - Financial Analytics Engine
محرك التحليلات المالية المتقدم
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class FinancialAnalyticsEngine:
    """
    محرك التحليلات المالية الشامل
    يقوم بتحليل البيانات المالية وإنتاج رؤى عميقة
    """
    
    def __init__(self):
        self.data = None
        self.results = {}
        self.indicators = {}
        
    def load_data(self, data: pd.DataFrame) -> None:
        """تحميل البيانات المالية"""
        self.data = data
        self.results = {}
        
    def calculate_liquidity_ratios(self) -> Dict[str, float]:
        """حساب نسب السيولة"""
        if self.data is None:
            return {}
            
        ratios = {}
        
        # النسبة الجارية
        if 'current_assets' in self.data.columns and 'current_liabilities' in self.data.columns:
            ratios['current_ratio'] = (
                self.data['current_assets'].sum() / 
                self.data['current_liabilities'].replace(0, np.nan).sum()
            )
            
        # النسبة السريعة
        if 'quick_assets' in self.data.columns and 'current_liabilities' in self.data.columns:
            ratios['quick_ratio'] = (
                self.data['quick_assets'].sum() / 
                self.data['current_liabilities'].replace(0, np.nan).sum()
            )
            
        # نسبة النقدية
        if 'cash' in self.data.columns and 'current_liabilities' in self.data.columns:
            ratios['cash_ratio'] = (
                self.data['cash'].sum() / 
                self.data['current_liabilities'].replace(0, np.nan).sum()
            )
            
        self.results['liquidity_ratios'] = ratios
        return ratios
    
    def calculate_profitability_ratios(self) -> Dict[str, float]:
        """حساب نسب الربحية"""
        if self.data is None:
            return {}
            
        ratios = {}
        
        # هامش الربح الصافي
        if 'net_income' in self.data.columns and 'revenue' in self.data.columns:
            ratios['net_profit_margin'] = (
                self.data['net_income'].sum() / 
                self.data['revenue'].replace(0, np.nan).sum() * 100
            )
            
        # العائد على الأصول (ROA)
        if 'net_income' in self.data.columns and 'total_assets' in self.data.columns:
            ratios['roa'] = (
                self.data['net_income'].sum() / 
                self.data['total_assets'].replace(0, np.nan).sum() * 100
            )
            
        # العائد على حقوق الملكية (ROE)
        if 'net_income' in self.data.columns and 'shareholders_equity' in self.data.columns:
            ratios['roe'] = (
                self.data['net_income'].sum() / 
                self.data['shareholders_equity'].replace(0, np.nan).sum() * 100
            )
            
        # هامش الربح الإجمالي
        if 'gross_profit' in self.data.columns and 'revenue' in self.data.columns:
            ratios['gross_profit_margin'] = (
                self.data['gross_profit'].sum() / 
                self.data['revenue'].replace(0, np.nan).sum() * 100
            )
            
        self.results['profitability_ratios'] = ratios
        return ratios
    
    def calculate_leverage_ratios(self) -> Dict[str, float]:
        """حساب نسب الرافعة المالية"""
        if self.data is None:
            return {}
            
        ratios = {}
        
        # نسبة الدين إلى الأصول
        if 'total_debt' in self.data.columns and 'total_assets' in self.data.columns:
            ratios['debt_to_assets'] = (
                self.data['total_debt'].sum() / 
                self.data['total_assets'].replace(0, np.nan).sum() * 100
            )
            
        # نسبة الدين إلى حقوق الملكية
        if 'total_debt' in self.data.columns and 'shareholders_equity' in self.data.columns:
            ratios['debt_to_equity'] = (
                self.data['total_debt'].sum() / 
                self.data['shareholders_equity'].replace(0, np.nan).sum() * 100
            )
            
        # نسبة تغطية الفائدة
        if 'ebit' in self.data.columns and 'interest_expense' in self.data.columns:
            ratios['interest_coverage'] = (
                self.data['ebit'].sum() / 
                self.data['interest_expense'].replace(0, np.nan).sum()
            )
            
        self.results['leverage_ratios'] = ratios
        return ratios
    
    def calculate_efficiency_ratios(self) -> Dict[str, float]:
        """حساب نسب الكفاءة"""
        if self.data is None:
            return {}
            
        ratios = {}
        
        # معدل دوران المخزون
        if 'cost_of_goods_sold' in self.data.columns and 'inventory' in self.data.columns:
            ratios['inventory_turnover'] = (
                self.data['cost_of_goods_sold'].sum() / 
                self.data['inventory'].replace(0, np.nan).mean()
            )
            
        # معدل دوران الذمم المدينة
        if 'revenue' in self.data.columns and 'accounts_receivable' in self.data.columns:
            ratios['receivables_turnover'] = (
                self.data['revenue'].sum() / 
                self.data['accounts_receivable'].replace(0, np.nan).mean()
            )
            
        # متوسط فترة التحصيل
        if 'receivables_turnover' in ratios:
            ratios['days_sales_outstanding'] = 365 / ratios['receivables_turnover']
            
        self.results['efficiency_ratios'] = ratios
        return ratios
    
    def generate_financial_health_score(self) -> Dict[str, Any]:
        """توليد درجة الصحة المالية الشاملة"""
        if not self.results:
            # حساب جميع النسب أولاً
            self.calculate_liquidity_ratios()
            self.calculate_profitability_ratios()
            self.calculate_leverage_ratios()
            self.calculate_efficiency_ratios()
            
        score = 0
        max_score = 100
        breakdown = {}
        
        # تقييم السيولة (25 نقطة)
        liquidity_score = 0
        if 'liquidity_ratios' in self.results:
            lr = self.results['liquidity_ratios']
            if lr.get('current_ratio', 0) >= 1.5:
                liquidity_score += 10
            elif lr.get('current_ratio', 0) >= 1.0:
                liquidity_score += 5
                
            if lr.get('quick_ratio', 0) >= 1.0:
                liquidity_score += 10
            elif lr.get('quick_ratio', 0) >= 0.5:
                liquidity_score += 5
                
            if lr.get('cash_ratio', 0) >= 0.5:
                liquidity_score += 5
                
        breakdown['liquidity'] = min(liquidity_score, 25)
        score += breakdown['liquidity']
        
        # تقييم الربحية (30 نقطة)
        profitability_score = 0
        if 'profitability_ratios' in self.results:
            pr = self.results['profitability_ratios']
            if pr.get('net_profit_margin', 0) >= 15:
                profitability_score += 10
            elif pr.get('net_profit_margin', 0) >= 5:
                profitability_score += 5
                
            if pr.get('roe', 0) >= 15:
                profitability_score += 10
            elif pr.get('roe', 0) >= 10:
                profitability_score += 5
                
            if pr.get('roa', 0) >= 8:
                profitability_score += 10
            elif pr.get('roa', 0) >= 5:
                profitability_score += 5
                
        breakdown['profitability'] = min(profitability_score, 30)
        score += breakdown['profitability']
        
        # تقييم الرافعة المالية (25 نقطة)
        leverage_score = 25  # نبدأ من 25 ونخصم
        if 'leverage_ratios' in self.results:
            lvr = self.results['leverage_ratios']
            if lvr.get('debt_to_assets', 100) > 70:
                leverage_score -= 10
            elif lvr.get('debt_to_assets', 100) > 50:
                leverage_score -= 5
                
            if lvr.get('debt_to_equity', 100) > 100:
                leverage_score -= 10
            elif lvr.get('debt_to_equity', 100) > 50:
                leverage_score -= 5
                
            if lvr.get('interest_coverage', 0) < 2:
                leverage_score -= 5
            elif lvr.get('interest_coverage', 0) < 3:
                leverage_score -= 2
                
        breakdown['leverage'] = max(leverage_score, 0)
        score += breakdown['leverage']
        
        # تقييم الكفاءة (20 نقطة)
        efficiency_score = 0
        if 'efficiency_ratios' in self.results:
            er = self.results['efficiency_ratios']
            if er.get('inventory_turnover', 0) >= 6:
                efficiency_score += 10
            elif er.get('inventory_turnover', 0) >= 3:
                efficiency_score += 5
                
            if er.get('receivables_turnover', 0) >= 8:
                efficiency_score += 10
            elif er.get('receivables_turnover', 0) >= 4:
                efficiency_score += 5
                
        breakdown['efficiency'] = min(efficiency_score, 20)
        score += breakdown['efficiency']
        
        # تحديد التصنيف
        if score >= 85:
            rating = "ممتاز"
            color = "green"
        elif score >= 70:
            rating = "جيد جداً"
            color = "lightgreen"
        elif score >= 55:
            rating = "جيد"
            color = "yellow"
        elif score >= 40:
            rating = "متوسط"
            color = "orange"
        else:
            rating = "ضعيف"
            color = "red"
            
        return {
            'overall_score': score,
            'max_score': max_score,
            'rating': rating,
            'color': color,
            'breakdown': breakdown,
            'timestamp': datetime.now().isoformat(),
            'ratios_summary': self.results
        }
    
    def detect_financial_anomalies(self) -> List[Dict[str, Any]]:
        """كشف الشذوذ المالي"""
        anomalies = []
        
        if self.data is None or self.results is None:
            return anomalies
            
        # تحليل التغيرات الكبيرة
        if 'profitability_ratios' in self.results:
            net_margin = self.results['profitability_ratios'].get('net_profit_margin', 0)
            if net_margin < 0:
                anomalies.append({
                    'type': 'negative_profit_margin',
                    'severity': 'high',
                    'description': 'هامش ربح صافي سالب - الشركة تحقق خسائر',
                    'value': net_margin,
                    'recommendation': 'مراجعة هيكل التكاليف والإيرادات'
                })
                
        if 'leverage_ratios' in self.results:
            debt_ratio = self.results['leverage_ratios'].get('debt_to_assets', 0)
            if debt_ratio > 70:
                anomalies.append({
                    'type': 'high_debt_ratio',
                    'severity': 'medium',
                    'description': 'نسبة دين مرتفعة جداً مقارنة بالأصول',
                    'value': debt_ratio,
                    'recommendation': 'إعادة هيكلة الديون أو زيادة رأس المال'
                })
                
        if 'liquidity_ratios' in self.results:
            current_ratio = self.results['liquidity_ratios'].get('current_ratio', 0)
            if current_ratio < 1.0:
                anomalies.append({
                    'type': 'low_liquidity',
                    'severity': 'high',
                    'description': 'سيولة منخفضة - قد تواجه صعوبة في سداد الالتزامات قصيرة الأجل',
                    'value': current_ratio,
                    'recommendation': 'تحسين إدارة رأس المال العامل'
                })
                
        return anomalies
    
    def export_analysis(self, format: str = 'json') -> str:
        """تصدير نتائج التحليل"""
        analysis_result = {
            'financial_health': self.generate_financial_health_score(),
            'anomalies': self.detect_financial_anomalies(),
            'detailed_ratios': self.results,
            'export_timestamp': datetime.now().isoformat()
        }
        
        if format == 'json':
            return json.dumps(analysis_result, indent=2, ensure_ascii=False)
        elif format == 'dict':
            return analysis_result
        else:
            return json.dumps(analysis_result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # مثال اختباري
    print("=" * 60)
    print("Finovate Analytics Engine - Test")
    print("=" * 60)
    
    # إنشاء بيانات تجريبية
    test_data = pd.DataFrame({
        'current_assets': [500000, 550000, 600000],
        'current_liabilities': [300000, 320000, 350000],
        'quick_assets': [350000, 380000, 420000],
        'cash': [150000, 160000, 180000],
        'total_assets': [1500000, 1600000, 1700000],
        'total_debt': [600000, 650000, 700000],
        'shareholders_equity': [900000, 950000, 1000000],
        'revenue': [2000000, 2200000, 2400000],
        'net_income': [250000, 280000, 300000],
        'gross_profit': [800000, 880000, 960000],
        'ebit': [400000, 450000, 480000],
        'interest_expense': [50000, 55000, 60000],
        'inventory': [150000, 170000, 180000],
        'accounts_receivable': [200000, 220000, 240000],
        'cost_of_goods_sold': [1200000, 1320000, 1440000]
    })
    
    engine = FinancialAnalyticsEngine()
    engine.load_data(test_data)
    
    # حساب جميع النسب
    print("\n📊 Liquidity Ratios:")
    print(engine.calculate_liquidity_ratios())
    
    print("\n💰 Profitability Ratios:")
    print(engine.calculate_profitability_ratios())
    
    print("\n📈 Leverage Ratios:")
    print(engine.calculate_leverage_ratios())
    
    print("\n⚙️ Efficiency Ratios:")
    print(engine.calculate_efficiency_ratios())
    
    print("\n🏥 Financial Health Score:")
    health = engine.generate_financial_health_score()
    print(f"Overall Score: {health['overall_score']}/{health['max_score']}")
    print(f"Rating: {health['rating']} ({health['color']})")
    print(f"Breakdown: {health['breakdown']}")
    
    print("\n⚠️ Anomalies Detected:")
    anomalies = engine.detect_financial_anomalies()
    for anomaly in anomalies:
        print(f"- {anomaly['description']} (Severity: {anomaly['severity']})")
    
    print("\n✅ Analytics Engine Test Complete!")

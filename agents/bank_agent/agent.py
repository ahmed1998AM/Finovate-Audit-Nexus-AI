"""
Finovate Audit Nexus AI
Bank & Treasury Audit Agent
وكيل مراجعة البنوك والخزينة

Developed By: Ahmed Mostafa Ibrahim
© 2025 Finovate – AHMED EG - All Rights Reserved
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import hashlib
import re


@dataclass
class BankTransaction:
    """هيكل بيانات معاملة بنكية"""
    transaction_id: str
    date: datetime
    description: str
    amount: float
    balance: float
    transaction_type: str
    reference: str
    counterparty: str
    status: str = "processed"


@dataclass
class BankReconciliationItem:
    """عنصر تسوية بنكية"""
    bank_statement_id: str
    ledger_id: str
    amount: float
    date_bank: datetime
    date_ledger: datetime
    difference: float
    status: str  # matched, outstanding, discrepancy
    notes: str = ""


@dataclass
class SuspiciousActivity:
    """نشاط مشبوه مكتشف"""
    activity_id: str
    transaction_ids: List[str]
    activity_type: str
    risk_score: float
    description: str
    evidence: List[str]
    recommended_action: str
    detected_at: datetime = field(default_factory=datetime.now)


class BankAuditAgent:
    """
    وكيل مراجعة البنوك والخزينة
    
    المهام:
    - مطابقة البنوك (Bank Reconciliation)
    - كشف الحركات المشبوهة
    - كشف التكرار
    - تحليل التدفقات النقدية
    - مراجعة التسويات البنكية
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.name = "Bank & Treasury Audit Agent"
        self.version = "1.0.0"
        self.suspicious_activities: List[SuspiciousActivity] = []
        self.reconciliation_items: List[BankReconciliationItem] = []
        
        # عتبات الكشف
        self.large_transaction_threshold = self.config.get('large_transaction_threshold', 100000)
        self.round_amount_threshold = self.config.get('round_amount_threshold', 10000)
        self.frequency_window_days = self.config.get('frequency_window_days', 7)
        self.same_amount_threshold = self.config.get('same_amount_threshold', 3)
        
    def analyze_bank_statement(
        self, 
        bank_statement: pd.DataFrame,
        bank_name: str = "Unknown Bank"
    ) -> Dict[str, Any]:
        """
        تحليل كشف حساب بنكي شامل
        
        Args:
            bank_statement: DataFrame يحتوي على حركات البنك
            bank_name: اسم البنك
            
        Returns:
            تقرير تحليل شامل
        """
        results = {
            'bank_name': bank_name,
            'analysis_date': datetime.now().isoformat(),
            'summary': {},
            'reconciliation': [],
            'suspicious_activities': [],
            'cash_flow_analysis': {},
            'recommendations': []
        }
        
        # التحقق من البيانات المطلوبة
        required_columns = ['date', 'amount', 'description']
        missing_cols = [col for col in required_columns if col not in bank_statement.columns]
        
        if missing_cols:
            return {
                'status': 'error',
                'message': f'Missing required columns: {missing_cols}',
                'results': results
            }
        
        # تحويل التواريخ
        bank_statement['date'] = pd.to_datetime(bank_statement['date'])
        
        # التحليل الأساسي
        results['summary'] = self._calculate_bank_summary(bank_statement)
        
        # مطابقة البنك
        results['reconciliation'] = self._perform_bank_reconciliation(bank_statement)
        
        # كشف الأنشطة المشبوهة
        suspicious = self._detect_suspicious_activities(bank_statement)
        results['suspicious_activities'] = [vars(s) for s in suspicious]
        self.suspicious_activities.extend(suspicious)
        
        # تحليل التدفق النقدي
        results['cash_flow_analysis'] = self._analyze_cash_flow(bank_statement)
        
        # التوصيات
        results['recommendations'] = self._generate_bank_recommendations(
            results['summary'],
            suspicious,
            results['reconciliation']
        )
        
        return {
            'status': 'success',
            'message': f'Bank analysis completed for {bank_name}',
            'results': results
        }
    
    def _calculate_bank_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """حساب ملخص إحصائيات البنك"""
        
        total_transactions = len(df)
        total_deposits = df[df['amount'] > 0]['amount'].sum()
        total_withdrawals = abs(df[df['amount'] < 0]['amount'].sum())
        net_flow = total_deposits - total_withdrawals
        
        avg_transaction = df['amount'].abs().mean()
        max_transaction = df['amount'].abs().max()
        min_transaction = df['amount'].abs().min()
        
        # تحليل حسب النوع
        transaction_types = df['transaction_type'].value_counts().to_dict() if 'transaction_type' in df.columns else {}
        
        # أكبر 10 معاملات
        top_10_deposits = df.nlargest(10, 'amount')[['date', 'amount', 'description']].to_dict('records') if 'amount' in df.columns else []
        top_10_withdrawals = df.nsmallest(10, 'amount')[['date', 'amount', 'description']].to_dict('records') if 'amount' in df.columns else []
        
        return {
            'total_transactions': int(total_transactions),
            'total_deposits': float(total_deposits),
            'total_withdrawals': float(total_withdrawals),
            'net_flow': float(net_flow),
            'average_transaction': float(avg_transaction),
            'max_transaction': float(max_transaction),
            'min_transaction': float(min_transaction),
            'transaction_types': transaction_types,
            'top_10_deposits': top_10_deposits,
            'top_10_withdrawals': top_10_withdrawals,
            'analysis_period': {
                'start_date': df['date'].min().isoformat() if 'date' in df.columns else None,
                'end_date': df['date'].max().isoformat() if 'date' in df.columns else None,
                'days_covered': (df['date'].max() - df['date'].min()).days if 'date' in df.columns else 0
            }
        }
    
    def _perform_bank_reconciliation(
        self, 
        bank_statement: pd.DataFrame,
        ledger_data: Optional[pd.DataFrame] = None
    ) -> List[Dict[str, Any]]:
        """
        إجراء مطابقة بنكية
        
        Args:
            bank_statement: كشف الحساب البنكي
            ledger_data: بيانات دفتر الأستاذ للمقارنة
            
        Returns:
            قائمة بنتائج المطابقة
        """
        reconciliation_results = []
        
        if ledger_data is None:
            # مطابقة داخلية فقط
            reconciliation_results = self._internal_reconciliation(bank_statement)
        else:
            # مطابقة بين البنك والدفتر
            reconciliation_results = self._external_reconciliation(bank_statement, ledger_data)
        
        return reconciliation_results
    
    def _internal_reconciliation(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """مطابقة داخلية لكشف الحساب"""
        
        results = []
        
        # كشف المعاملات المكررة المحتملة
        duplicates = self._find_duplicate_transactions(df)
        
        for idx, dup_group in enumerate(duplicates):
            rec_item = {
                'reconciliation_id': f'REC-INT-{idx+1:04d}',
                'type': 'potential_duplicate',
                'transaction_ids': dup_group['transaction_ids'],
                'amount': dup_group['amount'],
                'dates': [d.isoformat() for d in dup_group['dates']],
                'difference': 0,
                'status': 'requires_review',
                'description': f'Potential duplicate transactions detected: {len(dup_group["transaction_ids"])} transactions with same amount',
                'recommended_action': 'Review transactions for actual duplication'
            }
            results.append(rec_item)
        
        # كشف الفروقات الزمنية غير الطبيعية
        timing_issues = self._detect_timing_anomalies(df)
        results.extend(timing_issues)
        
        return results
    
    def _external_reconciliation(
        self, 
        bank_df: pd.DataFrame, 
        ledger_df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """مطابقة بين البنك ودفتر الأستاذ"""
        
        results = []
        
        # تطابق بناءً على المبلغ والتاريخ
        bank_df_copy = bank_df.copy()
        ledger_df_copy = ledger_df.copy()
        
        bank_df_copy['date'] = pd.to_datetime(bank_df_copy['date'])
        ledger_df_copy['date'] = pd.to_datetime(ledger_df_copy['date'])
        
        matched_count = 0
        unmatched_bank = []
        unmatched_ledger = []
        
        # خوارزمية المطابقة
        for bank_idx, bank_row in bank_df_copy.iterrows():
            matched = False
            
            for ledger_idx, ledger_row in ledger_df_copy.iterrows():
                # التحقق من التطابق في المبلغ (مع هامش خطأ بسيط)
                amount_match = abs(abs(bank_row['amount']) - abs(ledger_row['amount'])) < 0.01
                
                # التحقق من التطابق في التاريخ (±3 أيام)
                date_diff = abs((bank_row['date'] - ledger_row['date']).days)
                date_match = date_diff <= 3
                
                if amount_match and date_match:
                    # تم التطابق
                    rec_item = {
                        'reconciliation_id': f'REC-EXT-{matched_count+1:04d}',
                        'type': 'matched',
                        'bank_transaction_id': bank_row.get('id', bank_idx),
                        'ledger_transaction_id': ledger_row.get('id', ledger_idx),
                        'amount': float(abs(bank_row['amount'])),
                        'bank_date': bank_row['date'].isoformat(),
                        'ledger_date': ledger_row['date'].isoformat(),
                        'difference': 0,
                        'status': 'matched',
                        'description': 'Transaction matched between bank and ledger',
                        'recommended_action': 'No action required'
                    }
                    results.append(rec_item)
                    matched_count += 1
                    matched = True
                    break
            
            if not matched:
                unmatched_bank.append(bank_row)
        
        # إضافة المعاملات غير المطابقة
        for idx, row in enumerate(unmatched_bank):
            rec_item = {
                'reconciliation_id': f'REC-UNM-B-{idx+1:04d}',
                'type': 'unmatched_bank',
                'bank_transaction_id': row.get('id', idx),
                'amount': float(row['amount']),
                'bank_date': row['date'].isoformat() if pd.notna(row['date']) else None,
                'difference': float(row['amount']),
                'status': 'outstanding',
                'description': 'Bank transaction not found in ledger',
                'recommended_action': 'Investigate and record in ledger if valid'
            }
            results.append(rec_item)
        
        return results
    
    def _find_duplicate_transactions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """كشف المعاملات المكررة"""
        
        duplicates = []
        
        # تجميع حسب المبلغ والتاريخ
        df_copy = df.copy()
        df_copy['date_only'] = df_copy['date'].dt.date
        
        grouped = df_copy.groupby(['amount', 'date_only'])
        
        for (amount, date), group in grouped:
            if len(group) > 1:
                duplicates.append({
                    'transaction_ids': group.index.tolist(),
                    'amount': float(amount),
                    'dates': [row['date'] for _, row in group.iterrows()],
                    'count': len(group)
                })
        
        return duplicates
    
    def _detect_timing_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """كشف الشذوذ الزمني"""
        
        anomalies = []
        
        if len(df) < 2:
            return anomalies
        
        df_sorted = df.sort_values('date').reset_index(drop=True)
        
        for i in range(1, len(df_sorted)):
            time_diff = (df_sorted.loc[i, 'date'] - df_sorted.loc[i-1, 'date']).total_seconds()
            
            # معاملات متتالية بنفس المبلغ في وقت قصير جداً
            if (time_diff < 60 and  # أقل من دقيقة
                abs(df_sorted.loc[i, 'amount']) == abs(df_sorted.loc[i-1, 'amount'])):
                
                anomalies.append({
                    'reconciliation_id': f'REC-TIME-{len(anomalies)+1:04d}',
                    'type': 'timing_anomaly',
                    'transaction_ids': [df_sorted.loc[i-1, 'id'], df_sorted.loc[i, 'id']] if 'id' in df.columns else [i-1, i],
                    'amount': float(df_sorted.loc[i, 'amount']),
                    'time_difference_seconds': time_diff,
                    'status': 'requires_review',
                    'description': f'Two identical transactions within {time_diff:.0f} seconds',
                    'recommended_action': 'Verify if this is a system error or duplicate processing'
                })
        
        return anomalies
    
    def _detect_suspicious_activities(self, df: pd.DataFrame) -> List[SuspiciousActivity]:
        """
        كشف الأنشطة المشبوهة
        
        أنواع الأنشطة المشبوهة:
        - معاملات كبيرة جداً
        - مبالغ مدورة بشكل مشبوه
        - تكرار غير طبيعي
        - أنماط غسيل أموال محتملة
        - تحويلات إلى أطراف مشبوهة
        """
        
        suspicious = []
        
        # 1. كشف المعاملات الكبيرة جداً
        large_txns = self._detect_large_transactions(df)
        suspicious.extend(large_txns)
        
        # 2. كشف المبالغ المدورة المشبوهة
        round_amounts = self._detect_round_amounts(df)
        suspicious.extend(round_amounts)
        
        # 3. كشف التكرار غير الطبيعي
        frequency_patterns = self._detect_unusual_frequency(df)
        suspicious.extend(frequency_patterns)
        
        # 4. كشف أنماط غسيل الأموال (Structuring/Smurfing)
        structuring = self._detect_structuring(df)
        suspicious.extend(structuring)
        
        # 5. كشف المعاملات في أوقات غير عادية
        odd_time_txns = self._detect_odd_time_transactions(df)
        suspicious.extend(odd_time_txns)
        
        return suspicious
    
    def _detect_large_transactions(self, df: pd.DataFrame) -> List[SuspiciousActivity]:
        """كشف المعاملات الكبيرة جداً"""
        
        activities = []
        threshold = self.large_transaction_threshold
        
        large_txns = df[df['amount'].abs() > threshold]
        
        if len(large_txns) > 0:
            activity = SuspiciousActivity(
                activity_id=f'SUSP-LARGE-{len(activities)+1:04d}',
                transaction_ids=large_txns.index.tolist(),
                activity_type='large_transaction',
                risk_score=min(0.9, 0.5 + (large_txns['amount'].abs().max() / threshold) * 0.1),
                description=f'Detected {len(large_txns)} large transactions exceeding {threshold:,}',
                evidence=[
                    f'Largest transaction: {large_txns["amount"].abs().max():,.2f}',
                    f'Average large transaction: {large_txns["amount"].abs().mean():,.2f}',
                    f'Total large transactions value: {large_txns["amount"].abs().sum():,.2f}'
                ],
                recommended_action='Review source and purpose of large transactions'
            )
            activities.append(activity)
        
        return activities
    
    def _detect_round_amounts(self, df: pd.DataFrame) -> List[SuspiciousActivity]:
        """كشف المبالغ المدورة المشبوهة"""
        
        activities = []
        threshold = self.round_amount_threshold
        
        # كشف المبالغ التي تنتهي بأصفار متعددة
        round_txns = df[
            (df['amount'].abs() >= threshold) & 
            (df['amount'].abs() % 10000 == 0)
        ]
        
        if len(round_txns) > 0:
            activity = SuspiciousActivity(
                activity_id=f'SUSP-ROUND-{len(activities)+1:04d}',
                transaction_ids=round_txns.index.tolist(),
                activity_type='round_amount_pattern',
                risk_score=min(0.85, 0.4 + len(round_txns) * 0.05),
                description=f'Detected {len(round_txns)} suspiciously round amounts',
                evidence=[
                    f'Round amount transactions: {len(round_txns)}',
                    f'Total value: {round_txns["amount"].abs().sum():,.2f}',
                    'Round amounts may indicate artificial transactions'
                ],
                recommended_action='Investigate the nature of these round-amount transactions'
            )
            activities.append(activity)
        
        return activities
    
    def _detect_unusual_frequency(self, df: pd.DataFrame) -> List[SuspiciousActivity]:
        """كشف التكرار غير الطبيعي"""
        
        activities = []
        
        # تحليل التكرار اليومي
        df_copy = df.copy()
        df_copy['date_only'] = df_copy['date'].dt.date
        
        daily_counts = df_copy.groupby('date_only').size()
        avg_daily = daily_counts.mean()
        std_daily = daily_counts.std()
        
        # الأيام ذات النشاط غير الطبيعي
        if std_daily > 0:
            unusual_days = daily_counts[daily_counts > avg_daily + 2 * std_daily]
            
            if len(unusual_days) > 0:
                activity = SuspiciousActivity(
                    activity_id=f'SUSP-FREQ-{len(activities)+1:04d}',
                    transaction_ids=[],
                    activity_type='unusual_frequency',
                    risk_score=min(0.75, 0.3 + len(unusual_days) * 0.1),
                    description=f'Detected {len(unusual_days)} days with unusually high transaction frequency',
                    evidence=[
                        f'Average daily transactions: {avg_daily:.1f}',
                        f'Max daily transactions: {daily_counts.max()}',
                        f'Unusual days: {unusual_days.index.tolist()}'
                    ],
                    recommended_action='Review business justification for high-frequency days'
                )
                activities.append(activity)
        
        return activities
    
    def _detect_structuring(self, df: pd.DataFrame) -> List[SuspiciousActivity]:
        """
        كشف أنماط غسيل الأموال (Structuring/Smurfing)
        
        Structuring: تقسيم المعاملات الكبيرة إلى معاملات صغيرة لتجنب التقارير الإلزامية
        """
        
        activities = []
        
        # البحث عن مجموعات من المعاملات الصغيرة المتقاربة في الوقت والمبلغ
        df_copy = df.copy()
        df_copy['date_only'] = df_copy['date'].dt.date
        
        # عتبة التقارير الإلزامية (مثلاً 50,000 جنيه)
        reporting_threshold = 50000
        
        for date in df_copy['date_only'].unique():
            day_txns = df_copy[df_copy['date_only'] == date]
            
            # معاملات أقل بقليل من عتبة التقرير
            suspicious_range_min = reporting_threshold * 0.5
            suspicious_range_max = reporting_threshold * 0.95
            
            structuring_candidates = day_txns[
                (day_txns['amount'].abs() >= suspicious_range_min) &
                (day_txns['amount'].abs() <= suspicious_range_max)
            ]
            
            if len(structuring_candidates) >= 3:
                total_amount = structuring_candidates['amount'].abs().sum()
                
                activity = SuspiciousActivity(
                    activity_id=f'SUSP-STRUCT-{len(activities)+1:04d}',
                    transaction_ids=structuring_candidates.index.tolist(),
                    activity_type='potential_structuring',
                    risk_score=min(0.95, 0.6 + len(structuring_candidates) * 0.05),
                    description=f'Potential structuring detected on {date}: {len(structuring_candidates)} transactions just below reporting threshold',
                    evidence=[
                        f'Date: {date}',
                        f'Number of suspicious transactions: {len(structuring_candidates)}',
                        f'Total amount: {total_amount:,.2f}',
                        f'Individual amounts: {structuring_candidates["amount"].tolist()}'
                    ],
                    recommended_action='Immediate investigation required - potential money laundering'
                )
                activities.append(activity)
        
        return activities
    
    def _detect_odd_time_transactions(self, df: pd.DataFrame) -> List[SuspiciousActivity]:
        """كشف المعاملات في أوقات غير عادية"""
        
        activities = []
        
        if 'hour' not in df.columns and 'date' in df.columns:
            df['hour'] = pd.to_datetime(df['date']).dt.hour
        
        if 'hour' in df.columns:
            # ساعات العمل العادية: 9 صباحاً - 5 مساءً
            odd_hour_txns = df[(df['hour'] < 9) | (df['hour'] > 17)]
            
            if len(odd_hour_txns) > len(df) * 0.2:  # أكثر من 20%
                activity = SuspiciousActivity(
                    activity_id=f'SUSP-TIME-{len(activities)+1:04d}',
                    transaction_ids=odd_hour_txns.index.tolist(),
                    activity_type='odd_time_transactions',
                    risk_score=min(0.7, 0.3 + (len(odd_hour_txns) / len(df)) * 0.4),
                    description=f'{len(odd_hour_txns)} transactions ({len(odd_hour_txns)/len(df)*100:.1f}%) occurred outside business hours',
                    evidence=[
                        f'Total odd-time transactions: {len(odd_hour_txns)}',
                        f'Percentage: {len(odd_hour_txns)/len(df)*100:.1f}%',
                        'Business hours defined as 9:00 AM - 5:00 PM'
                    ],
                    recommended_action='Verify authorization for after-hours transactions'
                )
                activities.append(activity)
        
        return activities
    
    def _analyze_cash_flow(self, df: pd.DataFrame) -> Dict[str, Any]:
        """تحليل التدفقات النقدية"""
        
        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'])
        
        # تحليل شهري
        df_copy['month'] = df_copy['date'].dt.to_period('M')
        
        # تحليل الاتجاهات
        inflows = df_copy[df_copy['amount'] > 0].groupby('month')['amount'].sum()
        outflows = df_copy[df_copy['amount'] < 0].groupby('month')['amount'].apply(lambda x: abs(x.sum()))
        
        trend = 'stable'
        if len(inflows) > 1:
            inflow_trend = inflows.pct_change().mean()
            if pd.notna(inflow_trend):
                if inflow_trend > 0.1:
                    trend = 'increasing'
                elif inflow_trend < -0.1:
                    trend = 'decreasing'
        
        return {
            'trend': trend,
            'average_monthly_inflow': float(inflows.mean()) if len(inflows) > 0 else 0,
            'average_monthly_outflow': float(outflows.mean()) if len(outflows) > 0 else 0,
            'volatility': float(df['amount'].std()) if len(df) > 1 else 0,
            'liquidity_ratio': float(inflows.sum() / outflows.sum()) if outflows.sum() > 0 else 0
        }
    
    def _generate_bank_recommendations(
        self,
        summary: Dict[str, Any],
        suspicious_activities: List[SuspiciousActivity],
        reconciliation: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """توليد توصيات بناءً على التحليل"""
        
        recommendations = []
        
        # توصيات عامة
        if summary.get('total_transactions', 0) > 1000:
            recommendations.append({
                'priority': 'medium',
                'category': 'volume',
                'recommendation': 'High transaction volume detected. Consider automated reconciliation tools.',
                'impact': 'Efficiency improvement'
            })
        
        # توصيات بناءً على الأنشطة المشبوهة
        high_risk_count = sum(1 for s in suspicious_activities if s.risk_score > 0.7)
        if high_risk_count > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'fraud_prevention',
                'recommendation': f'{high_risk_count} high-risk suspicious activities require immediate investigation.',
                'impact': 'Fraud prevention'
            })
        
        # توصيات المطابقة
        unmatched_count = sum(1 for r in reconciliation if r.get('status') == 'outstanding')
        if unmatched_count > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'reconciliation',
                'recommendation': f'{unmatched_count} unreconciled items need attention.',
                'impact': 'Financial accuracy'
            })
        
        # توصيات التدفق النقدي
        if summary.get('net_flow', 0) < 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'cash_management',
                'recommendation': 'Negative net cash flow detected. Review cash management strategies.',
                'impact': 'Liquidity management'
            })
        
        return recommendations
    
    def generate_bank_reconciliation_report(
        self,
        bank_name: str,
        statement_date: datetime,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        توليد تقرير مطابقة بنكية احترافي
        
        Args:
            bank_name: اسم البنك
            statement_date: تاريخ الكشف
            results: نتائج التحليل
            
        Returns:
            تقرير جاهز للتصدير
        """
        
        report = {
            'report_title': 'Bank Reconciliation Report',
            'report_id': f'BANK-REC-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            'generated_at': datetime.now().isoformat(),
            'bank_info': {
                'bank_name': bank_name,
                'statement_date': statement_date.isoformat(),
                'prepared_by': 'Finovate Audit Nexus AI - Bank Agent'
            },
            'executive_summary': {
                'total_transactions': results['summary'].get('total_transactions', 0),
                'matched_items': sum(1 for r in results['reconciliation'] if r.get('status') == 'matched'),
                'unmatched_items': sum(1 for r in results['reconciliation'] if r.get('status') == 'outstanding'),
                'suspicious_activities': len(results['suspicious_activities']),
                'overall_risk_level': self._calculate_overall_risk(results['suspicious_activities'])
            },
            'detailed_findings': {
                'reconciliation_details': results['reconciliation'],
                'suspicious_activities': results['suspicious_activities'],
                'cash_flow_analysis': results['cash_flow_analysis']
            },
            'recommendations': results['recommendations'],
            'audit_trail': {
                'analysis_performed': [
                    'Transaction summary analysis',
                    'Bank reconciliation',
                    'Duplicate detection',
                    'Suspicious activity detection',
                    'Cash flow analysis',
                    'Pattern recognition'
                ],
                'data_sources': [bank_name],
                'confidence_score': self._calculate_confidence_score(results)
            }
        }
        
        return report
    
    def _calculate_overall_risk(self, suspicious_activities: List[SuspiciousActivity]) -> str:
        """حساب مستوى المخاطر العام"""
        
        if not suspicious_activities:
            return 'LOW'
        
        avg_risk = sum(s.risk_score for s in suspicious_activities) / len(suspicious_activities)
        max_risk = max(s.risk_score for s in suspicious_activities)
        
        if max_risk > 0.8 or avg_risk > 0.6:
            return 'HIGH'
        elif max_risk > 0.5 or avg_risk > 0.3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_confidence_score(self, results: Dict[str, Any]) -> float:
        """حساب درجة الثقة في النتائج"""
        
        score = 1.0
        
        # خصم لعدم اكتمال البيانات
        if results['summary'].get('total_transactions', 0) < 10:
            score -= 0.2
        
        # خصم لوجود أنشطة مشبوهة عالية المخاطر
        high_risk_count = sum(1 for s in self.suspicious_activities if s.risk_score > 0.8)
        score -= high_risk_count * 0.1
        
        # خصم لعدد العناصر غير المطابقة
        unmatched = sum(1 for r in results['reconciliation'] if r.get('status') == 'outstanding')
        score -= min(0.3, unmatched * 0.05)
        
        return max(0.5, min(1.0, score))
    
    def export_reconciliation_to_excel(
        self,
        results: Dict[str, Any],
        output_path: str
    ) -> bool:
        """
        تصدير نتائج المطابقة إلى Excel
        
        Args:
            results: نتائج التحليل
            output_path: مسار ملف الإخراج
            
        Returns:
            True إذا نجح التصدير
        """
        
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # ورقة الملخص
                summary_df = pd.DataFrame([{
                    'Metric': 'Total Transactions',
                    'Value': results['summary'].get('total_transactions', 0)
                }, {
                    'Metric': 'Total Deposits',
                    'Value': results['summary'].get('total_deposits', 0)
                }, {
                    'Metric': 'Total Withdrawals',
                    'Value': results['summary'].get('total_withdrawals', 0)
                }, {
                    'Metric': 'Net Flow',
                    'Value': results['summary'].get('net_flow', 0)
                }, {
                    'Metric': 'Suspicious Activities',
                    'Value': len(results['suspicious_activities'])
                }])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # ورقة المطابقات
                if results['reconciliation']:
                    rec_df = pd.DataFrame(results['reconciliation'])
                    rec_df.to_excel(writer, sheet_name='Reconciliation', index=False)
                
                # ورقة الأنشطة المشبوهة
                if results['suspicious_activities']:
                    susp_df = pd.DataFrame([
                        {
                            'ID': s['activity_id'],
                            'Type': s['activity_type'],
                            'Risk Score': s['risk_score'],
                            'Description': s['description'],
                            'Recommendation': s['recommended_action']
                        }
                        for s in results['suspicious_activities']
                    ])
                    susp_df.to_excel(writer, sheet_name='Suspicious Activities', index=False)
                
                # ورقة التوصيات
                if results['recommendations']:
                    rec_df = pd.DataFrame(results['recommendations'])
                    rec_df.to_excel(writer, sheet_name='Recommendations', index=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False


# مثال للاستخدام
if __name__ == "__main__":
    # إنشاء وكيل مراجعة البنوك
    agent = BankAuditAgent()
    
    # بيانات تجريبية
    sample_data = {
        'date': pd.date_range('2025-01-01', periods=20, freq='D'),
        'amount': [
            50000, -25000, 100000, -15000, 75000,
            -50000, 200000, -80000, 45000, -30000,
            150000, -60000, 90000, -40000, 120000,
            -70000, 180000, -95000, 65000, -35000
        ],
        'description': [f'Transaction {i+1}' for i in range(20)],
        'transaction_type': ['deposit' if amt > 0 else 'withdrawal' for amt in [
            50000, -25000, 100000, -15000, 75000,
            -50000, 200000, -80000, 45000, -30000,
            150000, -60000, 90000, -40000, 120000,
            -70000, 180000, -95000, 65000, -35000
        ]]
    }
    
    df = pd.DataFrame(sample_data)
    
    # تحليل البنك
    results = agent.analyze_bank_statement(df, "National Bank of Egypt")
    
    print("=" * 80)
    print("Finovate Audit Nexus AI - Bank & Treasury Audit Agent")
    print("=" * 80)
    print(f"\nStatus: {results['status']}")
    print(f"Message: {results['message']}")
    print("\nSummary:")
    for key, value in results['results']['summary'].items():
        if key not in ['top_10_deposits', 'top_10_withdrawals']:
            print(f"  {key}: {value}")
    
    print(f"\nSuspicious Activities Found: {len(results['results']['suspicious_activities'])}")
    for activity in results['results']['suspicious_activities'][:3]:
        print(f"  - {activity['activity_type']}: {activity['description']}")
    
    print(f"\nRecommendations: {len(results['results']['recommendations'])}")
    for rec in results['results']['recommendations']:
        print(f"  [{rec['priority'].upper()}] {rec['recommendation']}")
    
    print("\n" + "=" * 80)
    print("Developed By: Ahmed Mostafa Ibrahim")
    print("© 2025 Finovate – AHMED EG - All Rights Reserved")
    print("=" * 80)

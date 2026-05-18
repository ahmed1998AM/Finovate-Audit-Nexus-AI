"""
AI Quality Assurance Agent
وكيل ضمان جودة الذكاء الاصطناعي - مراجعة نتائج الوكلاء الذكية

المهام:
- كشف الهلوسة (Hallucination Detection)
- كشف التناقضات
- تقييم الثقة
- مراجعة النتائج
- التحقق من الدقة
- تقييم الجودة الشامل
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib


class AIQualityAssuranceAgent:
    """وكيل ضمان جودة الذكاء الاصطناعي"""
    
    def __init__(self):
        self.agent_name = "AI Quality Assurance Agent"
        self.agent_type = "qa"
        self.version = "1.0.0"
        
        # عتبات الجودة
        self.thresholds = {
            'min_confidence': 70.0,
            'high_confidence': 90.0,
            'max_contradictions': 2,
            'min_evidence_items': 3,
            'hallucination_indicators': [
                'ربما', 'قد يكون', 'من المحتمل', 'يبدو أن',
                'might be', 'possibly', 'seems like', 'appears to'
            ]
        }
    
    def review_agent_output(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """مراجعة مخرجات وكيل ذكي"""
        
        review = {
            'agent': self.agent_name,
            'timestamp': datetime.now().isoformat(),
            'review_id': hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12],
            'original_agent': agent_result.get('agent', 'unknown'),
            'quality_score': 0.0,
            'confidence_level': 'LOW',
            'issues_found': [],
            'contradictions': [],
            'hallucination_risk': 'LOW',
            'recommendations': [],
            'approved': False,
            'requires_human_review': False
        }
        
        # 1. فحص الثقة
        confidence_check = self._check_confidence(agent_result)
        review['issues_found'].extend(confidence_check['issues'])
        
        # 2. فحص التناقضات
        contradiction_check = self._check_contradictions(agent_result)
        review['contradictions'] = contradiction_check['contradictions']
        review['issues_found'].extend(contradiction_check['issues'])
        
        # 3. فحص الهلوسة
        hallucination_check = self._check_hallucinations(agent_result)
        review['hallucination_risk'] = hallucination_check['risk_level']
        review['issues_found'].extend(hallucination_check['issues'])
        
        # 4. فحص الأدلة
        evidence_check = self._check_evidence(agent_result)
        review['issues_found'].extend(evidence_check['issues'])
        
        # 5. فحص الاتساق الداخلي
        consistency_check = self._check_internal_consistency(agent_result)
        review['issues_found'].extend(consistency_check['issues'])
        
        # حساب درجة الجودة
        review['quality_score'] = self._calculate_quality_score(review)
        
        # تحديد مستوى الثقة
        if review['quality_score'] >= self.thresholds['high_confidence']:
            review['confidence_level'] = 'HIGH'
            review['approved'] = True
        elif review['quality_score'] >= self.thresholds['min_confidence']:
            review['confidence_level'] = 'MEDIUM'
            review['approved'] = True
        else:
            review['confidence_level'] = 'LOW'
            review['approved'] = False
            review['requires_human_review'] = True
        
        # توليد التوصيات
        review['recommendations'] = self._generate_recommendations(review)
        
        return review
    
    def _check_confidence(self, result: Dict) -> Dict[str, Any]:
        """فحص درجات الثقة"""
        
        issues = []
        
        # البحث عن حقول الثقة في النتيجة
        confidence_fields = ['confidence', 'confidence_score', 'probability', 'accuracy']
        
        found_confidence = None
        for field in confidence_fields:
            if field in result:
                found_confidence = result[field]
                break
        
        if found_confidence is not None:
            try:
                conf_value = float(found_confidence)
                
                if conf_value < self.thresholds['min_confidence']:
                    issues.append({
                        'type': 'LOW_CONFIDENCE',
                        'severity': 'HIGH',
                        'description': f'درجة الثقة {conf_value}% أقل من الحد الأدنى {self.thresholds["min_confidence"]}%',
                        'field': found_confidence
                    })
                elif conf_value < self.thresholds['high_confidence']:
                    issues.append({
                        'type': 'MODERATE_CONFIDENCE',
                        'severity': 'MEDIUM',
                        'description': f'درجة الثقة {conf_value}% متوسطة - يوصى بالمراجعة',
                        'field': found_confidence
                    })
            except (ValueError, TypeError):
                issues.append({
                    'type': 'INVALID_CONFIDENCE',
                    'severity': 'MEDIUM',
                    'description': 'قيمة الثقة غير صالحة',
                    'field': found_confidence
                })
        else:
            issues.append({
                'type': 'MISSING_CONFIDENCE',
                'severity': 'MEDIUM',
                'description': 'لم يتم العثور على درجة ثقة في النتيجة',
                'field': None
            })
        
        return {'issues': issues}
    
    def _check_contradictions(self, result: Dict) -> Dict[str, Any]:
        """فحص التناقضات"""
        
        contradictions = []
        issues = []
        
        # البحث عن تناقضات في الأرقام
        numeric_fields = {}
        for key, value in result.items():
            if isinstance(value, (int, float)) and value != 0:
                numeric_fields[key] = value
        
        # فحص العلاقات المنطقية
        if 'total' in numeric_fields and 'subtotal' in numeric_fields:
            if numeric_fields['total'] < numeric_fields['subtotal']:
                contradictions.append({
                    'type': 'NUMERIC_CONTRADICTION',
                    'fields': ['total', 'subtotal'],
                    'description': f'الإجمالي ({numeric_fields["total"]}) أقل من المجموع الجزئي ({numeric_fields["subtotal"]})'
                })
        
        if 'assets' in numeric_fields and 'liabilities' in numeric_fields and 'equity' in numeric_fields:
            expected_equity = numeric_fields['assets'] - numeric_fields['liabilities']
            diff_percent = abs(numeric_fields['equity'] - expected_equity) / expected_equity * 100 if expected_equity != 0 else 0
            
            if diff_percent > 5:
                contradictions.append({
                    'type': 'ACCOUNTING_EQUATION_ERROR',
                    'fields': ['assets', 'liabilities', 'equity'],
                    'description': f'معادلة الميزانية غير متوازنة: الفرق {diff_percent:.1f}%'
                })
        
        # فحص التناقضات النصية
        text_fields = {k: v for k, v in result.items() if isinstance(v, str)}
        
        status_keywords_positive = ['compliant', 'approved', 'valid', 'correct', 'موافق', 'صحيح']
        status_keywords_negative = ['non-compliant', 'rejected', 'invalid', 'error', 'غير موافق', 'خطأ']
        
        has_positive = any(kw in str(text_fields).lower() for kw in status_keywords_positive)
        has_negative = any(kw in str(text_fields).lower() for kw in status_keywords_negative)
        
        if has_positive and has_negative:
            contradictions.append({
                'type': 'STATUS_CONTRADICTION',
                'fields': list(text_fields.keys()),
                'description': 'توجد كلمات تدل على الموافق والرفض في نفس الوقت'
            })
        
        if len(contradictions) > self.thresholds['max_contradictions']:
            issues.append({
                'type': 'MULTIPLE_CONTRADICTIONS',
                'severity': 'CRITICAL',
                'description': f'تم اكتشاف {len(contradictions)} تناقضات - يتجاوز الحد المسموح',
                'count': len(contradictions)
            })
        elif contradictions:
            issues.append({
                'type': 'CONTRADICTIONS_FOUND',
                'severity': 'HIGH',
                'description': f'تم اكتشاف {len(contradictions)} تناقضات',
                'count': len(contradictions)
            })
        
        return {'contradictions': contradictions, 'issues': issues}
    
    def _check_hallucinations(self, result: Dict) -> Dict[str, Any]:
        """فحص مؤشرات الهلوسة"""
        
        risk_level = 'LOW'
        issues = []
        indicators_found = []
        
        # تحويل النتيجة إلى نص للفحص
        result_text = str(result).lower()
        
        # البحث عن مؤشرات الهلوسة
        for indicator in self.thresholds['hallucination_indicators']:
            if indicator.lower() in result_text:
                indicators_found.append(indicator)
        
        if len(indicators_found) > 3:
            risk_level = 'HIGH'
            issues.append({
                'type': 'HIGH_HALLUCINATION_RISK',
                'severity': 'CRITICAL',
                'description': f'تم اكتشاف {len(indicators_found)} مؤشر هلوسة',
                'indicators': indicators_found
            })
        elif len(indicators_found) > 0:
            risk_level = 'MEDIUM'
            issues.append({
                'type': 'POTENTIAL_HALLUCINATION',
                'severity': 'MEDIUM',
                'description': f'تم اكتشاف {len(indicators_found)} مؤشر هلوسة محتمل',
                'indicators': indicators_found
            })
        
        # فحص الادعاءات غير المدعومة
        claim_patterns = ['definitely', 'certainly', 'without doubt', 'بالتأكيد', 'بلا شك', 'قطعا']
        claims_found = sum(1 for pattern in claim_patterns if pattern in result_text)
        
        if claims_found > 2:
            issues.append({
                'type': 'UNSUBSTANTIATED_CLAIMS',
                'severity': 'MEDIUM',
                'description': 'توجد ادعاءات قاطعة بدون أدلة كافية',
                'count': claims_found
            })
        
        return {'risk_level': risk_level, 'issues': issues}
    
    def _check_evidence(self, result: Dict) -> Dict[str, Any]:
        """فحص وجود الأدلة"""
        
        issues = []
        
        # البحث عن حقول الأدلة
        evidence_fields = ['evidence', 'sources', 'references', 'proof', 'documentation', 'أدلة', 'مصادر']
        
        found_evidence = []
        for field in evidence_fields:
            if field in result:
                value = result[field]
                if isinstance(value, list) and len(value) > 0:
                    found_evidence.extend(value)
                elif isinstance(value, str) and value.strip():
                    found_evidence.append(value)
        
        if len(found_evidence) < self.thresholds['min_evidence_items']:
            issues.append({
                'type': 'INSUFFICIENT_EVIDENCE',
                'severity': 'HIGH',
                'description': f'عدد الأدلة {len(found_evidence)} أقل من الحد الأدنى {self.thresholds["min_evidence_items"]}',
                'evidence_count': len(found_evidence)
            })
        
        return {'issues': issues}
    
    def _check_internal_consistency(self, result: Dict) -> Dict[str, Any]:
        """فحص الاتساق الداخلي"""
        
        issues = []
        
        # فحص تواريخ النتيجة
        if 'timestamp' in result and 'start_time' in result and 'end_time' in result:
            try:
                start = result['start_time']
                end = result['end_time']
                
                if start > end:
                    issues.append({
                        'type': 'TIME_INCONSISTENCY',
                        'severity': 'HIGH',
                        'description': 'وقت البدء لاحق من وقت الانتهاء',
                        'details': f'{start} > {end}'
                    })
            except:
                pass
        
        # فحص تنسيق البيانات
        findings = result.get('findings', [])
        if isinstance(findings, list):
            empty_findings = sum(1 for f in findings if not f or (isinstance(f, dict) and not f))
            
            if empty_findings > len(findings) * 0.3:
                issues.append({
                    'type': 'EMPTY_FINDINGS',
                    'severity': 'MEDIUM',
                    'description': f'{empty_findings} من النتائج فارغة من أصل {len(findings)}',
                    'empty_count': empty_findings
                })
        
        return {'issues': issues}
    
    def _calculate_quality_score(self, review: Dict) -> float:
        """حساب درجة الجودة الشاملة"""
        
        base_score = 100.0
        
        # خصم للمشاكل المكتشفة
        severity_penalties = {
            'CRITICAL': 25.0,
            'HIGH': 15.0,
            'MEDIUM': 8.0,
            'LOW': 3.0
        }
        
        for issue in review['issues_found']:
            severity = issue.get('severity', 'MEDIUM')
            base_score -= severity_penalties.get(severity, 5.0)
        
        # خصم إضافي للتناقضات
        base_score -= len(review['contradictions']) * 10.0
        
        # خصم لخطر الهلوسة
        hallucination_penalties = {
            'HIGH': 30.0,
            'MEDIUM': 15.0,
            'LOW': 0.0
        }
        base_score -= hallucination_penalties.get(review['hallucination_risk'], 0.0)
        
        # التأكد من أن الدرجة بين 0 و 100
        return max(0.0, min(100.0, round(base_score, 2)))
    
    def _generate_recommendations(self, review: Dict) -> List[Dict[str, Any]]:
        """توليد التوصيات"""
        
        recommendations = []
        
        issue_types = set(issue['type'] for issue in review['issues_found'])
        
        if 'LOW_CONFIDENCE' in issue_types or 'MISSING_CONFIDENCE' in issue_types:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Confidence',
                'recommendation': 'يجب تحسين نموذج الذكاء الاصطناعي ليعطي درجات ثقة دقيقة',
                'action': 'إعادة التدريب أو ضبط المعلمات'
            })
        
        if 'CONTRADICTIONS_FOUND' in issue_types or 'NUMERIC_CONTRADICTION' in issue_types:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Consistency',
                'recommendation': 'مراجعة النتائج يدوياً للكشف عن مصدر التناقضات',
                'action': 'إجراء تحقق بشري قبل الاعتماد على النتائج'
            })
        
        if 'HIGH_HALLUCINATION_RISK' in issue_types or 'POTENTIAL_HALLUCINATION' in issue_types:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Hallucination',
                'recommendation': 'النتائج قد تحتوي على معلومات غير صحيحة',
                'action': 'استخدام نموذج أكثر دقة أو إضافة مصادر تحقق'
            })
        
        if 'INSUFFICIENT_EVIDENCE' in issue_types:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Evidence',
                'recommendation': 'توفير المزيد من الأدلة لدعم الاستنتاجات',
                'action': 'جمع بيانات إضافية أو توثيق المصادر'
            })
        
        if review['requires_human_review']:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Human Review',
                'recommendation': 'هذه النتيجة تتطلب مراجعة بشرية إلزامية',
                'action': 'إحالة إلى خبير للمراجعة النهائية'
            })
        
        if not recommendations:
            recommendations.append({
                'priority': 'LOW',
                'category': 'General',
                'recommendation': 'النتائج جيدة ولا تحتاج إلى إجراءات إضافية',
                'action': 'الاعتماد على النتائج'
            })
        
        return recommendations
    
    def batch_review(self, agent_results: List[Dict]) -> Dict[str, Any]:
        """مراجعة دفعة من نتائج الوكلاء"""
        
        batch_review = {
            'agent': self.agent_name,
            'timestamp': datetime.now().isoformat(),
            'batch_id': hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12],
            'total_reviews': len(agent_results),
            'reviews': [],
            'summary': {
                'approved': 0,
                'rejected': 0,
                'requires_human_review': 0,
                'avg_quality_score': 0.0,
                'critical_issues': 0,
                'by_agent': {}
            }
        }
        
        quality_sum = 0.0
        
        for result in agent_results:
            review = self.review_agent_output(result)
            batch_review['reviews'].append(review)
            
            # تحديث الملخص
            if review['approved']:
                batch_review['summary']['approved'] += 1
            else:
                batch_review['summary']['rejected'] += 1
            
            if review['requires_human_review']:
                batch_review['summary']['requires_human_review'] += 1
            
            quality_sum += review['quality_score']
            
            critical_issues = sum(1 for issue in review['issues_found'] if issue.get('severity') == 'CRITICAL')
            batch_review['summary']['critical_issues'] += critical_issues
            
            agent_name = review['original_agent']
            batch_review['summary']['by_agent'][agent_name] = batch_review['summary']['by_agent'].get(agent_name, 0) + 1
        
        if agent_results:
            batch_review['summary']['avg_quality_score'] = round(quality_sum / len(agent_results), 2)
        
        return batch_review


# مثال على الاستخدام
if __name__ == '__main__':
    agent = AIQualityAssuranceAgent()
    
    # نتيجة وكيل تجريبية جيدة
    good_result = {
        'agent': 'Fraud Detection Agent',
        'timestamp': datetime.now().isoformat(),
        'confidence_score': 92.5,
        'findings': [
            {'type': 'DUPLICATE_ENTRY', 'evidence': ['INV-001', 'INV-001 copy']},
            {'type': 'ANOMALY', 'evidence': ['Amount 50000 EGP exceeds threshold']}
        ],
        'fraud_score': 75.0,
        'recommendations': ['Review duplicate invoices', 'Verify large transactions']
    }
    
    # نتيجة وكيل تجريبية سيئة
    bad_result = {
        'agent': 'Tax Compliance Agent',
        'timestamp': datetime.now().isoformat(),
        'confidence_score': 45.0,
        'findings': [
            {'type': 'TAX_ISSUE'},
            {},
            None
        ],
        'status': 'non-compliant but possibly correct',
        'total': 50000,
        'subtotal': 60000,
        'notes': 'This might be an error, seems like there could be issues'
    }
    
    print("=" * 80)
    print("مراجعة جودة مخرجات الذكاء الاصطناعي")
    print("=" * 80)
    
    # مراجعة النتيجة الجيدة
    print("\n📊 مراجعة النتيجة الجيدة:")
    print("-" * 40)
    
    good_review = agent.review_agent_output(good_result)
    
    print(f"الوكيل الأصلي: {good_review['original_agent']}")
    print(f"درجة الجودة: {good_review['quality_score']}%")
    print(f"مستوى الثقة: {good_review['confidence_level']}")
    print(f"تمت الموافقة: {'✅ نعم' if good_review['approved'] else '❌ لا'}")
    print(f"يتطلب مراجعة بشرية: {'⚠️ نعم' if good_review['requires_human_review'] else '✅ لا'}")
    print(f"خطر الهلوسة: {good_review['hallucination_risk']}")
    
    if good_review['issues_found']:
        print(f"\nالمشاكل المكتشفة: {len(good_review['issues_found'])}")
        for issue in good_review['issues_found']:
            print(f"  • [{issue['severity']}] {issue['type']}: {issue['description']}")
    
    print("\nالتوصيات:")
    for rec in good_review['recommendations']:
        print(f"  [{rec['priority']}] {rec['recommendation']}")
    
    # مراجعة النتيجة السيئة
    print("\n" + "=" * 80)
    print("\n📊 مراجعة النتيجة السيئة:")
    print("-" * 40)
    
    bad_review = agent.review_agent_output(bad_result)
    
    print(f"الوكيل الأصلي: {bad_review['original_agent']}")
    print(f"درجة الجودة: {bad_review['quality_score']}%")
    print(f"مستوى الثقة: {bad_review['confidence_level']}")
    print(f"تمت الموافقة: {'✅ نعم' if bad_review['approved'] else '❌ لا'}")
    print(f"يتطلب مراجعة بشرية: {'⚠️ نعم' if bad_review['requires_human_review'] else '✅ لا'}")
    print(f"خطر الهلوسة: {bad_review['hallucination_risk']}")
    
    if bad_review['issues_found']:
        print(f"\nالمشاكل المكتشفة: {len(bad_review['issues_found'])}")
        for issue in bad_review['issues_found']:
            print(f"  • [{issue['severity']}] {issue['type']}: {issue['description']}")
    
    if bad_review['contradictions']:
        print(f"\nالتناقضات: {len(bad_review['contradictions'])}")
        for contra in bad_review['contradictions']:
            print(f"  • {contra['description']}")
    
    print("\nالتوصيات:")
    for rec in bad_review['recommendations']:
        print(f"  [{rec['priority']}] {rec['recommendation']}")
    
    # مراجعة دفعة
    print("\n" + "=" * 80)
    print("\n📋 مراجعة دفعة نتائج:")
    print("-" * 40)
    
    batch_results = [good_result, bad_result]
    batch_review = agent.batch_review(batch_results)
    
    print(f"إجمالي المراجعات: {batch_review['total_reviews']}")
    print(f"تمت الموافقة: {batch_review['summary']['approved']}")
    print(f"مرفوضة: {batch_review['summary']['rejected']}")
    print(f"تتطلب مراجعة بشرية: {batch_review['summary']['requires_human_review']}")
    print(f"متوسط درجة الجودة: {batch_review['summary']['avg_quality_score']}%")
    print(f"مشاكل حرجة: {batch_review['summary']['critical_issues']}")
    
    print("\n✅ اكتملت مراجعة الجودة بنجاح!")

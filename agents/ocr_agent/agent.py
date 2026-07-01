"""
OCR & Document Intelligence Agent
وكيل الذكاء البصري للمستندات - استخراج البيانات من المستندات المالية

المهام:
- OCR (التعرف الضوئي على الحروف) مع دعم PaddleOCR/Tesseract
- استخراج البيانات من الفواتير
- تصنيف الملفات
- فهم العقود والمستندات القانونية
- تحليل الجداول المالية
- دعم العربية والإنجليزية
"""

import hashlib
import re
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


class OCRDocumentIntelligenceAgent:
    """وكيل الذكاء البصري للمستندات"""

    def __init__(self, ocr_engine: str = 'auto'):
        """
        تهيئة وكيل OCR
        
        Args:
            ocr_engine: محرك OCR ('paddleocr', 'tesseract', 'auto', 'regex')
        """
        self.agent_name = "OCR & Document Intelligence Agent"
        self.agent_type = "ocr_document"
        self.version = "2.0.0"
        self.ocr_engine = ocr_engine
        
        # اللغات المدعومة
        self.supported_languages = ['ara', 'eng', 'fra', 'deu', 'spa']

        # أنواع المستندات المدعومة
        self.document_types = {
            'invoice': 'فاتورة ضريبية',
            'receipt': 'إيصال قبض',
            'contract': 'عقد',
            'bank_statement': 'كشف حساب بنكي',
            'tax_return': 'إقرار ضريبي',
            'financial_statement': 'قائمة مالية',
            'journal_entry': 'قيد يومية',
            'purchase_order': 'أمر شراء',
            'delivery_note': 'إذن صرف',
            'check': 'شيك',
        }

        # أنماط الاستخراج
        self.extraction_patterns = {
            'vat_number': r'\b\d{9}\b',  # الرقم الضريبي 9 أرقام
            'national_id': r'\b\d{14}\b',  # الرقم القومي 14 رقم
            'phone_egypt': r'(?:\+2|0)?1[0-9]{9}',  # أرقام الهواتف المصرية
            'amount': r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?',  # المبالغ
            'date_egypt': r'\d{1,2}/\d{1,2}/\d{2,4}',  # التواريخ
            'invoice_number': r'(?:INV|FAT|رقم).?(?:\s*:)?\s*([A-Z0-9\-]+)',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        }
        
        # تهيئة محرك OCR
        self._paddleocr_model = None
        self._tesseract_available = False
        self._init_ocr_engine()
    
    def _init_ocr_engine(self):
        """تهيئة محرك OCR المختار"""
        if self.ocr_engine == 'auto':
            # محاولة PaddleOCR أولاً ثم Tesseract
            try:
                from paddleocr import PaddleOCR
                self._paddleocr_model = PaddleOCR(use_angle_cls=True, lang='ar')
                self.ocr_engine = 'paddleocr'
                print("PaddleOCR initialized successfully")
            except ImportError:
                try:
                    import pytesseract
                    self._tesseract_available = True
                    self.ocr_engine = 'tesseract'
                    print("Tesseract initialized successfully")
                except ImportError:
                    self.ocr_engine = 'regex'
                    print("Using regex-based extraction only")
        elif self.ocr_engine == 'paddleocr':
            try:
                from paddleocr import PaddleOCR
                self._paddleocr_model = PaddleOCR(use_angle_cls=True, lang='ar')
            except ImportError:
                print("PaddleOCR not available, falling back to regex")
                self.ocr_engine = 'regex'
        elif self.ocr_engine == 'tesseract':
            try:
                import pytesseract
                self._tesseract_available = True
            except ImportError:
                print("Tesseract not available, falling back to regex")
                self.ocr_engine = 'regex'
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        استخراج النص من صورة باستخدام محرك OCR
        
        Args:
            image_path: مسار الصورة
            
        Returns:
            str: النص المستخرج
        """
        if not os.path.exists(image_path):
            return ""
        
        if self.ocr_engine == 'paddleocr' and self._paddleocr_model:
            try:
                result = self._paddleocr_model.ocr(image_path, cls=True)
                text_lines = []
                for line in result[0]:
                    text_lines.append(line[1][0])
                return '\n'.join(text_lines)
            except Exception as e:
                print(f"PaddleOCR error: {e}")
        
        elif self.ocr_engine == 'tesseract' and self._tesseract_available:
            try:
                import pytesseract
                from PIL import Image
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image, lang='ara+eng')
                return text
            except Exception as e:
                print(f"Tesseract error: {e}")
        
        return ""

    def process_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة مستند واستخراج البيانات"""

        result = {
            'agent': self.agent_name,
            'timestamp': datetime.now().isoformat(),
            'document_id': hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12],
            'document_type': 'unknown',
            'confidence_score': 0.0,
            'extracted_data': {},
            'fields': {},
            'tables': [],
            'warnings': [],
            'language_detected': 'ara'
        }

        # تحديد نوع المستند
        result['document_type'] = self._detect_document_type(document_data)

        # استخراج الحقول الأساسية
        result['fields'] = self._extract_fields(document_data)

        # استخراج الجداول
        result['tables'] = self._extract_tables(document_data)

        # حساب درجة الثقة
        result['confidence_score'] = self._calculate_confidence(result['fields'])

        # التحقق من صحة البيانات
        result['warnings'] = self._validate_extracted_data(result['fields'])

        return result

    def _detect_document_type(self, data: Dict) -> str:
        """تحديد نوع المستند"""

        text_content = str(data.get('text', '') + ' ' + data.get('content', '')).lower()

        keywords_map = {
            'invoice': ['فاتورة', 'invoice', 'ضريبية', 'tax invoice'],
            'receipt': ['إيصال', 'receipt', 'قبض', 'استلام'],
            'contract': ['عقد', 'contract', 'اتفاقية', 'agreement'],
            'bank_statement': ['كشف حساب', 'bank statement', 'بنك', 'movements'],
            'tax_return': ['إقرار', 'tax return', 'ضريبة', 'tax authority'],
            'financial_statement': ['قائمة مالية', 'financial statement', 'ميزانية', 'balance sheet'],
            'journal_entry': ['قيد', 'journal entry', 'يومية', 'debit', 'credit'],
            'purchase_order': ['أمر شراء', 'purchase order', 'order'],
            'delivery_note': ['إذن صرف', 'delivery note', 'تسليم'],
            'check': ['شيك', 'check', 'cheque'],
        }

        scores = {}
        for doc_type, keywords in keywords_map.items():
            score = sum(1 for kw in keywords if kw in text_content)
            scores[doc_type] = score

        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return 'unknown'

    def _extract_fields(self, data: Dict) -> Dict[str, Any]:
        """استخراج الحقول من المستند"""

        fields = {}
        text_content = str(data.get('text', '') + ' ' + data.get('content', ''))

        # استخراج التاريخ
        date_match = re.search(self.extraction_patterns['date_egypt'], text_content)
        if date_match:
            fields['date'] = date_match.group()

        # استخراج الرقم الضريبي
        vat_matches = re.findall(self.extraction_patterns['vat_number'], text_content)
        if vat_matches:
            fields['vat_number'] = vat_matches[0]

        # استخراج الرقم القومي
        nid_matches = re.findall(self.extraction_patterns['national_id'], text_content)
        if nid_matches:
            fields['national_id'] = nid_matches[0]

        # استخراج رقم الهاتف
        phone_matches = re.findall(self.extraction_patterns['phone_egypt'], text_content)
        if phone_matches:
            fields['phone'] = phone_matches[0]

        # استخراج البريد الإلكتروني
        email_matches = re.findall(self.extraction_patterns['email'], text_content)
        if email_matches:
            fields['email'] = email_matches[0]

        # استخراج المبالغ
        amount_matches = re.findall(self.extraction_patterns['amount'], text_content)
        if amount_matches:
            amounts = [float(a.replace(',', '')) for a in amount_matches]
            fields['amounts_found'] = amounts
            fields['total_amount'] = max(amounts) if amounts else 0

        # استخراج رقم الفاتورة
        inv_match = re.search(self.extraction_patterns['invoice_number'], text_content, re.IGNORECASE)
        if inv_match:
            fields['invoice_number'] = inv_match.group(1)

        # استخراج أسماء الأطراف
        fields['parties'] = self._extract_parties(text_content)

        # استخراج البنود
        fields['line_items'] = self._extract_line_items(data)

        return fields

    def _extract_parties(self, text: str) -> Dict[str, str]:
        """استخراج أطراف المستند"""

        parties = {}

        # محاولة استخراج اسم البائع/المورد
        seller_patterns = [
            r'البائع[:\\s]+([^\n]+)',
            r'المورد[:\\s]+([^\n]+)',
            r'seller[:\\s]+([^\n]+)',
            r'vendor[:\\s]+([^\n]+)',
            r'supplier[:\\s]+([^\n]+)',
        ]

        for pattern in seller_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parties['seller'] = match.group(1).strip()
                break

        # محاولة استخراج اسم المشتري/العميل
        buyer_patterns = [
            r'المشتري[:\\s]+([^\n]+)',
            r'العميل[:\\s]+([^\n]+)',
            r'buyer[:\\s]+([^\n]+)',
            r'customer[:\\s]+([^\n]+)',
            r'bill to[:\\s]+([^\n]+)',
        ]

        for pattern in buyer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parties['buyer'] = match.group(1).strip()
                break

        return parties

    def _extract_line_items(self, data: Dict) -> List[Dict[str, Any]]:
        """استخراج بنود الفاتورة"""

        line_items = []
        tables = data.get('tables', [])

        if tables:
            for table in tables:
                rows = table.get('rows', [])
                for row in rows:
                    item = {}

                    # محاولة تحديد الأعمدة
                    cells = row.get('cells', [])
                    if len(cells) >= 3:
                        item['description'] = str(cells[0]) if len(cells) > 0 else ''
                        item['quantity'] = self._parse_number(cells[1]) if len(cells) > 1 else 1
                        item['unit_price'] = self._parse_number(cells[2]) if len(cells) > 2 else 0
                        item['total'] = self._parse_number(cells[3]) if len(cells) > 3 else (item['quantity'] * item['unit_price'])

                        if item['description']:
                            line_items.append(item)

        return line_items

    def _parse_number(self, value: Any) -> float:
        """تحويل القيمة إلى رقم"""

        if isinstance(value, (int, float)):
            return float(value)

        try:
            cleaned = str(value).replace(',', '').replace(' ', '')
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0

    def _extract_tables(self, data: Dict) -> List[Dict[str, Any]]:
        """استخراج الجداول من المستند"""

        tables = []

        # إذا كانت الجداول موجودة بالفعل في البيانات
        if 'tables' in data:
            tables = data['tables']

        return tables

    def _calculate_confidence(self, fields: Dict) -> float:
        """حساب درجة الثقة في البيانات المستخرجة"""

        if not fields:
            return 0.0

        total_fields = 0
        confident_fields = 0

        critical_fields = ['date', 'amounts_found', 'vat_number', 'invoice_number']

        for field, value in fields.items():
            total_fields += 1

            if value:
                if isinstance(value, str) and len(value) > 2:
                    confident_fields += 1
                elif isinstance(value, list) and len(value) > 0:
                    confident_fields += 1
                elif isinstance(value, dict) and len(value) > 0:
                    confident_fields += 1
                elif isinstance(value, (int, float)) and value != 0:
                    confident_fields += 1

        base_confidence = (confident_fields / total_fields * 100) if total_fields > 0 else 0

        # تعزيز الثقة إذا كانت الحقول الحرجة موجودة
        for critical in critical_fields:
            if critical in fields and fields[critical]:
                base_confidence = min(100, base_confidence + 5)

        return round(base_confidence, 2)

    def _validate_extracted_data(self, fields: Dict) -> List[str]:
        """التحقق من صحة البيانات المستخرجة"""

        warnings = []

        # التحقق من الرقم الضريبي
        if 'vat_number' in fields:
            vat = fields['vat_number']
            if len(vat) != 9:
                warnings.append(f'الرقم الضريبي غير صالح: {vat} (يجب أن يكون 9 أرقام)')

        # التحقق من الرقم القومي
        if 'national_id' in fields:
            nid = fields['national_id']
            if len(nid) != 14:
                warnings.append(f'الرقم القومي غير صالح: {nid} (يجب أن يكون 14 رقم)')

        # التحقق من التاريخ
        if 'date' in fields:
            date_str = fields['date']
            if not re.match(r'\d{1,2}/\d{1,2}/\d{2,4}', date_str):
                warnings.append(f'صيغة التاريخ غير معتادة: {date_str}')

        # التحقق من المبالغ
        if 'amounts_found' in fields:
            amounts = fields['amounts_found']
            negative_amounts = [a for a in amounts if a < 0]
            if negative_amounts:
                warnings.append(f'تم اكتشاف مبالغ سالبة: {negative_amounts}')

        # التحقق من وجود تناقضات
        if 'total_amount' in fields and 'line_items' in fields:
            items_total = sum(item.get('total', 0) for item in fields['line_items'])
            if items_total > 0:
                diff_percent = abs(fields['total_amount'] - items_total) / items_total * 100
                if diff_percent > 5:
                    warnings.append(f'تناقض في المجاميع: الفرق {diff_percent:.1f}%')

        return warnings

    def extract_invoice_data(self, document_data: Dict) -> Dict[str, Any]:
        """استخراج بيانات فاتورة ضريبية بشكل متخصص"""

        result = self.process_document(document_data)

        if result['document_type'] != 'invoice':
            result['warnings'].append('هذا المستند قد لا يكون فاتورة ضريبية')

        # استخراج حقول خاصة بالفواتير
        fields = result['fields']

        invoice_specific = {
            'invoice_type': 'tax_invoice' if 'ضريبية' in str(document_data) else 'regular',
            'supply_date': fields.get('date'),
            'due_date': self._extract_due_date(document_data),
            'payment_terms': self._extract_payment_terms(document_data),
            'subtotal': fields.get('total_amount', 0),
            'vat_rate': 14.0,  # معدل VAT المصري
            'vat_amount': fields.get('total_amount', 0) * 0.14,
            'total_with_vat': fields.get('total_amount', 0) * 1.14,
            'currency': self._detect_currency(document_data),
            'discount': self._extract_discount(document_data),
        }

        result['invoice_data'] = invoice_specific

        return result

    def _extract_due_date(self, data: Dict) -> Optional[str]:
        """استخراج تاريخ الاستحقاق"""

        text = str(data.get('text', '') + ' ' + data.get('content', ''))

        patterns = [
            r'تاريخ الاستحقاق[:\\s]+(\d{1,2}/\d{1,2}/\d{2,4})',
            r'due date[:\\s]+(\d{1,2}/\d{1,2}/\d{2,4})',
            r'يستحق الدفع[:\\s]+(\d{1,2}/\d{1,2}/\d{2,4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_payment_terms(self, data: Dict) -> str:
        """استخراج شروط الدفع"""

        text = str(data.get('text', '') + ' ' + data.get('content', ''))

        terms_patterns = [
            r'شروط الدفع[:\\s]+([^\n]+)',
            r'payment terms[:\\s]+([^\n]+)',
            r'الدفع[:\\s]+([^\n]+)',
        ]

        for pattern in terms_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return 'نقداً'

    def _detect_currency(self, data: Dict) -> str:
        """اكتشاف العملة"""

        text = str(data.get('text', '') + ' ' + data.get('content', '')).lower()

        if 'جنيه' in text or 'egp' in text or 'jneh' in text:
            return 'EGP'
        elif 'دولار' in text or 'usd' in text or '$' in text:
            return 'USD'
        elif 'يورو' in text or 'eur' in text or '€' in text:
            return 'EUR'
        elif 'ريال' in text or 'sar' in text:
            return 'SAR'
        elif 'درهم' in text or 'aed' in text:
            return 'AED'

        return 'EGP'  # الافتراضي جنيه مصري

    def _extract_discount(self, data: Dict) -> float:
        """استخراج الخصم"""

        text = str(data.get('text', '') + ' ' + data.get('content', ''))

        patterns = [
            r'خصم[:\\s]+([\d.]+)%?',
            r'discount[:\\s]+([\d.]+)%?',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, TypeError):
                    pass

        return 0.0

    def batch_process(self, documents: List[Dict]) -> Dict[str, Any]:
        """معالجة دفعة من المستندات"""

        results = {
            'agent': self.agent_name,
            'timestamp': datetime.now().isoformat(),
            'batch_id': hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12],
            'total_documents': len(documents),
            'processed': 0,
            'results': [],
            'summary': {
                'by_type': {},
                'avg_confidence': 0.0,
                'total_warnings': 0
            }
        }

        confidence_sum = 0.0

        for doc in documents:
            result = self.process_document(doc)
            results['results'].append(result)
            results['processed'] += 1

            # تجميع حسب النوع
            doc_type = result['document_type']
            results['summary']['by_type'][doc_type] = results['summary']['by_type'].get(doc_type, 0) + 1

            confidence_sum += result['confidence_score']
            results['summary']['total_warnings'] += len(result['warnings'])

        if results['processed'] > 0:
            results['summary']['avg_confidence'] = round(confidence_sum / results['processed'], 2)

        return results


# مثال على الاستخدام
if __name__ == '__main__':
    agent = OCRDocumentIntelligenceAgent()

    # مستند تجريبي (فاتورة)
    sample_invoice = {
        'text': '''
        فاتورة ضريبية
        رقم الفاتورة: INV-2025-001234
        التاريخ: 15/01/2025

        البائع: شركة التقنية الحديثة للتجارة
        الرقم الضريبي: 123456789
        العنوان: القاهرة، شارع التحرير

        المشتري: مؤسسة الأمل للاستثمار
        الرقم القومي: 12345678901234
        الهاتف: 01225155329

        البنود:
        1. لابتوب Dell XPS 15 - عدد 2 - سعر الوحدة 25000 - الإجمالي 50000
        2. طابعة HP LaserJet - عدد 1 - سعر الوحدة 8000 - الإجمالي 8000
        3. حبر طابعة - عدد 5 - سعر الوحدة 500 - الإجمالي 2500

        المجموع: 60500 جنيه
        الشروط: الدفع خلال 30 يوم
        ''',
        'tables': [
            {
                'rows': [
                    {'cells': ['لابتوب Dell XPS 15', 2, 25000, 50000]},
                    {'cells': ['طابعة HP LaserJet', 1, 8000, 8000]},
                    {'cells': ['حبر طابعة', 5, 500, 2500]},
                ]
            }
        ]
    }

    print("=" * 80)
    print("تقرير معالجة المستندات بالذكاء البصري")
    print("=" * 80)

    result = agent.extract_invoice_data(sample_invoice)

    print(f"\n📄 نوع المستند: {result['document_type']}")
    print(f"🎯 درجة الثقة: {result['confidence_score']}%")

    print("\n📋 الحقول المستخرجة:")
    for field, value in result['fields'].items():
        print(f"  • {field}: {value}")

    if result.get('invoice_data'):
        print("\n💰 بيانات الفاتورة:")
        inv = result['invoice_data']
        print(f"  نوع الفاتورة: {inv['invoice_type']}")
        print(f"  التاريخ: {inv['supply_date']}")
        print(f"  الصافي: {inv['subtotal']:,.2f} {inv['currency']}")
        print(f"  الضريبة ({inv['vat_rate']}%): {inv['vat_amount']:,.2f} {inv['currency']}")
        print(f"  الإجمالي مع الضريبة: {inv['total_with_vat']:,.2f} {inv['currency']}")

    if result['warnings']:
        print("\n⚠️ التحذيرات:")
        for warning in result['warnings']:
            print(f"  ! {warning}")

    # معالجة دفعة
    print("\n" + "=" * 80)
    print("معالجة دفعة مستندات")
    print("=" * 80)

    batch_docs = [
        {'text': 'فاتورة ضريبية رقم 001 التاريخ 10/01/2025'},
        {'text': 'إيصال قبض مبلغ 5000 جنيه'},
        {'text': 'كشف حساب بنك مصر يناير 2025'},
        {'text': 'عقد إيجار شقة سكنية'},
    ]

    batch_result = agent.batch_process(batch_docs)

    print("\n📊 ملخص الدفعة:")
    print(f"  إجمالي المستندات: {batch_result['total_documents']}")
    print(f"  تم المعالجة: {batch_result['processed']}")
    print(f"  متوسط الثقة: {batch_result['summary']['avg_confidence']}%")
    print(f"  إجمالي التحذيرات: {batch_result['summary']['total_warnings']}")

    print("\n📁 التوزيع حسب النوع:")
    for doc_type, count in batch_result['summary']['by_type'].items():
        print(f"  • {doc_type}: {count}")

    print("\n✅ اكتملت معالجة المستندات بنجاح!")

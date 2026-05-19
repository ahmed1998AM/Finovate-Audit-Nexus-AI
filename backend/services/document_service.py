"""
Document Service - خدمة إدارة المستندات ومعالجتها
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
import hashlib

logger = logging.getLogger(__name__)


class DocumentService:
    """
    خدمة إدارة المستندات ومعالجتها
    
    المسؤولة عن:
    - رفع المستندات
    - تصنيف المستندات
    - OCR ومعالجة النصوص
    - استخراج البيانات
    - تخزين واسترجاع المستندات
    - إدارة الإصدارات
    """
    
    def __init__(self, storage_path: str = "./uploads"):
        """
        تهيئة خدمة المستندات
        
        Args:
            storage_path: مسار التخزين
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.documents = {}
        self.document_index = {}
        logger.info(f"DocumentService initialized with storage: {storage_path}")
    
    def upload_document(
        self,
        file_path: str,
        document_type: str,
        company_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        رفع مستند جديد
        
        Args:
            file_path: مسار الملف
            document_type: نوع المستند (invoice, receipt, contract, report, etc.)
            company_id: معرف الشركة
            metadata: بيانات وصفية إضافية
            
        Returns:
            معلومات المستند
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {'success': False, 'error': 'File not found'}
        
        # توليد معرف فريد
        doc_id = f"DOC-{company_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8].upper()}"
        
        # نقل الملف إلى مجلد التخزين
        dest_path = self.storage_path / f"{doc_id}_{file_path.name}"
        
        document = {
            'document_id': doc_id,
            'original_name': file_path.name,
            'stored_path': str(dest_path),
            'document_type': document_type,
            'company_id': company_id,
            'file_size': file_path.stat().st_size,
            'file_extension': file_path.suffix,
            'metadata': metadata or {},
            'status': 'uploaded',
            'ocr_status': 'pending',
            'data_extraction_status': 'pending',
            'uploaded_at': datetime.now(),
            'processed_at': None
        }
        
        self.documents[doc_id] = document
        
        # إضافة للفهرس
        if company_id not in self.document_index:
            self.document_index[company_id] = []
        self.document_index[company_id].append(doc_id)
        
        logger.info(f"Uploaded document: {doc_id}")
        return {'success': True, 'document': document}
    
    def process_ocr(self, document_id: str, language: str = 'ara+eng') -> Dict[str, Any]:
        """
        معالجة OCR للمستند
        
        Args:
            document_id: معرف المستند
            language: اللغات المطلوبة (ara+eng)
            
        Returns:
            نتيجة الـ OCR
        """
        if document_id not in self.documents:
            logger.error(f"Document {document_id} not found")
            return {'success': False, 'error': 'Document not found'}
        
        document = self.documents[document_id]
        
        logger.info(f"Processing OCR for document: {document_id}")
        
        # محاكاة عملية OCR
        ocr_result = {
            'success': True,
            'document_id': document_id,
            'text': "نص مستخرج من المستند - محاكاة",
            'confidence': 0.92,
            'language': language,
            'pages': 1,
            'processing_time_ms': 1250
        }
        
        document['ocr_status'] = 'completed'
        document['ocr_result'] = ocr_result
        document['metadata']['ocr_text'] = ocr_result['text']
        
        logger.info(f"OCR completed for document: {document_id}")
        return ocr_result
    
    def extract_data(self, document_id: str, extraction_type: str) -> Dict[str, Any]:
        """
        استخراج البيانات من المستند
        
        Args:
            document_id: معرف المستند
            extraction_type: نوع الاستخراج (invoice_data, receipt_data, contract_terms, etc.)
            
        Returns:
            البيانات المستخرجة
        """
        if document_id not in self.documents:
            logger.error(f"Document {document_id} not found")
            return {'success': False, 'error': 'Document not found'}
        
        document = self.documents[document_id]
        
        if document['ocr_status'] != 'completed':
            logger.warning(f"OCR not completed for document: {document_id}")
            return {'success': False, 'error': 'OCR not completed'}
        
        logger.info(f"Extracting {extraction_type} from document: {document_id}")
        
        # محاكاة استخراج البيانات
        extracted_data = {
            'success': True,
            'document_id': document_id,
            'extraction_type': extraction_type,
            'data': {},
            'confidence': 0.88
        }
        
        if extraction_type == 'invoice_data':
            extracted_data['data'] = {
                'invoice_number': 'INV-2025-001',
                'date': '2025-01-15',
                'vendor': 'شركة المثال التجارية',
                'total_amount': 15000.00,
                'tax_amount': 2250.00,
                'currency': 'EGP'
            }
        elif extraction_type == 'receipt_data':
            extracted_data['data'] = {
                'receipt_number': 'REC-001',
                'date': '2025-01-15',
                'amount': 5000.00,
                'payment_method': 'cash'
            }
        
        document['data_extraction_status'] = 'completed'
        document['extracted_data'] = extracted_data['data']
        document['processed_at'] = datetime.now()
        
        logger.info(f"Data extraction completed for document: {document_id}")
        return extracted_data
    
    def classify_document(self, document_id: str) -> Dict[str, Any]:
        """
        تصنيف المستند تلقائياً
        
        Args:
            document_id: معرف المستند
            
        Returns:
            نتيجة التصنيف
        """
        if document_id not in self.documents:
            logger.error(f"Document {document_id} not found")
            return {'success': False, 'error': 'Document not found'}
        
        document = self.documents[document_id]
        
        logger.info(f"Classifying document: {document_id}")
        
        # محاكاة التصنيف
        classification = {
            'success': True,
            'document_id': document_id,
            'predicted_type': document['document_type'],
            'confidence': 0.95,
            'alternative_types': [
                {'type': 'financial_document', 'confidence': 0.75},
                {'type': 'legal_document', 'confidence': 0.45}
            ]
        }
        
        document['classification'] = classification
        
        logger.info(f"Document classified: {classification['predicted_type']}")
        return classification
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        الحصول على معلومات مستند
        
        Args:
            document_id: معرف المستند
            
        Returns:
            معلومات المستند
        """
        if document_id not in self.documents:
            return {'exists': False}
        
        return {
            'exists': True,
            **self.documents[document_id]
        }
    
    def list_documents(
        self,
        company_id: Optional[int] = None,
        document_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        قائمة المستندات
        
        Args:
            company_id: تصفية حسب الشركة
            document_type: تصفية حسب النوع
            status: تصفية حسب الحالة
            
        Returns:
            قائمة المستندات
        """
        documents = list(self.documents.values())
        
        if company_id is not None:
            documents = [d for d in documents if d['company_id'] == company_id]
        
        if document_type is not None:
            documents = [d for d in documents if d['document_type'] == document_type]
        
        if status is not None:
            documents = [d for d in documents if d['status'] == status]
        
        return documents
    
    def search_documents(self, query: str, company_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        البحث في المستندات
        
        Args:
            query: نص البحث
            company_id: تصفية حسب الشركة
            
        Returns:
            نتائج البحث
        """
        results = []
        
        for doc_id, doc in self.documents.items():
            if company_id and doc['company_id'] != company_id:
                continue
            
            # البحث في الاسم والبيانات الوصفية والنص المستخرج
            searchable_text = f"{doc['original_name']} {doc.get('metadata', {})} {doc.get('ocr_result', {}).get('text', '')}".lower()
            
            if query.lower() in searchable_text:
                results.append(doc)
        
        return results
    
    def delete_document(self, document_id: str) -> bool:
        """
        حذف مستند
        
        Args:
            document_id: معرف المستند
            
        Returns:
            True إذا نجح الحذف
        """
        if document_id not in self.documents:
            logger.error(f"Document {document_id} not found")
            return False
        
        document = self.documents[document_id]
        
        # حذف الملف الفعلي
        file_path = Path(document['stored_path'])
        if file_path.exists():
            file_path.unlink()
        
        # حذف من الفهرس
        company_id = document['company_id']
        if company_id in self.document_index:
            if document_id in self.document_index[company_id]:
                self.document_index[company_id].remove(document_id)
        
        # حذف من القاموس
        del self.documents[document_id]
        
        logger.info(f"Deleted document: {document_id}")
        return True
    
    def get_statistics(self, company_id: Optional[int] = None) -> Dict[str, Any]:
        """
        إحصائيات المستندات
        
        Args:
            company_id: تصفية حسب الشركة
            
        Returns:
            الإحصائيات
        """
        documents = list(self.documents.values())
        
        if company_id is not None:
            documents = [d for d in documents if d['company_id'] == company_id]
        
        total_size = sum(d['file_size'] for d in documents)
        
        stats = {
            'total_documents': len(documents),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_type': {},
            'by_status': {},
            'ocr_completed': len([d for d in documents if d['ocr_status'] == 'completed']),
            'data_extracted': len([d for d in documents if d['data_extraction_status'] == 'completed'])
        }
        
        # حسب النوع
        for doc in documents:
            doc_type = doc['document_type']
            stats['by_type'][doc_type] = stats['by_type'].get(doc_type, 0) + 1
        
        # حسب الحالة
        for doc in documents:
            status = doc['status']
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        return stats

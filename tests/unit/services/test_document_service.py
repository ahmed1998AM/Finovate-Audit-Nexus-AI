"""
Unit Tests for DocumentService - اختبارات وحدة خدمة المستندات
"""

import os
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

from backend.services.document_service import DocumentService


class TestDocumentService:
    """اختبارات خدمة إدارة المستندات ومعالجتها"""

    @pytest.fixture
    def service(self, tmp_path):
        """إنشاء نسخة جديدة من الخدمة مع مسار تخزين مؤقت"""
        storage = tmp_path / "uploads"
        storage.mkdir()
        return DocumentService(storage_path=str(storage))

    @pytest.fixture
    def source_file(self, tmp_path):
        """إنشاء ملف مصدر للاختبار"""
        f = tmp_path / "test_invoice.pdf"
        f.write_text("dummy invoice content for testing")
        return f

    def test_init(self, service, tmp_path):
        """اختبار تهيئة الخدمة والتأكد من مسار التخزين"""
        assert service.storage_path == tmp_path / "uploads"
        assert service.documents == {}
        assert service.document_index == {}

    def test_upload_document_success(self, service, source_file):
        """اختبار رفع مستند بنجاح"""
        result = service.upload_document(str(source_file), "invoice", 1)
        assert result['success'] is True
        doc = result['document']
        assert doc['original_name'] == "test_invoice.pdf"
        assert doc['document_type'] == "invoice"
        assert doc['company_id'] == 1
        assert doc['file_extension'] == ".pdf"
        assert doc['status'] == 'uploaded'
        assert doc['ocr_status'] == 'pending'
        assert doc['data_extraction_status'] == 'pending'
        assert doc['file_size'] > 0
        assert 'document_id' in doc
        assert doc['document_id'].startswith('DOC-1-')

    def test_upload_document_missing_file(self, service):
        """اختبار رفع ملف غير موجود"""
        result = service.upload_document("C:\\nonexistent\\file.pdf", "invoice", 1)
        assert result['success'] is False
        assert result['error'] == 'File not found'

    def test_upload_document_various_types(self, service, tmp_path):
        """اختبار رفع مستندات بأنواع مختلفة"""
        types = ['invoice', 'receipt', 'contract', 'report', 'tax_form']
        for i, doc_type in enumerate(types):
            f = tmp_path / f"doc_{i}.pdf"
            f.write_text(f"content {i}")
            result = service.upload_document(str(f), doc_type, 1)
            assert result['success'] is True
            assert result['document']['document_type'] == doc_type

    def test_upload_document_different_companies(self, service, tmp_path):
        """اختبار رفع مستندات لشركات مختلفة وفحص الفهرس"""
        for cid in [1, 2, 3]:
            f = tmp_path / f"doc_c{cid}.pdf"
            f.write_text(f"content_{cid}")
            result = service.upload_document(str(f), "invoice", cid)
            assert result['success'] is True
            assert result['document']['company_id'] == cid
        assert len(service.documents) == 3
        assert len(service.document_index[1]) == 1
        assert len(service.document_index[2]) == 1
        assert len(service.document_index[3]) == 1

    def test_upload_document_with_metadata(self, service, source_file):
        """اختبار رفع مستند مع بيانات وصفية"""
        metadata = {'department': 'Finance', 'project': 'Q1 Audit', 'priority': 'high'}
        result = service.upload_document(str(source_file), "invoice", 1, metadata=metadata)
        assert result['document']['metadata'] == metadata

    def test_upload_document_default_metadata(self, service, source_file):
        """اختبار رفع مستند بدون بيانات وصفية"""
        result = service.upload_document(str(source_file), "invoice", 1)
        assert result['document']['metadata'] == {}

    def test_get_document_success(self, service, source_file):
        """اختبار الحصول على مستند موجود"""
        upload = service.upload_document(str(source_file), "invoice", 1)
        doc_id = upload['document']['document_id']
        result = service.get_document(doc_id)
        assert result['exists'] is True
        assert result['document_id'] == doc_id
        assert result['original_name'] == "test_invoice.pdf"

    def test_get_document_not_found(self, service):
        """اختبار الحصول على مستند غير موجود"""
        result = service.get_document("NONEXISTENT")
        assert result['exists'] is False

    def test_list_documents_all(self, service, source_file, tmp_path):
        """اختبار قائمة جميع المستندات"""
        service.upload_document(str(source_file), "invoice", 1)
        f2 = tmp_path / "receipt.pdf"
        f2.write_text("receipt content")
        service.upload_document(str(f2), "receipt", 2)
        docs = service.list_documents()
        assert len(docs) == 2

    def test_list_documents_by_company(self, service, source_file, tmp_path):
        """اختبار تصفية المستندات حسب الشركة"""
        service.upload_document(str(source_file), "invoice", 1)
        f2 = tmp_path / "doc2.pdf"
        f2.write_text("doc2")
        service.upload_document(str(f2), "receipt", 2)
        docs = service.list_documents(company_id=1)
        assert len(docs) == 1
        assert docs[0]['company_id'] == 1

    def test_list_documents_by_type(self, service, source_file, tmp_path):
        """اختبار تصفية المستندات حسب النوع"""
        service.upload_document(str(source_file), "invoice", 1)
        f2 = tmp_path / "receipt.pdf"
        f2.write_text("receipt")
        service.upload_document(str(f2), "receipt", 1)
        docs = service.list_documents(document_type='receipt')
        assert len(docs) == 1
        assert docs[0]['document_type'] == 'receipt'

    def test_list_documents_by_status(self, service, source_file):
        """اختبار تصفية المستندات حسب الحالة"""
        service.upload_document(str(source_file), "invoice", 1)
        docs = service.list_documents(status='uploaded')
        assert len(docs) == 1
        docs = service.list_documents(status='processing')
        assert len(docs) == 0

    def test_list_documents_multiple_filters(self, service, source_file, tmp_path):
        """اختبار تصفية المستندات بعدة معايير"""
        service.upload_document(str(source_file), "invoice", 1)
        f2 = tmp_path / "rep.pdf"
        f2.write_text("rep")
        service.upload_document(str(f2), "report", 2)
        docs = service.list_documents(company_id=1, document_type='invoice', status='uploaded')
        assert len(docs) == 1
        assert docs[0]['document_type'] == 'invoice'

    def test_search_documents_by_name(self, service, source_file, tmp_path):
        """اختبار البحث في المستندات حسب الاسم"""
        service.upload_document(str(source_file), "invoice", 1)
        f2 = tmp_path / "quarterly_report.pdf"
        f2.write_text("quarterly")
        service.upload_document(str(f2), "report", 2)
        results = service.search_documents("test_invoice")
        assert len(results) == 1
        assert results[0]['original_name'] == "test_invoice.pdf"

    def test_search_documents_after_ocr(self, service, source_file):
        """اختبار البحث في النص المستخرج من OCR"""
        upload = service.upload_document(str(source_file), "invoice", 1)
        doc_id = upload['document']['document_id']
        service.process_ocr(doc_id)
        results = service.search_documents("مستخرج")
        assert len(results) == 1

    def test_search_documents_empty_query(self, service, source_file):
        """اختبار البحث بنص فارغ"""
        service.upload_document(str(source_file), "invoice", 1)
        results = service.search_documents("")
        assert len(results) == 1

    def test_search_documents_no_results(self, service):
        """اختبار بحث بدون نتائج"""
        results = service.search_documents("nonexistent")
        assert results == []

    def test_search_documents_by_company(self, service, source_file, tmp_path):
        """اختبار البحث مع تصفية حسب الشركة"""
        service.upload_document(str(source_file), "invoice", 1)
        f2 = tmp_path / "invoice2.pdf"
        f2.write_text("inv2")
        service.upload_document(str(f2), "invoice", 2)
        results = service.search_documents("invoice", company_id=1)
        assert len(results) == 1
        assert results[0]['company_id'] == 1

    def test_delete_document_success(self, service, source_file):
        """اختبار حذف مستند بنجاح"""
        upload = service.upload_document(str(source_file), "invoice", 1)
        doc_id = upload['document']['document_id']
        assert service.delete_document(doc_id) is True
        assert doc_id not in service.documents

    def test_delete_document_not_found(self, service):
        """اختبار حذف مستند غير موجود"""
        assert service.delete_document("NONEXISTENT") is False

    def test_delete_document_removes_from_index(self, service, source_file):
        """اختبار إزالة المستند من الفهرس عند الحذف"""
        upload = service.upload_document(str(source_file), "invoice", 1)
        doc_id = upload['document']['document_id']
        cid = upload['document']['company_id']
        assert doc_id in service.document_index[cid]
        service.delete_document(doc_id)
        assert doc_id not in service.document_index[cid]

    def test_delete_document_removes_stored_file(self, service, source_file):
        """اختبار حذف الملف الفعلي من القرص عند حذف المستند"""
        upload = service.upload_document(str(source_file), "invoice", 1)
        doc_id = upload['document']['document_id']
        stored_path = upload['document']['stored_path']
        Path(stored_path).write_text("stored content")
        assert Path(stored_path).exists()
        service.delete_document(doc_id)
        assert not Path(stored_path).exists()

    def test_process_ocr_success(self, service, source_file):
        """اختبار معالجة OCR بنجاح"""
        upload = service.upload_document(str(source_file), "invoice", 1)
        doc_id = upload['document']['document_id']
        result = service.process_ocr(doc_id)
        assert result['success'] is True
        assert result['document_id'] == doc_id
        assert result['text'] == "نص مستخرج من المستند - محاكاة"
        assert result['confidence'] == 0.92
        assert result['language'] == 'ara+eng'
        assert result['pages'] == 1
        assert result['processing_time_ms'] == 1250
        assert service.documents[doc_id]['ocr_status'] == 'completed'

    def test_process_ocr_document_not_found(self, service):
        """اختبار OCR لمستند غير موجود"""
        result = service.process_ocr("NONEXISTENT")
        assert result['success'] is False
        assert result['error'] == 'Document not found'

    def test_process_ocr_with_custom_language(self, service, source_file):
        """اختبار OCR بلغة مخصصة"""
        upload = service.upload_document(str(source_file), "invoice", 1)
        doc_id = upload['document']['document_id']
        result = service.process_ocr(doc_id, language='eng')
        assert result['success'] is True
        assert result['language'] == 'eng'

    def test_extract_data_invoice(self, service, source_file):
        """اختبار استخراج بيانات فاتورة"""
        upload = service.upload_document(str(source_file), "invoice", 1)
        doc_id = upload['document']['document_id']
        service.process_ocr(doc_id)
        result = service.extract_data(doc_id, 'invoice_data')
        assert result['success'] is True
        assert result['extraction_type'] == 'invoice_data'
        assert result['data']['invoice_number'] == 'INV-2025-001'
        assert result['data']['total_amount'] == 15000.00
        assert result['data']['currency'] == 'EGP'
        assert result['data']['tax_amount'] == 2250.00

    def test_extract_data_receipt(self, service, source_file):
        """اختبار استخراج بيانات إيصال"""
        upload = service.upload_document(str(source_file), "receipt", 1)
        doc_id = upload['document']['document_id']
        service.process_ocr(doc_id)
        result = service.extract_data(doc_id, 'receipt_data')
        assert result['success'] is True
        assert result['data']['receipt_number'] == 'REC-001'
        assert result['data']['amount'] == 5000.00
        assert result['data']['payment_method'] == 'cash'

    def test_extract_data_unknown_type(self, service, source_file):
        """اختبار استخراج بيانات بنوع غير معروف"""
        upload = service.upload_document(str(source_file), "contract", 1)
        doc_id = upload['document']['document_id']
        service.process_ocr(doc_id)
        result = service.extract_data(doc_id, 'contract_terms')
        assert result['success'] is True
        assert result['data'] == {}

    def test_extract_data_without_ocr(self, service, source_file):
        """اختبار استخراج بيانات قبل إتمام OCR"""
        upload = service.upload_document(str(source_file), "invoice", 1)
        doc_id = upload['document']['document_id']
        result = service.extract_data(doc_id, 'invoice_data')
        assert result['success'] is False
        assert result['error'] == 'OCR not completed'

    def test_extract_data_document_not_found(self, service):
        """اختبار استخراج بيانات لمستند غير موجود"""
        result = service.extract_data("NONEXISTENT", 'invoice_data')
        assert result['success'] is False
        assert result['error'] == 'Document not found'

    def test_classify_document_success(self, service, source_file):
        """اختبار تصنيف مستند بنجاح"""
        upload = service.upload_document(str(source_file), "invoice", 1)
        doc_id = upload['document']['document_id']
        result = service.classify_document(doc_id)
        assert result['success'] is True
        assert result['predicted_type'] == 'invoice'
        assert result['confidence'] == 0.95
        assert len(result['alternative_types']) == 2

    def test_classify_document_not_found(self, service):
        """اختبار تصنيف مستند غير موجود"""
        result = service.classify_document("NONEXISTENT")
        assert result['success'] is False
        assert result['error'] == 'Document not found'

    def test_get_statistics_empty(self, service):
        """اختبار الإحصائيات عند عدم وجود مستندات"""
        stats = service.get_statistics()
        assert stats['total_documents'] == 0
        assert stats['total_size_bytes'] == 0
        assert stats['total_size_mb'] == 0.0
        assert stats['by_type'] == {}
        assert stats['by_status'] == {}
        assert stats['ocr_completed'] == 0
        assert stats['data_extracted'] == 0

    def test_get_statistics_with_documents(self, service, source_file, tmp_path):
        """اختبار الإحصائيات مع وجود مستندات"""
        service.upload_document(str(source_file), "invoice", 1)
        f2 = tmp_path / "report.pdf"
        f2.write_text("report content")
        service.upload_document(str(f2), "report", 2)
        stats = service.get_statistics()
        assert stats['total_documents'] == 2
        assert stats['total_size_bytes'] > 0
        assert stats['total_size_mb'] >= 0
        assert stats['by_type']['invoice'] == 1
        assert stats['by_type']['report'] == 1
        assert stats['by_status']['uploaded'] == 2

    def test_get_statistics_by_company(self, service, source_file, tmp_path):
        """اختبار الإحصائيات مصفاة حسب الشركة"""
        service.upload_document(str(source_file), "invoice", 1)
        f2 = tmp_path / "doc2.pdf"
        f2.write_text("doc2")
        service.upload_document(str(f2), "report", 2)
        stats = service.get_statistics(company_id=1)
        assert stats['total_documents'] == 1
        assert stats['by_type']['invoice'] == 1
        stats = service.get_statistics(company_id=2)
        assert stats['total_documents'] == 1
        assert stats['by_type']['report'] == 1

    def test_get_statistics_with_ocr_and_extraction(self, service, source_file):
        """اختبار إحصائيات OCR واستخراج البيانات"""
        upload = service.upload_document(str(source_file), "invoice", 1)
        doc_id = upload['document']['document_id']
        service.process_ocr(doc_id)
        service.extract_data(doc_id, 'invoice_data')
        stats = service.get_statistics()
        assert stats['ocr_completed'] == 1
        assert stats['data_extracted'] == 1

    def test_extract_data_updates_document_status(self, service, source_file):
        """اختبار تحديث حالة المستند بعد استخراج البيانات"""
        upload = service.upload_document(str(source_file), "invoice", 1)
        doc_id = upload['document']['document_id']
        service.process_ocr(doc_id)
        service.extract_data(doc_id, 'invoice_data')
        doc = service.documents[doc_id]
        assert doc['data_extraction_status'] == 'completed'
        assert doc['processed_at'] is not None
        assert 'extracted_data' in doc

#!/usr/bin/env python3
"""
Finovate Audit Nexus AI - Advanced OCR & Document Processing Demo
Demonstrates intelligent document processing with OCR, data extraction, and validation.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.ocr_agent import OCRAgent
from database.models import Document
from datetime import datetime


def main():
    print("=" * 70)
    print("OCR & Document Intelligence Demo")
    print("=" * 70)
    print()
    
    # Initialize OCR Agent
    ocr_agent = OCRAgent()
    
    # Sample invoice data (simulating OCR output)
    sample_invoice = {
        "document_type": "invoice",
        "vendor_name": "Tech Solutions LLC",
        "invoice_number": "INV-2024-0892",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "total_amount": 15750.00,
        "tax_amount": 2362.50,
        "currency": "USD",
        "line_items": [
            {"description": "Software License", "quantity": 10, "unit_price": 1200.00, "amount": 12000.00},
            {"description": "Support Services", "quantity": 1, "unit_price": 1387.50, "amount": 1387.50}
        ],
        "confidence_score": 0.96
    }
    
    print("[INFO] Processing invoice document...")
    print()
    
    # Process document through OCR agent
    result = ocr_agent.process_document(sample_invoice)
    
    print("📄 Document Information:")
    print(f"   Type: {result['document_type'].upper()}")
    print(f"   Vendor: {result['vendor_name']}")
    print(f"   Invoice #: {result['invoice_number']}")
    print(f"   Date: {result['invoice_date']}")
    print(f"   Due Date: {result['due_date']}")
    print()
    
    print("💰 Financial Details:")
    print(f"   Subtotal: ${result['total_amount'] - result['tax_amount']:,.2f}")
    print(f"   Tax: ${result['tax_amount']:,.2f}")
    print(f"   Total: ${result['total_amount']:,.2f}")
    print(f"   Currency: {result['currency']}")
    print()
    
    print("📦 Line Items:")
    for i, item in enumerate(result['line_items'], 1):
        print(f"   {i}. {item['description']}")
        print(f"      Qty: {item['quantity']} × ${item['unit_price']:,.2f} = ${item['amount']:,.2f}")
    print()
    
    print("🎯 Validation Results:")
    validation = ocr_agent.validate_extracted_data(result)
    print(f"   Data Quality Score: {validation['quality_score']*100:.1f}%")
    print(f"   Confidence Level: {validation['confidence_level']}")
    print(f"   Anomalies Detected: {len(validation['anomalies'])}")
    
    if validation['anomalies']:
        print("\n⚠️  Anomalies:")
        for anomaly in validation['anomalies']:
            print(f"   - {anomaly}")
    else:
        print("   ✅ No anomalies detected")
    print()
    
    # Create document record
    print("💾 Creating document record in database...")
    doc = Document(
        document_type=result['document_type'],
        file_name=f"{result['invoice_number']}.pdf",
        file_path="/documents/invoices/",
        upload_date=datetime.now(),
        processed=True,
        extracted_data=result,
        confidence_score=result['confidence_score']
    )
    
    print(f"   Document ID: DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    print(f"   Status: {'✅ Processed' if doc.processed else '❌ Failed'}")
    print()
    
    # Demonstrate multi-language support
    print("🌍 Multi-Language Support:")
    languages = ['en', 'ar', 'fr', 'de', 'es']
    for lang in languages:
        status = "✅" if ocr_agent.supports_language(lang) else "❌"
        print(f"   {status} {lang.upper()}")
    print()
    
    print("=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

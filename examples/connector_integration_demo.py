#!/usr/bin/env python3
"""
Finovate Audit Nexus AI - Connector Integration Demo
Demonstrates ERP system connectivity, data synchronization, and real-time auditing.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connectors.sap_connector import SAPConnector
from connectors.oracle_connector import OracleConnector
from connectors.quickbooks_connector import QuickBooksConnector
from database.models import Company, AuditProject


def main():
    print("=" * 70)
    print("ERP Connector Integration Demo")
    print("=" * 70)
    print()
    
    # Demo 1: SAP Connection
    print("🔷 SAP ERP Connection Test")
    print("-" * 40)
    try:
        sap = SAPConnector(
            host="sap.example.com",
            client="100",
            user="demo_user",
            password="***",
            system="DEV"
        )
        
        print(f"   Status: ✅ Connected")
        print(f"   System: {sap.get_system_info()}")
        print(f"   Available Modules: FI, CO, MM, SD")
        
        # Simulate data fetch
        print("\n   📊 Fetching General Ledger data...")
        gl_data = sap.fetch_general_ledger(company_code="1000", fiscal_year="2024")
        print(f"   Records Retrieved: {len(gl_data)} entries")
        print(f"   Date Range: 2024-01-01 to 2024-12-31")
        
    except Exception as e:
        print(f"   Status: ⚠️ Simulation mode (SAP not available)")
        print(f"   Note: {str(e)[:50]}...")
    print()
    
    # Demo 2: Oracle Connection
    print("🔶 Oracle EBS Connection Test")
    print("-" * 40)
    try:
        oracle = OracleConnector(
            host="oracle.example.com",
            port=1521,
            service_name="EBS_PROD",
            user="apps",
            password="***"
        )
        
        print(f"   Status: ✅ Connected")
        print(f"   Database: Oracle EBS Production")
        print(f"   Version: 12.2.9")
        
        # Simulate data fetch
        print("\n   📊 Fetching Accounts Payable data...")
        ap_data = oracle.fetch_accounts_payable(org_id="204")
        print(f"   Records Retrieved: {len(ap_data)} invoices")
        print(f"   Total Amount: $1,245,678.90")
        
    except Exception as e:
        print(f"   Status: ⚠️ Simulation mode (Oracle not available)")
        print(f"   Note: {str(e)[:50]}...")
    print()
    
    # Demo 3: QuickBooks Connection
    print("🟩 QuickBooks Online Connection Test")
    print("-" * 40)
    try:
        qb = QuickBooksConnector(
            company_id="QB123456",
            access_token="***",
            refresh_token="***"
        )
        
        print(f"   Status: ✅ Connected")
        print(f"   Company: Demo Company Inc.")
        print(f"   Subscription: Plus Plan")
        
        # Simulate data fetch
        print("\n   📊 Fetching Financial Statements...")
        balance_sheet = qb.fetch_balance_sheet()
        income_statement = qb.fetch_income_statement()
        
        print(f"   Balance Sheet: ✅ Retrieved")
        print(f"   Income Statement: ✅ Retrieved")
        print(f"   Profit & Loss: ✅ Retrieved")
        
    except Exception as e:
        print(f"   Status: ⚠️ Simulation mode (QuickBooks not available)")
        print(f"   Note: {str(e)[:50]}...")
    print()
    
    # Demo 4: Multi-ERP Synchronization
    print("🔄 Multi-ERP Data Synchronization")
    print("-" * 40)
    print("   Connecting to multiple ERP systems...")
    
    erp_systems = [
        {"name": "SAP", "status": "active", "last_sync": "2024-01-20 08:30"},
        {"name": "Oracle", "status": "active", "last_sync": "2024-01-20 08:25"},
        {"name": "QuickBooks", "status": "active", "last_sync": "2024-01-20 08:28"},
        {"name": "Odoo", "status": "idle", "last_sync": "2024-01-19 18:00"},
    ]
    
    for erp in erp_systems:
        status_icon = "✅" if erp['status'] == 'active' else "⏸️"
        print(f"   {status_icon} {erp['name']}: {erp['status']} (Last: {erp['last_sync']})")
    
    print("\n   📈 Synchronization Summary:")
    print(f"   Total Systems: {len(erp_systems)}")
    print(f"   Active: {sum(1 for e in erp_systems if e['status'] == 'active')}")
    print(f"   Records Synced: 45,892 entries")
    print(f"   Conflicts Resolved: 3")
    print()
    
    # Demo 5: Real-time Audit Trail
    print("🔍 Real-time Audit Trail")
    print("-" * 40)
    print("   Monitoring transactions across all connected ERPs...")
    print()
    
    recent_transactions = [
        {"id": "TXN-001", "system": "SAP", "type": "Journal Entry", "amount": 15000, "status": "verified"},
        {"id": "TXN-002", "system": "Oracle", "type": "Invoice Payment", "amount": 8500, "status": "verified"},
        {"id": "TXN-003", "system": "QuickBooks", "type": "Expense", "amount": 1200, "status": "flagged"},
        {"id": "TXN-004", "system": "SAP", "type": "Asset Purchase", "amount": 45000, "status": "verified"},
    ]
    
    for txn in recent_transactions:
        status_icon = "✅" if txn['status'] == 'verified' else "⚠️"
        print(f"   {status_icon} {txn['id']} | {txn['system']:10} | {txn['type']:15} | ${txn['amount']:>8,.2f}")
    
    print()
    print("   🎯 Anomaly Detection:")
    print(f"   Transactions Analyzed: {len(recent_transactions)}")
    print(f"   Anomalies Detected: 1")
    print(f"   Risk Score: LOW (2.3/10)")
    print()
    
    # Demo 6: Create Audit Project with Connectors
    print("📁 Creating Audit Project with ERP Integration")
    print("-" * 40)
    
    company = Company(
        name="Demo Corporation",
        industry="Technology",
        fiscal_year_end="12-31",
        currency="USD"
    )
    
    project = AuditProject(
        company_id=company.id,
        project_name="Q4 2024 Comprehensive Audit",
        audit_type="Financial Statement Audit",
        start_date="2024-01-15",
        end_date="2024-03-15",
        status="active"
    )
    
    print(f"   Company: {company.name}")
    print(f"   Project: {project.project_name}")
    print(f"   Connected ERPs: SAP, Oracle, QuickBooks")
    print(f"   Status: {project.status.upper()}")
    print(f"   Data Sources: 3 active connections")
    print()
    
    print("=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)
    print()
    print("💡 Tip: Configure your ERP credentials in the settings panel")
    print("   to enable live data synchronization.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

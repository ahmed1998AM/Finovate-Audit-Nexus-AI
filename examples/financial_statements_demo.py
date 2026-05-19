#!/usr/bin/env python3
"""
Finovate Audit Nexus AI - Financial Statements Generation Demo
Demonstrates automated financial statement preparation with AI analysis.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.financial_statements_agent import FinancialStatementsAgent
from backend.services.reporting_service import ReportingService
from datetime import datetime


def main():
    print("=" * 70)
    print("Financial Statements Generation Demo")
    print("=" * 70)
    print()
    
    # Initialize agents
    fs_agent = FinancialStatementsAgent()
    reporting = ReportingService()
    
    # Sample financial data
    sample_data = {
        "company_name": "Tech Innovations Corp",
        "fiscal_year": 2024,
        "currency": "USD",
        "balance_sheet": {
            "assets": {
                "current_assets": {
                    "cash_and_equivalents": 2500000,
                    "accounts_receivable": 1800000,
                    "inventory": 950000,
                    "prepaid_expenses": 150000,
                    "total_current_assets": 5400000
                },
                "non_current_assets": {
                    "property_plant_equipment": 8500000,
                    "intangible_assets": 2200000,
                    "investments": 1500000,
                    "total_non_current_assets": 12200000
                },
                "total_assets": 17600000
            },
            "liabilities": {
                "current_liabilities": {
                    "accounts_payable": 1200000,
                    "short_term_debt": 800000,
                    "accrued_expenses": 450000,
                    "total_current_liabilities": 2450000
                },
                "non_current_liabilities": {
                    "long_term_debt": 5000000,
                    "deferred_tax": 650000,
                    "total_non_current_liabilities": 5650000
                },
                "total_liabilities": 8100000
            },
            "equity": {
                "common_stock": 5000000,
                "retained_earnings": 4200000,
                "other_comprehensive_income": 300000,
                "total_equity": 9500000
            }
        },
        "income_statement": {
            "revenue": 15800000,
            "cost_of_goods_sold": 9480000,
            "gross_profit": 6320000,
            "operating_expenses": {
                "selling_general_admin": 3200000,
                "research_development": 1500000,
                "depreciation_amortization": 420000,
                "total_operating_expenses": 5120000
            },
            "operating_income": 1200000,
            "other_income_expense": -180000,
            "income_before_tax": 1020000,
            "income_tax_expense": 255000,
            "net_income": 765000
        },
        "cash_flow": {
            "operating_activities": 1850000,
            "investing_activities": -2200000,
            "financing_activities": 650000,
            "net_change_in_cash": 300000
        }
    }
    
    print(f"📊 Company: {sample_data['company_name']}")
    print(f"📅 Fiscal Year: {sample_data['fiscal_year']}")
    print(f"💱 Currency: {sample_data['currency']}")
    print()
    
    # Generate Balance Sheet
    print("=" * 70)
    print("BALANCE SHEET")
    print("=" * 70)
    print()
    
    bs = sample_data['balance_sheet']
    
    print("ASSETS")
    print("-" * 40)
    print("Current Assets:")
    for key, value in bs['assets']['current_assets'].items():
        if key != 'total_current_assets':
            print(f"   {key.replace('_', ' ').title():<30} ${value:>12,.2f}")
    print(f"   {'Total Current Assets':<30} ${bs['assets']['current_assets']['total_current_assets']:>12,.2f}")
    print()
    
    print("Non-Current Assets:")
    for key, value in bs['assets']['non_current_assets'].items():
        if key != 'total_non_current_assets':
            print(f"   {key.replace('_', ' ').title():<30} ${value:>12,.2f}")
    print(f"   {'Total Non-Current Assets':<30} ${bs['assets']['non_current_assets']['total_non_current_assets']:>12,.2f}")
    print()
    print(f"   {'TOTAL ASSETS':<30} ${bs['assets']['total_assets']:>12,.2f}")
    print()
    
    print("LIABILITIES & EQUITY")
    print("-" * 40)
    print("Current Liabilities:")
    for key, value in bs['liabilities']['current_liabilities'].items():
        if key != 'total_current_liabilities':
            print(f"   {key.replace('_', ' ').title():<30} ${value:>12,.2f}")
    print(f"   {'Total Current Liabilities':<30} ${bs['liabilities']['current_liabilities']['total_current_liabilities']:>12,.2f}")
    print()
    
    print("Non-Current Liabilities:")
    for key, value in bs['liabilities']['non_current_liabilities'].items():
        if key != 'total_non_current_liabilities':
            print(f"   {key.replace('_', ' ').title():<30} ${value:>12,.2f}")
    print(f"   {'Total Non-Current Liabilities':<30} ${bs['liabilities']['non_current_liabilities']['total_non_current_liabilities']:>12,.2f}")
    print()
    print(f"   {'Total Liabilities':<30} ${bs['liabilities']['total_liabilities']:>12,.2f}")
    print()
    
    print("Equity:")
    for key, value in bs['equity'].items():
        if key != 'total_equity':
            print(f"   {key.replace('_', ' ').title():<30} ${value:>12,.2f}")
    print(f"   {'Total Equity':<30} ${bs['equity']['total_equity']:>12,.2f}")
    print()
    print(f"   {'TOTAL LIABILITIES & EQUITY':<30} ${bs['liabilities']['total_liabilities'] + bs['equity']['total_equity']:>12,.2f}")
    print()
    
    # Generate Income Statement
    print("=" * 70)
    print("INCOME STATEMENT")
    print("=" * 70)
    print()
    
    is_data = sample_data['income_statement']
    
    print(f"   {'Revenue':<30} ${is_data['revenue']:>12,.2f}")
    print(f"   {'Cost of Goods Sold':<30} ${is_data['cost_of_goods_sold']:>12,.2f}")
    print(f"   {'─' * 30}")
    print(f"   {'Gross Profit':<30} ${is_data['gross_profit']:>12,.2f}")
    print()
    
    print("Operating Expenses:")
    for key, value in is_data['operating_expenses'].items():
        if key != 'total_operating_expenses':
            print(f"   {key.replace('_', ' ').title():<30} ${value:>12,.2f}")
    print(f"   {'Total Operating Expenses':<30} ${is_data['operating_expenses']['total_operating_expenses']:>12,.2f}")
    print()
    
    print(f"   {'Operating Income':<30} ${is_data['operating_income']:>12,.2f}")
    print(f"   {'Other Income/Expense':<30} ${is_data['other_income_expense']:>12,.2f}")
    print(f"   {'─' * 30}")
    print(f"   {'Income Before Tax':<30} ${is_data['income_before_tax']:>12,.2f}")
    print(f"   {'Income Tax Expense':<30} ${is_data['income_tax_expense']:>12,.2f}")
    print(f"   {'─' * 30}")
    print(f"   {'NET INCOME':<30} ${is_data['net_income']:>12,.2f}")
    print()
    
    # AI Analysis
    print("=" * 70)
    print("AI FINANCIAL ANALYSIS")
    print("=" * 70)
    print()
    
    analysis = fs_agent.analyze_financial_health(sample_data)
    
    print("🎯 Financial Health Score:")
    score = analysis.get('overall_score', 85)
    rating = "Excellent" if score >= 90 else "Good" if score >= 75 else "Fair" if score >= 60 else "Poor"
    print(f"   Score: {score}/100 ({rating})")
    print()
    
    print("📈 Key Ratios:")
    ratios = analysis.get('ratios', {})
    print(f"   Current Ratio: {ratios.get('current_ratio', 2.2):.2f}")
    print(f"   Debt-to-Equity: {ratios.get('debt_to_equity', 0.85):.2f}")
    print(f"   Return on Equity: {ratios.get('roe', 8.05):.2f}%")
    print(f"   Gross Margin: {ratios.get('gross_margin', 40.0):.1f}%")
    print(f"   Net Profit Margin: {ratios.get('net_margin', 4.84):.2f}%")
    print()
    
    print("✅ Strengths:")
    for strength in analysis.get('strengths', ["Strong liquidity position", "Healthy profit margins"]):
        print(f"   • {strength}")
    print()
    
    print("⚠️ Areas for Improvement:")
    for area in analysis.get('weaknesses', ["High debt-to-equity ratio", "Low asset turnover"]):
        print(f"   • {area}")
    print()
    
    print("💡 Recommendations:")
    for rec in analysis.get('recommendations', []):
        print(f"   • {rec}")
    print()
    
    # Export options
    print("=" * 70)
    print("EXPORT OPTIONS")
    print("=" * 70)
    print()
    
    formats = ['PDF', 'Excel', 'Word', 'HTML', 'JSON']
    for fmt in formats:
        status = "✅ Available"
        print(f"   {fmt:<10} {status}")
    print()
    
    print("📧 Distribution:")
    print("   • Email to stakeholders: Ready")
    print("   • Upload to regulatory portal: Ready")
    print("   • Archive in document management: Ready")
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

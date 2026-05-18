#!/usr/bin/env python3
"""
Finovate Audit Nexus AI - Demo Example
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
import random

print("Loading agents...")

# Import agents
from agents.journal_agent.agent import JournalEntryAuditAgent
from agents.ledger_agent.agent import GeneralLedgerAuditAgent  
from agents.tb_agent.agent import TrialBalanceAuditAgent
from agents.tax_agent.agent import TaxComplianceAgent
from backend.orchestrator.agent_orchestrator import AgentOrchestrator

print("Agents loaded successfully!")

async def run_demo():
    print("=" * 80)
    print("Finovate Audit Nexus AI - Comprehensive Demo")
    print("=" * 80)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    print(f"Orchestrator initialized: {orchestrator.orchestrator_id}")
    
    # Initialize agents
    journal_agent = JournalEntryAuditAgent()
    ledger_agent = GeneralLedgerAuditAgent()
    tb_agent = TrialBalanceAuditAgent()
    tax_agent = TaxComplianceAgent(country="EG")
    
    # Register agents
    orchestrator.register_agent("journal_agent", journal_agent)
    orchestrator.register_agent("ledger_agent", ledger_agent)
    orchestrator.register_agent("tb_agent", tb_agent)
    orchestrator.register_agent("tax_agent", tax_agent)
    
    print(f"Registered {len(orchestrator.agents)} agents")
    
    # Generate sample data
    print("\nGenerating sample data...")
    
    # Sample journal entries
    entries = []
    base_date = datetime(2024, 1, 1)
    for i in range(50):
        amount = random.randint(1000, 50000)
        if i % 10 == 0:
            amount = 100000  # Large round amount
        entries.append({
            "entry_id": f"JE{i+1:05d}",
            "posting_date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
            "account_code": random.choice(["1001", "1002", "2001", "4001"]),
            "amount": amount,
            "description": "Sample entry",
            "created_by": random.choice(["user1", "user2"])
        })
    journal_data = pd.DataFrame(entries)
    print(f"Generated {len(journal_data)} journal entries")
    
    # Sample trial balance
    tb_data = pd.DataFrame([
        {"account_code": "1001", "account_name": "Cash", "debit": 500000, "credit": 0},
        {"account_code": "1002", "account_name": "AR", "debit": 300000, "credit": 0},
        {"account_code": "2001", "account_name": "AP", "debit": 0, "credit": 250000},
        {"account_code": "3001", "account_name": "Equity", "debit": 0, "credit": 400000},
        {"account_code": "4001", "account_name": "Revenue", "debit": 0, "credit": 800000},
        {"account_code": "5001", "account_name": "Expenses", "debit": 650000, "credit": 0},
    ])
    print(f"Generated {len(tb_data)} TB accounts")
    
    # Run audits
    print("\n" + "-" * 80)
    print("Running Journal Entry Audit...")
    journal_results = await journal_agent.analyze_journal_entries(journal_data)
    print(f"Risk Score: {journal_results['risk_score']}/100")
    
    print("\nRunning Ledger Audit...")
    ledger_results = await ledger_agent.analyze_ledger(journal_data)
    print(f"Total Entries: {ledger_results['total_entries']}")
    
    print("\nRunning Trial Balance Audit...")
    tb_results = await tb_agent.analyze_trial_balance(tb_data)
    print(f"Balanced: {tb_results['is_balanced']}")
    
    print("\n" + "=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)
    print("\nFinovate Audit Nexus AI - Developed by Ahmed Mostafa Ibrahim")

if __name__ == "__main__":
    asyncio.run(run_demo())

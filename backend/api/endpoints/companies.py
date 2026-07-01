"""
Finovate Audit Nexus AI - Companies API Endpoints
Company Management and Configuration
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.database.models import ChartOfAccount, JournalEntry
from backend.database.models import Company as CompanyModel

router = APIRouter()

class CompanyCreate(BaseModel):
    name: str
    tax_id: str
    commercial_registration: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    fiscal_year_start: int = 1
    currency: str = 'EGP'

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    fiscal_year_start: Optional[int] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None

class CompanyResponse(BaseModel):
    id: int
    name: str
    tax_id: str
    commercial_registration: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    fiscal_year_start: int
    currency: str
    is_active: bool
    created_at: datetime

@router.get("/", response_model=List[CompanyResponse])
async def get_companies(db: Session = Depends(get_db)):
    companies = db.query(CompanyModel).order_by(CompanyModel.name).all()
    return [
        CompanyResponse(
            id=c.id, name=c.name, tax_id=c.tax_id,
            commercial_registration=c.commercial_registration, address=c.address,
            phone=c.phone, email=c.email, fiscal_year_start=c.fiscal_year_start,
            currency=c.currency, is_active=c.is_active, created_at=c.created_at
        ) for c in companies
    ]

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = CompanyModel(
        name=company.name, tax_id=company.tax_id,
        commercial_registration=company.commercial_registration,
        address=company.address, phone=company.phone, email=company.email,
        fiscal_year_start=company.fiscal_year_start, currency=company.currency
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return CompanyResponse(
        id=db_company.id, name=db_company.name, tax_id=db_company.tax_id,
        commercial_registration=db_company.commercial_registration,
        address=db_company.address, phone=db_company.phone, email=db_company.email,
        fiscal_year_start=db_company.fiscal_year_start, currency=db_company.currency,
        is_active=db_company.is_active, created_at=db_company.created_at
    )

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return CompanyResponse(
        id=company.id, name=company.name, tax_id=company.tax_id,
        commercial_registration=company.commercial_registration,
        address=company.address, phone=company.phone, email=company.email,
        fiscal_year_start=company.fiscal_year_start, currency=company.currency,
        is_active=company.is_active, created_at=company.created_at
    )

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: int, company_update: CompanyUpdate, db: Session = Depends(get_db)):
    company = db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    update_data = company_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return CompanyResponse(
        id=company.id, name=company.name, tax_id=company.tax_id,
        commercial_registration=company.commercial_registration,
        address=company.address, phone=company.phone, email=company.email,
        fiscal_year_start=company.fiscal_year_start, currency=company.currency,
        is_active=company.is_active, created_at=company.created_at
    )

@router.delete("/{company_id}")
async def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
    if company:
        company.is_active = False
        db.commit()
    return {"success": True, "message": "Company deactivated successfully"}

@router.get("/{company_id}/chart-of-accounts")
async def get_chart_of_accounts(company_id: int, db: Session = Depends(get_db)):
    accounts = db.query(ChartOfAccount).filter(ChartOfAccount.company_id == company_id).all()
    return {
        "accounts": [
            {
                "id": a.id, "account_code": a.account_code,
                "account_name_ar": a.account_name_ar,
                "account_name_en": a.account_name_en,
                "account_type": a.account_type, "level": a.level,
                "is_active": a.is_active
            } for a in accounts
        ]
    }

@router.get("/{company_id}/journal-entries")
async def get_journal_entries(company_id: int, year: int = None, period: int = None, db: Session = Depends(get_db)):
    query = db.query(JournalEntry).filter(JournalEntry.company_id == company_id)
    if year:
        query = query.filter(JournalEntry.fiscal_year == year)
    if period:
        query = query.filter(JournalEntry.fiscal_period == period)
    entries = query.order_by(JournalEntry.entry_date.desc()).all()
    return {
        "entries": [
            {
                "id": e.id, "entry_number": e.entry_number,
                "entry_date": e.entry_date, "description": e.description,
                "source_system": e.source_system, "is_posted": e.is_posted,
                "fiscal_year": e.fiscal_year, "fiscal_period": e.fiscal_period
            } for e in entries
        ]
    }

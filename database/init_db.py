"""
Database Initialization Script
==============================
Initializes the SQLite/PostgreSQL database for Finovate Audit Nexus AI.
"""
import os
import sys
from sqlalchemy import create_all, create_engine
from database.models.schema import Base

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def init_db():
    """تهيئة قاعدة البيانات"""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./finovate_audit.db")
    print(f"🔄 Initializing database at: {db_url}")
    
    try:
        engine = create_engine(db_url)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()

"""
Database Initialization Script
==============================
Initializes the SQLite/PostgreSQL database for Finovate Audit Nexus AI.
"""
import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

def init_db():
    """تهيئة قاعدة البيانات"""
    from backend.database import init_db as backend_init
    from backend.database import get_db_session
    from backend.database.bootstrap import seed_default_data

    db_url = os.getenv("DATABASE_URL", "sqlite:///./finovate_audit.db")
    logger.info("Initializing database at: %s", db_url)

    try:
        backend_init()
        logger.info("Database tables created successfully!")
        with get_db_session() as session:
            seed_default_data(session)
        logger.info("Default data seeded successfully!")
    except Exception as e:
        logger.error("Error initializing database: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    init_db()

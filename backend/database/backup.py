"""
Finovate Audit Nexus AI - Database Backup Module
"""
import datetime
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

BACKUP_DIR = os.getenv("BACKUP_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backups"))
MAX_BACKUPS = int(os.getenv("MAX_BACKUPS", "10"))


def _ensure_backup_dir():
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)


def _cleanup_old_backups(prefix: str):
    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith(prefix) and f.endswith(".backup")],
        reverse=True
    )
    for old in backups[MAX_BACKUPS:]:
        os.remove(os.path.join(BACKUP_DIR, old))
        logger.info("Removed old backup: %s", old)


def backup_sqlite(db_path: str) -> Optional[str]:
    _ensure_backup_dir()
    if not os.path.exists(db_path):
        logger.error("Database file not found: %s", db_path)
        return None
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"finovate_sqlite_{timestamp}.backup"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    try:
        shutil.copy2(db_path, backup_path)
        logger.info("SQLite backup created: %s (%d bytes)", backup_path, os.path.getsize(backup_path))
        _cleanup_old_backups("finovate_sqlite_")
        return backup_path
    except Exception as e:
        logger.error("SQLite backup failed: %s", e)
        return None


def backup_postgres(database_url: str) -> Optional[str]:
    _ensure_backup_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"finovate_postgres_{timestamp}.backup"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    try:
        result = subprocess.run(
            ["pg_dump", database_url, "--no-owner", "--format=custom", "--file", backup_path],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            logger.info("PostgreSQL backup created: %s", backup_path)
            _cleanup_old_backups("finovate_postgres_")
            return backup_path
        else:
            logger.error("pg_dump failed: %s", result.stderr)
            return None
    except FileNotFoundError:
        logger.error("pg_dump not installed. Cannot backup PostgreSQL.")
        return None
    except Exception as e:
        logger.error("PostgreSQL backup failed: %s", e)
        return None


def create_backup(database_url: Optional[str] = None) -> Optional[str]:
    db_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./finovate_audit.db")
    if db_url.startswith("sqlite"):
        db_path = db_url.replace("sqlite:///", "")
        return backup_sqlite(db_path)
    elif db_url.startswith("postgresql"):
        return backup_postgres(db_url)
    else:
        logger.warning("Unsupported database type for backup: %s", db_url)
        return None


def list_backups() -> list:
    _ensure_backup_dir()
    backups = []
    for f in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if f.endswith(".backup"):
            fpath = os.path.join(BACKUP_DIR, f)
            backups.append({
                "filename": f,
                "size_bytes": os.path.getsize(fpath),
                "created_at": datetime.datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat()
            })
    return backups


def restore_backup(backup_filename: str, database_url: Optional[str] = None) -> bool:
    db_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./finovate_audit.db")
    _ensure_backup_dir()
    safe_path = os.path.normpath(os.path.join(BACKUP_DIR, backup_filename))
    if not safe_path.startswith(os.path.normpath(BACKUP_DIR)):
        logger.error("Path traversal detected: %s", backup_filename)
        return False
    if not os.path.exists(safe_path):
        logger.error("Backup file not found: %s", safe_path)
        return False
    try:
        if db_url.startswith("sqlite"):
            db_path = db_url.replace("sqlite:///", "")
            shutil.copy2(safe_path, db_path)
            logger.info("SQLite restored from: %s", safe_path)
            return True
        elif db_url.startswith("postgresql"):
            result = subprocess.run(
                ["pg_restore", "--clean", "--no-owner", "--dbname", db_url, safe_path],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                logger.info("PostgreSQL restored from: %s", safe_path)
                return True
            else:
                logger.error("pg_restore failed: %s", result.stderr)
                return False
        else:
            logger.warning("Unsupported database type for restore: %s", db_url)
            return False
    except Exception as e:
        logger.error("Restore failed: %s", e)
        return False

"""
Finovate Audit Nexus AI - Database Package (Deprecated)
======================================================
WARNING: This package is deprecated. Use `backend.database` instead.
This module re-exports from backend.database for backward compatibility.
"""
import warnings
import logging

logger = logging.getLogger(__name__)
logger.warning(
    "The `database` package at project root is deprecated. "
    "Use `backend.database` instead."
)

from backend.database import (  # noqa: F401, E402
    DatabaseConfig,
    init_db,
    get_db,
    get_db_session,
    db_config,
)

__all__ = ["DatabaseConfig", "init_db", "get_db", "get_db_session", "db_config"]

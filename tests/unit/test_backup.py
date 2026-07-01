"""
Tests for the database backup module
"""
import os
import time
import tempfile
import shutil
from unittest.mock import patch

import pytest

from backend.database.backup import (
    _ensure_backup_dir,
    _cleanup_old_backups,
    backup_sqlite,
    create_backup,
    list_backups,
    restore_backup,
)


class TestBackup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "test.db")
        with open(self.db_path, "w") as f:
            f.write("test database content")
        with patch("backend.database.backup.BACKUP_DIR", self.tmp_dir):
            yield
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_ensure_backup_dir_creates(self):
        new_dir = os.path.join(self.tmp_dir, "nested", "backups")
        with patch("backend.database.backup.BACKUP_DIR", new_dir):
            _ensure_backup_dir()
            assert os.path.exists(new_dir)

    def test_backup_sqlite_creates_file(self):
        result = backup_sqlite(self.db_path)
        assert result is not None
        assert result.endswith(".backup")
        assert os.path.exists(result)

    def test_backup_sqlite_missing_db(self):
        result = backup_sqlite("/nonexistent/path.db")
        assert result is None

    def test_create_backup_sqlite(self):
        with patch.dict(os.environ, {"DATABASE_URL": f"sqlite:///{self.db_path}"}):
            result = create_backup()
            assert result is not None
            assert os.path.exists(result)

    def test_list_backups(self):
        backup_sqlite(self.db_path)
        time.sleep(1.1)
        backup_sqlite(self.db_path)
        backups = list_backups()
        assert len(backups) == 2
        for b in backups:
            assert "filename" in b
            assert "size_bytes" in b
            assert "created_at" in b

    def test_restore_backup(self):
        backup_path = backup_sqlite(self.db_path)
        assert backup_path is not None
        filename = os.path.basename(backup_path)
        original_content = open(self.db_path).read()
        with open(self.db_path, "w") as f:
            f.write("modified content")
        with patch.dict(os.environ, {"DATABASE_URL": f"sqlite:///{self.db_path}"}):
            ok = restore_backup(filename)
            assert ok is True
            assert open(self.db_path).read() == original_content

    def test_restore_backup_not_found(self):
        ok = restore_backup("nonexistent.backup")
        assert ok is False

    def test_restore_backup_path_traversal(self):
        ok = restore_backup("../../etc/passwd")
        assert ok is False

    def test_cleanup_old_backups(self):
        for i in range(15):
            p = os.path.join(self.tmp_dir, f"finovate_sqlite_{i:04d}.backup")
            with open(p, "w") as f:
                f.write(str(i))
        with patch("backend.database.backup.MAX_BACKUPS", 10):
            _cleanup_old_backups("finovate_sqlite_")
            remaining = [f for f in os.listdir(self.tmp_dir) if f.endswith(".backup")]
            assert len(remaining) <= 10

    def test_backup_unsupported_db_type(self):
        with patch.dict(os.environ, {"DATABASE_URL": "mysql://localhost/test"}):
            result = create_backup()
            assert result is None

    def test_list_backups_empty(self):
        backups = list_backups()
        assert backups == []

    def test_create_backup_default_url(self):
        result = create_backup(database_url=f"sqlite:///{self.db_path}")
        assert result is not None
        assert os.path.exists(result)

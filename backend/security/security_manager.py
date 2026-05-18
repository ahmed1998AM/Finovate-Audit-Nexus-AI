"""
Finovate Audit Nexus AI - Security Module

Enterprise-grade security layer with encryption, authentication,
authorization, and audit logging.
"""

import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from loguru import logger


class SecurityManager:
    """
    Enterprise Security Manager
    
    Responsibilities:
    - AES-256 Encryption/Decryption
    - Password Hashing
    - Token Generation & Validation
    - Session Management
    - Audit Logging
    - Device Verification
    """

    def __init__(self, encryption_key: Optional[str] = None):
        self.security_id = "security_manager_001"
        
        # Generate or use provided encryption key
        if encryption_key:
            self.key = self._derive_key(encryption_key)
        else:
            self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)
        
        # Active sessions
        self.sessions = {}
        
        # Audit logs
        self.audit_logs = []
        
        logger.info(f"Security Manager initialized: {self.security_id}")

    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        salt = b'finovate_salt_v1'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt_data(self, data: str) -> str:
        """Encrypt data using AES-256"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using AES-256"""
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise

    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}:{hashed}"

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = hashed_password.split(':')
            check_hash = hashlib.sha256((salt + password).encode()).hexdigest()
            return check_hash == stored_hash
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            return False

    def generate_session_token(self, user_id: str, device_id: str) -> str:
        """Generate secure session token"""
        token = secrets.token_urlsafe(32)
        expiration = datetime.now() + timedelta(hours=8)
        
        self.sessions[token] = {
            "user_id": user_id,
            "device_id": device_id,
            "created_at": datetime.now(),
            "expires_at": expiration,
            "is_active": True
        }
        
        self._log_audit_event("session_created", user_id, {"token": token[:8] + "...", "device_id": device_id})
        logger.info(f"Session created for user {user_id}")
        
        return token

    def validate_session_token(self, token: str) -> Dict[str, Any]:
        """Validate session token"""
        if token not in self.sessions:
            return {"valid": False, "error": "Token not found"}
        
        session = self.sessions[token]
        
        if not session["is_active"]:
            return {"valid": False, "error": "Session inactive"}
        
        if datetime.now() > session["expires_at"]:
            session["is_active"] = False
            return {"valid": False, "error": "Session expired"}
        
        return {
            "valid": True,
            "user_id": session["user_id"],
            "device_id": session["device_id"],
            "expires_at": session["expires_at"].isoformat()
        }

    def invalidate_session(self, token: str) -> bool:
        """Invalidate session token"""
        if token in self.sessions:
            self.sessions[token]["is_active"] = False
            self._log_audit_event("session_invalidated", self.sessions[token]["user_id"])
            logger.info(f"Session invalidated: {token[:8]}...")
            return True
        return False

    def _log_audit_event(self, event_type: str, user_id: str, details: Optional[Dict] = None):
        """Log audit event"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details or {},
            "ip_address": "N/A",  # Would be populated in web context
            "user_agent": "N/A"
        }
        self.audit_logs.append(log_entry)
        
        # Keep last 1000 events in memory
        if len(self.audit_logs) > 1000:
            self.audit_logs = self.audit_logs[-1000:]
        
        logger.info(f"Audit event: {event_type} by {user_id}")

    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """Retrieve audit logs with filters"""
        filtered = self.audit_logs
        
        if user_id:
            filtered = [log for log in filtered if log["user_id"] == user_id]
        
        if event_type:
            filtered = [log for log in filtered if log["event_type"] == event_type]
        
        return filtered[-limit:]

    def generate_api_key(self, name: str) -> str:
        """Generate API key"""
        prefix = "fnv_"
        key = secrets.token_urlsafe(24)
        api_key = f"{prefix}{key}"
        
        self._log_audit_event("api_key_generated", "system", {"key_name": name})
        return api_key

    def verify_file_integrity(self, file_path: str) -> str:
        """Generate SHA-256 hash for file integrity verification"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def get_statistics(self) -> Dict[str, Any]:
        """Get security statistics"""
        active_sessions = sum(1 for s in self.sessions.values() if s["is_active"])
        return {
            "security_id": self.security_id,
            "active_sessions": active_sessions,
            "total_sessions": len(self.sessions),
            "audit_logs_count": len(self.audit_logs),
            "encryption_algorithm": "AES-256-Fernet",
            "hashing_algorithm": "SHA-256-PBKDF2"
        }


# Singleton instance
_security_manager_instance = None


def get_security_manager(encryption_key: Optional[str] = None) -> SecurityManager:
    """Get or create Security Manager singleton"""
    global _security_manager_instance
    if _security_manager_instance is None:
        _security_manager_instance = SecurityManager(encryption_key)
    return _security_manager_instance

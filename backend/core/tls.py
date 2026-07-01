"""
Finovate Audit Nexus AI - TLS/SSL Configuration
HTTPS support for production deployments
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class TLSConfig:
    def __init__(self):
        self.enabled = os.getenv("TLS_ENABLED", "false").lower() == "true"
        self.cert_path = os.getenv("TLS_CERT_PATH", "")
        self.key_path = os.getenv("TLS_KEY_PATH", "")
        self._validate()

    def _validate(self):
        if not self.enabled:
            return
        if not self.cert_path or not self.key_path:
            logger.warning("TLS enabled but cert/key paths not set. Falling back to HTTP.")
            self.enabled = False
            return
        cert = Path(self.cert_path)
        key = Path(self.key_path)
        if not cert.exists():
            logger.error(f"TLS certificate not found: {self.cert_path}")
            self.enabled = False
            return
        if not key.exists():
            logger.error(f"TLS key not found: {self.key_path}")
            self.enabled = False
            return
        logger.info(f"TLS configured: cert={self.cert_path}, key={self.key_path}")

    def get_ssl_context(self) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        import ssl
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(self.cert_path, self.key_path)
        return context

    def get_uvicorn_kwargs(self) -> Dict[str, Any]:
        if not self.enabled:
            return {}
        return {
            "ssl_certfile": self.cert_path,
            "ssl_keyfile": self.key_path,
        }


tls_config = TLSConfig()

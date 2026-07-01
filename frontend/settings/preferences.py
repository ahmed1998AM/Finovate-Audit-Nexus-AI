"""
Finovate Audit Nexus AI - Preferences Manager
Enterprise AI Financial Audit & Intelligence Platform
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class PreferencesManager:
    """Manages application preferences and settings with validation"""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path.home() / ".finovate" / "preferences.json"

        self.config_path = config_path
        self.preferences: Dict[str, Any] = {}
        self._dirty = False
        self.load_preferences()
        logger.debug(f"Preferences loaded from {config_path}")

    def load_preferences(self) -> None:
        """Load preferences from file, merging with defaults"""
        defaults = self.get_default_preferences()

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                self.preferences = self._deep_merge(defaults, loaded)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Error loading preferences: {e}, using defaults")
                self.preferences = defaults
        else:
            self.preferences = defaults
            self.save_preferences()

    def save_preferences(self) -> bool:
        """Save preferences to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            self._dirty = False
            logger.info("Preferences saved successfully")
            return True
        except IOError as e:
            logger.error(f"Error saving preferences: {e}")
            return False

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """Recursively merge override into base dict"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = PreferencesManager._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    @staticmethod
    def get_default_preferences() -> Dict[str, Any]:
        """Get factory-default preferences"""
        return {
            "general": {
                "language": "ar",
                "currency": "EGP",
                "fiscal_year_start": "January",
                "theme": "Dark Professional",
                "company_name": "",
                "auto_save_interval": 5
            },
            "ai": {
                "provider": "OpenAI",
                "model": "GPT-4",
                "temperature": 0.7,
                "max_tokens": 4000,
                "local_ai_enabled": False,
                "ollama_url": "http://localhost:11434",
                "streaming_enabled": True
            },
            "connectors": {
                "sap_enabled": False,
                "oracle_enabled": False,
                "dynamics_enabled": False,
                "odoo_enabled": False,
                "zoho_enabled": False,
                "quickbooks_enabled": False,
                "xero_enabled": False,
                "sql_enabled": False
            },
            "security": {
                "mfa_enabled": False,
                "session_timeout": 30,
                "encryption_enabled": True,
                "audit_logging_enabled": True,
                "password_min_length": 12,
                "max_login_attempts": 5
            },
            "reporting": {
                "default_format": "PDF",
                "include_logo": True,
                "include_qr_code": True,
                "digital_signature": False,
                "page_orientation": "portrait",
                "font_size": "normal"
            },
            "notifications": {
                "email_alerts": False,
                "sound_enabled": True,
                "desktop_notifications": True
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get a preference value using dot notation (e.g. 'general.language')"""
        keys = key.split('.')
        value = self.preferences

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> bool:
        """Set a preference value using dot notation"""
        keys = key.split('.')
        config = self.preferences

        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
        self._dirty = True
        return self.save_preferences()

    def set_many(self, updates: Dict[str, Any]) -> bool:
        """Set multiple preferences at once from a flat dict of dot-notation keys"""
        for key, value in updates.items():
            keys = key.split('.')
            config = self.preferences
            for k in keys[:-1]:
                if k not in config or not isinstance(config[k], dict):
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
        return self.save_preferences()

    def reset_to_defaults(self) -> bool:
        """Reset all preferences to factory defaults"""
        self.preferences = self.get_default_preferences()
        self._dirty = True
        logger.info("Preferences reset to defaults")
        return self.save_preferences()

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    def __repr__(self) -> str:
        return f"<PreferencesManager path={self.config_path} dirty={self._dirty}>"

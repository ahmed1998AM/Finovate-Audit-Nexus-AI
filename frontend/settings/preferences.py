"""
Finovate Audit Nexus AI - Preferences Manager
Enterprise AI Financial Audit & Intelligence Platform
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

class PreferencesManager:
    """Manages application preferences and settings"""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path.home() / ".finovate" / "preferences.json"
        
        self.config_path = config_path
        self.preferences: Dict[str, Any] = {}
        self.load_preferences()
    
    def load_preferences(self) -> None:
        """Load preferences from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.preferences = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading preferences: {e}")
                self.preferences = self.get_default_preferences()
        else:
            self.preferences = self.get_default_preferences()
            self.save_preferences()
    
    def save_preferences(self) -> bool:
        """Save preferences to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving preferences: {e}")
            return False
    
    def get_default_preferences(self) -> Dict[str, Any]:
        """Get default preferences"""
        return {
            "general": {
                "language": "en",
                "currency": "USD",
                "fiscal_year_start": "January",
                "theme": "Dark Professional"
            },
            "ai": {
                "provider": "OpenAI",
                "model": "GPT-4",
                "temperature": 0.7,
                "max_tokens": 2000,
                "local_ai_enabled": False,
                "ollama_url": "http://localhost:11434"
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
                "audit_logging_enabled": True
            },
            "reporting": {
                "default_format": "PDF",
                "include_logo": True,
                "include_qr_code": True,
                "digital_signature": False
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a preference value"""
        keys = key.split('.')
        value = self.preferences
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Set a preference value"""
        keys = key.split('.')
        config = self.preferences
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        return self.save_preferences()
    
    def reset_to_defaults(self) -> bool:
        """Reset all preferences to defaults"""
        self.preferences = self.get_default_preferences()
        return self.save_preferences()

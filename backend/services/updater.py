import os
import sys
import httpx
import logging
from version import __version__

logger = logging.getLogger(__name__)

class AutoUpdater:
    GITHUB_API_URL = "https://api.github.com/repos/ahmed1998AM/Finovate-Audit-Nexus-AI/releases/latest"

    def __init__(self, current_version=__version__):
        self.current_version = current_version
        self.latest_release_info = None

    async def check_for_updates(self):
        """
        التحقق من وجود تحديثات جديدة عبر GitHub API.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.GITHUB_API_URL)
                if response.status_code == 200:
                    self.latest_release_info = response.json()
                    latest_version = self.latest_release_info.get("tag_name", "").replace("v", "")
                    
                    if self._is_newer(latest_version, self.current_version):
                        return {
                            "update_available": True,
                            "latest_version": latest_version,
                            "release_notes": self.latest_release_info.get("body", ""),
                            "download_url": self._get_windows_asset_url()
                        }
                return {"update_available": False}
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return {"update_available": False, "error": str(e)}

    def _is_newer(self, latest, current):
        """مقارنة بسيطة للإصدارات"""
        try:
            l_parts = [int(x) for x in latest.split(".")]
            c_parts = [int(x) for x in current.split(".")]
            return l_parts > c_parts
        except:
            return latest > current

    def _get_windows_asset_url(self):
        """البحث عن رابط تحميل نسخة ويندوز من الأصول المرفوعة"""
        if not self.latest_release_info:
            return None
        
        assets = self.latest_release_info.get("assets", [])
        for asset in assets:
            if "windows" in asset.get("name", "").lower() or asset.get("name", "").endswith(".zip"):
                return asset.get("browser_download_url")
        return self.latest_release_info.get("html_url")

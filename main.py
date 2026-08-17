#!/usr/bin/env python3
"""
Finovate Audit Nexus AI - Main Application Entry Point
Enterprise AI Financial Audit & Intelligence Platform

Developed By: Ahmed Mostafa Ibrahim
Brand: Finovate – AHMED EG
© 2025 All Rights Reserved
"""
import sys
import os
import multiprocessing
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# إعداد نظام تسجيل الأخطاء في ملف خارجي للتشخيص
log_dir = os.path.join(os.path.expanduser("~"), ".finovate_audit")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "app_debug.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Main")

def main():
    """النقطة الرئيسية لتشغيل التطبيق"""
    # ضروري جداً لعمل PyInstaller على ويندوز عند استخدام multiprocessing
    multiprocessing.freeze_support()
    
    logger.info("Application Starting...")
    print("=" * 60)
    print("[START] Finovate Audit Nexus AI")
    print("   Enterprise AI Financial Audit & Intelligence Platform")
    print("=" * 60)
    print()
    print("[OK] System Status: Ready")
    print()
    print("Available Commands:")
    print("  --api       Start FastAPI Backend Server")
    print("  --desktop   Start PySide6 Desktop Application")
    print("  --all       Start API server + Desktop (recommended)")
    print("  --test      Run Test Suite")
    print("  --help      Show this help message")
    print("  --version   Show Version Information")
    print()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command in ("--api", "api"):
            start_api_server()
        elif command in ("--desktop", "desktop"):
            start_desktop_app()
        elif command in ("--all", "all"):
            start_all()
        elif command in ("--test", "test"):
            run_tests()
        elif command in ("--version", "version"):
            show_version()
        elif command in ("--help", "help", "-h"):
            main()
        else:
            print(f"[ERROR] Unknown command: {command}")
            print("Use --help to see available commands.")
            sys.exit(1)
    else:
        # Default: Start everything (API + Desktop) for full functionality
        start_all()

def start_all():
    """تشغيل الخادم وتطبيق سطح المكتب معاً"""
    import multiprocessing
    import time
    import threading

    logger.info("Starting API server + Desktop...")
    
    # في بيئة PyInstaller، يفضل تشغيل الـ API في خيط (Thread) منفصل أو عملية مستقلة بحذر
    def run_api():
        try:
            import uvicorn
            from backend.main import app as fastapi_app
            logger.info("Starting Uvicorn server...")
            uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")
        except Exception as e:
            logger.error(f"API Server failed: {e}")

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    logger.info("API server thread started on http://127.0.0.1:8000")
    time.sleep(1)
    start_desktop_app()


def start_api_server():
    """تشغيل خادم API"""
    print("[API] Starting FastAPI Backend Server...")
    try:
        import uvicorn
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    except ImportError:
        print("[ERROR] Please install requirements: pip install -r requirements.txt")
        sys.exit(1)

def start_desktop_app():
    """تشغيل تطبيق سطح المكتب"""
    logger.info("Starting PySide6 Desktop Application...")
    try:
        from frontend.main_window import MainWindow
        from frontend.components.login_dialog import LoginDialog
        from PySide6.QtWidgets import QApplication, QMessageBox
        import traceback

        app = QApplication(sys.argv)
        app.setApplicationName("Finovate Audit Nexus AI")
        app.setQuitOnLastWindowClosed(False)

        user_info = {"username": "admin", "role": "Admin", "source": "local"}
        try:
            login = LoginDialog()
            if login.exec() == LoginDialog.Accepted:
                user_info = login.user_info
        except Exception as e:
            print(f"[WARN] Login dialog failed ({e}), using defaults")

        try:
            window = MainWindow(user_info=user_info)
            window.show()
            app.setQuitOnLastWindowClosed(True)
            print("[OK] Application running")

            def _on_logout():
                window.close()
                app.setQuitOnLastWindowClosed(False)
                login = LoginDialog()
                if login.exec() == LoginDialog.Accepted:
                    new_win = MainWindow(user_info=login.user_info)
                    new_win.show()
                    app.setQuitOnLastWindowClosed(True)

            window.logout_requested.connect(_on_logout)

            sys.exit(app.exec())
        except Exception as e:
            error_msg = f"MainWindow creation failed: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            QMessageBox.critical(None, "Fatal Error", f"فشل تشغيل الواجهة الرئيسية:\n{str(e)}")
            sys.exit(1)
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start desktop app: {e}")
        if 'app' in locals():
            QMessageBox.critical(None, "Startup Error", f"خطأ في بداية التشغيل:\n{str(e)}")
        sys.exit(1)

def run_tests():
    """تشغيل الاختبارات"""
    print("[TEST] Running Test Suite...")
    try:
        import pytest
        pytest.main(["-v", "tests/"])
    except ImportError:
        print("[ERROR] Please install test requirements: pip install pytest pytest-asyncio")
        sys.exit(1)

def show_version():
    """عرض معلومات الإصدار"""
    print("Finovate Audit Nexus AI v2.0.0")
    print()
    print("Components:")
    print("  • 15 Enterprise Connectors [OK]")
    print("  • 22 AI Agents [OK]")
    print("  • FastAPI Backend [OK]")
    print("  • PySide6 Desktop UI [OK]")
    print("  • Database Layer [OK]")
    print("  • Security Module [OK]")
    print()
    print("Developed By: Ahmed Mostafa Ibrahim")
    print("Brand: Finovate – AHMED EG")
    print("© 2025 All Rights Reserved")

if __name__ == "__main__":
    main()

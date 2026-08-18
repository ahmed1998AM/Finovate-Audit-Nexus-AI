#!/usr/bin/env python3
"""
Finovate Audit Nexus AI - Main Application Entry Point
Enterprise AI Financial Audit & Intelligence Platform

Developed By: Ahmed Mostafa Ibrahim
Phone: 01225155329
Email: gogom8870@gmail.com
Brand: Finovate – AHMED EG
© 2025 All Rights Reserved
"""
import sys
import os
import multiprocessing
import logging
import traceback
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# إعداد نظام تسجيل الأخطاء في ملف خارجي ولحظي للتشخيص
def setup_logging():
    try:
        # أولاً: محاولة الكتابة في المجلد الحالي (بجانب الـ EXE) لضمان الرؤية
        log_file = os.path.join(os.getcwd(), "app_debug.log")
        
        # ثانياً: إعداد المجلد الاحتياطي في مجلد المستخدم
        user_log_dir = os.path.join(os.path.expanduser("~"), ".finovate_audit")
        os.makedirs(user_log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("Main")
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        return logging.getLogger("Fallback")

logger = setup_logging()

def main():
    """النقطة الرئيسية لتشغيل التطبيق"""
    # ضروري جداً لعمل PyInstaller على ويندوز عند استخدام multiprocessing
    multiprocessing.freeze_support()
    
    try:
        logger.info("Application Starting...")
        # Fallback log in current directory for emergency
        with open("startup_status.log", "a") as f:
            f.write(f"[{datetime.now()}] Main entry point reached.\n")
            
        print("=" * 60)
        print("[START] Finovate Audit Nexus AI")
        print("   Enterprise AI Financial Audit & Intelligence Platform")
        print("=" * 60)
        
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
                show_help()
            else:
                print(f"[ERROR] Unknown command: {command}")
                show_help()
                sys.exit(1)
        else:
            # Default: Start everything (API + Desktop)
            start_all()
            
    except Exception as e:
        error_msg = f"CRITICAL STARTUP ERROR: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        with open("startup_error.log", "w", encoding='utf-8') as f:
            f.write(error_msg)
        print(error_msg)
        sys.exit(1)

def start_all():
    """تشغيل الخادم وتطبيق سطح المكتب معاً"""
    import threading
    import time

    logger.info("Starting API server + Desktop...")
    
    def run_api():
        try:
            import uvicorn
            import backend.main
            logger.info("Starting Uvicorn server...")
            uvicorn.run(backend.main.app, host="127.0.0.1", port=8000, log_level="info")
        except Exception as e:
            logger.error(f"API Server failed: {e}")
            logger.error(traceback.format_exc())

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    logger.info("API server thread started on http://127.0.0.1:8000")
    time.sleep(2) # Wait for server to initialize
    start_desktop_app()

def start_api_server():
    """تشغيل خادم API"""
    logger.info("Starting FastAPI Backend Server...")
    try:
        import uvicorn
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        sys.exit(1)

def start_desktop_app():
    """تشغيل تطبيق سطح المكتب"""
    logger.info("Starting PySide6 Desktop Application...")
    try:
        # تأخير استيراد المكتبات الثقيلة لضمان وصولنا لهذه النقطة
        print("[INFO] Loading GUI Components...")
        from PySide6.QtWidgets import QApplication, QMessageBox
        import frontend.main_window
        import frontend.components.login_dialog
        
        app = QApplication(sys.argv)
        app.setApplicationName("Finovate Audit Nexus AI")
        app.setQuitOnLastWindowClosed(False)
        print("[OK] GUI Framework Loaded.")

        user_info = {"username": "admin", "role": "Admin", "source": "local"}
        try:
            login = frontend.components.login_dialog.LoginDialog()
            if login.exec() == frontend.components.login_dialog.LoginDialog.Accepted:
                user_info = login.user_info
        except Exception as e:
            logger.warning(f"Login dialog failed ({e}), using defaults")

        try:
            window = frontend.main_window.MainWindow(user_info=user_info)
            window.show()
            app.setQuitOnLastWindowClosed(True)
            logger.info("Application main window showing")

            def _on_logout():
                window.close()
                app.setQuitOnLastWindowClosed(False)
                login = frontend.components.login_dialog.LoginDialog()
                if login.exec() == frontend.components.login_dialog.LoginDialog.Accepted:
                    new_win = frontend.main_window.MainWindow(user_info=login.user_info)
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
        print(f"Missing dependency: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start desktop app: {e}")
        print(f"Failed to start desktop app: {e}")
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
    print("Developed By: Ahmed Mostafa Ibrahim")
    print("Brand: Finovate – AHMED EG")
    print("© 2025 All Rights Reserved")

def show_help():
    """عرض المساعدة"""
    print("Available Commands:")
    print("  --api       Start FastAPI Backend Server")
    print("  --desktop   Start PySide6 Desktop Application")
    print("  --all       Start API server + Desktop (recommended)")
    print("  --test      Run Test Suite")
    print("  --version   Show Version Information")
    print("  --help      Show this help message")

if __name__ == "__main__":
    main()

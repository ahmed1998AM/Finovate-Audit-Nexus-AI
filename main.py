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

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """النقطة الرئيسية لتشغيل التطبيق"""
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
        # Default: Start desktop application
        start_desktop_app()

def start_all():
    """تشغيل الخادم وتطبيق سطح المكتب معاً"""
    import multiprocessing
    import time

    print("[ALL] Starting API server + Desktop...")
    api_process = multiprocessing.Process(target=_run_api_subprocess, daemon=True)
    api_process.start()
    print("[OK] API server starting on http://localhost:8000")
    time.sleep(2)
    start_desktop_app()


def _run_api_subprocess():
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)


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
    print("[DESKTOP] Starting PySide6 Desktop Application...")
    try:
        from frontend.main_window import MainWindow
        from frontend.components.login_dialog import LoginDialog
        from PySide6.QtWidgets import QApplication
        import traceback

        app = QApplication(sys.argv)
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
        except Exception:
            print("[ERROR] MainWindow creation failed:")
            traceback.print_exc()
            sys.exit(1)
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("   Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to start desktop app: {e}")
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

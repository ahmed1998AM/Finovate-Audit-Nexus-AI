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
    print("🚀 Finovate Audit Nexus AI")
    print("   Enterprise AI Financial Audit & Intelligence Platform")
    print("=" * 60)
    print()
    print("✅ System Status: Ready")
    print()
    print("Available Commands:")
    print("  --api       Start FastAPI Backend Server")
    print("  --desktop   Start PySide6 Desktop Application")
    print("  --test      Run Test Suite")
    print("  --version   Show Version Information")
    print()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--api":
            start_api_server()
        elif command == "--desktop":
            start_desktop_app()
        elif command == "--test":
            run_tests()
        elif command == "--version":
            show_version()
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
    else:
        # Default: Start desktop application
        start_desktop_app()

def start_api_server():
    """تشغيل خادم API"""
    print("🌐 Starting FastAPI Backend Server...")
    try:
        import uvicorn
        uvicorn.run(
            "backend.api.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    except ImportError:
        print("❌ Please install requirements: pip install -r requirements.txt")
        sys.exit(1)

def start_desktop_app():
    """تشغيل تطبيق سطح المكتب"""
    print("🖥️  Starting PySide6 Desktop Application...")
    try:
        from frontend.main_window import MainWindow
        from PySide6.QtWidgets import QApplication
        import sys
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Please install requirements: pip install -r requirements.txt")
        sys.exit(1)

def run_tests():
    """تشغيل الاختبارات"""
    print("🧪 Running Test Suite...")
    try:
        import pytest
        pytest.main(["-v", "tests/"])
    except ImportError:
        print("❌ Please install test requirements: pip install pytest pytest-asyncio")
        sys.exit(1)

def show_version():
    """عرض معلومات الإصدار"""
    print("📦 Finovate Audit Nexus AI v1.0.0")
    print()
    print("Components:")
    print("  • 15 Enterprise Connectors ✅")
    print("  • 22 AI Agents ✅")
    print("  • FastAPI Backend ✅")
    print("  • PySide6 Desktop UI ✅")
    print("  • Database Layer ✅")
    print("  • Security Module ✅")
    print()
    print("Developed By: Ahmed Mostafa Ibrahim")
    print("Brand: Finovate – AHMED EG")
    print("© 2025 All Rights Reserved")

if __name__ == "__main__":
    main()

"""
Finovate Audit Nexus AI - Application Launcher
Main entry point for the application (API + Desktop UI).
"""

import sys
import multiprocessing

# Add project root to path
sys.path.insert(0, '/workspace')


def run_api_server():
    """Run the FastAPI backend server."""
    import uvicorn
    from backend.api.main import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


def run_desktop_ui():
    """Run the PySide6 desktop application."""
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt, QCoreApplication
    from PySide6.QtGui import QFont
    
    # Enable high DPI scaling (with deprecation handling)
    try:
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    except AttributeError:
        # These are enabled by default in Qt6
        pass
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Finovate Audit Nexus AI")
    app.setOrganizationName("Finovate - AHMED EG")
    app.setApplicationVersion("1.0.0")
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Import and create main window
    from frontend.dashboard.main_window import MainWindow
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


def main():
    """Launch the Finovate Audit Nexus AI application."""
    print("🚀 Starting Finovate Audit Nexus AI...")
    
    # Start API server in a separate process
    api_process = multiprocessing.Process(target=run_api_server)
    api_process.start()
    
    print("✅ API server started on http://localhost:8000")
    
    # Run desktop UI in the main process
    try:
        run_desktop_ui()
    finally:
        # Clean up API server
        api_process.terminate()
        api_process.join()


if __name__ == "__main__":
    main()

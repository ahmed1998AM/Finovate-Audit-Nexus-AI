"""
Finovate Audit Nexus AI - Desktop Application Launcher
Main entry point for the PySide6 desktop application.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QFont

# Add project root to path
sys.path.insert(0, '/workspace')

from frontend.dashboard.main_window import MainWindow


def main():
    """Launch the Finovate Audit Nexus AI desktop application."""
    
    # Enable high DPI scaling
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
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
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

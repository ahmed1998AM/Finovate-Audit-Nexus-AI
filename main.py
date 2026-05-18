"""
Finovate Audit Nexus AI - Main Application Entry Point

Enterprise AI Financial Audit & Intelligence Platform
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt
from loguru import logger

# Configure logging
logger.add("logs/app.log", rotation="10 MB", retention="30 days", level="DEBUG")


class MainWindow(QMainWindow):
    """Main application window for Finovate Audit Nexus AI"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Finovate Audit Nexus AI")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
        """)
        
        logger.info("Main window initialized")


def main():
    """Main entry point for the application"""
    logger.info("Starting Finovate Audit Nexus AI...")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    logger.info("Application started successfully")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

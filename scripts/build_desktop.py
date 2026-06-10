"""
Desktop Build Script - Packaging the application for Windows/macOS/Linux
سيناريو بناء تطبيق سطح المكتب - تغليف التطبيق لأنظمة التشغيل المختلفة
"""
import os
import subprocess
import sys

def build():
    print("🚀 Starting Finovate Audit Nexus AI Desktop Build...")
    
    # Check for PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Define the command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=FinovateAuditNexus",
        "--add-data=frontend/web_dashboard/audit_dashboard.html:frontend/web_dashboard",
        "--add-data=assets:assets",
        "--icon=assets/icon.ico" if os.path.exists("assets/icon.ico") else "",
        "main.py"
    ]
    
    # Filter out empty strings
    cmd = [c for c in cmd if c]
    
    print(f"🛠️ Executing: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("✅ Build Successful! Check the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build Failed: {e}")

if __name__ == "__main__":
    build()

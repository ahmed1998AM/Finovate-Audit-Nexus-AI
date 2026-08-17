"""
Desktop Build Script - Packaging the application for Windows/macOS/Linux
سيناريو بناء تطبيق سطح المكتب - تغليف التطبيق لأنظمة التشغيل المختلفة
"""
import os
import subprocess
import sys

def build():
    print("=" * 60)
    print("Finovate Audit Nexus AI - Desktop Build")
    print("=" * 60)
    
    # Ensure we are in project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Check for PyInstaller
    try:
        import PyInstaller
        print(f"[OK] PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("[INFO] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller installed")

    # Install dependencies first
    print("[INFO] Detecting OS and installing dependencies...")
    
    req_file = "requirements.txt"
    if sys.platform == "win32":
        req_file = "requirements-windows.txt"
    
    print(f"[INFO] Using {req_file} for {sys.platform}")
    
    try:
        print(f"[INFO] Installing all dependencies from {req_file}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        print("[OK] Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"[WARN] Dependency installation had some issues: {e}")

    # Verify critical dependencies before building
    print("[INFO] Verifying critical dependencies...")
    critical_pkgs = ["PySide6", "uvicorn", "fastapi", "sqlalchemy", "loguru", "pandas"]
    for pkg in critical_pkgs:
        try:
            __import__(pkg)
            print(f"[OK] Found {pkg}")
        except ImportError:
            print(f"[WARN] {pkg} not found, attempting direct install...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

    # Build using the optimized spec file (supports both onedir/onefile)
    # Use 'python -m PyInstaller' to ensure we use the correct environment
    spec_file = "finovate_audit.spec"
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", spec_file]
    
    print(f"[BUILD] {' '.join(cmd)}")
    print()
    
    try:
        subprocess.check_call(cmd)
        print()
        print("=" * 60)
        print("[SUCCESS] Build Complete!")
        print(f"[OUTPUT] dist/FinovateAudit/")
        print("=" * 60)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()

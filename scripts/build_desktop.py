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
    print(f"Python Version: {sys.version}")
    print(f"Platform: {sys.platform}")
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
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Try installing one by one if bulk fails
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        except:
            print("[WARN] Bulk install failed, trying individual installs...")
            with open(req_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            subprocess.check_call([sys.executable, "-m", "pip", "install", line, "--only-binary", ":all:"])
                        except:
                            try:
                                subprocess.check_call([sys.executable, "-m", "pip", "install", line])
                            except:
                                print(f"[ERROR] Failed to install {line}")
        print("[OK] Dependencies process finished")
    except Exception as e:
        print(f"[ERROR] Pip setup failed: {e}")

    # Verify critical dependencies before building
    print("[INFO] Verifying critical dependencies...")
    # We split packages into categories
    core_pkgs = ["PySide6", "uvicorn", "fastapi", "sqlalchemy", "loguru", "pandas"]
    auth_pkgs = ["jose", "passlib", "bcrypt"]
    ai_pkgs = ["openai", "anthropic"] # Reduced AI list for 3.9 compatibility

    def install_pkg(pkg, force_binary=True):
        try:
            # Map import name to pip name if different
            pip_name = pkg
            if pkg == "jose": pip_name = "python-jose[cryptography]"
            if pkg == "passlib": pip_name = "passlib[bcrypt]"
            
            print(f"[INFO] Checking {pkg}...")
            __import__(pkg.split('[')[0])
            print(f"[OK] {pkg} is ready")
        except Exception:
            print(f"[WARN] {pkg} missing, installing...")
            try:
                args = [sys.executable, "-m", "pip", "install", pip_name]
                if force_binary: args.append("--only-binary=:all:")
                subprocess.check_call(args)
                print(f"[OK] {pkg} installed")
            except:
                print(f"[ERROR] Failed to install {pkg}")

    print("[INFO] Installing Core Packages...")
    for p in core_pkgs: install_pkg(p)
    
    print("[INFO] Installing Auth Packages...")
    for p in auth_pkgs: install_pkg(p)
    
    print("[INFO] Installing AI Packages (Optional for build stability)...")
    for p in ai_pkgs: install_pkg(p, force_binary=False)

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

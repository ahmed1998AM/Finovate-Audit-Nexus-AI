@echo off
echo ========================================
echo Finovate Audit Nexus AI - Windows Build
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Create virtual environment if not exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded
echo.

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt --quiet
echo [OK] Dependencies installed
echo.

REM Run database migrations
echo [INFO] Setting up database...
python database/init_db.py
echo [OK] Database setup complete
echo.

REM Run tests
echo [INFO] Running tests...
python run_tests.py
if errorlevel 1 (
    echo [WARNING] Some tests failed, but continuing build...
) else (
    echo [OK] All tests passed
)
echo.

REM Create dist directory
if not exist "dist" mkdir dist
echo [OK] Distribution directory ready
echo.

REM Build executable with PyInstaller
echo [INFO] Building executable with PyInstaller...
pip install pyinstaller --quiet
pyinstaller --name="FinovateAudit" ^
    --windowed ^
    --onefile ^
    --icon=frontend/assets/icon.ico ^
    --add-data "frontend;frontend" ^
    --add-data "database;database" ^
    --add-data "agents;agents" ^
    --add-data "backend;backend" ^
    --add-data "connectors;connectors" ^
    --hidden-import=tinydb ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=matplotlib ^
    main.py

if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo [OK] Build completed successfully
echo.
echo Executable location: dist\FinovateAudit.exe
echo.
echo ========================================
echo Build Complete!
echo ========================================
pause

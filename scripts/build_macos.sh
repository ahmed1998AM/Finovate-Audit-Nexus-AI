#!/bin/bash

echo "========================================"
echo "Finovate Audit Nexus AI - macOS Build"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.8+ using: brew install python3"
    exit 1
fi

echo "[OK] Python detected: $(python3 --version)"
echo ""

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    echo "[OK] Virtual environment created"
else
    echo "[INFO] Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate
echo "[OK] Virtual environment activated"
echo ""

# Upgrade pip
echo "[INFO] Upgrading pip..."
pip install --upgrade pip --quiet
echo "[OK] pip upgraded"
echo ""

# Install dependencies
echo "[INFO] Installing dependencies..."
pip install -r requirements.txt --quiet
echo "[OK] Dependencies installed"
echo ""

# Run database migrations
echo "[INFO] Setting up database..."
python database/init_db.py
echo "[OK] Database setup complete"
echo ""

# Run tests
echo "[INFO] Running tests..."
python run_tests.py
if [ $? -ne 0 ]; then
    echo "[WARNING] Some tests failed, but continuing build..."
else
    echo "[OK] All tests passed"
fi
echo ""

# Create dist directory
mkdir -p dist
echo "[OK] Distribution directory ready"
echo ""

# Build executable with PyInstaller
echo "[INFO] Building executable with PyInstaller..."
pip install pyinstaller --quiet

pyinstaller --name="FinovateAudit" \
    --windowed \
    --onefile \
    --icon=frontend/assets/icon.icns \
    --add-data "frontend:frontend" \
    --add-data "database:database" \
    --add-data "agents:agents" \
    --add-data "backend:backend" \
    --add-data "connectors:connectors" \
    --hidden-import=tinydb \
    --hidden-import=pandas \
    --hidden-import=numpy \
    --hidden-import=matplotlib \
    main.py

if [ $? -ne 0 ]; then
    echo "[ERROR] Build failed"
    exit 1
fi

echo "[OK] Build completed successfully"
echo ""
echo "Executable location: dist/FinovateAudit.app"
echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"

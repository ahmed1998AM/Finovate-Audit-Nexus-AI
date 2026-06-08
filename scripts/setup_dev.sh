#!/bin/bash
# Setup script for Finovate Audit Nexus AI development environment

echo "🚀 Setting up development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "🆙 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env from .env.example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️ Please update the .env file with your actual API keys and configuration."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs data uploads exports reports

echo "✅ Setup complete! You can now run the application or tests."
echo "👉 Run tests: pytest tests/"
echo "👉 Run app: python main.py"

#!/bin/bash
# Script to setup development environment and run tests
# سيناريو إعداد بيئة التطوير وتشغيل الاختبارات

echo "🚀 Setting up Finovate Audit Nexus AI Development Environment..."

# 1. Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx sqlalchemy passlib[bcrypt] python-jose[cryptography] cryptography numpy pandas

# 2. Setup database
echo "🗄️ Initializing database..."
python3 -c "from database.db_manager import get_db_manager; get_db_manager().create_tables()"

# 3. Run unit tests
echo "🧪 Running unit tests..."
pytest tests/unit/

# 4. Start backend server (Mock)
echo "🌐 Starting backend server in development mode..."
# uvicorn backend.api.app:app --reload --port 8000 &

echo "✅ Setup complete!"

# Finovate Audit Nexus AI - Setup Guide

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14+ (optional, for production)
- Redis 6+ (for async tasks)
- Ollama (for local AI)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Finovate_Audit_Nexus_AI
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Add API keys, database credentials, etc.
```

### 5. Set Up Database

#### Option A: SQLite (Development)
```bash
# SQLite is configured by default
# No additional setup required
```

#### Option B: PostgreSQL (Production)
```sql
CREATE DATABASE finovate_audit_db;
CREATE USER finovate_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE finovate_audit_db TO finovate_user;
```

Update `.env` with PostgreSQL credentials.

### 6. Set Up Redis

```bash
# Install Redis
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
redis-server
```

### 7. Set Up Local AI (Optional)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama3
ollama pull mistral
```

### 8. Run the Application

#### Development Mode

```bash
# Run the main application
python main.py
```

#### With Backend API

```bash
# Start FastAPI backend
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker
celery -A backend.tasks.celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A backend.tasks.celery_app beat --loglevel=info
```

## Project Structure

```
Finovate_Audit_Nexus_AI/
├── backend/              # Backend API and business logic
│   ├── core/            # Core configuration and utilities
│   ├── ai_engine/       # AI processing engine
│   ├── orchestrator/    # Agent orchestration
│   ├── workflows/       # Workflow management
│   ├── memory/          # Memory & context management
│   ├── analytics/       # Analytics engine
│   ├── security/        # Security layer
│   └── compliance/      # Compliance engine
├── agents/              # 22 AI Agents
├── connectors/          # ERP & System Connectors
├── frontend/            # Desktop UI (PySide6)
├── uploads/             # Upload directory
├── exports/             # Export directory
├── reports/             # Generated reports
├── vector_store/        # Vector database storage
├── logs/                # System logs
├── database/            # Database files
└── docs/                # Documentation
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: Database connection string
- `REDIS_HOST`: Redis server host
- `OPENAI_API_KEY`: OpenAI API key
- `OLLAMA_HOST`: Local Ollama server URL
- `SECRET_KEY`: Application secret key

### AI Provider Configuration

The system supports multiple AI providers:

- **Cloud AI**: OpenAI, Anthropic, Google, DeepSeek, Mistral, xAI, Cohere
- **Local AI**: Ollama, LM Studio

Configure in `.env`:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_HOST=http://localhost:11434
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_fraud_agent.py
```

## Development

### Code Style

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8 .

# Type checking
mypy .
```

### Adding New Agents

1. Create agent directory in `agents/`
2. Implement agent class following existing patterns
3. Register agent in orchestrator
4. Add tests

## Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure PostgreSQL
- [ ] Set up Redis cluster
- [ ] Configure SSL/TLS
- [ ] Set up monitoring
- [ ] Configure backup strategy
- [ ] Review security settings
- [ ] Set appropriate log levels

### Docker Deployment (Coming Soon)

```bash
docker-compose up -d
```

## Troubleshooting

### Common Issues

**Database Connection Error**
```
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running
- Verify credentials
```

**Redis Connection Error**
```
- Check REDIS_HOST and REDIS_PORT
- Ensure Redis is running: redis-cli ping
```

**AI Provider Error**
```
- Verify API keys in .env
- Check API quota
- Test connectivity
```

## Support

For issues and questions:
- GitHub Issues: [Link]
- Email: gogom8870@gmail.com
- Phone: 01225155329

## License

© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved

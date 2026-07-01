# Finovate Audit Nexus AI - Dependency Structure

## Overview

This project now uses a modular dependency structure that allows users to install only the components they need. This significantly reduces the installation footprint and makes maintenance easier.

## Installation Options

### 1. Core Installation (Recommended for most users)

```bash
pip install finovate-audit-nexus-ai[core]
```

This installs the main FastAPI backend, database support, AI providers (OpenAI/Anthropic/Gemini/Groq), and basic ERP connectivity.

**What you get:**
- Main backend services
- 7 core ERP connectors (QuickBooks, Xero, Zoho, NetSuite, Odoo, Infor, Workday)
- Database (PostgreSQL/SQLite), Redis caching
- Auth, API endpoints, report generation

### 2. Desktop Application

```bash
pip install finovate-audit-nexus-ai[core,desktop]
```

Adds PySide6 for the desktop GUI application.

**What you get:** All core features + 11-page desktop application with navigation, charts, and native UI.

### 3. Machine Learning Support

```bash
pip install finovate-audit-nexus-ai[core,ml]
```

Adds TensorFlow, scikit-learn, and OpenCV for advanced ML capabilities.

**What you get:** All core features + ML-powered fraud detection, risk scoring, and pattern analysis.

### 4. SAP and Oracle ERP

```bash
pip install finovate-audit-nexus-ai[core,connector-sap,connector-oracle]
```

Adds specialized connectors for SAP (pyrfc) and Oracle (cx-Oracle/EBS).

**What you get:** All core features + SAP and Oracle ERP integration.

### 5. Development Package

```bash
pip install finovate-audit-nexus-ai[dev]
```

Complete development setup with testing tools, linting, and formatting.

**What you get:** Core + dev tools + testing.

### 6. All Components

```bash
pip install finovate-audit-nexus-ai[all]
```

Installs everything except the meta-package reference.

**What you get:** Full enterprise suite with all features.

## Traditional `pip install finovate-audit-nexus-ai`

For backwards compatibility, the main `dependencies` entry now points to `finovate-audit-nexus-ai[core]`, which installs the minimum required functionality.

## Dependency Groups Explained

| Group | Dependencies | Use Case |
|-------|-------------|----------|
| **core** | FastAPI, PostgreSQL, SQLAlchemy, OpenAI/Anthropic/Gemini, Redis, HTTPS auth | Production deployment |
| **ml** | TensorFlow, scikit-learn, OpenCV | Advanced ML analytics |
| **desktop** | PySide6 | Desktop GUI |
| **connector-sap** | pyrfc | SAP ERP connectivity |
| **connector-oracle** | cx-Oracle | Oracle/EBS connectivity |
| **connector-dynamics** | msal | Microsoft Dynamics 365 |
| **connector-netsuite** | requests_oauthlib | Oracle NetSuite |
| **connector-zoho** | requests | Zoho Books |
| **connector-quickbooks** | requests + requests_oauthlib | QuickBooks Online |
| **connector-xero** | requests + requests_oauthlib | Xero Accounting |
| **connector-odoo** | requests | Odoo |
| **connector-infor** | requests | Infor CloudSuite |
| **connector-workday** | requests + requests_oauthlib | Workday |
| **connector-ebs** | oracledb | Oracle E-Business Suite |
| **connector-sage** | requests | Sage ERP |
| **dev** | testing, linting, formatting | Development |
| **docs** | Sphinx documentation | Documentation generation |
| **retry** | retry | Reliability |

## Benefits

1. **Reduced Footprint**: Install only what you need
2. **Faster Installation**: Core is ~50MB vs 10GB with ML
3. **Better Security**: Limited attack surface
4. **Easier Updates**: Patch-specific groups
5. **Flexible Deployment**: Different environments can have different dependencies
6. **Backwards Compatible**: Existing installations continue to work

## Migration Guide

### Upgrading from older versions

If you have a previous version installed:

```bash
pip uninstall finovate-audit-nexus-ai
pip install finovate-audit-nexus-ai[core]  # or your specific group
```

### Changing dependency groups

To add a new dependency group:

```bash
pip install finovate-audit-nexus-ai[core,connector-sap]
```

To remove:

```bash
pip uninstall finovate-audit-nexus-ai
pip install finovate-audit-nexus-ai[core]
```

## Docker Usage

The Docker setup uses the same dependency structure:

```bash
# Core Docker image
docker build -t finovate/audit-nexus-ai:core .

# Desktop Docker image (includes UI)
docker build -t finovate/audit-nexus-ai:desktop -f Dockerfile .
```

Docker Compose uses the `core` group as the base.

## Environment Variables

The `.env` file should contain:

```ini
# Core database credentials
DATABASE_URL=sqlite:///./finovate_audit.db

# AI providers (at least one)
OPENAI_API_KEY=sk-...

# Security
JWT_SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
```

## Performance Impact

| Installation | Approximate Size | Dependencies |
|-------------|------------------|-------------|
| **core** | ~50MB | FastAPI, Postgres, 7 connectors |
| **all** | ~10GB | Includes ML (TensorFlow), Desktop (Qt), All connectors |

## Support

For installation issues, use:

1. `pip install finovate-audit-nexus-ai[core]` (for most users)
2. `pip install finovate-audit-nexus-ai[all]` (if you need everything)
3. Check the [GitHub Issues](https://github.com/finovate/audit-nexus-ai/issues) for known issues

The modular dependency structure makes installation and maintenance much easier while maintaining full functionality.

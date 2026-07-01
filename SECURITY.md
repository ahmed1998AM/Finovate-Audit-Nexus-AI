# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.0.0   | ✅ Current |
| < 2.0.0 | ❌ Unsupported |

## Reporting a Vulnerability

If you discover a security vulnerability in Finovate Audit Nexus AI, please report it responsibly.

### How to Report

**Email:** security@finovate-audit.com

**Please include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

### Response Time

- **Critical:** Within 24 hours
- **High:** Within 48 hours
- **Medium:** Within 72 hours
- **Low:** Within 1 week

### What to Expect

1. We will acknowledge receipt within 24 hours
2. We will provide a timeline for investigation
3. We will notify you when a fix is deployed
4. We will credit you in the release notes (if desired)

## Security Best Practices

### For Users

- Keep dependencies updated
- Use strong passwords
- Enable MFA when available
- Review audit logs regularly
- Use HTTPS in production
- Never commit `.env` files
- Rotate API keys periodically

### For Developers

- Follow OWASP guidelines
- Use parameterized queries
- Validate all inputs
- Implement rate limiting
- Enable audit logging
- Use environment variables for secrets
- Run security scans before commits

## Security Features

- **Authentication:** JWT + bcrypt password hashing
- **Authorization:** RBAC with 6 roles and 25 permissions
- **Encryption:** AES-256 for sensitive data
- **TLS/HTTPS:** Configurable for production
- **Rate Limiting:** 200 requests/minute per IP
- **Audit Trail:** Complete logging of user actions
- **Input Validation:** Pydantic models for all API inputs
- **SQL Injection Protection:** SQLAlchemy ORM with parameterized queries
- **CORS:** Configurable domain whitelist
- **Secrets Detection:** Pre-commit hooks with detect-secrets

## Dependency Security

We regularly scan dependencies for vulnerabilities using:
- `safety` - Security vulnerability scanner
- `bandit` - Python security linter
- `detect-secrets` - Secret detection in code

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For security-related questions:
- Email: security@finovate-audit.com
- GitHub: @finovate

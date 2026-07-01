# Finovate Audit Nexus AI — API Reference

Base URL: `http://localhost:8000`
Authentication: JWT Bearer Token

---

## Authentication

### POST `/api/v1/auth/login`
Login with username/password.

```json
// Request
{ "username": "admin", "password": "..." }
// Response
{ "access_token": "jwt...", "token_type": "bearer", "expires_in": 86400, "user_info": { "username": "admin", "role": "Admin" } }
```

### GET `/api/v1/auth/me`
Get current user info. Requires JWT.

### POST `/api/v1/auth/register`
Register new user.

### POST `/api/v1/auth/change-password`
Change password. Requires JWT.

### POST `/api/v1/auth/logout`
Logout. Requires JWT.

### POST `/api/v1/auth/refresh-token`
Refresh JWT token.

---

## Dashboard

### GET `/api/v1/audit/dashboard`
Main dashboard KPIs: riskScore, complianceScore, findingsCount, auditStatus.

### GET `/api/v1/audit/dashboard/summary-report`
Executive summary with overall assessment, critical issues, compliance rate.

### GET `/api/v1/audit/dashboard/recommendations`
Structured recommendations: immediate_actions, short_term, long_term.

---

## Audit Projects

### GET `/api/v1/audit-projects/`
List all projects. Optional query: `?status_filter=Completed`.

### POST `/api/v1/audit-projects/`
```json
{ "project_name": "...", "company_id": 1, "audit_type": "full", "scope": "..." }
```

### GET `/api/v1/audit-projects/{id}`
Single project details.

### GET `/api/v1/audit-projects/{id}/findings`
Project findings.

### GET `/api/v1/audit-projects/{id}/workpapers`
Project workpapers.

---

## Findings

### GET `/api/v1/findings/`
List all findings.

### PUT `/api/v1/findings/{id}`
Update finding.

### DELETE `/api/v1/findings/{id}`
Delete finding.

### PATCH `/api/v1/findings/{id}/status`
Update finding status.

---

## Reports

### GET `/api/v1/reports`
List reports. Optional: `?project_id=1`.

### POST `/api/v1/reports/create`
`?project_id=1&report_type=audit|executive`

### POST `/api/v1/reports/{id}/summary`
Generate executive summary for report.

### POST `/api/v1/reports/{id}/export`
Export report. `?format=pdf|html|json|xlsx`

---

## Agents

### GET `/api/v1/agents/`
List registered AI agents.

### POST `/api/v1/agents/execute`
```json
{ "agent_name": "fraud_agent", "data": { ... } }
```

### POST `/api/v1/agents/{agent_name}/start`
Start an agent.

### POST `/api/v1/agents/{agent_name}/stop`
Stop an agent.

---

## AI Providers

### GET `/api/v1/ai/providers`
List configured AI/LLM providers.

### GET `/api/v1/ai/status`
AI engine status: available providers, active provider.

### POST `/api/v1/ai/providers/{name}/test`
Test provider connection.

---

## Connectors

### GET `/api/v1/connectors`
List connectors.

### POST `/api/v1/connectors`
```json
{ "connector_name": "...", "connector_type": "sap|oracle|...", "company_id": 1, "config": {} }
```

### POST `/api/v1/connectors/{id}/test`
Test connection.

### POST `/api/v1/connectors/{id}/sync`
Sync data from connector.

### DELETE `/api/v1/connectors/{id}`
Remove connector.

---

## Documents

### POST `/api/v1/documents/upload`
Upload file (multipart/form-data).

### GET `/api/v1/documents`
List uploaded documents.

### POST `/api/v1/documents/{id}/ocr`
Process OCR on document.

---

## Audits

### POST `/api/v1/audits/start`
`?project_id=1&audit_type=full|fraud`

### GET `/api/v1/audits`
List audits.

### GET `/api/v1/audits/stats/summary`
Audit statistics.

---

## Predictives

### POST `/api/v1/predictive/revenue`
Predict revenue trends.

### POST `/api/v1/predictive/fraud-risk`
Predict fraud risk score.

### POST `/api/v1/predictive/cash-flow`
Predict cash flow.

---

## Health

### GET `/health`
Basic health check.

### GET `/api/health`
Full health check with database and AI status.

---

## WebSocket

### WS `/ws?token={jwt_token}&company_id={int}`
Real-time bidirectional connection.

**Query Parameters:**
- `token` (required): JWT token for authentication
- `company_id` (optional): Company scope for room-based broadcasting

**Protocol (JSON messages):**
```json
// Client -> Server
"ping"

// Server -> Client
{ "type": "pong" }
{ "type": "notification", "data": { ... } }
{ "type": "audit_update", "data": { ... } }
{ "type": "fraud_alert", "data": { ... } }
```

**Rooms:** Users are automatically joined to rooms: `all`, `user:{user_id}`, `company:{company_id}`, `admins` (for admin role).

---

## Webhooks

### POST `/api/v1/webhooks/register`
Register a new webhook subscription.

```json
{ "url": "https://example.com/webhook", "events": ["audit.completed", "fraud.detected"], "secret": "optional-secret", "retry_count": 3, "timeout": 30 }
```

### DELETE `/api/v1/webhooks/{subscription_id}`
Unregister a webhook subscription.

### GET `/api/v1/webhooks`
List all registered webhook subscriptions.

### GET `/api/v1/webhooks/delivery-log`
View webhook delivery history. `?limit=100`

---

## Tasks (Async Queue)

### GET `/api/v1/tasks`
List tasks. Optional: `?status=running|success|failed&limit=50`

### GET `/api/v1/tasks/{task_id}`
Get task status and info.

### GET `/api/v1/tasks/{task_id}/result`
Get task result (if completed).

### POST `/api/v1/tasks/{task_id}/cancel`
Cancel a pending/running task.

---

## Notifications

### POST `/api/v1/notifications/send`
Send notification via multiple channels.

```json
{ "channel": "email|inapp|slack|teams", "title": "...", "message": "...", "recipients": ["..."], "alert_type": "info|warning|critical" }
```

### POST `/api/v1/notifications/fraud-alert`
Send fraud alert notification. `?project_id=X&risk_level=high&description=...`

### POST `/api/v1/notifications/audit-reminder`
Send audit reminder.

### GET `/api/v1/notifications/history`
View notification history.

### GET `/api/v1/notifications/channels`
List available notification channels and their status.

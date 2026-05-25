# Kubernetes Deployment Guide for Finovate Audit Nexus AI

## Overview

This guide provides comprehensive instructions for deploying Finovate Audit Nexus AI on Kubernetes clusters for production environments.

## Prerequisites

- Kubernetes cluster (v1.25+)
- kubectl configured
- Helm v3.0+ (optional)
- Container registry access
- PostgreSQL database
- Redis cache
- SSL/TLS certificates

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   Ingress Controller                   │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌─────────────────────────▼─────────────────────────────┐  │
│  │              Load Balancer Service                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌────────────┬────────────┼────────────┬───────────────┐  │
│  │            │            │            │               │  │
│  ▼            ▼            ▼            ▼               ▼  │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐       │  │
│  │ API  │ │ API  │ │ Agent│ │ Agent│ │ Frontend │       │  │
│  │ Pod  │ │ Pod  │ │ Pod  │ │ Pod  │ │   Pod    │       │  │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────────┘       │  │
│  │            │            │            │               │  │
│  └────────────┴────────────┴────────────┴───────────────┘  │
│                            │                                 │
│  ┌─────────────────────────▼─────────────────────────────┐  │
│  │           StatefulSet (PostgreSQL + Redis)             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/finovate/audit-nexus-ai.git
cd audit-nexus-ai/kubernetes
```

### 2. Create Namespace

```bash
kubectl create namespace finovate-audit
```

### 3. Create Secrets

```bash
# Database credentials
kubectl create secret generic db-credentials \
  --from-literal=POSTGRES_USER=audit_user \
  --from-literal=POSTGRES_PASSWORD=$(openssl rand -base64 32) \
  --from-literal=POSTGRES_DB=finovate_audit \
  -n finovate-audit

# API keys
kubectl create secret generic api-keys \
  --from-literal=OPENAI_API_KEY=your-key \
  --from-literal=ENCRYPTION_KEY=$(openssl rand -hex 32) \
  -n finovate-audit

# TLS certificates
kubectl create secret tls tls-secret \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  -n finovate-audit
```

### 4. Deploy Infrastructure

```bash
# Deploy PostgreSQL
kubectl apply -f infrastructure/postgresql-statefulset.yaml

# Deploy Redis
kubectl apply -f infrastructure/redis-statefulset.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgresql -n finovate-audit --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n finovate-audit --timeout=300s
```

### 5. Deploy Application

```bash
# Deploy backend services
kubectl apply -f backend/api-deployment.yaml
kubectl apply -f backend/agent-deployment.yaml

# Deploy frontend
kubectl apply -f frontend/frontend-deployment.yaml

# Deploy services
kubectl apply -f services/
```

### 6. Deploy Ingress

```bash
kubectl apply -f ingress/ingress.yaml
```

### 7. Verify Deployment

```bash
kubectl get pods -n finovate-audit
kubectl get services -n finovate-audit
kubectl get ingress -n finovate-audit
```

## Configuration Files

### ConfigMap Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: finovate-config
  namespace: finovate-audit
data:
  DATABASE_URL: "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@postgresql:5432/$(POSTGRES_DB)"
  REDIS_URL: "redis://redis:6379/0"
  LOG_LEVEL: "INFO"
  MAX_WORKERS: "4"
  AGENT_TIMEOUT: "300"
```

### Deployment Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: finovate-api
  namespace: finovate-audit
spec:
  replicas: 3
  selector:
    matchLabels:
      app: finovate-api
  template:
    metadata:
      labels:
        app: finovate-api
    spec:
      containers:
      - name: api
        image: finovate/audit-nexus-ai:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: finovate-config
        - secretRef:
            name: db-credentials
        - secretRef:
            name: api-keys
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: finovate-api-hpa
  namespace: finovate-audit
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: finovate-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: finovate-network-policy
  namespace: finovate-audit
spec:
  podSelector:
    matchLabels:
      app: finovate-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: finovate-audit
    ports:
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
```

## Monitoring

### Prometheus Configuration

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: finovate-monitor
  namespace: finovate-audit
spec:
  selector:
    matchLabels:
      app: finovate-api
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### Grafana Dashboard

Import the provided dashboard JSON from `monitoring/grafana-dashboard.json`.

## Scaling

### Manual Scaling

```bash
# Scale API deployment
kubectl scale deployment finovate-api --replicas=5 -n finovate-audit

# Scale agent deployment
kubectl scale deployment finovate-agents --replicas=10 -n finovate-audit
```

### Auto-scaling

HPA is pre-configured. Monitor with:

```bash
kubectl get hpa -n finovate-audit
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
kubectl exec -it postgresql-0 -n finovate-audit -- \
  pg_dump -U audit_user finovate_audit > backup.sql

# Restore from backup
kubectl exec -i postgresql-0 -n finovate-audit -- \
  psql -U audit_user finovate_audit < backup.sql
```

### Disaster Recovery

1. Restore database from backup
2. Redeploy application
3. Verify data integrity
4. Update DNS if needed

## Security Best Practices

1. **Use Secrets**: Never hardcode credentials
2. **Network Policies**: Restrict pod-to-pod communication
3. **RBAC**: Implement role-based access control
4. **Pod Security**: Use security contexts
5. **TLS**: Encrypt all traffic
6. **Regular Updates**: Keep images and dependencies updated

### Pod Security Context

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
```

## Troubleshooting

### Common Issues

**Pods not starting:**
```bash
kubectl describe pod <pod-name> -n finovate-audit
kubectl logs <pod-name> -n finovate-audit
```

**Database connection issues:**
```bash
kubectl exec -it postgresql-0 -n finovate-audit -- psql -U audit_user
```

**High memory usage:**
```bash
kubectl top pods -n finovate-audit
```

### Debug Mode

Enable debug logging:
```bash
kubectl set env deployment/finovate-api LOG_LEVEL=DEBUG -n finovate-audit
```

## Helm Chart (Optional)

```bash
# Add repository
helm repo add finovate https://charts.finovate.com
helm repo update

# Install
helm install finovate-audit finovate/audit-nexus-ai \
  --namespace finovate-audit \
  --values values-production.yaml
```

## Production Checklist

- [ ] All secrets created
- [ ] Database backups configured
- [ ] Monitoring enabled
- [ ] HPA configured
- [ ] Network policies applied
- [ ] TLS certificates valid
- [ ] Resource limits set
- [ ] Logging configured
- [ ] Alert rules created
- [ ] DR plan tested

## Support

For issues and questions:
- GitHub Issues: https://github.com/finovate/audit-nexus-ai/issues
- Documentation: https://docs.finovate-audit.com
- Email: support@finovate-audit.com

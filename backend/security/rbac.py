"""
Finovate Audit Nexus AI - Role-Based Access Control
RBAC authorization for API endpoints and services
"""

import logging
from enum import Enum
from functools import wraps
from typing import Callable, Dict, List, Set

from fastapi import Depends, HTTPException, status

logger = logging.getLogger(__name__)


class Role(Enum):
    ADMIN = "admin"
    AUDITOR = "auditor"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Permission(Enum):
    # Audit permissions
    AUDIT_CREATE = "audit:create"
    AUDIT_READ = "audit:read"
    AUDIT_UPDATE = "audit:update"
    AUDIT_DELETE = "audit:delete"
    AUDIT_APPROVE = "audit:approve"

    # Connector permissions
    CONNECTOR_CREATE = "connector:create"
    CONNECTOR_READ = "connector:read"
    CONNECTOR_UPDATE = "connector:update"
    CONNECTOR_DELETE = "connector:delete"
    CONNECTOR_CONNECT = "connector:connect"
    CONNECTOR_SYNC = "connector:sync"

    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Report permissions
    REPORT_CREATE = "report:create"
    REPORT_READ = "report:read"
    REPORT_EXPORT = "report:export"
    REPORT_DELETE = "report:delete"

    # System permissions
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"
    SYSTEM_HEALTH = "system:health"

    # AI permissions
    AI_CONFIGURE = "ai:configure"
    AI_RUN = "ai:run"

    # Compliance
    COMPLIANCE_READ = "compliance:read"
    COMPLIANCE_OVERRIDE = "compliance:override"

    # Admin
    ADMIN_ACCESS = "admin:access"


ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.AUDIT_CREATE, Permission.AUDIT_READ, Permission.AUDIT_UPDATE,
        Permission.AUDIT_DELETE, Permission.AUDIT_APPROVE,
        Permission.CONNECTOR_CREATE, Permission.CONNECTOR_READ,
        Permission.CONNECTOR_UPDATE, Permission.CONNECTOR_DELETE,
        Permission.CONNECTOR_CONNECT, Permission.CONNECTOR_SYNC,
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.REPORT_CREATE, Permission.REPORT_READ, Permission.REPORT_EXPORT,
        Permission.REPORT_DELETE,
        Permission.SYSTEM_CONFIG, Permission.SYSTEM_LOGS, Permission.SYSTEM_HEALTH,
        Permission.AI_CONFIGURE, Permission.AI_RUN,
        Permission.COMPLIANCE_READ, Permission.COMPLIANCE_OVERRIDE,
        Permission.ADMIN_ACCESS,
    },
    Role.AUDITOR: {
        Permission.AUDIT_CREATE, Permission.AUDIT_READ, Permission.AUDIT_UPDATE,
        Permission.AUDIT_APPROVE,
        Permission.CONNECTOR_READ, Permission.CONNECTOR_CONNECT, Permission.CONNECTOR_SYNC,
        Permission.REPORT_CREATE, Permission.REPORT_READ, Permission.REPORT_EXPORT,
        Permission.AI_RUN,
        Permission.COMPLIANCE_READ, Permission.COMPLIANCE_OVERRIDE,
        Permission.SYSTEM_HEALTH,
    },
    Role.MANAGER: {
        Permission.AUDIT_CREATE, Permission.AUDIT_READ, Permission.AUDIT_UPDATE,
        Permission.CONNECTOR_READ, Permission.CONNECTOR_SYNC,
        Permission.REPORT_CREATE, Permission.REPORT_READ, Permission.REPORT_EXPORT,
        Permission.AI_RUN,
        Permission.COMPLIANCE_READ,
        Permission.SYSTEM_HEALTH,
    },
    Role.ANALYST: {
        Permission.AUDIT_READ,
        Permission.CONNECTOR_READ,
        Permission.REPORT_READ, Permission.REPORT_EXPORT,
        Permission.AI_RUN,
        Permission.COMPLIANCE_READ,
        Permission.SYSTEM_HEALTH,
    },
    Role.VIEWER: {
        Permission.AUDIT_READ,
        Permission.REPORT_READ,
        Permission.SYSTEM_HEALTH,
    },
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())


def get_role_permissions(role: Role) -> Set[Permission]:
    return ROLE_PERMISSIONS.get(role, set())


def require_permission(permission: Permission):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("current_user") or next(
                (v for k, v in kwargs.items() if "user" in k.lower()), None
            )
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            user_role = getattr(user, "role", None)
            if not user_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User has no role assigned"
                )
            try:
                role = Role(user_role.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Invalid role: {user_role}"
                )
            if not has_permission(role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def require_role(allowed_roles: List[Role]):
    async def dependency(current_user=None) -> bool:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        user_role = getattr(current_user, "role", None)
        if not user_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No role assigned")
        try:
            role = Role(user_role.lower())
        except ValueError:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid role: {user_role}")
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return True
    return Depends(dependency)

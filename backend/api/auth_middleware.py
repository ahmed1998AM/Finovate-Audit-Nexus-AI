"""
Finovate Audit Nexus AI - Auth Middleware
مصادقة موحدة لجميع نقاط API
"""
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.api.endpoints.auth import _get_jwt_secret
from backend.database import get_db
from backend.database.models import User as UserModel

security = HTTPBearer(auto_error=False)

async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    if credentials is None:
        return None
    try:
        payload = jwt.decode(credentials.credentials, _get_jwt_secret(), algorithms=["HS256"],
                             options={"verify_exp": True, "require": ["exp"]})
        username = payload.get("sub")
    except JWTError:
        return None
    user = db.query(UserModel).filter(
        UserModel.username == username, UserModel.is_active.is_(True)
    ).first()
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, _get_jwt_secret(), algorithms=["HS256"],
                             options={"verify_exp": True, "require": ["exp"]})
        username = payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(UserModel).filter(
        UserModel.username == username, UserModel.is_active.is_(True)
    ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

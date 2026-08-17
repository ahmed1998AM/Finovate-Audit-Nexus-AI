"""
Finovate Audit Nexus AI - Authentication API Endpoints
Professional User Authentication and Authorization
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.database.models import User as UserModel
from backend.security import hash_password, verify_password

security = HTTPBearer(auto_error=True)

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "Auditor"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: dict


_dev_jwt_secret: Optional[str] = None


def _get_jwt_secret() -> str:
    global _dev_jwt_secret
    key = os.getenv("JWT_SECRET_KEY")
    if key:
        return key
    if _dev_jwt_secret is None:
        import logging
        import secrets
        _dev_jwt_secret = secrets.token_hex(32)
        logging.warning("JWT_SECRET_KEY not set - using ephemeral development key.")
    return _dev_jwt_secret

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, _get_jwt_secret(), algorithm="HS256")

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(
        UserModel.username == login_data.username,
        UserModel.is_active.is_(True)
    ).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    user.last_login = datetime.utcnow()
    db.commit()
    access_token = create_access_token(data={"sub": login_data.username, "role": user.role})
    return TokenResponse(
        access_token=access_token,
        expires_in=86400,
        user_info={"username": login_data.username, "role": user.role, "must_change_password": user.must_change_password}
    )

@router.post("/register")
async def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(
        (UserModel.username == register_data.username) | (UserModel.email == register_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    db_user = UserModel(
        username=register_data.username, email=register_data.email,
        password_hash=hash_password(register_data.password), role=register_data.role,
        must_change_password=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {
        "success": True, "message": "User registered successfully",
        "user": {"username": db_user.username, "email": db_user.email, "role": db_user.role}
    }

@router.get("/me")
async def get_current_user_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
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
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "username": user.username, "email": user.email,
        "role": user.role, "is_active": user.is_active,
        "must_change_password": user.must_change_password
    }


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(credentials.credentials, _get_jwt_secret(), algorithms=["HS256"],
                             options={"verify_exp": True, "require": ["exp"]})
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(UserModel).filter(UserModel.username == username, UserModel.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(req.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    user.password_hash = hash_password(req.new_password)
    user.must_change_password = False
    db.commit()
    # حذف ملف .initial_passwords إذا كان موجودًا بعد تغيير كلمة المرور
    import os
    pw_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".initial_passwords")
    if os.path.exists(pw_file):
        os.remove(pw_file)
    return {"success": True, "message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(credentials.credentials, _get_jwt_secret(), algorithms=["HS256"],
                             options={"verify_exp": True, "require": ["exp"]})
        username = payload.get("sub")
        if username:
            user = db.query(UserModel).filter(UserModel.username == username).first()
            if user:
                user.last_login = None
                db.commit()
    except JWTError:
        pass
    return {"success": True, "message": "Logged out successfully"}

@router.post("/refresh-token")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(credentials.credentials, _get_jwt_secret(), algorithms=["HS256"],
                             options={"verify_exp": False, "require": ["exp"]})
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        user = db.query(UserModel).filter(
            UserModel.username == username, UserModel.is_active.is_(True)
        ).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        new_token = create_access_token(data={"sub": username, "role": payload.get("role", "Auditor")})
        return {"access_token": new_token, "token_type": "bearer", "expires_in": 86400}
    except jwt.ExpiredSignatureError:
        username = jwt.decode(credentials.credentials, _get_jwt_secret(), algorithms=["HS256"],
                              options={"verify_exp": False}).get("sub")
        if username:
            user = db.query(UserModel).filter(UserModel.username == username).first()
            if user and user.is_active:
                new_token = create_access_token(data={"sub": username, "role": user.role})
                return {"access_token": new_token, "token_type": "bearer", "expires_in": 86400}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cannot refresh expired token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

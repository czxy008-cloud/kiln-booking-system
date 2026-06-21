from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.config import settings
from app.utils.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_auth,
    hash_password,
    get_user_by_username,
    init_default_admin
)

router = APIRouter(prefix="/api/auth", tags=["认证"])

init_done = False


@router.on_event("startup")
def init_admin():
    global init_done
    if init_done:
        return
    db = next(get_db())
    try:
        init_default_admin(db)
        init_done = True
    finally:
        db.close()


@router.post("/login", response_model=schemas.Token)
def login(
    login_data: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.User.model_validate(user)
    }


@router.get("/me", response_model=schemas.User)
def get_me(current_user: models.User = Depends(require_auth)):
    return current_user


@router.post("/register", response_model=schemas.User, status_code=201)
def register(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user)
):
    existing = get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    if not current_user or current_user.role != "admin":
        if user_data.role == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权创建管理员账号"
            )

    user = models.User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

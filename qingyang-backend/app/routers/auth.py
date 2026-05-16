from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.crud.user import create_user, authenticate_user, get_user_by_email, get_user_by_username
from app.utils.security import create_access_token
from app.dependencies import get_db
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 检查邮箱是否已存在
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="该邮箱已被注册")
    # 检查用户名是否已存在
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=409, detail="该用户名已被使用")
    # 创建用户（内部会自动哈希密码）
    db_user = create_user(db, user)
    # 生成JWT令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    # 返回用户信息+token
    db_user_dict = {
        "id": db_user.id,
        "email": db_user.email,
        "username": db_user.username,
        "created_at": db_user.created_at
    }
    return {**db_user_dict, "access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
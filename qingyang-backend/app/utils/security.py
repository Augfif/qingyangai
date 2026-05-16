from datetime import datetime, timedelta
from typing import Any, Optional
from passlib.context import CryptContext
from jose import jwt

# 从settings读取配置（先按默认值写，后续和你的config对齐即可）
SECRET_KEY = "your-secret-key-here-please-change-in-production"  # 后续替换成你自己的密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 全局单例：密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """密码哈希"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否正确"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict[str, Any]:
    """解码JWT令牌（不处理异常，由调用方处理）"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
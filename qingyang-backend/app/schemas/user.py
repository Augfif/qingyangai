from datetime import datetime
from pydantic import BaseModel, field_validator, Field

# 用户创建请求模型
class UserCreate(BaseModel):
    email: str
    username: str = Field(..., min_length=2, max_length=50)
    password: str

    # 密码校验：长度至少6位
    @field_validator("password")
    def password_length_check(cls, v):
        if len(v) < 6:
            raise ValueError("密码长度不能少于6位")
        return v

    # 邮箱简单格式校验（替代 pydantic.EmailStr，避免额外依赖）
    @field_validator("email")
    def email_format_check(cls, v):
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("邮箱格式不正确")
        return v


# 用户登录请求模型
class UserLogin(BaseModel):
    email: str
    password: str


# 用户信息响应模型
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

    # 支持 ORM 模型自动转换
    model_config = {"from_attributes": True}


# Token 响应模型
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Token 数据模型（内部使用）
class TokenData(BaseModel):
    email: str | None = None
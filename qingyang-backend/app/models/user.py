from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")

    # 用户名（唯一）
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")

    # 邮箱（唯一）
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")

    # 加密后的密码
    hashed_password = Column(String(255), nullable=False, comment="加密密码")

    # 创建时间（自动生成）
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
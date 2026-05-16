from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite 必须加 connect_args 配置
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # 关键修复
    echo=False  # 可选：开启后会打印SQL日志，调试用
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
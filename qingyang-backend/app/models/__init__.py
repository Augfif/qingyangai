from app.db.base import Base
from app.db.session import engine

# 关键：导入User模型，让SQLAlchemy识别并创建表
from app.models.user import User

# 自动创建所有表（表不存在时才创建）
Base.metadata.create_all(bind=engine)
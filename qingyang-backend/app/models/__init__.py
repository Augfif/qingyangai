# 导入 User ORM 模型，确保它在 Base.metadata 中注册
# 建表由 main.py 的 startup 事件统一管理
from app.models.user import User
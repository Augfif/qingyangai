from pydantic import BaseModel, Field
from typing import Optional, List

class MealPlanRequest(BaseModel):
    # 把goal改成target，和路由、测试命令统一
    target: str
    # 把dietary_restrictions改成restrictions，并改成List类型
    restrictions: Optional[List[str]] = None
    calorie_target: Optional[int] = None
    # 把preferences改成List类型，支持传列表
    preferences: Optional[List[str]] = None

class MealItem(BaseModel):
    items: List[str]
    ingredients: Optional[str] = None
    calories: Optional[str] = None
    tips: Optional[str] = None

class MealPlanResponse(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    target: str
    breakfast: MealItem
    lunch: MealItem
    dinner: MealItem

    # 加上教程要求的ORM支持配置
    model_config = {"from_attributes": True}

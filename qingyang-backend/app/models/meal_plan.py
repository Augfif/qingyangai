from pydantic import BaseModel, Field
from typing import Optional, List


class MealPlanRequest(BaseModel):
    goal: str
    dietary_restrictions: Optional[str] = None
    calorie_target: Optional[int] = None
    preferences: Optional[str] = None


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

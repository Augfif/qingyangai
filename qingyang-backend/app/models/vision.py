from pydantic import BaseModel


class VisionResponse(BaseModel):
    food_name: str
    estimated_calories: str
    health_evaluation: str
    suggestions: str

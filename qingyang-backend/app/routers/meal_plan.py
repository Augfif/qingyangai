from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.schemas.meal_plan import MealPlanRequest, MealPlanResponse
from app.services.ai_client import AIService, AIServiceError
from app.services.meal_plan_parser import parse_meal_plan, MealPlanParseError
from app.dependencies import get_ai_service

router = APIRouter()

SYSTEM_PROMPT = (
    "你是'轻养AI'膳食规划专家。根据用户的目标、饮食限制和偏好，生成一个结构化的每日膳食计划。\n\n"
    "你必须严格以 JSON 格式输出，不包含 markdown 标记、代码栅栏或额外说明。"
    "只输出原始 JSON 对象，不输出其他内容。\n\n"
    "输出必须使用以下结构：\n"
    "{\n"
    '  "date": "YYYY-MM-DD（今天的日期）",\n'
    '  "target": "总体饮食目标的简要说明",\n'
    '  "breakfast": {\n'
    '    "items": ["食物1", "食物2", ...],\n'
    '    "ingredients": "食材和准备说明"\n'
    "  },\n"
    '  "lunch": {\n'
    '    "items": ["食物1", "食物2", ...],\n'
    '    "calories": "约 XXX 千卡"\n'
    "  },\n"
    '  "dinner": {\n'
    '    "items": ["食物1", "食物2", ...],\n'
    '    "tips": "用餐提示和注意事项"\n'
    "  }\n"
    "}\n\n"
    "items 必须是字符串数组。所有字符串值必须使用中文。"
)


def _build_user_message(req: MealPlanRequest) -> str:
    parts = [f"目标：{req.target}"]
    if req.dietary_restrictions:
        parts.append(f"饮食限制：{req.dietary_restrictions}")
    if req.calorie_target:
        parts.append(f"每日摄入目标：{req.calorie_target}千卡")
    if req.preferences:
        parts.append(f"偏好：{req.preferences}")
    return "，".join(parts)


@router.post("/api/tasks/meal-plan")
async def generate_meal_plan(
    req: MealPlanRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Generate a structured three-meal plan based on user parameters.
    AI output is forced to JSON via system prompt + `response_format`.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_message(req)},
    ]

    # Retry once on parse failure
    for attempt in range(2):
        try:
            raw = await ai_service.respond(
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
                response_format={"type": "json_object"},
            )
            meal_plan = parse_meal_plan(raw)
            # Ensure date is set to today if missing/invalid
            if not meal_plan.date:
                meal_plan.date = date.today().isoformat()
            return meal_plan
        except MealPlanParseError:
            if attempt == 1:
                return JSONResponse(
                    status_code=502,
                    content={"detail": "膳食计划生成失败，请稍后重试"},
                )
            continue
        except AIServiceError as e:
            return JSONResponse(
                status_code=502,
                content={"detail": e.message},
            )

    # Should not reach here
    return JSONResponse(
        status_code=502,
        content={"detail": "膳食计划生成失败，请稍后重试"},
    )

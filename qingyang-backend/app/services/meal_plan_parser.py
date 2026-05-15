import re
import json

from app.models.meal_plan import MealPlanResponse


class MealPlanParseError(Exception):
    """Raised when AI output cannot be parsed into a valid meal plan JSON."""

    def __init__(self, message: str = "膳食计划生成失败，请稍后重试"):
        self.message = message
        super().__init__(self.message)


class VisionParseError(Exception):
    """Raised when AI output cannot be parsed into a valid vision response JSON."""

    def __init__(self, message: str = "图片识别失败，请更换图片后重试"):
        self.message = message
        super().__init__(self.message)


def extract_json(text: str) -> dict:
    """
    Extract a JSON object from AI raw text output using 3-level fallback.

    1. Direct json.loads()
    2. Markdown code block (```json ... ```)
    3. First {...} brace pair
    """
    # Level 1: direct parse
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Level 2: markdown code block
    match = re.search(
        r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL
    )
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Level 3: first { ... } (with balanced braces)
    brace_start = text.find("{")
    if brace_start >= 0:
        depth = 0
        for i in range(brace_start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[brace_start : i + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        pass

    raise MealPlanParseError()


def parse_meal_plan(raw_text: str) -> MealPlanResponse:
    """Extract JSON from AI output and validate against MealPlanResponse."""
    data = extract_json(raw_text)
    return MealPlanResponse.model_validate(data)

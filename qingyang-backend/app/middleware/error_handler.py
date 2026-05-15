import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from openai import (
    APIError,
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
    APIConnectionError,
)

from app.services.ai_client import AIServiceError
from app.services.meal_plan_parser import MealPlanParseError, VisionParseError

logger = logging.getLogger("error_handler")


def register_handlers(app):
    """Register global exception handlers with friendly Chinese error messages."""

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError):
        logger.error(f"AI AuthenticationError: {exc}")
        return JSONResponse(
            status_code=502,
            content={"detail": "AI 服务认证失败，请联系管理员"},
        )

    @app.exception_handler(RateLimitError)
    async def rate_limit_handler(request: Request, exc: RateLimitError):
        logger.warning(f"AI RateLimitError: {exc}")
        return JSONResponse(
            status_code=429,
            content={"detail": "请求过于频繁，请稍后重试"},
        )

    @app.exception_handler(APITimeoutError)
    @app.exception_handler(APIConnectionError)
    async def timeout_handler(request: Request, exc: Exception):
        logger.error(f"AI Timeout/ConnectionError: {exc}")
        return JSONResponse(
            status_code=504,
            content={"detail": "AI 服务响应超时，请稍后重试"},
        )

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        logger.error(f"AI APIError: {exc}")
        return JSONResponse(
            status_code=502,
            content={"detail": "AI 服务暂时不可用，请稍后重试"},
        )

    @app.exception_handler(AIServiceError)
    async def ai_service_error_handler(request: Request, exc: AIServiceError):
        logger.error(f"AIServiceError [{exc.request_id}]: {exc.message}")
        return JSONResponse(
            status_code=502,
            content={"detail": exc.message},
        )

    @app.exception_handler(MealPlanParseError)
    async def meal_plan_parse_error_handler(
        request: Request, exc: MealPlanParseError
    ):
        logger.error(f"MealPlanParseError: {exc.message}")
        return JSONResponse(
            status_code=502,
            content={"detail": exc.message},
        )

    @app.exception_handler(VisionParseError)
    async def vision_parse_error_handler(request: Request, exc: VisionParseError):
        logger.error(f"VisionParseError: {exc.message}")
        return JSONResponse(
            status_code=502,
            content={"detail": exc.message},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误，请稍后重试"},
        )

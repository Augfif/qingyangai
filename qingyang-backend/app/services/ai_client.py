import uuid
import logging
from typing import Optional, List, Dict, AsyncGenerator

from openai import AsyncOpenAI
from openai import (
    APIError,
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
    APIConnectionError,
)

from app.config import settings

logger = logging.getLogger("ai_client")


class AIServiceError(Exception):
    """Custom exception for AI service failures with user-facing Chinese message."""

    def __init__(self, message: str, request_id: str):
        self.message = message
        self.request_id = request_id
        super().__init__(self.message)


class AIService:
    """AsyncOpenAI wrapper for all AI API calls."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL,
            default_headers={"Content-Type": "application/json; charset=utf-8"},
        )

    def _make_request_id(self) -> str:
        return str(uuid.uuid4())

    def _log_usage(
        self,
        request_id: str,
        endpoint: str,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
    ):
        logger.info(
            "token_usage",
            extra={
                "event": "token_usage",
                "request_id": request_id,
                "endpoint": endpoint,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
        )

    async def respond(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: Optional[Dict] = None,
    ) -> str:
        """Send a non-streaming chat completion request."""
        request_id = self._make_request_id()
        kwargs = dict(
            model=settings.AI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_query={"request_id": request_id},
        )
        if response_format:
            try:
                kwargs["response_format"] = response_format
                response = await self.client.chat.completions.create(**kwargs)
                if getattr(response, "choices", None):
                    content = response.choices[0].message.content or ""
                    return content
            except Exception:
                pass
            del kwargs["response_format"]

        try:
            response = await self.client.chat.completions.create(**kwargs)
            # 1. 安全校验：如果 choices 不存在或为空
            if not getattr(response, "choices", None):
                # 将完整的异常响应打印到控制台，以便我们排查
                error_msg = f"Vivo AI 接口异常: {response}"
                print("\n" + "=" * 50)
                print(error_msg)
                print("=" * 50 + "\n")
                raise AIServiceError(
                    message='AI 服务返回异常，请稍后重试',
                    request_id=request_id,
                )

            # 2. 正常获取内容
            content = response.choices[0].message.content or ""
            return content






            if not getattr(response, "choices", None):
                # 将完整的异常响应打印到控制台，以便我们排查
                error_msg = f"Vivo AI 接口异常: {response}"
                print("\n" + "="*50)
                print(error_msg)
                print("="*50 + "\n")
                # 直接抛出包含真实原因的异常，前端会显示这个中文信息
                raise ValueError(error_msg)

            return content

        except AuthenticationError as e:
            raise AIServiceError(
                message="AI 服务认证失败，请联系管理员",
                request_id=request_id,
            ) from e
        except RateLimitError as e:
            raise AIServiceError(
                message="请求过于频繁，请稍后重试",
                request_id=request_id,
            ) from e
        except (APITimeoutError, APIConnectionError) as e:
            raise AIServiceError(
                message="AI 服务响应超时，请稍后重试",
                request_id=request_id,
            ) from e
        except APIError as e:
            raise AIServiceError(
                message="AI 服务暂时不可用，请稍后重试",
                request_id=request_id,
            ) from e

    async def respond_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """Send a streaming chat completion request, yielding content chunks."""
        request_id = self._make_request_id()

        try:
            stream = await self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                stream_options={"include_usage": True},
                extra_query={"request_id": request_id},
            )

            async for chunk in stream:
                # The final chunk may carry usage stats
                if hasattr(chunk, "usage") and chunk.usage:
                    self._log_usage(
                        request_id=request_id,
                        endpoint="respond_stream",
                        prompt_tokens=chunk.usage.prompt_tokens,
                        completion_tokens=chunk.usage.completion_tokens,
                        total_tokens=chunk.usage.total_tokens,
                    )
                    continue

                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

        except AuthenticationError as e:
            raise AIServiceError(
                message="AI 服务认证失败，请联系管理员",
                request_id=request_id,
            ) from e
        except RateLimitError as e:
            raise AIServiceError(
                message="请求过于频繁，请稍后重试",
                request_id=request_id,
            ) from e
        except (APITimeoutError, APIConnectionError) as e:
            raise AIServiceError(
                message="AI 服务响应超时，请稍后重试",
                request_id=request_id,
            ) from e
        except APIError as e:
            raise AIServiceError(
                message="AI 服务暂时不可用，请稍后重试",
                request_id=request_id,
            ) from e

import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openai import APIError

from app.models.chat import ChatRequest, ChatResponse
from app.services.ai_client import AIService, AIServiceError
from app.dependencies import get_ai_service

router = APIRouter()

SYSTEM_PROMPT = (
    "你是'轻养AI'智能膳食助手，一个专业、亲切的营养健康顾问。"
    "你擅长回答关于饮食营养、健康管理、膳食搭配等方面的问题。"
    "请用中文回答，语言简洁清晰，适当给出具体建议。"
    "如果用户提到疾病相关的饮食需求，请建议其咨询专业医师。"
)


async def _stream_chat_generator(
    messages: list,
    ai_service: AIService,
):
    """SSE generator: yields `data: {...}\n\n` chunks."""
    try:
        async for chunk in ai_service.respond_stream(
            messages=messages, temperature=0.7, max_tokens=2048
        ):
            yield f"data: {json.dumps({'reply': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    except AIServiceError as e:
        yield f"data: {json.dumps({'error': e.message}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"


@router.post("/api/chat")
async def chat(
    req: ChatRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Smart dialogue endpoint.
    - `stream: false` (default) → returns `{ "reply": "..." }`
    - `stream: true` → returns SSE stream `data: {"reply": "chunk"}\n\n`
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": req.message},
    ]

    if req.stream:
        return StreamingResponse(
            _stream_chat_generator(messages, ai_service),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # Non-streaming path
    try:
        reply = await ai_service.respond(
            messages=messages, temperature=0.7, max_tokens=2048
        )
    except AIServiceError as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=502,
            content={"detail": e.message},
        )

    return ChatResponse(reply=reply)

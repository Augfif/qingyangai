import json
import uuid
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from openai import APIError

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_client import AIService, AIServiceError
from app.dependencies import get_ai_service

router = APIRouter()

# 会话存储（开发用，生产换 Redis）
session_memory: Dict[str, List[Dict]] = {}

# 最大历史消息数（防止超tokens & 内存爆炸）
MAX_HISTORY_LENGTH = 20

SYSTEM_PROMPT = (
    "你是'轻养AI'智能膳食助手，专业、亲切的营养健康顾问。"
    "擅长饮食营养、健康管理、膳食搭配建议。"
    "中文回答，简洁清晰，给出具体可操作建议。"
    "疾病相关饮食请建议咨询专业医师。"
)


async def _stream_chat_generator(
    messages: list,
    ai_service: AIService,
    session_id: str,
):
    """流式生成器，并在结束后保存历史消息"""
    full_reply = ""
    try:
        async for chunk in ai_service.respond_stream(
            messages=messages, temperature=0.7, max_tokens=2048
        ):
            full_reply += chunk
            yield f"data: {json.dumps({'reply': chunk}, ensure_ascii=False)}\n\n"

        # 流式完成后 → 把完整回答写入历史（修复核心bug）
        if session_id in session_memory:
            session_memory[session_id].append({
                "role": "assistant",
                "content": full_reply
            })
            # 限制长度
            if len(session_memory[session_id]) > MAX_HISTORY_LENGTH:
                session_memory[session_id] = session_memory[session_id][-MAX_HISTORY_LENGTH:]

        yield "data: [DONE]\n\n"

    except AIServiceError as e:
        yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': '服务器异常'}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"


@router.post("/api/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    # 1. 会话ID
    sid = req.session_id or str(uuid.uuid4())

    # 2. 正确加载历史（修复逻辑bug）
    if sid not in session_memory:
        session_memory[sid] = req.history if req.history else []

    # 3. 限制历史长度
    if len(session_memory[sid]) > MAX_HISTORY_LENGTH:
        session_memory[sid] = session_memory[sid][-MAX_HISTORY_LENGTH:]

    # 4. 添加用户当前消息
    session_memory[sid].append({"role": "user", "content": req.message})

    # 5. 构造模型消息
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + session_memory[sid]

    # 6. 流式响应
    if req.stream:
        return StreamingResponse(
            _stream_chat_generator(messages, ai_service, sid),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # 7. 非流式响应
    try:
        reply = await ai_service.respond(
            messages=messages, temperature=0.7, max_tokens=2048
        )
    except AIServiceError as e:
        return JSONResponse(
            status_code=502,
            content={"detail": str(e)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="服务内部错误")

    # 8. 保存AI回复
    session_memory[sid].append({"role": "assistant", "content": reply})

    # 9. 返回
    return ChatResponse(reply=reply, session_id=sid)
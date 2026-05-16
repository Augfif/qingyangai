"""
WebSocket 语音识别端点 — 前端 WebSocket ↔ 后端透传 ↔ Vivo ASR
"""

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.speech_asr import VivoASRClient, ASRClientError

logger = logging.getLogger("speech_router")
router = APIRouter()


@router.websocket("/ws/speech")
async def speech_websocket(websocket: WebSocket):
    """前端 WebSocket → 透传 → Vivo ASR → 透传 → 前端"""
    await websocket.accept()
    logger.info("Speech WebSocket accepted")

    asr_client = VivoASRClient()

    try:
        # 1. 连接 Vivo ASR
        await asr_client.connect()
    except ASRClientError as e:
        logger.error("ASR connect failed: %s", e)
        await websocket.send_json({"error": str(e)})
        await websocket.close()
        return

    # 2. 并发执行：前端→ASR 转发 + ASR→前端 转发
    async def forward_audio_to_asr():
        """从前端 WebSocket 接收 PCM 音频帧，转发给 ASR"""
        try:
            while True:
                data = await websocket.receive()
                if "bytes" in data:
                    await asr_client.send_audio_chunk(data["bytes"])
                elif "text" in data:
                    text = data["text"]
                    if text == "--stop--":
                        # 前端通知录音结束
                        break
        except WebSocketDisconnect:
            logger.info("Frontend WebSocket disconnected")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.warning("forward_audio_to_asr error: %s", e)

    async def forward_result_to_frontend():
        """从 ASR 接收识别结果，转发给前端"""
        try:
            result = await asr_client.receive_result()
            if result:
                await websocket.send_json({"text": result, "success": True})
            else:
                await websocket.send_json({"text": "", "success": False, "error": "未识别到语音内容"})
        except Exception as e:
            logger.warning("forward_result_to_frontend error: %s", e)
            try:
                await websocket.send_json({"text": "", "success": False, "error": str(e)})
            except Exception:
                pass

    # 启动转发任务
    forward_task = asyncio.create_task(forward_audio_to_asr())

    try:
        # 等待音频转发完成（前端发送 --stop-- 或断开）
        await forward_task
    except Exception:
        pass

    # 3. 发送结束标记，等待 ASR 最终结果
    await asr_client.send_end()
    await forward_result_to_frontend()

    # 4. 清理
    await asr_client.close()
    try:
        await websocket.close()
    except Exception:
        pass

    logger.info("Speech WebSocket closed")

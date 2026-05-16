"""
Vivo ASR WebSocket 客户端 — 纯透传，不做音频格式转换。

协议：
1. 连接 ws://api-ai.vivo.com.cn/asr/v2?app_id=...&app_key=...&...
2. 发送 JSON started 帧（含 asr_info：pcm, 16kHz, 单声道）
3. 逐帧发送 PCM 二进制数据（每次 1280 bytes）
4. 接收 JSON 识别结果（action=result, type=asr, data.text）
5. 发送 --end-- 和 --close-- 标记结束
"""

import json
import uuid
import time
import logging
from typing import Optional
from urllib.parse import urlencode

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from app.config import settings

logger = logging.getLogger("speech_asr")

ASR_HOST = "api-ai.vivo.com.cn"
ASR_PATH = "/asr/v2"
SAMPLE_FRAMES = 1280  # 每次发送的 PCM 帧数


class ASRClientError(Exception):
    """语音识别客户端异常"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class VivoASRClient:
    """Vivo AI 语音识别 WebSocket 客户端。

    Usage:
        client = VivoASRClient()
        await client.connect()
        await client.send_audio_chunk(pcm_bytes)
        async for text in client.receive_results():
            if text:
                print(f"识别结果: {text}")
        await client.close()
    """

    def __init__(self):
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._request_id = str(uuid.uuid4())
        self._is_closed = False
        self._result_text = ""

    # ---------- 连接 ----------

    def _build_url(self) -> str:
        """构造带鉴权参数的 WebSocket URL"""
        t = int(round(time.time() * 1000))
        params = {
            "app_id": settings.SPEECH_ASR_APP_ID,
            "app_key": settings.SPEECH_ASR_APP_KEY,
            "client_version": "qingyang-1.0",
            "product": "qingyang-ai",
            "package": "com.qingyang.app",
            "sdk_version": "1.0.0",
            "user_id": str(uuid.uuid4()),
            "android_version": "12",
            "system_time": str(t),
            "net_type": "1",
            "engineid": "shortasrinput",
            "requestId": self._request_id,
        }
        return f"ws://{ASR_HOST}{ASR_PATH}?{urlencode(params)}"

    async def connect(self) -> None:
        """建立到 Vivo ASR 的 WebSocket 连接并发送 started 帧"""
        url = self._build_url()
        logger.info("ASR connecting: %s", url[:120])

        try:
            self._ws = await websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=5,
                max_size=2 ** 20,
            )
        except (ConnectionError, WebSocketException, OSError) as e:
            raise ASRClientError(f"ASR 服务连接失败: {e}")

        # 发送 started 帧
        start_msg = {
            "type": "started",
            "request_id": self._request_id,
            "asr_info": {
                "front_vad_time": 6000,
                "end_vad_time": 2000,
                "audio_type": "pcm",
                "chinese2digital": 1,
                "punctuation": 2,
            },
            "business_info": json.dumps(
                {"scenes_pkg": "com.qingyang.app", "editor_type": "3"}
            ),
        }
        await self._ws.send(json.dumps(start_msg))
        logger.info("ASR started frame sent, request_id=%s", self._request_id)

    # ---------- 音频发送 ----------

    async def send_audio_chunk(self, chunk: bytes) -> None:
        """发送一帧 PCM 音频数据"""
        if self._is_closed or self._ws is None:
            return
        try:
            await self._ws.send(chunk)
        except ConnectionClosed:
            self._is_closed = True
        except WebSocketException as e:
            logger.warning("ASR send error: %s", e)
            self._is_closed = True

    # ---------- 结果接收 ----------

    async def receive_result(self) -> Optional[str]:
        """阻塞等待并返回最终识别文本（is_last=true 时），否则返回 None"""
        if self._ws is None:
            return None

        try:
            async for raw in self._ws:
                msg = json.loads(raw)
                action = msg.get("action", "")

                if action == "error":
                    logger.error("ASR error: %s", msg)
                    self._is_closed = True
                    return None

                if action == "result" and msg.get("type") == "asr":
                    data = msg.get("data", {})
                    text = data.get("text", "")
                    is_last = data.get("is_last", False)
                    if is_last:
                        self._result_text = text
                        return text if text else ""

            return None

        except ConnectionClosed:
            self._is_closed = True
            return self._result_text if self._result_text else None
        except (WebSocketException, json.JSONDecodeError) as e:
            logger.warning("ASR receive error: %s", e)
            self._is_closed = True
            return None

    # ---------- 发送结束标记 ----------

    async def send_end(self) -> None:
        """发送 --end-- 和 --close-- 标记"""
        if self._is_closed or self._ws is None:
            return
        try:
            await self._ws.send(b"--end--")
            await self._ws.send(b"--close--")
        except (ConnectionClosed, WebSocketException):
            pass

    # ---------- 关闭 ----------

    async def close(self) -> None:
        """关闭 WebSocket 连接"""
        self._is_closed = True
        if self._ws is not None:
            try:
                await self._ws.close()
            except (ConnectionClosed, WebSocketException):
                pass
            self._ws = None

from typing import Optional, List, Dict

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str = ""
    stream: bool = False
    messages: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    reply: str

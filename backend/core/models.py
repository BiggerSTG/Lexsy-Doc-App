from pydantic import BaseModel
from typing import List


class ChatMessage(BaseModel):
    role: str
    message: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage]


class GenerateRequest(BaseModel):
    conversation_history: List[ChatMessage]

"""
Pydantic Schemas for API requests/responses
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ========== Message Schemas ==========
class MessageBase(BaseModel):
    role: str
    content: str


class MessageCreate(MessageBase):
    conversation_id: int
    reasoning_content: Optional[str] = None
    model: Optional[str] = None
    thinking_enabled: bool = False


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    reasoning_content: Optional[str] = None
    model: Optional[str] = None
    thinking_enabled: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Conversation Schemas ==========
class ConversationBase(BaseModel):
    title: str = "新对话"


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None


class ConversationResponse(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse] = []


# ========== Chat Request/Response ==========
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    messages: List[ChatMessage]
    model: str = "deepseek-chat"
    thinking: bool = False


class UsageInfo(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    completion_tokens_details: Optional[dict] = None
    prompt_tokens_details: Optional[dict] = None


class ChatResponse(BaseModel):
    conversation_id: int
    answer: str
    reasoning: Optional[str] = None
    model: Optional[str] = None
    usage: Optional[UsageInfo] = None

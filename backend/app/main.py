from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .db import engine, get_db, Base
from .models import Conversation, Message
from .schemas import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationWithMessages,
    ChatRequest,
    ChatResponse,
    UsageInfo,
)
from .deepseek_client import chat_with_thinking, chat_with_thinking_stream

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7000", "http://127.0.0.1:7000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== Health Check ==========
@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    return {"status": "ok", "version": "0.2.0"}


# ========== Conversation APIs ==========
@app.get("/api/conversations", response_model=List[ConversationResponse])
async def list_conversations(db: Session = Depends(get_db)):
    """获取会话列表"""
    conversations = (
        db.query(Conversation)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return conversations


@app.post("/api/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
):
    """创建新会话"""
    db_conversation = Conversation(
        title=conversation.title,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


@app.get("/api/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    """获取单个会话详情（包含消息）"""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    # 转换为响应格式
    from sqlalchemy.orm import Session as SqlaSess
    conversation.messages = messages
    return conversation


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    """删除会话（物理删除，同时删除相关消息）"""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 删除相关消息（cascade 会自动处理）
    db.delete(conversation)
    db.commit()
    return {"message": "会话已删除"}


@app.put("/api/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    update_data: ConversationUpdate,
    db: Session = Depends(get_db),
):
    """更新会话标题"""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    if update_data.title is not None:
        conversation.title = update_data.title
    conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(conversation)
    return conversation


# ========== Chat API ==========
@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    聊天接口：
    - conversation_id: 可选，提供则添加到现有会话，否则创建新会话
    - thinking: 是否启用思考模式
    """
    # 获取或创建会话
    if payload.conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == payload.conversation_id)
            .first()
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")
    else:
        # 创建新会话，使用第一条消息作为标题
        first_msg = payload.messages[0].content if payload.messages else "新对话"
        title = first_msg[:30] + "..." if len(first_msg) > 30 else first_msg
        conversation = Conversation(
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 保存用户消息
    for msg in payload.messages:
        if msg.role == "user":
            db_message = Message(
                conversation_id=conversation.id,
                role=msg.role,
                content=msg.content,
                thinking_enabled=payload.thinking,
            )
            db.add(db_message)

    db.commit()

    # 调用 DeepSeek API
    messages_dict = [m.model_dump() for m in payload.messages]

    try:
        result = chat_with_thinking(
            messages_dict,
            model=payload.model,
            enable_thinking=payload.thinking,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DeepSeek 调用失败：{exc}") from exc

    # 保存 AI 回复
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=result.get("answer") or "",
        reasoning_content=result.get("reasoning"),
        model=result.get("model"),
        thinking_enabled=payload.thinking,
    )
    db.add(assistant_message)

    # 更新会话标题（如果是第一条消息）
    # 使用 count() 而不是 len() 因为 messages 是 lazy="dynamic"
    if conversation.messages.count() == 0:
        first_msg = payload.messages[0].content if payload.messages else "新对话"
        conversation.title = first_msg[:30] + "..." if len(first_msg) > 30 else first_msg
    conversation.updated_at = datetime.utcnow()

    db.commit()

    # 构建用量信息
    usage_dict = result.get("usage")
    usage_obj = None
    if isinstance(usage_dict, dict):
        usage_obj = UsageInfo(
            prompt_tokens=usage_dict.get("prompt_tokens", 0),
            completion_tokens=usage_dict.get("completion_tokens", 0),
            total_tokens=usage_dict.get("total_tokens", 0),
        )

    return ChatResponse(
        conversation_id=conversation.id,
        answer=result.get("answer") or "",
        reasoning=result.get("reasoning"),
        model=result.get("model"),
        usage=usage_obj,
    )


# ========== Streaming Chat API ==========
@app.post("/api/chat/stream")
async def chat_stream(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    流式聊天接口（SSE）：
    - conversation_id: 可选，提供则添加到现有会话，否则创建新会话
    - thinking: 是否启用思考模式
    """
    # 获取或创建会话
    if payload.conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == payload.conversation_id)
            .first()
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")
    else:
        # 创建新会话，使用第一条消息作为标题
        first_msg = payload.messages[0].content if payload.messages else "新对话"
        title = first_msg[:30] + "..." if len(first_msg) > 30 else first_msg
        conversation = Conversation(
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 保存用户消息
    for msg in payload.messages:
        if msg.role == "user":
            db_message = Message(
                conversation_id=conversation.id,
                role=msg.role,
                content=msg.content,
                thinking_enabled=payload.thinking,
            )
            db.add(db_message)

    db.commit()

    # 调用 DeepSeek API 流式接口
    messages_dict = [m.model_dump() for m in payload.messages]

    async def generate():
        reasoning_content = ""
        answer_content = ""
        model_name = ""
        usage = None

        # 使用同步生成器包装
        for chunk in chat_with_thinking_stream(
            messages_dict,
            model=payload.model,
            enable_thinking=payload.thinking,
        ):
            # 解析 chunk 数据用于累积
            try:
                import json as json_mod
                if chunk.startswith('data: '):
                    data = json_mod.loads(chunk[6:])
                    if data.get('type') == 'reasoning':
                        reasoning_content += data.get('content', '')
                    elif data.get('type') == 'answer':
                        answer_content += data.get('content', '')
                    elif data.get('type') == 'done':
                        model_name = data.get('model', '')
                        usage = data.get('usage')
            except:
                pass

            yield chunk

        # 流式输出结束后，保存 AI 回复到数据库
        if answer_content:
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=answer_content,
                reasoning_content=reasoning_content or None,
                model=model_name or payload.model,
                thinking_enabled=payload.thinking,
            )
            db.add(assistant_message)

            # 更新会话标题（如果是第一条消息）
            if conversation.messages.count() == 0:
                first_msg = payload.messages[0].content if payload.messages else "新对话"
                conversation.title = first_msg[:30] + "..." if len(first_msg) > 30 else first_msg
            conversation.updated_at = datetime.utcnow()

            db.commit()

    return StreamingResponse(generate(), media_type="text/event-stream")

"""
数据库模型定义
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .db import Base


class Conversation(Base):
    """会话表"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="新对话")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联消息
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}')>"


class Message(Base):
    """消息表"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    reasoning_content = Column(Text, nullable=True)  # 思考过程
    model = Column(String(100), nullable=True)  # 使用的模型
    thinking_enabled = Column(Boolean, default=False, nullable=False)  # 是否启用思考模式
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关联会话
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"

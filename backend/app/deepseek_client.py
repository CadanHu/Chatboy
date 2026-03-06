"""
DeepSeek 客户端封装

统一使用 deepseek-chat 模型，并通过 extra_body 开启思考 (thinking) 模式。
API Key 从环境变量 DEEPSEEK_API_KEY 读取，请在使用前设置。
"""

import os
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from dotenv import load_dotenv

# 加载 .env 文件（从当前脚本所在目录的父目录）
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

from openai import OpenAI


# 从环境变量读取 API Key，如果未设置则提示用户
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError(
        "请设置环境变量 DEEPSEEK_API_KEY。"
        "例如：export DEEPSEEK_API_KEY='your-api-key-here'"
        "或在 .env 文件中设置 DEEPSEEK_API_KEY=your-api-key-here"
    )

DEEPSEEK_BASE_URL = "https://api.deepseek.com"


class ChatMessageDict(TypedDict):
    role: str
    content: str


def _get_client() -> OpenAI:
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def chat_with_thinking(
    messages: List[ChatMessageDict],
    model: str = "deepseek-chat",
    enable_thinking: bool = True,
) -> Dict[str, Any]:
    """
    调用 DeepSeek 对话接口，返回提炼后的结构：

    - answer: 最终回答文本（message.content）
    - reasoning: 思考过程文本（message.reasoning_content）
    - model: 实际返回的模型名称
    - usage: token 用量信息
    - raw: 完整原始响应（用于调试/前端精细控制）
    
    Args:
        messages: 对话消息列表
        model: 模型名称，默认 deepseek-chat
        enable_thinking: 是否启用思考模式，默认 True
    """
    client = _get_client()
    
    # 构建请求参数
    create_kwargs = {
        "model": model,
        "messages": messages,
    }
    
    # 只在启用思考模式时添加 extra_body
    if enable_thinking:
        create_kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
    
    resp = client.chat.completions.create(**create_kwargs)
    data = resp.model_dump()

    choices = data.get("choices") or []
    answer = ""
    reasoning = None

    if choices:
        message = (choices[0] or {}).get("message") or {}
        answer = message.get("content") or ""
        reasoning = message.get("reasoning_content")

    return {
        "answer": answer,
        "reasoning": reasoning,
        "model": data.get("model"),
        "usage": data.get("usage"),
        "raw": data,
    }

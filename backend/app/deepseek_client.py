"""
DeepSeek 客户端封装

统一使用 deepseek-chat 模型，并通过 extra_body 开启思考(thinking)模式。
后续正式环境请将 API Key 改为从环境变量读取。
"""

from typing import Any, Dict, List, TypedDict

from openai import OpenAI


DEEPSEEK_API_KEY = "sk-cc710e55d7354d99971ac42ff57f7dd4"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"


class ChatMessageDict(TypedDict):
    role: str
    content: str


def _get_client() -> OpenAI:
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def chat_with_thinking(
    messages: List[ChatMessageDict],
    model: str = "deepseek-chat",
) -> Dict[str, Any]:
    """
    调用 DeepSeek 对话接口（开启思考模式），返回提炼后的结构：

    - answer: 最终回答文本（message.content）
    - reasoning: 思考过程文本（message.reasoning_content）
    - model: 实际返回的模型名称
    - usage: token 用量信息
    - raw: 完整原始响应（用于调试/前端精细控制）
    """
    client = _get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        extra_body={"thinking": {"type": "enabled"}},
    )
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


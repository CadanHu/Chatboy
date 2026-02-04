from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .deepseek_client import chat_with_thinking


app = FastAPI()


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    return {"status": "ok", "version": "0.1.0"}


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class DeepSeekChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "deepseek-chat"


class DeepSeekUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    completion_tokens_details: Optional[Dict[str, Any]] = None
    prompt_tokens_details: Optional[Dict[str, Any]] = None
    prompt_cache_hit_tokens: Optional[int] = None
    prompt_cache_miss_tokens: Optional[int] = None


class DeepSeekChatResponse(BaseModel):
    answer: str
    reasoning: Optional[str]
    model: Optional[str]
    usage: Optional[DeepSeekUsage]
    raw: Dict[str, Any]


@app.post("/api/chat/deepseek", response_model=DeepSeekChatResponse)
async def deepseek_chat(payload: DeepSeekChatRequest) -> DeepSeekChatResponse:
    """
    对话接口（非流式）：
    - 统一使用 deepseek-chat + thinking 模式
    - 返回：
      - answer: 最终回答（用于聊天气泡）
      - reasoning: 思考过程（用于“思考过程”面板）
      - usage: token 用量
      - raw: 完整原始响应（保留给前端/调试）
    """
    if not payload.messages:
        raise HTTPException(status_code=400, detail="messages 不能为空")

    # 将 Pydantic 模型转换为 dict 列表，以适配 deepseek_client
    messages_dict = [m.model_dump() for m in payload.messages]

    try:
        result = chat_with_thinking(messages_dict, model=payload.model)
    except Exception as exc:  # noqa: BLE001
        # 简单包装为 HTTP 错误，前端可展示 detail
        raise HTTPException(status_code=500, detail=f"DeepSeek 调用失败: {exc}") from exc

    usage_dict = result.get("usage")
    usage_obj: Optional[DeepSeekUsage] = None
    if isinstance(usage_dict, dict):
        # 只映射我们关心的字段，其余保留在 raw 中
        usage_obj = DeepSeekUsage(
            prompt_tokens=usage_dict.get("prompt_tokens", 0),
            completion_tokens=usage_dict.get("completion_tokens", 0),
            total_tokens=usage_dict.get("total_tokens", 0),
            completion_tokens_details=usage_dict.get("completion_tokens_details"),
            prompt_tokens_details=usage_dict.get("prompt_tokens_details"),
            prompt_cache_hit_tokens=usage_dict.get("prompt_cache_hit_tokens"),
            prompt_cache_miss_tokens=usage_dict.get("prompt_cache_miss_tokens"),
        )

    return DeepSeekChatResponse(
        answer=result.get("answer") or "",
        reasoning=result.get("reasoning"),
        model=result.get("model"),
        usage=usage_obj,
        raw=result.get("raw") or {},
    )

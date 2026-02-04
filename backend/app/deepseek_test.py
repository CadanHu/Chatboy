"""
DeepSeek 模型接口测试脚本（Phase 3 预备）

功能：
- 使用官方 OpenAI Python SDK 方式调用 DeepSeek 接口（base_url 指向 https://api.deepseek.com）
- 统一使用 deepseek-chat 模型，并通过 extra_body 开启思考模式（thinking）
- 演示：
  1）非流式调用：打印完整 JSON 响应结构
  2）流式调用：按 chunk 打印关键信息，并分别累积 reasoning_content 和 content

用法（在 backend 目录下）：
  1. 激活虚拟环境：
       source .venv/bin/activate
  2. 安装依赖：
       pip install openai
  3. 运行测试脚本：
       python -m app.deepseek_test

运行后请观察控制台输出和生成的 JSON 文件（可用于前端接口字段对接）。
"""

import json
from pathlib import Path

from openai import OpenAI


# 注意：此 API Key 仅用于当前测试阶段，正式环境请改为读取环境变量
DEEPSEEK_API_KEY = "sk-cc710e55d7354d99971ac42ff57f7dd4"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"


def create_client() -> OpenAI:
  """
  创建 DeepSeek 客户端（使用 OpenAI SDK 风格）。
  """
  client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
  return client


def test_non_stream_chat() -> None:
  """
  非流式调用 deepseek-chat + thinking，用于观察完整返回结构。
  """
  print("=== 非流式调用 deepseek-chat + thinking，开始 ===")
  client = create_client()

  messages = [
    {"role": "user", "content": "请用简短中文回答：9.11 和 9.8 哪个更大？"},
  ]

  response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    extra_body={"thinking": {"type": "enabled"}},
  )

  # OpenAI SDK v1 使用 .model_dump() 导出为 Python dict
  response_dict = response.model_dump()

  # 打印关键信息
  print("id:", response_dict.get("id"))
  print("model:", response_dict.get("model"))
  print("object:", response_dict.get("object"))
  print("created:", response_dict.get("created"))

  choices = response_dict.get("choices", [])
  if choices:
    choice0 = choices[0]
    message = choice0.get("message", {})
    content = message.get("content")
    reasoning_content = message.get("reasoning_content")
    finish_reason = choice0.get("finish_reason")

    print("--- choices[0] 关键信息 ---")
    print("finish_reason:", finish_reason)
    print("message.role:", message.get("role"))
    print("message.content:", content)
    print("message.reasoning_content:", reasoning_content)

  usage = response_dict.get("usage")
  print("--- usage ---")
  print(usage)

  # 将完整响应写入文件，便于前端/后续分析字段
  out_dir = Path(__file__).resolve().parent / "deepseek_logs"
  out_dir.mkdir(exist_ok=True)
  out_path = out_dir / "non_stream_chat_response.json"
  out_path.write_text(json.dumps(response_dict, ensure_ascii=False, indent=2), encoding="utf-8")
  print(f"完整 JSON 已写入: {out_path}")


def test_stream_chat() -> None:
  """
  流式调用 deepseek-chat + thinking：
  - 迭代 chunk，区分 reasoning_content 和 content
  - 将每个 chunk 的原始结构记录到文件
  """
  print("=== 流式调用 deepseek-chat + thinking，开始 ===")
  client = create_client()

  messages = [
    {"role": "user", "content": "9.11 和 9.8 哪个更大？请先推理再给出结论。"},
  ]

  response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stream=True,
    extra_body={"thinking": {"type": "enabled"}},
  )

  reasoning_content = ""
  content = ""
  chunks_export = []

  for idx, chunk in enumerate(response):
    # chunk 也是一个 Pydantic 模型对象
    chunk_dict = chunk.model_dump()
    chunks_export.append(chunk_dict)

    choices = chunk_dict.get("choices") or []
    if not choices:
      continue

    delta = choices[0].get("delta") or {}
    delta_reasoning = delta.get("reasoning_content") or ""
    delta_content = delta.get("content") or ""

    if delta_reasoning:
      reasoning_content += delta_reasoning
      print(f"[chunk {idx}] reasoning_delta: {delta_reasoning!r}")
    if delta_content:
      content += delta_content
      print(f"[chunk {idx}] content_delta: {delta_content!r}")

  print("=== 流式调用结束 ===")
  print("最终 reasoning_content：")
  print(reasoning_content)
  print("最终 content：")
  print(content)

  # 将所有流式 chunk 序列化到文件，便于分析字段结构
  out_dir = Path(__file__).resolve().parent / "deepseek_logs"
  out_dir.mkdir(exist_ok=True)
  out_path = out_dir / "stream_chat_chunks.json"
  out_path.write_text(json.dumps(chunks_export, ensure_ascii=False, indent=2), encoding="utf-8")
  print(f"所有流式 chunk JSON 已写入: {out_path}")


def main() -> None:
  """
  入口：依次执行非流式和流式两个测试。
  """
  test_non_stream_chat()
  print("\n" + "=" * 80 + "\n")
  test_stream_chat()


if __name__ == "__main__":
  main()


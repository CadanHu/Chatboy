# 类 ChatGPT 对话问答系统

基于 Python (FastAPI) + Vue 3 的类 ChatGPT 对话问答系统，集成 DeepSeek 模型，支持思考过程展示。

## 项目结构

```
.
├── backend/          # FastAPI 后端
│   └── app/
│       ├── main.py              # FastAPI 主应用
│       ├── deepseek_client.py   # DeepSeek 客户端封装
│       └── deepseek_test.py     # DeepSeek 接口测试脚本
├── frontend/         # Vue 3 前端
│   └── src/
│       └── components/
│           ├── ChatLayout.vue      # 主聊天界面组件
│           └── LayoutChatApp.js    # 状态管理
└── .gitignore
```

## 快速开始

### 1. 后端设置

```bash
cd backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install fastapi uvicorn openai

# 配置 API Key
# 方式1：设置环境变量
export DEEPSEEK_API_KEY='your-api-key-here'

# 方式2：创建 .env 文件（推荐）
cp .env.example .env
# 然后编辑 .env 文件，填入你的 DEEPSEEK_API_KEY

# 启动后端服务
uvicorn app.main:app --reload --port 7090
```

### 2. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npx vite
```

前端默认运行在 `http://localhost:7000`，会自动代理 `/api` 请求到后端 `http://localhost:7090`。

## 功能特性

- ✅ Phase 1: 项目初始化 + 健康检查接口
- ✅ Phase 2: 前端 UI 开发（聊天界面 + 思考过程面板）
- ✅ Phase 3: 后端接入 DeepSeek（非流式对话 + 思考模式）
- 🔄 Phase 4: 流式输出支持（计划中）

## API 接口

### 健康检查
```
GET /api/health
```

### DeepSeek 对话（非流式）
```
POST /api/chat/deepseek
Content-Type: application/json

{
  "messages": [
    { "role": "user", "content": "你的问题" }
  ],
  "model": "deepseek-chat"  // 可选，默认 deepseek-chat
}

响应：
{
  "answer": "AI 的回答",
  "reasoning": "思考过程内容",
  "model": "deepseek-reasoner",
  "usage": { ... },
  "raw": { ... }
}
```

## 注意事项

- **API Key 安全**：请勿将 API Key 提交到代码仓库。使用 `.env` 文件或环境变量管理。
- **环境变量**：后端启动前必须设置 `DEEPSEEK_API_KEY`，否则会抛出错误提示。
- **思考模式**：当前统一使用 `deepseek-chat` 模型 + `thinking` 参数开启思考模式。

## 开发计划

- [ ] Phase 4: 实现流式输出（SSE），支持打字机效果
- [ ] Phase 5: 会话持久化（数据库存储）
- [ ] Phase 6: 用户认证与权限管理
- [ ] Phase 7: RAG 知识库集成

## 技术栈

- **后端**: FastAPI, OpenAI SDK (for DeepSeek), Python 3.9+
- **前端**: Vue 3, Vite, Composition API

## License

MIT

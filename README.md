# 类 ChatGPT 对话问答系统

基于 Python (FastAPI) + Vue 3 的类 ChatGPT 对话问答系统，集成 DeepSeek 模型，支持思考过程展示、会话管理、数据持久化等功能。

## 项目结构

```
.
├── backend/          # FastAPI 后端
│   ├── .env.example          # 环境变量模板
│   ├── requirements.txt      # Python 依赖
│   └── app/
│       ├── main.py           # FastAPI 主应用 + API 路由
│       ├── db.py             # 数据库配置和会话管理
│       ├── models.py         # SQLAlchemy 数据模型
│       ├── schemas.py        # Pydantic 请求/响应模型
│       └── deepseek_client.py # DeepSeek 客户端封装
├── frontend/         # Vue 3 前端
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       └── components/
│           ├── ChatLayout.vue      # 主聊天界面组件
│           └── LayoutChatApp.js    # 状态管理
└── README.md
```

## 快速开始

### 1. 后端设置

```bash
cd backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 DEEPSEEK_API_KEY 和数据库配置

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

- ✅ **DeepSeek 模型集成**：支持 `deepseek-chat` 模型，可开启思考模式
- ✅ **思考过程展示**：可查看 AI 回答前的推理思考过程
- ✅ **会话管理**：创建、切换、删除会话
- ✅ **数据持久化**：使用 PostgreSQL 存储会话和消息，支持刷新后恢复
- ✅ **响应式 UI**：现代化聊天界面，支持桌面和移动端

## API 接口

### 健康检查
```
GET /api/health
```

### 会话管理
```
# 获取会话列表
GET /api/conversations

# 创建新会话
POST /api/conversations
Content-Type: application/json
{"title": "会话标题"}

# 获取会话详情（含消息）
GET /api/conversations/{id}

# 更新会话标题
PUT /api/conversations/{id}
Content-Type: application/json
{"title": "新标题"}

# 删除会话
DELETE /api/conversations/{id}
```

### 聊天接口
```
POST /api/chat
Content-Type: application/json

{
  "conversation_id": 1,        // 可选，提供则添加到现有会话，否则创建新会话
  "messages": [
    {"role": "user", "content": "你的问题"}
  ],
  "model": "deepseek-chat",    // 可选，默认 deepseek-chat
  "thinking": true             // 是否启用思考模式，默认 false
}

响应：
{
  "conversation_id": 1,
  "answer": "AI 的回答",
  "reasoning": "思考过程内容",  // 启用 thinking 时返回
  "model": "deepseek-chat",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

## 数据库配置

后端使用 PostgreSQL 存储数据，默认配置：
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatboy
```

启动后端前请确保：
1. PostgreSQL 服务已启动
2. 已创建 `chatboy` 数据库
3. `.env` 文件中配置了正确的数据库连接信息

## 注意事项

- **API Key 安全**：请勿将 API Key 提交到代码仓库。使用 `.env` 文件或环境变量管理。
- **环境变量**：后端启动前必须设置 `DEEPSEEK_API_KEY`，否则会抛出错误提示。
- **思考模式**：通过 `thinking` 参数控制是否启用思考模式，启用后会返回 `reasoning` 字段。

## 开发计划

- [ ] 流式输出（SSE），支持打字机效果
- [ ] 用户认证与权限管理
- [ ] RAG 知识库集成
- [ ] 对话导出功能
- [ ] 多模型支持切换

## 技术栈

- **后端**: FastAPI, SQLAlchemy, Pydantic, Python 3.9+
- **前端**: Vue 3, Vite, Composition API
- **数据库**: PostgreSQL

## License

MIT

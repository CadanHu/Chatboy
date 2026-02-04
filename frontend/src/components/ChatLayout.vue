<template>
  <div class="chat-app">
    <aside class="sidebar">
      <header class="sidebar-header">
        <h1 class="logo">DeepSeek Chat</h1>
        <p class="subtitle">Phase 2 · 前端 UI 演示</p>
      </header>
      <button class="new-chat-btn" type="button">
        ＋ 新建会话
      </button>
      <div class="conversation-list">
        <button
          v-for="c in chat.conversations"
          :key="c.id"
          class="conversation-item"
          :class="{ active: c.id === chat.activeConversationId }"
          type="button"
          @click="chat.switchConversation(c.id)"
        >
          <div class="conversation-title">
            {{ c.title }}
          </div>
          <div class="conversation-meta">
            {{ c.updatedAt }}
          </div>
        </button>
      </div>
    </aside>

    <main class="chat-main">
      <header class="chat-header">
        <div class="chat-header-left">
          <h2 class="chat-title">
            {{ activeConversation?.title || '未选择会话' }}
          </h2>
          <p class="chat-desc">
            已接入 DeepSeek deepseek-chat（非流式），支持思考模式。
          </p>
        </div>
        <div class="chat-header-right">
          <button
            class="reasoning-toggle"
            type="button"
            @click="chat.toggleReasoning"
          >
            {{ chat.state.reasoningVisible ? '隐藏思考过程' : '查看思考过程' }}
          </button>
        </div>
      </header>

      <section class="chat-body">
        <div class="messages" ref="messagesEl">
          <div
            v-for="m in activeMessages"
            :key="m.id"
            class="message-row"
            :class="m.role"
          >
            <div class="avatar">
              <span v-if="m.role === 'user'">我</span>
              <span v-else>AI</span>
            </div>
            <div class="bubble">
              <div class="bubble-content">
                {{ m.content }}
              </div>
              <div class="bubble-meta">
                {{ m.createdAt }}
              </div>
            </div>
          </div>
        </div>

        <section
          v-if="chat.state.reasoningVisible"
          class="reasoning-panel"
        >
          <header class="reasoning-header">
            <h3>DeepSeek 模型思考过程</h3>
            <p>当前展示的是接口返回的 reasoning_content。</p>
          </header>
          <pre class="reasoning-content">
{{ chat.state.reasoningContent }}
          </pre>
        </section>
      </section>

      <footer class="chat-input-area">
        <div v-if="chat.state.error" class="error-banner">
          {{ chat.state.error }}
        </div>
        <textarea
          v-model="chat.state.draft"
          class="chat-input"
          rows="3"
          :placeholder="chat.state.sending ? '正在向 DeepSeek 请求回答…' : '输入你的问题，按 Ctrl+Enter 发送'"
          @keydown.ctrl.enter.prevent="chat.sendMessage"
        ></textarea>
        <div class="chat-input-toolbar">
          <span class="tip">
            Ctrl+Enter 发送 · 当前调用的是后端 DeepSeek 接口（非流式）
          </span>
          <button
            class="send-btn"
            type="button"
            :disabled="chat.state.sending"
            @click="chat.sendMessage"
          >
            {{ chat.state.sending ? '发送中…' : '发送' }}
          </button>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useChatState } from './LayoutChatApp'

const chat = useChatState()
const { activeConversation, activeMessages } = chat

const messagesEl = ref(null)

function scrollToBottom() {
  const el = messagesEl.value
  if (!el) return
  requestAnimationFrame(() => {
    el.scrollTop = el.scrollHeight
  })
}

onMounted(scrollToBottom)

watch(
  () => activeMessages.value.length,
  () => {
    scrollToBottom()
  },
)
</script>

<style scoped>
.chat-app {
  display: flex;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui,
    -system-ui, sans-serif;
  background: #0f172a;
  color: #e5e7eb;
}

.sidebar {
  width: 260px;
  border-right: 1px solid #1f2937;
  background: radial-gradient(circle at top left, #1e293b, #020617);
  display: flex;
  flex-direction: column;
  padding: 16px;
  box-sizing: border-box;
}

.sidebar-header {
  margin-bottom: 16px;
}

.logo {
  font-size: 18px;
  font-weight: 700;
  color: #e5e7eb;
  margin: 0;
}

.subtitle {
  margin: 4px 0 0;
  font-size: 12px;
  color: #9ca3af;
}

.new-chat-btn {
  margin-bottom: 12px;
  border-radius: 999px;
  border: 1px solid #374151;
  background: #111827;
  color: #e5e7eb;
  padding: 8px 12px;
  font-size: 13px;
  cursor: pointer;
  text-align: left;
}

.new-chat-btn:hover {
  background: #1f2937;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  width: 100%;
  border: none;
  background: transparent;
  text-align: left;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 4px;
  color: #e5e7eb;
}

.conversation-item:hover {
  background: rgba(55, 65, 81, 0.75);
}

.conversation-item.active {
  background: linear-gradient(135deg, #2563eb, #4f46e5);
}

.conversation-title {
  font-size: 14px;
  font-weight: 500;
}

.conversation-meta {
  font-size: 12px;
  color: #9ca3af;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: radial-gradient(circle at top, #0f172a, #020617);
}

.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid #1f2937;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.chat-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.chat-desc {
  margin: 4px 0 0;
  font-size: 13px;
  color: #9ca3af;
}

.reasoning-toggle {
  border-radius: 999px;
  border: 1px solid #4b5563;
  background: #020617;
  color: #e5e7eb;
  padding: 6px 12px;
  font-size: 13px;
  cursor: pointer;
}

.reasoning-toggle:hover {
  border-color: #818cf8;
  color: #a5b4fc;
}

.chat-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages {
  flex: 1;
  padding: 16px 20px;
  overflow-y: auto;
}

.message-row {
  display: flex;
  margin-bottom: 12px;
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: #1f2937;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #e5e7eb;
  margin: 0 8px;
}

.bubble {
  max-width: min(640px, 80%);
  background: #020617;
  border-radius: 14px;
  padding: 10px 12px;
  border: 1px solid #1f2937;
}

.message-row.user .bubble {
  background: #1d4ed8;
  border-color: #2563eb;
}

.bubble-content {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.bubble-meta {
  margin-top: 4px;
  font-size: 11px;
  color: #9ca3af;
}

.reasoning-panel {
  border-top: 1px solid #1f2937;
  background: rgba(15, 23, 42, 0.96);
  padding: 12px 20px 16px;
  max-height: 220px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.reasoning-header h3 {
  margin: 0;
  font-size: 14px;
}

.reasoning-header p {
  margin: 4px 0 8px;
  font-size: 12px;
  color: #9ca3af;
}

.reasoning-content {
  flex: 1;
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  overflow-y: auto;
  background: transparent;
  color: #e5e7eb;
}

.chat-input-area {
  border-top: 1px solid #1f2937;
  padding: 10px 20px 16px;
  background: rgba(15, 23, 42, 0.98);
}

.error-banner {
  margin-bottom: 6px;
  padding: 6px 10px;
  border-radius: 8px;
  background: rgba(220, 38, 38, 0.1);
  color: #fecaca;
  font-size: 12px;
}

.chat-input {
  width: 100%;
  resize: none;
  border-radius: 12px;
  border: 1px solid #4b5563;
  background: #020617;
  color: #e5e7eb;
  padding: 8px 10px;
  font-size: 14px;
  box-sizing: border-box;
}

.chat-input:focus {
  outline: none;
  border-color: #6366f1;
}

.chat-input-toolbar {
  margin-top: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #9ca3af;
}

.send-btn {
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: white;
  padding: 6px 16px;
  cursor: pointer;
  font-size: 13px;
}

.send-btn:hover {
  filter: brightness(1.05);
}

@media (max-width: 768px) {
  .chat-app {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #1f2937;
    flex-direction: row;
    align-items: center;
    gap: 12px;
  }

  .conversation-list {
    display: none;
  }
}
</style>


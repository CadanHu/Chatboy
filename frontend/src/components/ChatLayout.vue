<template>
  <div class="chat-app" :style="{ '--sidebar-width': sidebarWidth + 'px' }">
    <aside class="sidebar">
      <header class="sidebar-header">
        <div class="logo-wrapper">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1 class="logo">DeepSeek Chat</h1>
        </div>
        <p class="subtitle">AI 智能对话助手</p>
      </header>
      
      <button class="new-chat-btn" type="button" @click="chat.createNewConversation">
        <svg class="plus-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        新建会话
      </button>

      <div class="conversation-list">
        <div class="conversation-section-title">最近对话</div>
        <div v-if="chat.state.conversations.length === 0" class="empty-conversations">
          暂无会话，点击"新建会话"开始
        </div>
        <div
          v-for="c in chat.state.conversations"
          :key="c.id"
          class="conversation-item-wrapper"
          :class="{ active: c.id === chat.state.activeConversationId }"
        >
          <div
            class="conversation-item"
            @click="chat.switchConversation(c.id)"
          >
            <div class="conversation-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="conversation-info">
              <input
                v-if="chat.state.editingId === c.id"
                v-model="chat.state.editTitle"
                class="conversation-title-input"
                maxlength="15"
                @click.stop
                @keyup.enter="chat.saveTitle(c.id)"
                @keyup.escape="chat.cancelEdit(c.id)"
                ref="editInput"
              />
              <div v-else class="conversation-title">{{ c.title }}</div>
              <div class="conversation-meta">{{ c.updatedAt }}</div>
            </div>
          </div>
          <div class="conversation-actions">
            <button
              v-if="chat.state.editingId !== c.id"
              class="rename-conversation"
              type="button"
              @click.stop="chat.startEdit(c.id, c.title)"
              title="重命名会话"
            >
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13M18.5 5.5C18.8978 5.10217 19.4374 4.87868 20 4.87868C20.5626 4.87868 21.1022 5.10217 21.5 5.5C21.8978 5.89782 22.1213 6.43739 22.1213 7C22.1213 7.56261 21.8978 8.10217 21.5 8.5L12 18L8 19L9 15L18.5 5.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="delete-conversation" type="button" @click.stop="chat.deleteConversation(c.id)" title="删除会话">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 6H5H21M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </aside>

    <div class="sidebar-resizer" @mousedown="startResize"></div>

    <main class="chat-main">
      <header class="chat-header">
        <div class="chat-header-left">
          <h2 class="chat-title">
            {{ activeConversation?.title || '未选择会话' }}
          </h2>
          <p class="chat-desc">
            <span class="status-dot"></span>
            已接入 DeepSeek 大模型
            <span class="model-badge" :class="{ thinking: chat.state.thinkingEnabled }">
              {{ chat.state.thinkingEnabled ? '深度思考模式' : '普通对话模式' }}
            </span>
          </p>
        </div>
        <div class="chat-header-right">
          <button
            class="thinking-toggle"
            :class="{ active: chat.state.thinkingEnabled }"
            type="button"
            @click="chat.toggleThinking"
            title="启用深度思考模式，适合复杂问题推理"
          >
            <svg class="brain-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9.66347 4.13793C10.7813 3.42526 12.2187 3.42526 13.3365 4.13793L19.1769 7.85219C20.2947 8.56486 21 9.78396 21 11.1043V17.8957C21 19.216 20.2947 20.4351 19.1769 21.1478L13.3365 24.8621C12.2187 25.5747 10.7813 25.5747 9.66347 24.8621L3.82311 21.1478C2.70526 20.4351 2 19.216 2 17.8957V11.1043C2 9.78396 2.70526 8.56486 3.82311 7.85219L9.66347 4.13793Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 8V16M8 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-if="chat.state.thinkingEnabled"/>
            </svg>
            <span class="toggle-label">深度思考</span>
          </button>
          <button
            class="reasoning-toggle"
            :class="{ active: chat.state.reasoningVisible }"
            type="button"
            @click="chat.toggleReasoning"
          >
            <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12H15M9 16H15M12 8V8.01M5.6 5.6C4.34651 6.85349 3.58379 8.44655 3.23852 10.1538C3.06589 11.0074 3 11.9412 3 13C3 14.0588 3.06589 14.9926 3.23852 15.8462C3.58379 17.5534 4.34651 19.1465 5.6 20.4C6.85349 21.6535 8.44655 22.4162 10.1538 22.7615C11.0074 22.9341 11.9412 23 13 23C14.0588 23 14.9926 22.9341 15.8462 22.7615C17.5534 22.4162 19.1465 21.6535 20.4 20.4C21.6535 19.1465 22.4162 17.5534 22.7615 15.8462C22.9341 14.9926 23 14.0588 23 13C23 11.9412 22.9341 11.0074 22.7615 10.1538C22.4162 8.44655 21.6535 6.85349 20.4 5.6C19.1465 4.34651 17.5534 3.58379 15.8462 3.23852C14.9926 3.06589 14.0588 3 13 3C11.9412 3 11.0074 3.06589 10.1538 3.23852C8.44655 3.58379 6.85349 4.34651 5.6 5.6Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="toggle-label">查看思考</span>
          </button>
        </div>
      </header>

      <section class="chat-body">
        <div class="messages" ref="messagesEl">
          <div v-if="activeMessages.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 10H8.01M12 10H12.01M16 10H16.01M9 16H15M21 12C21 16.9706 16.9706 21 12 21C5 21 5 21 5 21C5 21 3 17 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3>开始新的对话</h3>
            <p>向我提问任何问题，我会尽力为您解答</p>
          </div>
          
          <div
            v-for="m in activeMessages"
            :key="m.id"
            class="message-row"
            :class="m.role"
          >
            <div class="avatar" :class="m.role">
              <span v-if="m.role === 'user'">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
              <span v-else>
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
            </div>
            <div class="message-content">
              <div class="bubble" :class="m.role">
                <div class="bubble-content markdown-body" v-html="renderMarkdown(m.content)"></div>
              </div>
              <div class="bubble-meta">{{ m.createdAt }}</div>
            </div>
          </div>
        </div>

        <section v-if="chat.state.reasoningVisible" class="reasoning-panel">
          <header class="reasoning-header">
            <div class="reasoning-title">
              <svg class="brain-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9.66347 4.13793C10.7813 3.42526 12.2187 3.42526 13.3365 4.13793L19.1769 7.85219C20.2947 8.56486 21 9.78396 21 11.1043V17.8957C21 19.216 20.2947 20.4351 19.1769 21.1478L13.3365 24.8621C12.2187 25.5747 10.7813 25.5747 9.66347 24.8621L3.82311 21.1478C2.70526 20.4351 2 19.216 2 17.8957V11.1043C2 9.78396 2.70526 8.56486 3.82311 7.85219L9.66347 4.13793Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>AI 思考过程</span>
            </div>
            <p>深度推理分析</p>
          </header>
          <pre class="reasoning-content">{{ chat.state.reasoningContent }}</pre>
        </section>
      </section>

      <footer class="chat-input-area">
        <div class="input-wrapper">
          <div v-if="chat.state.error" class="error-banner">
            <svg class="error-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M12 8V12M12 16H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            {{ chat.state.error }}
          </div>
          
          <div class="input-container">
            <textarea
              v-model="chat.state.draft"
              class="chat-input"
              rows="1"
              :placeholder="chat.state.sending ? 'AI 正在思考中...' : '输入您的问题，按 Ctrl+Enter 发送'"
              :disabled="chat.state.sending"
              @keydown.ctrl.enter.prevent="chat.sendMessage"
            ></textarea>
            <button
              class="send-btn"
              type="button"
              :disabled="chat.state.sending || !chat.state.draft.trim()"
              @click="chat.sendMessage"
            >
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          
          <div class="input-footer">
            <span class="tip">AI 生成内容仅供参考，请仔细甄别</span>
            <span class="shortcut">Ctrl+Enter 发送</span>
          </div>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, computed } from 'vue'
import { useChatState } from './LayoutChatApp'
import { marked } from 'marked'
import hljs from 'highlight.js'

// 配置 marked 使用 highlight.js 进行代码高亮
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
})

const chat = useChatState()
const { activeConversation, activeMessages } = chat

// 侧边栏宽度控制
const sidebarWidth = ref(260)
const isResizing = ref(false)
const minSidebarWidth = 200
const maxSidebarWidth = 450

function startResize(e) {
  isResizing.value = true
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

function handleResize(e) {
  if (!isResizing.value) return
  const newWidth = Math.min(Math.max(e.clientX, minSidebarWidth), maxSidebarWidth)
  sidebarWidth.value = newWidth
}

function stopResize() {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

// 使用 computed 包裹 marked 渲染
const renderMarkdown = (text) => {
  if (!text) return ''
  return marked.parse(text)
}

const messagesEl = ref(null)

function scrollToBottom() {
  const el = messagesEl.value
  if (!el) return
  requestAnimationFrame(() => {
    el.scrollTop = el.scrollHeight
  })
}

onMounted(async () => {
  await chat.loadConversations()
  scrollToBottom()
})

watch(
  () => activeMessages.value.length,
  () => {
    scrollToBottom()
  },
)
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.chat-app {
  display: flex;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: #f8fafc;
  color: #1e293b;
}

/* ========== Sidebar ========== */
.sidebar {
  width: var(--sidebar-width, 260px);
  border-right: 1px solid #e2e8f0;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  display: flex;
  flex-direction: column;
  padding: 20px 16px;
  box-sizing: border-box;
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar-resizer {
  width: 6px;
  cursor: col-resize;
  background: transparent;
  transition: background 0.2s;
  flex-shrink: 0;
}

.sidebar-resizer:hover {
  background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
}

.sidebar-header {
  margin-bottom: 24px;
  padding: 0 8px;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.logo-icon svg {
  width: 20px;
  height: 20px;
}

.logo {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.02em;
}

.subtitle {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  margin-bottom: 20px;
  border-radius: 12px;
  border: 1px dashed #cbd5e1;
  background: #f1f5f9;
  color: #475569;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.new-chat-btn:hover {
  background: #e2e8f0;
  border-color: #94a3b8;
  color: #1e293b;
}

.plus-icon {
  width: 18px;
  height: 18px;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
}

.conversation-section-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
  margin-bottom: 12px;
  padding: 0 8px;
}

.conversation-item-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  position: relative;
}

.conversation-item-wrapper.active .conversation-item {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.conversation-item-wrapper.active .conversation-item .delete-conversation {
  color: rgba(255, 255, 255, 0.7);
}

.conversation-item-wrapper.active .conversation-item .delete-conversation:hover {
  color: white;
  background: rgba(255, 255, 255, 0.2);
}

.conversation-item {
  flex: 1;
  border: none;
  background: transparent;
  text-align: left;
  padding: 12px 40px 12px 12px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s ease;
}

.conversation-item:hover {
  background: #f1f5f9;
}

.empty-conversations {
  padding: 20px 12px;
  text-align: center;
  font-size: 13px;
  color: #94a3b8;
}

.delete-conversation {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #ef4444;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  padding: 0;
  flex-shrink: 0;
}

.delete-conversation:hover {
  background: #fee2e2;
  color: #dc2626;
  transform: scale(1.1);
}

.delete-conversation svg {
  width: 16px;
  height: 16px;
}

.conversation-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  flex-shrink: 0;
}

.conversation-item.active .conversation-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.conversation-icon svg {
  width: 18px;
  height: 18px;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-size: 14px;
  font-weight: 500;
  color: inherit;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-title-input {
  width: 100%;
  font-size: 13px;
  font-weight: 500;
  padding: 4px 6px;
  border: 1px solid #6366f1;
  border-radius: 4px;
  background: #fff;
  color: #1e293b;
  outline: none;
}

.conversation-item.active .conversation-title-input {
  background: rgba(255, 255, 255, 0.95);
}

.conversation-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.conversation-item-wrapper:hover .conversation-actions {
  opacity: 1;
}

.rename-conversation {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  padding: 0;
  flex-shrink: 0;
}

.rename-conversation:hover {
  background: #e0e7ff;
  color: #6366f1;
}

.rename-conversation svg {
  width: 14px;
  height: 14px;
}

.conversation-meta {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

.conversation-item.active .conversation-meta {
  color: rgba(255, 255, 255, 0.7);
}

/* ========== Main Chat Area ========== */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

.chat-header {
  padding: 20px 28px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.chat-header-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.chat-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #0f172a;
  letter-spacing: -0.02em;
}

.chat-desc {
  margin: 0;
  font-size: 13px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.model-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.model-badge.thinking {
  background: linear-gradient(135deg, #f3e8ff 0%, #ede9fe 100%);
  color: #7c3aed;
  border-color: #ddd6fe;
}

.chat-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.thinking-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.thinking-toggle:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #475569;
}

.thinking-toggle.active {
  background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
}

.thinking-toggle .brain-icon {
  width: 18px;
  height: 18px;
}

.reasoning-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reasoning-toggle:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #475569;
}

.reasoning-toggle.active {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-color: transparent;
  color: white;
}

.toggle-icon {
  width: 16px;
  height: 16px;
}

.toggle-label {
  white-space: nowrap;
}

/* ========== Messages Area ========== */
.chat-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages {
  flex: 1;
  padding: 28px;
  overflow-y: auto;
  background: #ffffff;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #94a3b8;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
  color: #cbd5e1;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-state h3 {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 600;
  color: #475569;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  color: #94a3b8;
}

.message-row {
  display: flex;
  margin-bottom: 24px;
  gap: 16px;
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #64748b;
  background: #f1f5f9;
}

.avatar.user {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.avatar.assistant {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.avatar svg {
  width: 20px;
  height: 20px;
}

.message-content {
  display: flex;
  flex-direction: column;
  max-width: min(900px, 85%);
  gap: 8px;
}

.message-row.user .message-content {
  align-items: flex-end;
}

.bubble {
  border-radius: 16px;
  padding: 14px 18px;
  line-height: 1.6;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  width: 100%;
}

.message-row.user .bubble {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.message-row.assistant .bubble {
  background: #f8fafc;
  color: #1e293b;
  border: 1px solid #e2e8f0;
}

.bubble-content {
  font-size: 15px;
  white-space: pre-wrap;
  word-break: break-word;
}

.bubble-meta {
  font-size: 12px;
  color: #94a3b8;
  padding: 0 4px;
}

/* ========== Reasoning Panel ========== */
.reasoning-panel {
  border-top: 1px solid #e2e8f0;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px 28px;
  max-height: 280px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.reasoning-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.reasoning-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

.brain-icon {
  width: 20px;
  height: 20px;
  color: #6366f1;
}

.reasoning-header p {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
}

.reasoning-content {
  flex: 1;
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  overflow-y: auto;
  background: #ffffff;
  color: #475569;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  font-family: "SF Mono", "Monaco", "Inconsolata", "Fira Mono", monospace;
}

/* ========== Input Area ========== */
.chat-input-area {
  border-top: 1px solid #e2e8f0;
  padding: 20px 28px 24px;
  background: #ffffff;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 12px 16px;
  transition: all 0.2s ease;
}

.input-container:focus-within {
  border-color: #6366f1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
  background: #ffffff;
}

.chat-input {
  flex: 1;
  resize: none;
  border: none;
  background: transparent;
  color: #1e293b;
  padding: 0;
  font-size: 15px;
  line-height: 1.5;
  max-height: 200px;
  font-family: inherit;
}

.chat-input::placeholder {
  color: #94a3b8;
}

.chat-input:focus {
  outline: none;
}

.chat-input:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 20px;
  height: 20px;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #94a3b8;
}

.tip {
  display: flex;
  align-items: center;
  gap: 6px;
}

.shortcut {
  font-weight: 500;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: #dc2626;
  font-size: 13px;
  border: 1px solid #fecaca;
}

.error-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* ========== Scrollbar ========== */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .chat-app {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
    flex-direction: row;
    align-items: center;
    gap: 16px;
    padding: 16px 20px;
  }

  .sidebar-header {
    margin-bottom: 0;
  }

  .new-chat-btn,
  .conversation-list {
    display: none;
  }

  .chat-header {
    padding: 16px 20px;
  }

  .chat-title {
    font-size: 18px;
  }

  .messages {
    padding: 20px;
  }

  .chat-input-area {
    padding: 16px 20px;
  }

  .message-content {
    max-width: 85%;
  }
}

/* ========== Markdown Styles ========== */
.markdown-body {
  font-size: 14px;
  line-height: 1.5;
}

.markdown-body p {
  margin: 0 0 0.8em;
}

.markdown-body p:last-child {
  margin-bottom: 0;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin: 1.5em 0 0.8em;
  font-weight: 600;
  line-height: 1.4;
}

.markdown-body h1:first-child,
.markdown-body h2:first-child,
.markdown-body h3:first-child {
  margin-top: 0;
}

.markdown-body h1 { font-size: 1.6em; }
.markdown-body h2 { font-size: 1.4em; }
.markdown-body h3 { font-size: 1.2em; }
.markdown-body h4 { font-size: 1.1em; }
.markdown-body h5 { font-size: 1em; }
.markdown-body h6 { font-size: 0.9em; }

.markdown-body ul,
.markdown-body ol {
  margin: 0.8em 0;
  padding-left: 1.8em;
}

.markdown-body li {
  margin: 0.4em 0;
}

.markdown-body code {
  font-family: "SF Mono", "Monaco", "Inconsolata", "Fira Mono", monospace;
  font-size: 0.9em;
  padding: 0.2em 0.4em;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.06);
}

.bubble.assistant .markdown-body code {
  background: rgba(255, 255, 255, 0.15);
}

.markdown-body pre {
  margin: 1em 0;
  padding: 0;
  overflow: hidden;
  border-radius: 8px;
}

.markdown-body pre code {
  display: block;
  padding: 16px;
  overflow-x: auto;
  font-size: 0.85em;
  line-height: 1.6;
  background: #1e293b;
  color: #e2e8f0;
  white-space: pre;
  word-wrap: normal;
}

.markdown-body blockquote {
  margin: 1em 0;
  padding: 0.5em 1em;
  border-left: 4px solid #6366f1;
  background: rgba(99, 102, 241, 0.1);
  color: #64748b;
}

.markdown-body a {
  color: #6366f1;
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}

.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.markdown-body th,
.markdown-body td {
  border: 1px solid #e2e8f0;
  padding: 0.6em 1em;
  text-align: left;
}

.markdown-body th {
  background: #f1f5f9;
  font-weight: 600;
}

.markdown-body hr {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 1.5em 0;
}
</style>

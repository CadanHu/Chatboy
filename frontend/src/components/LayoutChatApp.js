import { reactive, computed } from 'vue'

// 格式化时间显示
function formatTime(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`

  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 从 localStorage 获取当前激活的会话 ID
function getActiveConversationId() {
  return localStorage.getItem('activeConversationId')
}

function setActiveConversationId(id) {
  localStorage.setItem('activeConversationId', id)
}

export function useChatState() {
  const state = reactive({
    conversations: [],
    activeConversationId: null,
    messagesByConversation: {},
    draft: '',
    reasoningVisible: false,
    reasoningContent: '',
    sending: false,
    error: null,
    thinkingEnabled: false,
    loading: true,
  })

  const activeConversation = computed(() =>
    state.conversations.find((c) => c.id === state.activeConversationId),
  )

  const activeMessages = computed(
    () => state.messagesByConversation[state.activeConversationId] || [],
  )

  // 加载会话列表
  async function loadConversations() {
    try {
      const res = await fetch('/api/conversations')
      if (!res.ok) throw new Error('加载会话失败')
      const data = await res.json()
      state.conversations = data.map((c) => ({
        id: c.id,
        title: c.title,
        updatedAt: formatTime(c.updated_at),
      }))

      // 加载激活会话的消息
      if (state.activeConversationId) {
        await loadConversationMessages(state.activeConversationId)
      } else if (data.length > 0) {
        // 默认选择第一个会话
        state.activeConversationId = data[0].id
        setActiveConversationId(data[0].id)
        await loadConversationMessages(data[0].id)
      }
    } catch (e) {
      console.error('加载会话列表失败:', e)
      state.error = e?.message || String(e)
    } finally {
      state.loading = false
    }
  }

  // 加载单个会话的消息
  async function loadConversationMessages(conversationId) {
    try {
      const res = await fetch(`/api/conversations/${conversationId}`)
      if (!res.ok) return
      const data = await res.json()
      state.messagesByConversation[conversationId] = data.messages.map((m) => ({
        id: m.id,
        role: m.role,
        content: m.content,
        createdAt: formatTime(m.created_at),
        reasoningContent: m.reasoning_content,
      }))
    } catch (e) {
      console.error('加载消息失败:', e)
    }
  }

  // 创建新会话
  async function createNewConversation() {
    try {
      const res = await fetch('/api/conversations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: '新对话' }),
      })
      if (!res.ok) throw new Error('创建会话失败')
      const data = await res.json()

      state.conversations.unshift({
        id: data.id,
        title: data.title,
        updatedAt: '刚刚',
      })
      state.messagesByConversation[data.id] = []
      state.activeConversationId = data.id
      setActiveConversationId(data.id)
      state.reasoningContent = ''
      state.reasoningVisible = false

      return data.id
    } catch (e) {
      console.error('创建会话失败:', e)
      state.error = e?.message || String(e)
      return null
    }
  }

  // 删除会话
  async function deleteConversation(conversationId) {
    if (!confirm('确定要删除这个会话吗？')) return

    try {
      const res = await fetch(`/api/conversations/${conversationId}`, {
        method: 'DELETE',
      })
      if (!res.ok) throw new Error('删除失败')

      state.conversations = state.conversations.filter((c) => c.id !== conversationId)
      delete state.messagesByConversation[conversationId]

      if (state.activeConversationId === conversationId) {
        state.activeConversationId = state.conversations[0]?.id || null
        if (state.activeConversationId) {
          setActiveConversationId(state.activeConversationId)
          await loadConversationMessages(state.activeConversationId)
        } else {
          localStorage.removeItem('activeConversationId')
        }
      }
    } catch (e) {
      console.error('删除会话失败:', e)
      state.error = e?.message || String(e)
    }
  }

  function switchConversation(id) {
    state.activeConversationId = id
    setActiveConversationId(id)
    loadConversationMessages(id)
  }

  function toggleReasoning() {
    state.reasoningVisible = !state.reasoningVisible
  }

  function toggleThinking() {
    state.thinkingEnabled = !state.thinkingEnabled
  }

  async function sendMessage() {
    const text = state.draft.trim()
    if (!text) return
    if (state.sending) return

    const convId = state.activeConversationId
    const list = state.messagesByConversation[convId] || []
    const idBase = `m${Date.now()}`

    // 添加用户消息到 UI
    const userMessage = {
      id: idBase,
      role: 'user',
      content: text,
      createdAt: '刚刚',
    }
    state.messagesByConversation[convId] = [...list, userMessage]
    state.draft = ''
    state.sending = true
    state.error = null

    // 创建临时的 assistant 消息用于流式显示
    const assistantMessageId = `m${Date.now()}-assistant`
    const assistantMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      createdAt: '刚刚',
      reasoningContent: '',
      isStreaming: true,
    }
    state.messagesByConversation[convId] = [...state.messagesByConversation[convId], assistantMessage]

    try {
      // 获取当前会话的所有消息（包括刚发送的）
      const allMessages = state.messagesByConversation[convId]
        .filter((m) => m.role === 'user' || m.role === 'assistant')
        .map((m) => ({
          role: m.role,
          content: m.content,
        }))

      // 使用 SSE 流式请求
      const res = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: convId,
          messages: allMessages,
          thinking: state.thinkingEnabled,
        }),
      })

      if (!res.ok) {
        const textError = await res.text()
        throw new Error(`请求失败：${res.status} ${textError}`)
      }

      // 读取流式响应
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let reasoningText = ''
      let answerText = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 保留不完整的一行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.type === 'reasoning') {
                reasoningText += data.content
                assistantMessage.reasoningContent = reasoningText
                // 更新 UI
                const messages = state.messagesByConversation[convId]
                const idx = messages.findIndex(m => m.id === assistantMessageId)
                if (idx !== -1) {
                  messages[idx] = { ...messages[idx], reasoningContent }
                  state.messagesByConversation[convId] = [...messages]
                }
              } else if (data.type === 'answer') {
                answerText += data.content
                // 更新 UI
                const messages = state.messagesByConversation[convId]
                const idx = messages.findIndex(m => m.id === assistantMessageId)
                if (idx !== -1) {
                  messages[idx] = { ...messages[idx], content: answerText }
                  state.messagesByConversation[convId] = [...messages]
                }
              } else if (data.type === 'done') {
                // 流式结束，重新加载真实消息
                await loadConversationMessages(convId)
                await loadConversations()
              }
            } catch (e) {
              console.error('解析 SSE 数据失败:', e)
            }
          }
        }
      }

      // 显示思考过程
      if (reasoningText && !state.reasoningVisible) {
        state.reasoningVisible = true
      }
      state.reasoningContent = reasoningText
    } catch (e) {
      state.error = e?.message || String(e)
      // 出错时恢复用户消息
      state.messagesByConversation[convId] = list
    } finally {
      state.sending = false
    }
  }

  return {
    state,
    activeConversation,
    activeMessages,
    loadConversations,
    createNewConversation,
    deleteConversation,
    switchConversation,
    toggleReasoning,
    toggleThinking,
    sendMessage,
  }
}

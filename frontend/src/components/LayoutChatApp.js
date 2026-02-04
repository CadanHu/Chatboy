import { reactive, computed } from 'vue'

// 简单的前端模拟数据和状态管理，用于 Phase 2 UI 演示
export function useChatState() {
  const state = reactive({
    conversations: [
      {
        id: 'c1',
        title: '与 DeepSeek 的示例对话',
        updatedAt: '刚刚',
      },
      {
        id: 'c2',
        title: '产品需求讨论',
        updatedAt: '10 分钟前',
      },
    ],
    activeConversationId: 'c1',
    messagesByConversation: {
      c1: [],
      c2: [],
    },
    draft: '',
    // 思考过程相关的演示数据
    reasoningVisible: false,
    reasoningContent: '',
    sending: false,
    error: null,
  })

  const activeConversation = computed(() =>
    state.conversations.find((c) => c.id === state.activeConversationId),
  )

  const activeMessages = computed(
    () => state.messagesByConversation[state.activeConversationId] || [],
  )

  function switchConversation(id) {
    state.activeConversationId = id
  }

  function toggleReasoning() {
    state.reasoningVisible = !state.reasoningVisible
  }

  async function sendMessage() {
    const text = state.draft.trim()
    if (!text) return
    if (state.sending) return

    const convId = state.activeConversationId
    const existing = state.messagesByConversation[convId] || []
    const list = [...existing]
    const idBase = `m${list.length + 1}`

    const userMessage = {
      id: idBase,
      role: 'user',
      content: text,
      createdAt: '刚刚',
    }

    list.push(userMessage)
    state.messagesByConversation[convId] = list
    state.draft = ''
    state.sending = true
    state.error = null

    try {
      const payloadMessages = list.map((m) => ({
        role: m.role,
        content: m.content,
      }))

      const res = await fetch('/api/chat/deepseek', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: payloadMessages,
        }),
      })

      if (!res.ok) {
        const textError = await res.text()
        throw new Error(`后端错误: ${res.status} ${textError}`)
      }

      const data = await res.json()

      const answerText = data.answer || ''
      const reasoningText = data.reasoning || ''

      const assistantMessage = {
        id: `${idBase}-assistant`,
        role: 'assistant',
        content: answerText || '（后端未返回回答内容）',
        createdAt: '刚刚',
      }

      const updatedList = [...state.messagesByConversation[convId], assistantMessage]
      state.messagesByConversation[convId] = updatedList

      // 更新思考过程区域
      state.reasoningContent = reasoningText
      if (reasoningText && !state.reasoningVisible) {
        state.reasoningVisible = true
      }
    } catch (e) {
      state.error = e?.message || String(e)
    } finally {
      state.sending = false
    }
  }

  return {
    state,
    activeConversation,
    activeMessages,
    switchConversation,
    toggleReasoning,
    sendMessage,
  }
}


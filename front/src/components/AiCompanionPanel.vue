<template>
  <div class="ai-companion-panel">
    <div v-if="settingsStore.loading && !settingsStore.initialized" class="ai-loading-config">
      <span>正在检查配置...</span>
    </div>

    <div v-else-if="!settingsStore.status?.ai_key_configured" class="ai-unconfigured">
      <p>未配置 API Key，无法使用 AI 伴读功能。</p>
      <router-link to="/profile" class="config-link">前往个人中心配置 -></router-link>
    </div>

    <template v-else>
      <!-- Preset Prompts -->
      <div class="ai-presets" v-if="chatMessages.length === 0">
        <p class="ai-presets-title">✨ AI 伴读</p>
        <div class="preset-buttons">
          <button 
            v-for="(prompt, idx) in presetPrompts" 
            :key="idx" 
            class="preset-button"
            @click="sendPreset(prompt.value)"
          >
            <span class="preset-icon">{{ prompt.icon }}</span>
            {{ prompt.label }}
          </button>
        </div>
      </div>

      <!-- Chat History -->
      <div class="ai-chat-history" v-if="chatMessages.length > 0">
        <div 
          v-for="(msg, idx) in chatMessages" 
          :key="idx" 
          :class="['chat-bubble', `chat-${msg.role}`]"
        >
          <div class="bubble-content" v-html="renderMarkdown(msg.content)"></div>
          <div class="bubble-actions" v-if="msg.role === 'assistant' && !msg.isStreaming">
            <button class="action-btn" @click="copyToClipboard(msg.content)" title="一键复制">
              📋 一键复制
            </button>
            <button v-if="idx === chatMessages.length - 1" class="action-btn" @click="retryLast" title="重新生成">
              🔄 重试
            </button>
          </div>
        </div>
        <div v-if="isLoading" class="ai-typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>

      <!-- Chat Input -->
      <div class="ai-chat-input-wrapper">
        <input 
          v-model="inputValue" 
          class="ai-chat-input" 
          placeholder="向 AI 追问更多细节..." 
          @keydown.enter="sendCustom"
          :disabled="isLoading"
        />
        <button class="ai-send-btn" @click="sendCustom" :disabled="!inputValue.trim() || isLoading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useSettingsStore } from '../stores/settings'
import { ElMessage } from 'element-plus'
import { useClipboard } from '@vueuse/core'

const props = defineProps<{
  highlightId: number | string
  text: string
  book: string
}>()

const settingsStore = useSettingsStore()
const { copy, isSupported } = useClipboard()

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
}

const presetPrompts = [
  { icon: '💬', label: '通俗解释', value: '请用通俗易懂的话解释这段内容，它想表达的核心观点是什么？' },
  { icon: '💡', label: '举个例子', value: '能不能给我举一个生活中的实际例子来说明这段话？' },
  { icon: '⚖️', label: '潜在局限性', value: '这段话有什么潜在的局限性，或者存在什么可能的反驳视角？' }
]

const chatMessages = ref<ChatMessage[]>([])
const inputValue = ref('')
const isLoading = ref(false)

onMounted(async () => {
  await settingsStore.fetchStatus()
})

function renderMarkdown(rawText: string) {
  const rawHtml = marked.parse(rawText) as string
  return DOMPurify.sanitize(rawHtml)
}

function copyToClipboard(content: string) {
  if (isSupported.value) {
    copy(content)
    ElMessage.success('已一键复制 AI 回答')
  } else {
    ElMessage.warning('当前环境不支持快捷复制')
  }
}

function sendPreset(promptValue: string) {
  if (isLoading.value) return
  sendMessage(promptValue)
}

function sendCustom() {
  if (isLoading.value || !inputValue.value.trim()) return
  const val = inputValue.value.trim()
  inputValue.value = ''
  sendMessage(val)
}

function retryLast() {
  if (isLoading.value || chatMessages.value.length < 2) return
  chatMessages.value.pop() // remove AI msg
  const lastUserMsg = chatMessages.value[chatMessages.value.length - 1]
  if (lastUserMsg && lastUserMsg.role === 'user') {
    requestAiStreamResponse(lastUserMsg.content)
  }
}

async function sendMessage(userText: string) {
  chatMessages.value.push({ role: 'user', content: userText })
  await requestAiStreamResponse(userText)
}

async function requestAiStreamResponse(userPrompt: string) {
  isLoading.value = true
  const assistantMsg: ChatMessage = { role: 'assistant', content: '', isStreaming: true }
  chatMessages.value.push(assistantMsg)
  
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
    const token = localStorage.getItem('weread_review_token')
    
    // Here we make a real request. Note: The backend endpoint might not exist yet,
    // so this will likely return a 404/500, and fall into the catch block gracefully.
    const response = await fetch(`${baseUrl}/api/highlights/${props.highlightId}/ai-chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify({ message: userPrompt })
    })

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    
    if (reader) {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        assistantMsg.content += decoder.decode(value, { stream: true })
      }
    }
  } catch (err: any) {
    console.error('AI Stream Error:', err)
    assistantMsg.content = `> 请求 AI 服务失败，请检查配置或稍后重试。\n\n**错误详情**：${err.message || '网络连接异常'}`
  } finally {
    assistantMsg.isStreaming = false
    isLoading.value = false
  }
}
</script>

<style scoped>
.ai-loading-config, .ai-unconfigured {
  padding: 10px;
  text-align: center;
  color: var(--muted);
  font-size: 14px;
}
.ai-unconfigured p {
  margin: 0 0 10px 0;
}
.config-link {
  color: var(--green);
  font-weight: 500;
  text-decoration: none;
  background: var(--wash);
  padding: 6px 16px;
  border-radius: 20px;
  display: inline-block;
  transition: all 0.2s;
}
.config-link:hover {
  background: var(--green-dark);
  color: white;
}
</style>

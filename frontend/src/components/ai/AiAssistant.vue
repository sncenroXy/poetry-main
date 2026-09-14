<template>
  <div class="ai-assistant">
    <!-- 标题栏 -->
    <div class="assistant-header">
      <div class="flex items-center gap-2.5">
        <div class="header-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
            <path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z" />
            <line x1="9" y1="21" x2="15" y2="21" />
          </svg>
        </div>
        <div>
          <h2 class="text-[16px] font-semibold text-ink leading-tight">AI 诗词助手</h2>
          <p class="text-[11px] text-ink-light mt-0.5">赏析 · 典故 · 格律 · 百科</p>
        </div>
      </div>
      <button
        v-if="messages.length"
        class="clear-btn"
        @click="clearChat"
        title="清空对话"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-3.5 h-3.5">
          <polyline points="1 4 1 10 7 10" /><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
        </svg>
      </button>
    </div>

    <!-- 预设问题 — 网格布局填满空间 -->
    <div v-if="!messages.length" class="preset-section">
      <p class="text-[12px] text-ink-light mb-2.5">试试问我：</p>
      <div class="preset-grid">
        <button
          v-for="q in presetQuestions"
          :key="q.text"
          class="preset-card"
          @click="sendPreset(q.text)"
        >
          <span class="preset-emoji">{{ q.emoji }}</span>
          <span class="preset-text">{{ q.text }}</span>
        </button>
      </div>
    </div>

    <!-- 聊天区域 -->
    <div v-if="messages.length" ref="chatArea" class="chat-area">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="chat-bubble-row"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <!-- AI 头像 -->
        <div v-if="msg.role === 'assistant'" class="ai-avatar">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-3.5 h-3.5">
            <path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z" />
          </svg>
        </div>
        <div
          class="chat-bubble"
          :class="msg.role === 'user' ? 'bubble-user' : 'bubble-ai'"
        >
          <div class="bubble-content" v-html="renderContent(msg.content)"></div>
        </div>
      </div>

      <!-- 加载动画 -->
      <div v-if="loading" class="chat-bubble-row justify-start">
        <div class="ai-avatar">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-3.5 h-3.5">
            <path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z" />
          </svg>
        </div>
        <div class="chat-bubble bubble-ai">
          <div class="typing-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="input-area">
      <div class="input-wrapper">
        <input
          v-model="inputText"
          type="text"
          placeholder="请输入诗词相关问题…"
          maxlength="500"
          class="chat-input"
          @keydown.enter="sendMessage"
          :disabled="loading"
        />
        <button
          class="send-btn"
          :class="{ active: inputText.trim() && !loading }"
          :disabled="!inputText.trim() || loading"
          @click="sendMessage"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { chatWithAssistant } from '@/api/assistant'

const presetQuestions = [
  { emoji: '\u5E73', text: '什么是平仄？' },
  { emoji: '\u674E', text: '李白代表作有哪些？' },
  { emoji: '\u6C99', text: '赏析"大漠孤烟直，长河落日圆"' },
  { emoji: '\u8BCD', text: '唐诗和宋词有什么区别？' },
  { emoji: '\u521D', text: '"人生若只如初见"出自哪里？' },
  { emoji: '\u5F8B', text: '如何写一首七言绝句？' },
]

const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const chatArea = ref(null)

function renderContent(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
    .replace(/「([^」]+)」/g, '<span class="quote-mark">「$1」</span>')
}

async function scrollToBottom() {
  await nextTick()
  if (chatArea.value) {
    chatArea.value.scrollTop = chatArea.value.scrollHeight
  }
}

function sendPreset(question) {
  inputText.value = question
  sendMessage()
}

function clearChat() {
  messages.value = []
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const history = messages.value.slice(0, -1).map(m => ({
      role: m.role,
      content: m.content,
    }))

    const data = await chatWithAssistant(text, history)
    messages.value.push({ role: 'assistant', content: data.reply })
  } catch {
    messages.value.push({
      role: 'assistant',
      content: '抱歉，网络似乎出了点问题，请稍后再试。',
    })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}
</script>

<style scoped>
.ai-assistant {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(200, 133, 26, 0.12);
  box-shadow:
    var(--shadow-card),
    var(--inset-card);
  display: flex;
  flex-direction: column;
  min-height: 360px;
}

/* 标题栏 */
.assistant-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(200, 133, 26, 0.10);
}

.header-icon {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  background: linear-gradient(135deg, rgba(200, 133, 26, 0.15), rgba(229, 77, 66, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c8851a;
  flex-shrink: 0;
}

.clear-btn {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid rgba(200, 133, 26, 0.08);
  background: rgba(0, 0, 0, 0.03);
  color: #AEAEB2;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.clear-btn:hover {
  background: rgba(0, 0, 0, 0.06);
  color: #6E6E73;
  border-color: rgba(200, 133, 26, 0.12);
}

/* 预设问题 — 2 列网格 */
.preset-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.preset-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  flex: 1;
}

.preset-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(200, 133, 26, 0.08);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.preset-card:hover {
  background: rgba(200, 133, 26, 0.06);
  border-color: rgba(200, 133, 26, 0.18);
  box-shadow:
    0 2px 8px rgba(200, 133, 26, 0.10),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.preset-card:active {
  transform: scale(0.97);
}

.preset-emoji {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(200, 133, 26, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Noto Serif SC', 'KaiTi', '楷体', serif;
  font-size: 13px;
  font-weight: 600;
  color: #c8851a;
  flex-shrink: 0;
}

.preset-text {
  font-size: 13px;
  color: #1D1D1F;
  line-height: 1.4;
  font-weight: 450;
}

/* 聊天区域 */
.chat-area {
  flex: 1;
  max-height: 380px;
  overflow-y: auto;
  padding: 4px 0 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  scroll-behavior: smooth;
}

.chat-area::-webkit-scrollbar {
  width: 3px;
}

.chat-area::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.08);
  border-radius: 2px;
}

/* AI 头像 */
.ai-avatar {
  width: 24px;
  height: 24px;
  border-radius: 7px;
  background: linear-gradient(135deg, rgba(200, 133, 26, 0.15), rgba(229, 77, 66, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c8851a;
  flex-shrink: 0;
  margin-top: 2px;
}

/* 气泡行 */
.chat-bubble-row {
  display: flex;
  gap: 8px;
  animation: slideUp 0.25s ease;
}

/* 气泡 */
.chat-bubble {
  max-width: 82%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 13.5px;
  line-height: 1.75;
  word-break: break-word;
}

.bubble-user {
  background: linear-gradient(135deg, #c8851a, #d4922e);
  color: white;
  border-bottom-right-radius: 4px;
  border: 1px solid #b5760f;
  box-shadow:
    0 2px 8px rgba(200, 133, 26, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.bubble-ai {
  background: rgba(255, 255, 255, 0.88);
  color: #1D1D1F;
  border-bottom-left-radius: 4px;
  border: 1px solid rgba(200, 133, 26, 0.08);
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.bubble-content :deep(.quote-mark) {
  color: #c8851a;
  font-weight: 500;
}

/* 打点动画 */
.typing-dots {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 4px 0;
}

.typing-dots span {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #c8851a;
  opacity: 0.35;
  animation: typingBounce 1.2s infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%, 60%, 100% { opacity: 0.35; transform: translateY(0); }
  30% { opacity: 1; transform: translateY(-3px); }
}

@keyframes slideUp {
  0% { opacity: 0; transform: translateY(6px); }
  100% { opacity: 1; transform: translateY(0); }
}

/* 输入区域 */
.input-area {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(200, 133, 26, 0.08);
}

.input-wrapper {
  display: flex;
  gap: 8px;
  align-items: center;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 22px;
  padding: 3px 3px 3px 14px;
  border: 1px solid rgba(200, 133, 26, 0.10);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
}

.input-wrapper:focus-within {
  border-color: rgba(200, 133, 26, 0.25);
  box-shadow:
    inset 0 2px 4px rgba(0, 0, 0, 0.04),
    0 0 0 3px rgba(200, 133, 26, 0.08);
}

.chat-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 13.5px;
  color: #1D1D1F;
  padding: 7px 0;
}

.chat-input::placeholder {
  color: #AEAEB2;
}

.send-btn {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid rgba(200, 133, 26, 0.06);
  background: rgba(0, 0, 0, 0.04);
  color: #AEAEB2;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.send-btn.active {
  background: linear-gradient(180deg, #d4922e, #c8851a);
  border: 1px solid #b5760f;
  color: white;
  box-shadow:
    0 2px 8px rgba(200, 133, 26, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.send-btn.active:hover {
  background: linear-gradient(180deg, #c8851a, #b5760f);
  box-shadow:
    0 4px 12px rgba(200, 133, 26, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.send-btn:disabled {
  cursor: not-allowed;
}
</style>

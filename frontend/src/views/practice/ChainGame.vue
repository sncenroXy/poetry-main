<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- 页面标题 -->
    <div class="content-container pt-6 pb-4">
      <h1 class="text-[24px] lg:text-[32px] font-semibold text-ink tracking-tight">飞花令</h1>
      <p class="text-ink-light text-[15px] mt-1">诗词接龙，与 AI 一较高下</p>
    </div>

    <div class="content-container">
      <!-- 模式切换 -->
      <div class="tab-bar mb-5">
        <button
          class="tab-btn"
          :class="{ active: mode === 'classic' }"
          @click="switchMode('classic')"
        >经典模式</button>
        <button
          class="tab-btn"
          :class="{ active: mode === 'ai' }"
          @click="switchMode('ai')"
        >AI 对战</button>
      </div>

      <div class="max-w-2xl">
        <!-- ===== 经典模式 ===== -->
        <template v-if="mode === 'classic'">
          <!-- 当前题目 -->
          <div class="glass-card-accent p-6 mb-4 text-center">
            <p class="text-[12px] text-ink-light mb-3">请写出下一句</p>
            <p class="poem-body text-[22px] text-ink mb-2">{{ currentLine }}</p>
            <div class="divider-brush" />
          </div>

          <!-- AI 渐进提示 -->
          <div v-if="hints.length" class="mb-4">
            <div class="space-y-2">
              <div
                v-for="(h, idx) in hints"
                :key="idx"
                class="glass-card px-4 py-3 animate-fade-in"
              >
                <div class="flex items-start gap-2">
                  <span class="hint-badge">提示{{ h.level }}</span>
                  <div>
                    <p class="text-[14px] text-ink">{{ h.hint }}</p>
                    <p v-if="h.source_title" class="text-[12px] text-ink-light mt-1">
                      出自《{{ h.source_title }}》
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 用户输入 -->
          <div class="bg-sys-bg-secondary rounded-apple px-4 py-3 mb-4">
            <input
              v-model="userAnswer"
              class="w-full bg-transparent border-none outline-none text-[15px] text-ink placeholder:text-text-tertiary"
              placeholder="请输入下一句诗…"
              @keyup.enter="submitClassic"
            />
          </div>

          <!-- 操作按钮 -->
          <div class="flex gap-3 mb-4">
            <van-button
              plain
              size="large"
              class="flex-1"
              style="border-radius: 12px"
              :loading="hintLoading"
              :disabled="hintLevel > 3"
              @click="getProgressiveHint"
            >
              {{ hintLevel > 3 ? '已无更多提示' : `提示 (${hintLevel}/3)` }}
            </van-button>
            <van-button
              color="#c8851a"
              size="large"
              class="flex-1"
              style="border-radius: 12px"
              :disabled="!userAnswer.trim()"
              :loading="submitLoading"
              @click="submitClassic"
            >
              提交
            </van-button>
          </div>

          <!-- AI 反馈卡片 -->
          <div v-if="feedback" class="glass-card p-5 mb-4 animate-slide-up" :class="feedback.correct ? 'border-l-4 border-success' : 'border-l-4 border-accent'">
            <p class="text-[16px] font-semibold mb-2" :class="feedback.correct ? 'text-success' : 'text-accent'">
              {{ feedback.correct ? '回答正确！' : '回答错误' }}
            </p>
            <p v-if="feedback.explanation" class="text-[14px] text-ink leading-relaxed mb-2">{{ feedback.explanation }}</p>
            <div v-if="!feedback.correct && feedback.correct_answer" class="bg-sys-bg-secondary rounded-apple px-3 py-2 mb-2">
              <p class="text-[13px] text-ink-light">正确答案：<span class="font-medium text-ink poem-body">{{ feedback.correct_answer }}</span></p>
            </div>
            <p v-if="feedback.source_title" class="text-[12px] text-ink-light">
              出自《{{ feedback.source_title }}》{{ feedback.source_author ? ' — ' + feedback.source_author : '' }}
            </p>
            <div class="mt-3">
              <van-button size="small" color="#c8851a" style="border-radius: 10px" @click="nextClassicRound">下一题</van-button>
            </div>
          </div>

          <!-- 得分 -->
          <div class="mt-6 flex justify-center gap-8 text-center">
            <div>
              <p class="text-[18px] font-bold text-primary">{{ challengeStore.chainScore }}</p>
              <p class="text-[12px] text-ink-light mt-0.5">总分</p>
            </div>
            <div>
              <p class="text-[18px] font-bold text-accent">{{ challengeStore.chainStreak }}</p>
              <p class="text-[12px] text-ink-light mt-0.5">连续正确</p>
            </div>
          </div>
        </template>

        <!-- ===== AI 对战模式 ===== -->
        <template v-else>
          <!-- 对话区域 -->
          <div class="chat-area mb-4" ref="chatAreaRef">
            <div v-if="!challengeStore.chainHistory.length" class="text-center py-8">
              <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 7.5a4.5 4.5 0 1 1 4.5 4.5M12 7.5A4.5 4.5 0 1 0 7.5 12M12 7.5V9m-4.5 3a4.5 4.5 0 1 0 4.5 4.5M7.5 12H9m3 4.5a4.5 4.5 0 1 0 4.5-4.5M12 16.5V15m4.5-3a4.5 4.5 0 1 1-4.5-4.5M16.5 12H15" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </div>
              <h3 class="text-[18px] font-semibold text-ink mb-2">AI 诗词对战</h3>
              <p class="text-ink-light text-[14px] mb-4">输入一句诗开始，AI 会接句并出新题</p>
              <p class="text-[12px] text-ink-light">你来我往，看谁更懂诗词</p>
            </div>

            <!-- 聊天气泡 -->
            <div
              v-for="(msg, idx) in challengeStore.chainHistory"
              :key="idx"
              class="chat-message animate-fade-in"
              :class="msg.role === 'user' ? 'chat-user' : 'chat-ai'"
            >
              <div class="chat-bubble" :class="msg.role === 'user' ? 'bubble-user' : 'bubble-ai'">
                <p class="poem-body text-[16px]">{{ msg.content }}</p>
                <p v-if="msg.title" class="text-[12px] mt-1 opacity-70">—《{{ msg.title }}》{{ msg.author ? ' ' + msg.author : '' }}</p>
                <p v-if="msg.comment" class="text-[12px] mt-1 opacity-70 italic">{{ msg.comment }}</p>
              </div>
            </div>

            <!-- AI 思考中 -->
            <div v-if="aiThinking" class="chat-message chat-ai animate-fade-in">
              <div class="chat-bubble bubble-ai">
                <div class="flex items-center gap-2">
                  <span class="typing-dot" />
                  <span class="typing-dot delay-1" />
                  <span class="typing-dot delay-2" />
                  <span class="text-[13px] text-ink-light ml-1">AI 思考中…</span>
                </div>
              </div>
            </div>
          </div>

          <!-- AI 对战输入 -->
          <div class="bg-sys-bg-secondary rounded-apple px-4 py-3 mb-4">
            <input
              v-model="aiUserInput"
              class="w-full bg-transparent border-none outline-none text-[15px] text-ink placeholder:text-text-tertiary"
              :placeholder="aiInputPlaceholder"
              @keyup.enter="submitAITurn"
            />
          </div>

          <van-button
            color="#c8851a"
            block
            size="large"
            style="border-radius: 12px"
            :disabled="!aiUserInput.trim()"
            :loading="aiThinking"
            @click="submitAITurn"
          >
            {{ challengeStore.chainHistory.length ? '接句' : '出题' }}
          </van-button>

          <!-- AI 对战得分 -->
          <div class="mt-6 flex justify-center gap-8 text-center">
            <div>
              <p class="text-[18px] font-bold text-primary">{{ aiRounds }}</p>
              <p class="text-[12px] text-ink-light mt-0.5">对战轮次</p>
            </div>
            <div>
              <p class="text-[18px] font-bold text-accent">{{ challengeStore.chainScore }}</p>
              <p class="text-[12px] text-ink-light mt-0.5">总分</p>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 底部留白 -->
    <div class="h-12"></div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getAIHint, aiValidateChain, aiChainTurn } from '@/api/challenge'
import { useChallengeStore } from '@/stores/challenge'
import { showToast } from 'vant'

const router = useRouter()
const challengeStore = useChallengeStore()

// ---------- 模式切换 ----------
const mode = ref(challengeStore.chainMode)

function switchMode(m) {
  mode.value = m
  challengeStore.setChainMode(m)
  // 重置经典模式状态
  if (m === 'classic') {
    nextClassicRound()
  }
}

// ---------- 经典模式 ----------

const DEFAULT_LINES = [
  '床前明月光', '春眠不觉晓', '白日依山尽', '举头望明月',
  '锄禾日当午', '独在异乡为异客', '慈母手中线', '大漠孤烟直',
  '明月几时有', '春风又绿江南岸', '飞流直下三千尺', '两个黄鹂鸣翠柳',
]

const currentLine = ref(DEFAULT_LINES[Math.floor(Math.random() * DEFAULT_LINES.length)])
const userAnswer = ref('')
const hints = ref([])
const hintLevel = ref(1)
const hintLoading = ref(false)
const submitLoading = ref(false)
const feedback = ref(null)

async function getProgressiveHint() {
  if (hintLevel.value > 3) return
  hintLoading.value = true
  try {
    const data = await getAIHint(currentLine.value, hintLevel.value)
    hints.value.push(data)
    hintLevel.value++
  } catch {
    showToast('获取提示失败')
  } finally {
    hintLoading.value = false
  }
}

async function submitClassic() {
  if (!userAnswer.value.trim() || submitLoading.value) return
  submitLoading.value = true
  try {
    const data = await aiValidateChain(currentLine.value, userAnswer.value.trim())
    feedback.value = data
    if (data.correct) {
      challengeStore.addChainScore(10)
    } else {
      challengeStore.resetChainStreak()
    }
  } catch {
    showToast('校验失败，请重试')
  } finally {
    submitLoading.value = false
  }
}

function nextClassicRound() {
  feedback.value = null
  userAnswer.value = ''
  hints.value = []
  hintLevel.value = 1
  currentLine.value = DEFAULT_LINES[Math.floor(Math.random() * DEFAULT_LINES.length)]
}

// ---------- AI 对战模式 ----------

const aiUserInput = ref('')
const aiThinking = ref(false)
const chatAreaRef = ref(null)

const aiRounds = computed(() => {
  return Math.floor(challengeStore.chainHistory.filter(m => m.role === 'ai').length)
})

const aiInputPlaceholder = computed(() => {
  if (!challengeStore.chainHistory.length) return '输入一句诗开始对战…'
  const last = challengeStore.chainHistory[challengeStore.chainHistory.length - 1]
  if (last.role === 'ai' && last.type === 'new_line') return '请接出这句诗的下一句…'
  return '输入下一句诗…'
})

// 判断是否为认输/不知道类输入
const FORFEIT_PATTERNS = /^(不知道|我不知道|不会|跳过|认输|投降|放弃|pass|skip|idk|不清楚|答不上|接不上|想不起)/i

function isForfeitInput(text) {
  return FORFEIT_PATTERNS.test(text.trim())
}

// 找到上一条 AI 出题消息
function getLastAIQuestion() {
  const history = challengeStore.chainHistory
  for (let i = history.length - 1; i >= 0; i--) {
    if (history[i].role === 'ai' && history[i].type === 'new_line') {
      return history[i]
    }
  }
  return null
}

async function submitAITurn() {
  const input = aiUserInput.value.trim()
  if (!input || aiThinking.value) return

  // 检测是否是认输/不知道
  if (isForfeitInput(input) && challengeStore.chainHistory.length > 0) {
    const lastQuestion = getLastAIQuestion()

    challengeStore.addChainMessage({
      role: 'user',
      content: input,
      type: 'forfeit',
    })
    aiUserInput.value = ''
    aiThinking.value = true

    await nextTick()
    scrollChatToBottom()

    try {
      // 调用 AI，让它给出正确答案并出新题
      const questionLine = lastQuestion ? lastQuestion.content : input
      const data = await aiChainTurn(questionLine)

      // AI 告知正确答案
      challengeStore.addChainMessage({
        role: 'ai',
        content: data.ai_answer,
        title: data.ai_answer_title,
        author: data.ai_answer_author,
        comment: '这回给你一道经典题！',
        type: 'answer',
      })

      // AI 出新题
      if (data.new_line) {
        await new Promise(r => setTimeout(r, 600))
        challengeStore.addChainMessage({
          role: 'ai',
          content: data.new_line,
          title: data.new_line_title,
          author: data.new_line_author,
          type: 'new_line',
        })
      }
    } catch {
      showToast('AI 暂时无法应答，请重试')
    } finally {
      aiThinking.value = false
      await nextTick()
      scrollChatToBottom()
    }
    return
  }

  // 正常诗句回答流程
  challengeStore.addChainMessage({
    role: 'user',
    content: input,
    type: 'answer',
  })
  aiUserInput.value = ''
  aiThinking.value = true

  await nextTick()
  scrollChatToBottom()

  try {
    const data = await aiChainTurn(input)

    // AI 接句
    challengeStore.addChainMessage({
      role: 'ai',
      content: data.ai_answer,
      title: data.ai_answer_title,
      author: data.ai_answer_author,
      comment: data.comment,
      type: 'answer',
    })

    challengeStore.addChainScore(10)

    // AI 出新题
    if (data.new_line) {
      await new Promise(r => setTimeout(r, 600))
      challengeStore.addChainMessage({
        role: 'ai',
        content: data.new_line,
        title: data.new_line_title,
        author: data.new_line_author,
        type: 'new_line',
      })
    }
  } catch {
    showToast('AI 暂时无法应答，请重试')
  } finally {
    aiThinking.value = false
    await nextTick()
    scrollChatToBottom()
  }
}

function scrollChatToBottom() {
  if (chatAreaRef.value) {
    chatAreaRef.value.scrollTop = chatAreaRef.value.scrollHeight
  }
}
</script>

<style scoped>
/* Tab 切换 */
.tab-bar {
  display: inline-flex;
  gap: 4px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 12px;
  padding: 4px;
}

.tab-btn {
  padding: 8px 24px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  color: #6E6E73;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: white;
  color: #1D1D1F;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.tab-btn:active {
  transform: scale(0.97);
}

/* 提示徽章 */
.hint-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(200, 133, 26, 0.12);
  color: #c8851a;
  flex-shrink: 0;
  margin-top: 2px;
}

/* 聊天区域 */
.chat-area {
  max-height: 500px;
  overflow-y: auto;
  padding: 4px 0;
}

.chat-message {
  display: flex;
  margin-bottom: 12px;
}

.chat-user {
  justify-content: flex-end;
}

.chat-ai {
  justify-content: flex-start;
}

.chat-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 16px;
}

.bubble-user {
  background: rgba(200, 133, 26, 0.12);
  color: #1D1D1F;
  border-bottom-right-radius: 4px;
}

.bubble-ai {
  background: rgba(0, 0, 0, 0.04);
  color: #1D1D1F;
  border-bottom-left-radius: 4px;
}

/* 打字动画 */
.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #AEAEB2;
  animation: typing 1.2s ease-in-out infinite;
}

.delay-1 { animation-delay: 0.2s; }
.delay-2 { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; transform: scale(0.8); }
  30% { opacity: 1; transform: scale(1); }
}

/* 动画 */
.animate-fade-in {
  animation: fadeIn 0.3s ease;
}

.animate-slide-up {
  animation: slideUp 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

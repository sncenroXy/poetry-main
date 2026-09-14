<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- 页面标题 -->
    <div class="content-container pt-6 pb-4">
      <h1 class="text-[24px] lg:text-[32px] font-semibold text-ink tracking-tight">答题闯关</h1>
      <p class="text-ink-light text-[15px] mt-1">AI 出题，全面考验诗词功底</p>
    </div>

    <div class="content-container py-4">
      <div class="max-w-2xl">
        <!-- 题目状态栏 -->
        <div v-if="started && !finished" class="flex justify-between items-center mb-4 text-[13px] text-ink-light">
          <span>第 {{ currentIndex + 1 }} / {{ questions.length }} 题</span>
          <span>正确：{{ challengeStore.quizCorrect }}</span>
        </div>

        <!-- 加载中 -->
        <Loading v-if="loading" :text="loadingText" />

        <!-- 题目内容 -->
        <div v-else-if="currentQuestion && !finished" class="glass-card-accent p-6 animate-slide-up">
          <!-- 题型标签 -->
          <div class="flex items-center gap-2 mb-4">
            <span class="type-badge" :class="'type-' + (currentQuestion.type || 'fill_blank')">
              {{ typeLabels[currentQuestion.type] || '填空' }}
            </span>
            <span v-if="currentQuestion.source" class="text-[12px] text-ink-light">{{ currentQuestion.source }}</span>
          </div>

          <!-- 题目 -->
          <p class="poem-body text-[20px] text-ink text-center mb-5 leading-relaxed">{{ currentQuestion.question }}</p>
          <div class="divider-brush mb-5" />

          <!-- 选项 -->
          <div class="space-y-3">
            <div
              v-for="(opt, idx) in currentQuestion.options"
              :key="idx"
              class="option-item rounded-apple px-4 py-3.5 text-ink cursor-pointer transition-all"
              :class="getOptionClass(idx)"
              @click="selectOption(idx)"
            >
              <span class="inline-flex items-center justify-center w-6 h-6 rounded-full mr-3 text-[13px] font-medium"
                :class="selected === idx ? 'bg-primary text-white' : 'bg-sys-bg-secondary text-ink-light'">
                {{ ['A', 'B', 'C', 'D'][idx] }}
              </span>
              {{ opt }}
            </div>
          </div>

          <!-- 答题结果 + AI 解析 -->
          <div v-if="answered" class="mt-4">
            <!-- 对错反馈 -->
            <div class="p-4 rounded-apple animate-fade-in"
              :class="isCorrect ? 'bg-success/8' : 'bg-accent/8'">
              <p class="text-[15px] font-semibold" :class="isCorrect ? 'text-success' : 'text-accent'">
                {{ isCorrect ? '回答正确！' : '回答错误' }}
              </p>
              <p v-if="!isCorrect" class="text-[13px] text-ink-light mt-1">
                正确答案是：{{ ['A', 'B', 'C', 'D'][currentQuestion.answer] }}
              </p>
            </div>

            <!-- AI 解析卡片 -->
            <div v-if="explanation" class="mt-3 glass-card p-4 animate-slide-up">
              <button class="w-full flex items-center justify-between text-left" @click="showExplanation = !showExplanation">
                <span class="text-[14px] font-medium text-primary">AI 解析</span>
                <van-icon :name="showExplanation ? 'arrow-up' : 'arrow-down'" size="14" color="#c8851a" />
              </button>
              <div v-show="showExplanation" class="mt-3 space-y-2">
                <p class="text-[14px] text-ink leading-relaxed">{{ explanation.explanation }}</p>
                <div v-if="explanation.full_poem" class="bg-sys-bg-secondary rounded-apple px-3 py-2">
                  <p class="text-[13px] text-ink poem-body whitespace-pre-line">{{ explanation.full_poem }}</p>
                </div>
                <p v-if="explanation.knowledge" class="text-[12px] text-ink-light">
                  <span class="font-medium text-ink">知识扩展：</span>{{ explanation.knowledge }}
                </p>
              </div>
            </div>

            <!-- AI 解析加载中 -->
            <div v-else-if="explainLoading" class="mt-3 glass-card p-4">
              <div class="flex items-center gap-2">
                <div class="mini-spinner" />
                <span class="text-[13px] text-ink-light">AI 正在解析…</span>
              </div>
            </div>

            <!-- 下一题按钮 -->
            <van-button
              color="#c8851a"
              block
              style="border-radius: 12px"
              class="mt-4"
              @click="nextQuestion"
            >
              {{ currentIndex < questions.length - 1 ? '下一题' : '查看总结' }}
            </van-button>
          </div>
        </div>

        <!-- AI 总结页 -->
        <div v-else-if="finished" class="animate-slide-up">
          <!-- 成绩概览 -->
          <div class="glass-card-accent p-8 text-center mb-4">
            <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5C7 4 6 7 6 7" />
                <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5C17 4 18 7 18 7" />
                <path d="M4 22h16" />
                <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" />
                <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" />
                <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
              </svg>
            </div>
            <h3 class="text-[22px] font-semibold text-ink mb-2">挑战完成！</h3>
            <p class="text-ink-light text-[15px]">
              本轮答对 <span class="text-primary font-bold text-[20px]">{{ correctCount }}</span> / {{ questions.length }} 题
            </p>
          </div>

          <!-- AI 总结 -->
          <div v-if="summaryLoading" class="glass-card p-6 text-center mb-4">
            <div class="flex items-center justify-center gap-3 mb-3">
              <div class="mini-spinner" />
              <span class="text-[14px] text-ink-light">{{ summaryLoadingText }}</span>
            </div>
          </div>

          <div v-else-if="summary" class="space-y-4 mb-4">
            <!-- 总评 -->
            <div class="glass-card p-5">
              <h4 class="text-[15px] font-semibold text-ink mb-2">总体评价</h4>
              <p class="text-[14px] text-ink leading-relaxed">{{ summary.score_comment }}</p>
            </div>

            <!-- 薄弱点 -->
            <div v-if="summary.weak_points && summary.weak_points.length" class="glass-card p-5">
              <h4 class="text-[15px] font-semibold text-ink mb-2">需要加强</h4>
              <div class="space-y-1">
                <p v-for="(wp, idx) in summary.weak_points" :key="idx" class="text-[14px] text-ink-light flex items-start gap-2">
                  <span class="text-accent flex-shrink-0">·</span>{{ wp }}
                </p>
              </div>
            </div>

            <!-- 推荐学习 -->
            <div v-if="summary.recommendations && summary.recommendations.length" class="glass-card p-5">
              <h4 class="text-[15px] font-semibold text-ink mb-3">推荐学习</h4>
              <div class="space-y-3">
                <div v-for="(rec, idx) in summary.recommendations" :key="idx" class="flex items-start gap-3">
                  <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <span class="text-primary text-[13px] font-semibold">{{ idx + 1 }}</span>
                  </div>
                  <div>
                    <p class="text-[14px] text-ink font-medium">《{{ rec.title }}》<span v-if="rec.author" class="text-ink-light font-normal"> — {{ rec.author }}</span></p>
                    <p v-if="rec.reason" class="text-[13px] text-ink-light mt-0.5">{{ rec.reason }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 鼓励语 -->
            <div v-if="summary.encouragement" class="glass-card-accent p-5 text-center">
              <p class="text-[15px] text-ink poem-body leading-relaxed italic">「{{ summary.encouragement }}」</p>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex gap-3 justify-center">
            <van-button plain size="normal" style="border-radius: 10px" @click="router.back()">返回</van-button>
            <van-button color="#c8851a" size="normal" style="border-radius: 10px" @click="startQuiz">再来一轮</van-button>
          </div>
        </div>

        <!-- 开始页 -->
        <div v-else class="glass-card p-8 text-center">
          <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
            </svg>
          </div>
          <h3 class="text-[20px] font-semibold text-ink mb-2">AI 诗词答题</h3>
          <p class="text-ink-light text-[14px] mb-6">AI 将生成多种题型，全面考验你的诗词知识</p>
          <p class="text-[12px] text-ink-light mb-6">题型包括：诗句填空 · 上下句配对 · 作者识别 · 意境判断</p>
          <van-button color="#c8851a" size="large" style="border-radius: 12px" @click="startQuiz">开始答题</van-button>
        </div>
      </div>
    </div>

    <!-- 底部留白 -->
    <div class="h-12"></div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getAIQuiz, aiExplainAnswer, aiQuizSummary } from '@/api/challenge'
import { useChallengeStore } from '@/stores/challenge'
import Loading from '@/components/common/Loading.vue'
import { showToast } from 'vant'

const router = useRouter()
const challengeStore = useChallengeStore()

const typeLabels = {
  fill_blank: '填空',
  next_line: '上下句',
  author: '作者识别',
  sentiment: '意境判断',
}

const questions = ref([])
const currentIndex = ref(0)
const selected = ref(null)
const answered = ref(false)
const finished = ref(false)
const started = ref(false)
const loading = ref(false)
const correctCount = ref(0)

// AI 解析
const explanation = ref(null)
const explainLoading = ref(false)
const showExplanation = ref(true)

// AI 总结
const summary = ref(null)
const summaryLoading = ref(false)
const summaryLoadingTexts = ['AI 正在分析你的答题表现…', '正在归纳薄弱知识点…', '正在生成学习建议…']
const summaryLoadingText = ref(summaryLoadingTexts[0])

// 加载动画
const loadingTexts = ['AI 正在出题…', '精选诗词题目中…', '构思干扰选项中…']
const loadingText = ref(loadingTexts[0])

const currentQuestion = computed(() => questions.value[currentIndex.value] || null)
const isCorrect = computed(() => selected.value === currentQuestion.value?.answer)

function getOptionClass(idx) {
  if (!answered.value) {
    return selected.value === idx ? 'bg-primary/8 border border-primary' : 'bg-sys-bg-secondary hover:bg-primary/5'
  }
  if (idx === currentQuestion.value?.answer) {
    return 'bg-success/10 border border-success'
  }
  if (selected.value === idx && !isCorrect.value) {
    return 'bg-accent/10 border border-accent'
  }
  return 'bg-sys-bg-secondary opacity-50'
}

function selectOption(idx) {
  if (answered.value) return
  selected.value = idx
  answered.value = true

  const correct = isCorrect.value
  if (correct) {
    correctCount.value++
    challengeStore.recordQuizAnswer(true)
  } else {
    challengeStore.recordQuizAnswer(false)
  }

  // 记录结果用于 AI 总结
  const q = currentQuestion.value
  challengeStore.addQuizResult({
    question: q.question,
    options: q.options,
    answer: q.answer,
    user_answer: idx,
    correct,
    type: q.type || 'fill_blank',
    source: q.source || '',
  })

  // 请求 AI 解析
  fetchExplanation(q, idx)
}

async function fetchExplanation(q, userAnswer) {
  explainLoading.value = true
  explanation.value = null
  try {
    const data = await aiExplainAnswer(q, userAnswer)
    explanation.value = data
  } catch {
    // AI 解析失败，使用题目自带的 explanation
    if (q.explanation) {
      explanation.value = {
        is_correct: isCorrect.value,
        correct_option: q.options[q.answer],
        explanation: q.explanation,
        full_poem: '',
        knowledge: '',
      }
    }
  } finally {
    explainLoading.value = false
  }
}

function nextQuestion() {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
    selected.value = null
    answered.value = false
    explanation.value = null
    showExplanation.value = true
  } else {
    finished.value = true
    fetchSummary()
  }
}

async function fetchSummary() {
  summaryLoading.value = true
  summary.value = null
  let idx = 0
  summaryLoadingText.value = summaryLoadingTexts[0]
  const timer = setInterval(() => {
    idx = (idx + 1) % summaryLoadingTexts.length
    summaryLoadingText.value = summaryLoadingTexts[idx]
  }, 2000)

  try {
    const data = await aiQuizSummary(challengeStore.quizResults)
    summary.value = data
  } catch {
    summary.value = {
      score_comment: correctCount.value >= 4 ? '表现优秀！' : correctCount.value >= 3 ? '表现不错！' : '需要多加练习！',
      weak_points: [],
      recommendations: [],
      encouragement: '每一次练习都是进步，继续坚持吧！',
    }
  } finally {
    summaryLoading.value = false
    clearInterval(timer)
  }
}

async function startQuiz() {
  loading.value = true
  started.value = true
  finished.value = false
  currentIndex.value = 0
  selected.value = null
  answered.value = false
  correctCount.value = 0
  explanation.value = null
  summary.value = null
  challengeStore.resetQuiz()

  let idx = 0
  loadingText.value = loadingTexts[0]
  const timer = setInterval(() => {
    idx = (idx + 1) % loadingTexts.length
    loadingText.value = loadingTexts[idx]
  }, 1500)

  try {
    const data = await getAIQuiz(5)
    questions.value = Array.isArray(data) ? data : []
  } catch {
    questions.value = []
    showToast('出题失败，请稍后再试')
  } finally {
    loading.value = false
    clearInterval(timer)
  }
}
</script>

<style scoped>
.option-item {
  border: 1px solid transparent;
}

/* 题型标签 */
.type-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.type-fill_blank {
  background: rgba(200, 133, 26, 0.10);
  color: #c8851a;
}

.type-next_line {
  background: rgba(52, 199, 89, 0.10);
  color: #34C759;
}

.type-author {
  background: rgba(0, 122, 255, 0.10);
  color: #007AFF;
}

.type-sentiment {
  background: rgba(175, 82, 222, 0.10);
  color: #AF52DE;
}

/* 迷你加载动画 */
.mini-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-top-color: #c8851a;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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

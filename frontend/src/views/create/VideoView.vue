<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- 页面标题 -->
    <div class="content-container pt-6 pb-4">
      <h1 class="text-[24px] lg:text-[32px] font-semibold text-ink tracking-tight">诗境动画</h1>
      <p class="text-ink-light text-[15px] mt-1">以诗词意境生成短视频</p>
    </div>

    <div class="content-container py-4">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 左栏：输入 -->
        <div>
          <div class="glass-card p-5 mb-4">
            <h3 class="text-[15px] font-semibold text-ink mb-3">输入诗词</h3>
            <textarea
              v-model="poemText"
              rows="5"
              placeholder="输入或粘贴一首诗词…&#10;如：床前明月光，疑是地上霜。&#10;举头望明月，低头思故乡。"
              class="w-full bg-sys-bg-secondary rounded-apple p-3.5 text-[15px] text-ink placeholder:text-text-tertiary border-none outline-none resize-none poem-body"
            />
          </div>

          <div class="glass-card p-5 mb-4">
            <h3 class="text-[15px] font-semibold text-ink mb-3">视频设置</h3>

            <div class="mb-3">
              <label class="text-[13px] text-ink-light mb-2 block font-medium">诗词标题（可选）</label>
              <input
                v-model="title"
                placeholder="如：静夜思"
                class="w-full bg-sys-bg-secondary rounded-apple p-3 text-[15px] text-ink placeholder:text-text-tertiary border-none outline-none"
              />
            </div>

            <div>
              <label class="text-[13px] text-ink-light mb-2 block font-medium">视频风格</label>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="s in videoStyles"
                  :key="s"
                  class="tag-item"
                  :class="style === s ? 'tag-active' : ''"
                  @click="style = s"
                >{{ s }}</span>
              </div>
            </div>
          </div>

          <van-button
            block
            color="#c8851a"
            size="large"
            style="border-radius: 12px"
            :disabled="!poemText.trim() || status === 'processing'"
            :loading="submitting"
            :loading-text="submitLoadingText"
            @click="doSubmit"
          >
            生成动画
          </van-button>

          <!-- 其他入口 -->
          <div class="text-center mt-3 mb-4">
            <button class="text-[13px] text-primary font-medium cursor-pointer" @click="router.push('/create/image')">
              诗画互生 →
            </button>
            <span class="text-[13px] text-ink-light mx-2">|</span>
            <button class="text-[13px] text-primary font-medium cursor-pointer" @click="router.push('/create')">
              诗词创作 →
            </button>
          </div>
        </div>

        <!-- 右栏：结果 -->
        <div>
          <!-- 生成中状态 -->
          <div v-if="status === 'processing'" class="glass-card-accent p-8 text-center animate-slide-up">
            <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <div class="video-spinner" />
            </div>
            <h3 class="text-[18px] font-semibold text-ink mb-2">视频生成中</h3>
            <p class="text-ink-light text-[14px] mb-4">{{ pollingText }}</p>

            <!-- 进度提示 -->
            <div class="bg-sys-bg-secondary rounded-apple px-4 py-3 mb-4 text-left">
              <div class="flex items-center gap-2 mb-2">
                <span class="w-2 h-2 rounded-full bg-success animate-pulse" />
                <span class="text-[13px] text-ink">任务已提交</span>
              </div>
              <div class="flex items-center gap-2 mb-2">
                <span class="w-2 h-2 rounded-full" :class="pollCount > 2 ? 'bg-success animate-pulse' : 'bg-sys-bg-tertiary'" />
                <span class="text-[13px]" :class="pollCount > 2 ? 'text-ink' : 'text-ink-light'">AI 解析诗词意境</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full" :class="pollCount > 6 ? 'bg-success animate-pulse' : 'bg-sys-bg-tertiary'" />
                <span class="text-[13px]" :class="pollCount > 6 ? 'text-ink' : 'text-ink-light'">渲染视频画面</span>
              </div>
            </div>

            <!-- Prompt 预览 -->
            <div v-if="promptUsed" class="bg-sys-bg-secondary rounded-apple px-4 py-3 text-left">
              <p class="text-[12px] text-ink-light mb-1 font-medium">AI 画面描述</p>
              <p class="text-[12px] text-ink-light leading-relaxed italic">{{ promptUsed }}</p>
            </div>
          </div>

          <!-- 生成完成 -->
          <div v-else-if="status === 'completed' && videoUrl" class="animate-slide-up">
            <h2 class="text-[20px] font-semibold text-ink mb-4">生成结果</h2>

            <div class="glass-card-accent p-5">
              <!-- 视频播放器 -->
              <div class="video-frame">
                <video
                  ref="videoRef"
                  :src="videoUrl"
                  controls
                  playsinline
                  class="generated-video"
                />
              </div>

              <!-- 原诗 -->
              <div class="mt-4 pt-3 border-t border-sys-divider">
                <p v-if="title" class="poem-title text-[16px] text-ink text-center mb-2">
                  《{{ title }}》
                </p>
                <p class="text-[13px] text-ink-light text-center leading-relaxed poem-body">
                  {{ poemText }}
                </p>
              </div>

              <!-- Prompt 预览 -->
              <div v-if="promptUsed" class="mt-3 bg-sys-bg-secondary rounded-apple px-3 py-2">
                <p class="text-[12px] text-ink-light leading-relaxed italic">{{ promptUsed }}</p>
              </div>

              <!-- 操作按钮 -->
              <div class="flex gap-2 mt-4 pt-3 border-t border-sys-divider">
                <van-button plain size="small" style="border-radius: 10px" @click="downloadVideo">
                  下载视频
                </van-button>
                <van-button plain size="small" style="border-radius: 10px" @click="resetAll">
                  重新生成
                </van-button>
              </div>
            </div>
          </div>

          <!-- 生成失败 -->
          <div v-else-if="status === 'failed'" class="glass-card p-8 text-center animate-slide-up">
            <div class="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-accent" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="15" y1="9" x2="9" y2="15" />
                <line x1="9" y1="9" x2="15" y2="15" />
              </svg>
            </div>
            <h3 class="text-[18px] font-semibold text-ink mb-2">生成失败</h3>
            <p class="text-ink-light text-[14px] mb-4">视频生成未能完成，请稍后重试</p>
            <van-button color="#c8851a" size="normal" style="border-radius: 10px" @click="resetAll">重新生成</van-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部留白 -->
    <div class="h-12"></div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { submitVideoTask, queryVideoStatus } from '@/api/video'
import { showToast } from 'vant'

const router = useRouter()

const videoStyles = ['水墨国风', '青绿山水', '工笔重彩', '写意泼墨']

const poemText = ref('')
const title = ref('')
const style = ref('水墨国风')

const submitting = ref(false)
const status = ref('') // '' | 'processing' | 'completed' | 'failed'
const taskId = ref('')
const videoUrl = ref('')
const promptUsed = ref('')
const pollCount = ref(0)
const videoRef = ref(null)

const submitLoadingTexts = ['正在提交…', 'AI 翻译诗词意境…', '构建画面描述…']
const submitLoadingText = ref(submitLoadingTexts[0])

const pollingTexts = ['AI 正在构思画面…', '渲染诗词意境中…', '水墨晕染流动…', '光影变幻中…', '即将完成…']
const pollingText = ref(pollingTexts[0])

let pollTimer = null
let loadingTimer = null

async function doSubmit() {
  if (!poemText.value.trim() || submitting.value) return

  submitting.value = true
  let idx = 0
  submitLoadingText.value = submitLoadingTexts[0]
  loadingTimer = setInterval(() => {
    idx = (idx + 1) % submitLoadingTexts.length
    submitLoadingText.value = submitLoadingTexts[idx]
  }, 2000)

  try {
    const data = await submitVideoTask({
      poem_text: poemText.value.trim(),
      title: title.value.trim(),
      style: style.value,
    })
    taskId.value = data.task_id
    promptUsed.value = data.prompt_used || ''
    status.value = 'processing'
    pollCount.value = 0
    startPolling()
  } catch {
    showToast('视频生成任务提交失败')
  } finally {
    submitting.value = false
    clearInterval(loadingTimer)
  }
}

function startPolling() {
  stopPolling()
  let textIdx = 0
  pollingText.value = pollingTexts[0]

  pollTimer = setInterval(async () => {
    pollCount.value++
    textIdx = Math.min(Math.floor(pollCount.value / 3), pollingTexts.length - 1)
    pollingText.value = pollingTexts[textIdx]

    try {
      const data = await queryVideoStatus(taskId.value)
      if (data.status === 'completed') {
        videoUrl.value = data.video_url || ''
        status.value = 'completed'
        stopPolling()
      } else if (data.status === 'failed') {
        status.value = 'failed'
        stopPolling()
      }
      // 'processing' — continue polling
    } catch {
      // 网络错误不中断轮询，但设上限
      if (pollCount.value > 60) {
        status.value = 'failed'
        stopPolling()
      }
    }
  }, 5000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function resetAll() {
  stopPolling()
  status.value = ''
  taskId.value = ''
  videoUrl.value = ''
  promptUsed.value = ''
  pollCount.value = 0
}

function downloadVideo() {
  if (!videoUrl.value) return
  const a = document.createElement('a')
  a.href = videoUrl.value
  a.download = `${title.value || '诗境动画'}.mp4`
  a.target = '_blank'
  a.click()
}

onUnmounted(() => {
  stopPolling()
  clearInterval(loadingTimer)
})
</script>

<style scoped>
/* 视频播放器 */
.video-frame {
  border-radius: 12px;
  overflow: hidden;
  background: #1D1D1F;
}

.generated-video {
  width: 100%;
  display: block;
  border-radius: 12px;
}

/* 加载动画 */
.video-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(200, 133, 26, 0.15);
  border-top-color: #c8851a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 渐入动画 */
.animate-slide-up {
  animation: slideUp 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

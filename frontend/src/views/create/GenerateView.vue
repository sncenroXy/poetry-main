<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- 标题 -->
    <div class="content-container pt-6 pb-4">
      <h1 class="text-[28px] lg:text-[36px] font-semibold text-ink tracking-tight">诗词创作</h1>
      <p class="text-ink-light text-[15px] mt-1">描述你的灵感，AI 为你挥毫</p>
    </div>

    <div class="content-container">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 左栏：创作输入 -->
        <div>
          <!-- 自由描述（主要入口） -->
          <div class="glass-card p-5 mb-4">
            <h3 class="text-[15px] font-semibold text-ink mb-3">创作灵感</h3>
            <textarea
              v-model="form.prompt"
              rows="4"
              placeholder="用自然语言描述你想创作的诗词…&#10;例如：写一首关于秋雨夜独坐窗前思念故人的七言绝句&#10;例如：以长江为背景，表达壮志豪情&#10;例如：仿李清照风格写一首关于春天的词"
              class="w-full bg-sys-bg-secondary rounded-apple p-3.5 text-[15px] text-ink placeholder:text-text-tertiary border-none outline-none resize-none leading-relaxed"
            />

            <!-- 灵感提示词 -->
            <div class="mt-3">
              <p class="text-[12px] text-ink-light mb-2">试试这些灵感：</p>
              <div class="flex flex-wrap gap-1.5">
                <span
                  v-for="hint in inspirations"
                  :key="hint"
                  class="inspiration-chip"
                  @click="form.prompt = hint"
                >{{ hint }}</span>
              </div>
            </div>
          </div>

          <!-- 辅助选项（可收起） -->
          <div class="glass-card mb-4 overflow-hidden">
            <button class="w-full flex items-center justify-between p-4 text-left" @click="showOptions = !showOptions">
              <span class="text-[14px] font-medium text-ink-light">辅助选项</span>
              <van-icon :name="showOptions ? 'arrow-up' : 'arrow-down'" size="14" color="#AEAEB2" />
            </button>

            <div v-show="showOptions" class="px-5 pb-5 space-y-4">
              <!-- 风格 -->
              <div>
                <label class="text-[13px] text-ink-light mb-2 block font-medium">诗词风格</label>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="s in styles"
                    :key="s"
                    class="tag-item tag-sm"
                    :class="form.style === s ? 'tag-active' : ''"
                    @click="form.style = form.style === s ? '' : s"
                  >{{ s }}</span>
                </div>
              </div>

              <!-- 情感 -->
              <div>
                <label class="text-[13px] text-ink-light mb-2 block font-medium">情感基调</label>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="e in emotions"
                    :key="e"
                    class="tag-item tag-sm"
                    :class="form.emotion === e ? 'tag-active' : ''"
                    @click="form.emotion = form.emotion === e ? '' : e"
                  >{{ e }}</span>
                </div>
              </div>

              <!-- 意象 -->
              <div>
                <label class="text-[13px] text-ink-light mb-2 block font-medium">融入意象（可多选）</label>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="img in imageOptions"
                    :key="img"
                    class="tag-item tag-sm"
                    :class="form.images.includes(img) ? 'tag-active' : ''"
                    @click="toggleImage(img)"
                  >{{ img }}</span>
                </div>
              </div>

            </div>
          </div>

          <!-- 生成按钮 -->
          <van-button
            block
            color="#c8851a"
            size="large"
            style="border-radius: 12px"
            :disabled="!canGenerate"
            :loading="loading"
            :loading-text="loadingText"
            @click="doGenerate"
          >
            开始创作
          </van-button>

          <!-- 其他入口 -->
          <div class="text-center mt-3 mb-4">
            <button class="text-[13px] text-primary font-medium cursor-pointer" @click="router.push('/create/mimic')">
              进入仿写工坊 →
            </button>
            <span class="text-[13px] text-ink-light mx-2">|</span>
            <button class="text-[13px] text-primary font-medium cursor-pointer" @click="router.push('/create/image')">
              诗画互生 →
            </button>
          </div>
        </div>

        <!-- 右栏：生成结果 -->
        <div v-if="results.length">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-[20px] font-semibold text-ink">生成结果</h2>
          </div>

          <div class="space-y-4 pb-8">
            <div
              v-for="poem in results"
              :key="poem.id"
              class="glass-card-accent p-5 animate-slide-up"
            >
              <h3 class="poem-title text-[20px] text-ink text-center mb-1">{{ poem.title || '无题' }}</h3>
              <p v-if="poem.genre || poem.style" class="text-[12px] text-ink-light text-center mb-4">
                {{ [poem.genre, poem.style].filter(Boolean).join(' · ') }}
              </p>

              <PoemText :poem="poem" />

              <!-- 赏析 -->
              <div v-if="poem.analysis" class="mt-4 pt-3 border-t border-sys-divider">
                <p v-if="poem.analysis.translation" class="text-[13px] text-ink-light mb-2">
                  <span class="font-medium text-ink">译文：</span>{{ poem.analysis.translation }}
                </p>
                <p v-if="poem.analysis.appreciation" class="text-[13px] text-ink-light">
                  <span class="font-medium text-ink">赏析：</span>{{ poem.analysis.appreciation }}
                </p>
              </div>

              <div class="flex gap-2 mt-4 pt-3 border-t border-sys-divider">
                <van-button
                  plain
                  size="small"
                  style="border-radius: 10px"
                  :loading="optimizing === poem.id"
                  @click="doOptimize(poem)"
                >
                  润色
                </van-button>
                <van-button
                  plain
                  size="small"
                  style="border-radius: 10px"
                  @click="sharePoem(poem)"
                >
                  分享
                </van-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { generatePoem, optimizePoem } from '@/api/generate'
import PoemText from '@/components/poetry/PoemText.vue'
import { showToast } from 'vant'

const router = useRouter()

const emotions = ['喜悦', '思乡', '豪迈', '惆怅', '婉约', '闲适', '悲壮', '爱国']
const styles = ['五言绝句', '七言绝句', '五言律诗', '七言律诗', '词', '古风']
const imageOptions = ['明月', '春风', '梅花', '江水', '西风', '雁', '柳', '桂花', '青山', '酒', '落叶', '孤舟']

const inspirations = [
  '写一首中秋望月思乡的五言绝句',
  '以大漠孤烟为意象写一首边塞诗',
  '仿李白风格写一首饮酒豪放之作',
  '描绘江南烟雨中撑伞独行的画面',
  '以落花流水表达离别之情',
  '写一首登高望远抒发壮志的七言律诗',
]

const form = reactive({
  prompt: '',
  emotion: '',
  style: '',
  images: [],
})

const showOptions = ref(false)
const results = ref([])
const loading = ref(false)
const optimizing = ref(null)

const canGenerate = computed(() => {
  return form.prompt.trim() || form.emotion || form.style || form.images.length > 0
})

const loadingTexts = ['正在研墨…', '斟字酌句中…', '灵感涌现中…', '挥毫泼墨中…']
let loadingTextIdx = 0
const loadingText = ref(loadingTexts[0])
let loadingTimer = null

function toggleImage(img) {
  const idx = form.images.indexOf(img)
  if (idx >= 0) {
    form.images.splice(idx, 1)
  } else if (form.images.length < 3) {
    form.images.push(img)
  }
}

async function doGenerate() {
  loading.value = true
  loadingTextIdx = 0
  loadingText.value = loadingTexts[0]
  loadingTimer = setInterval(() => {
    loadingTextIdx = (loadingTextIdx + 1) % loadingTexts.length
    loadingText.value = loadingTexts[loadingTextIdx]
  }, 1200)

  try {
    const params = { count: 1 }
    if (form.prompt.trim()) params.prompt = form.prompt.trim()
    if (form.style) params.style = form.style
    if (form.emotion) params.emotion = form.emotion
    if (form.images.length) params.images = form.images

    const data = await generatePoem(params)
    results.value = Array.isArray(data) ? data : [data]
  } catch {
    showToast('生成失败，请稍后再试')
  } finally {
    loading.value = false
    clearInterval(loadingTimer)
  }
}

async function doOptimize(poem) {
  optimizing.value = poem.id
  try {
    const data = await optimizePoem(poem.id)
    const idx = results.value.findIndex(p => p.id === poem.id)
    if (idx >= 0) results.value[idx] = data
    showToast('润色完成')
  } catch {
    showToast('润色失败')
  } finally {
    optimizing.value = null
  }
}

function sharePoem(poem) {
  const lines = Array.isArray(poem.content) ? poem.content.join('\n') : (poem.content || '')
  const text = `《${poem.title || '无题'}》\n${lines}\n—— 来自诗词雅韵`
  if (navigator.share) {
    navigator.share({ title: poem.title, text })
  } else {
    navigator.clipboard?.writeText(text).then(() => showToast('已复制到剪贴板'))
  }
}
</script>

<style scoped>
.inspiration-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 12px;
  background: rgba(200, 133, 26, 0.08);
  color: #c8851a;
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
}

.inspiration-chip:hover {
  background: rgba(200, 133, 26, 0.15);
}

.inspiration-chip:active {
  transform: scale(0.96);
}

.tag-sm {
  padding: 4px 12px;
  font-size: 13px;
}

.animate-slide-up {
  animation: slideUp 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

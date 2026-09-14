<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- 页面标题 -->
    <div class="content-container pt-6 pb-4 px-5 lg:px-0">
      <h1 class="text-[24px] lg:text-[32px] font-semibold text-ink tracking-tight">诗境漫游</h1>
      <p class="text-ink-light text-[14px] mt-1">探索诗词意象，解读文化密码</p>
    </div>

    <div class="content-container px-5 lg:px-0">
      <!-- 输入区 -->
      <!-- 加载中（全页） -->
      <div v-if="loading" class="loading-section animate-fade-in">
        <div class="loading-card">
          <div class="loading-compass">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-10 h-10 text-primary">
              <circle cx="12" cy="12" r="10" /><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
            </svg>
          </div>
          <p class="text-[16px] font-semibold text-ink mt-4">正在解读意境</p>
          <p class="text-[13px] text-ink-light mt-1">AI 正在深度分析诗词意象，{{ elapsedText }}</p>
          <div class="loading-bar mt-4"><div class="loading-bar-inner"></div></div>
          <p v-if="poemTitle" class="text-[14px] text-ink-light mt-4 poem-body">{{ poemTitle }}</p>
        </div>
      </div>

      <div v-if="!result && !loading" class="input-section">
        <div class="glass-card p-5 mb-4">
          <h3 class="text-[15px] font-semibold text-ink mb-3">输入诗词</h3>
          <textarea
            v-model="poemText"
            rows="5"
            placeholder="输入或粘贴一首诗词…&#10;如：床前明月光，疑是地上霜。&#10;举头望明月，低头思故乡。"
            class="w-full bg-sys-bg-secondary rounded-apple p-3.5 text-[15px] text-ink placeholder:text-text-tertiary border-none outline-none resize-none poem-body"
          />
        </div>

        <div class="grid grid-cols-2 gap-3 mb-5">
          <div class="glass-card p-4">
            <label class="text-[12px] text-ink-light mb-1.5 block font-medium">诗词标题</label>
            <input
              v-model="poemTitle"
              placeholder="如：静夜思"
              class="w-full bg-sys-bg-secondary rounded-[10px] p-2.5 text-[14px] text-ink placeholder:text-text-tertiary border-none outline-none"
            />
          </div>
          <div class="glass-card p-4">
            <label class="text-[12px] text-ink-light mb-1.5 block font-medium">作者</label>
            <input
              v-model="poemAuthor"
              placeholder="如：李白"
              class="w-full bg-sys-bg-secondary rounded-[10px] p-2.5 text-[14px] text-ink placeholder:text-text-tertiary border-none outline-none"
            />
          </div>
        </div>

        <!-- 快捷示例 -->
        <div class="mb-5">
          <p class="text-[12px] text-ink-light mb-2">或选择示例：</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="ex in examples"
              :key="ex.title"
              class="example-tag"
              @click="loadExample(ex)"
            >{{ ex.title }}</button>
          </div>
        </div>

        <button
          class="explore-btn w-full"
          :disabled="!poemText.trim()"
          @click="startAnalysis"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
            <circle cx="12" cy="12" r="10" /><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
          </svg>
          开始探索
        </button>
      </div>

      <!-- 结果区 -->
      <div v-if="result" class="result-section animate-fade-in">
        <!-- 顶部信息栏 -->
        <div class="result-header mb-4">
          <div>
            <h2 v-if="poemTitle" class="text-[18px] font-semibold text-ink">{{ poemTitle }}</h2>
            <p class="text-[13px] text-ink-light mt-0.5">{{ result.poem_summary }}</p>
          </div>
          <button class="reset-btn" @click="resetAll" title="重新分析">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
              <polyline points="1 4 1 10 7 10" /><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
            </svg>
            重新分析
          </button>
        </div>

        <!-- 诗词原文 -->
        <div class="poem-original-card mb-5">
          <p
            v-for="(line, idx) in poemText.split('\n').filter(l => l.trim())"
            :key="idx"
            class="poem-body text-[16px] text-ink leading-[2.2] text-center"
          >{{ line }}</p>
          <p v-if="poemAuthor" class="text-[13px] text-ink-light text-center mt-2">— {{ poemAuthor }}</p>
        </div>

        <!-- 星图 + 详情 双栏布局 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 pb-8">
          <div>
            <h3 class="text-[14px] font-semibold text-ink mb-3">意境星图</h3>
            <ImageryStarMap
              :nodes="result.imagery_nodes"
              :title="poemTitle"
              :selected-node="selectedNode?.name || ''"
              @select="selectNode"
            />
          </div>
          <div>
            <h3 class="text-[14px] font-semibold text-ink mb-3">意象详情</h3>
            <ImageryDetail
              :node="selectedNode"
              @close="selectedNode = null"
              @go-poem="goRelatedPoem"
            />
            <div v-if="!selectedNode" class="empty-detail">
              <p class="text-[13px] text-text-tertiary">点击星图中的意象节点，探索其文化含义</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { analyzeImagery } from '@/api/imagery'
import ImageryStarMap from '@/components/imagery/ImageryStarMap.vue'
import ImageryDetail from '@/components/imagery/ImageryDetail.vue'

const route = useRoute()
const router = useRouter()

const poemText = ref('')
const poemTitle = ref('')
const poemAuthor = ref('')
const loading = ref(false)
const result = ref(null)
const selectedNode = ref(null)
const elapsedSeconds = ref(0)
let elapsedTimer = null

const elapsedText = computed(() => {
  const s = elapsedSeconds.value
  if (s < 10) return '请稍候…'
  if (s < 30) return `已用时 ${s} 秒…`
  return `已用时 ${s} 秒，即将完成…`
})

const examples = [
  { title: '静夜思', author: '李白', text: '床前明月光\n疑是地上霜\n举头望明月\n低头思故乡' },
  { title: '春晓', author: '孟浩然', text: '春眠不觉晓\n处处闻啼鸟\n夜来风雨声\n花落知多少' },
  { title: '登鹳雀楼', author: '王之涣', text: '白日依山尽\n黄河入海流\n欲穷千里目\n更上一层楼' },
  { title: '枫桥夜泊', author: '张继', text: '月落乌啼霜满天\n江枫渔火对愁眠\n姑苏城外寒山寺\n夜半钟声到客船' },
]

function loadExample(ex) {
  poemText.value = ex.text
  poemTitle.value = ex.title
  poemAuthor.value = ex.author
}

// 从 URL query 自动填充
onMounted(() => {
  if (route.query.poem) {
    poemText.value = route.query.poem
    poemTitle.value = route.query.title || ''
    poemAuthor.value = route.query.author || ''
    startAnalysis()
  }
})

onUnmounted(() => {
  if (elapsedTimer) clearInterval(elapsedTimer)
})

async function startAnalysis() {
  if (!poemText.value.trim() || loading.value) return
  loading.value = true
  selectedNode.value = null
  result.value = null
  elapsedSeconds.value = 0
  elapsedTimer = setInterval(() => { elapsedSeconds.value++ }, 1000)

  try {
    const data = await analyzeImagery({
      poem_text: poemText.value.trim(),
      title: poemTitle.value.trim(),
      author: poemAuthor.value.trim(),
    })
    result.value = data
  } catch (err) {
    console.error('[Imagery] 分析请求失败:', err)
    result.value = {
      poem_summary: '分析失败，请稍后再试。',
      imagery_nodes: [],
    }
  } finally {
    clearInterval(elapsedTimer)
    elapsedTimer = null
    loading.value = false
  }
}

function selectNode(node) {
  selectedNode.value = selectedNode.value?.name === node.name ? null : node
}

function resetAll() {
  result.value = null
  selectedNode.value = null
}

function goRelatedPoem(poem) {
  router.push(`/search?q=${encodeURIComponent(poem.title + ' ' + poem.author)}`)
}
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 14px;
  border: 0.5px solid rgba(0, 0, 0, 0.04);
}

.example-tag {
  padding: 5px 12px;
  border-radius: 16px;
  font-size: 13px;
  color: #6E6E73;
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.15s ease;
}

.example-tag:hover {
  background: rgba(200, 133, 26, 0.06);
  color: #c8851a;
  border-color: rgba(200, 133, 26, 0.2);
}

.explore-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 0;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #c8851a, #d4922e);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 16px rgba(200, 133, 26, 0.25);
}

.explore-btn:hover:not(:disabled) {
  box-shadow: 0 6px 24px rgba(200, 133, 26, 0.35);
}

.explore-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 加载中 */
.loading-section {
  display: flex;
  justify-content: center;
  padding: 40px 0 60px;
}

.loading-card {
  text-align: center;
  padding: 40px 32px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 20px;
  border: 0.5px solid rgba(0, 0, 0, 0.04);
  max-width: 360px;
  width: 100%;
}

.loading-compass {
  display: inline-flex;
  animation: compassSpin 3s ease-in-out infinite;
}

@keyframes compassSpin {
  0% { transform: rotate(0deg); }
  25% { transform: rotate(90deg); }
  50% { transform: rotate(180deg); }
  75% { transform: rotate(270deg); }
  100% { transform: rotate(360deg); }
}

.loading-bar {
  height: 3px;
  border-radius: 2px;
  background: rgba(200, 133, 26, 0.1);
  overflow: hidden;
}

.loading-bar-inner {
  height: 100%;
  border-radius: 2px;
  background: linear-gradient(90deg, #c8851a, #d4922e);
  animation: loadingSlide 2s ease-in-out infinite;
  width: 40%;
}

@keyframes loadingSlide {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(350%); }
}

/* 结果区 */
.result-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.reset-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  color: #6E6E73;
  background: rgba(0, 0, 0, 0.03);
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.reset-btn:hover {
  background: rgba(0, 0, 0, 0.06);
  color: #1D1D1F;
}

.poem-original-card {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.8), rgba(245, 214, 138, 0.08));
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 14px;
  padding: 20px;
  border: 0.5px solid rgba(200, 133, 26, 0.1);
}

.empty-detail {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 14px;
  border: 1px dashed rgba(0, 0, 0, 0.08);
}
</style>

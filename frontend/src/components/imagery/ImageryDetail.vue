<template>
  <transition name="slide-up">
    <div v-if="node" class="detail-panel">
      <!-- 标题栏 -->
      <div class="detail-header">
        <div class="flex items-center gap-2.5">
          <span class="detail-node-name">{{ node.name }}</span>
          <span class="detail-category">{{ node.category }}</span>
        </div>
        <button class="close-btn" @click="$emit('close')">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <p class="text-[13px] text-ink-light mb-3">{{ node.significance }}</p>

      <!-- Tab 切换 -->
      <div class="tab-bar">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >{{ tab.label }}</button>
      </div>

      <!-- Tab 内容 -->
      <div class="tab-content">
        <!-- 文化含义 -->
        <div v-if="activeTab === 'meaning'" class="meaning-content">
          <p class="text-[14px] text-ink leading-[1.8]">{{ node.cultural_meaning }}</p>
        </div>

        <!-- 关联诗句 -->
        <div v-if="activeTab === 'poems'" class="poems-content">
          <div
            v-for="(poem, idx) in node.related_poems"
            :key="idx"
            class="related-poem-card"
            @click="$emit('go-poem', poem)"
          >
            <p class="poem-quote">「{{ poem.quote }}」</p>
            <p class="poem-source">
              {{ poem.author }}
              <span class="text-text-tertiary">· {{ poem.dynasty }}</span>
              《{{ poem.title }}》
            </p>
          </div>
          <div v-if="!node.related_poems?.length" class="text-[13px] text-text-tertiary text-center py-6">
            暂无关联诗句
          </div>
        </div>

        <!-- 意境配图 -->
        <div v-if="activeTab === 'image'" class="image-content">
          <div v-if="!generatedImage && !imageLoading" class="image-placeholder">
            <p class="text-[13px] text-ink-light mb-3">AI 将为「{{ node.name }}」意象生成一幅国风画作</p>
            <button class="generate-btn" @click="generateImage">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
              生成意境配图
            </button>
          </div>

          <div v-if="imageLoading" class="image-loading">
            <div class="typing-dots">
              <span></span><span></span><span></span>
            </div>
            <p class="text-[12px] text-ink-light mt-2">正在绘制…</p>
          </div>

          <div v-if="generatedImage" class="image-result">
            <img :src="generatedImage" alt="意境配图" class="generated-img" />
          </div>

          <div v-if="imageError" class="text-[13px] text-accent text-center py-4">
            {{ imageError }}
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import request from '@/api/index'

const props = defineProps({
  node: { type: Object, default: null },
})

defineEmits(['close', 'go-poem'])

const tabs = [
  { key: 'meaning', label: '文化含义' },
  { key: 'poems', label: '关联诗句' },
  { key: 'image', label: '意境配图' },
]

const activeTab = ref('meaning')
const generatedImage = ref('')
const imageLoading = ref(false)
const imageError = ref('')

// 切换节点时重置状态
watch(() => props.node?.name, () => {
  activeTab.value = 'meaning'
  generatedImage.value = ''
  imageError.value = ''
  imageLoading.value = false
})

async function generateImage() {
  if (!props.node) return
  imageLoading.value = true
  imageError.value = ''

  try {
    const prompt = `${props.node.name} — ${props.node.significance}`
    const data = await request.post('/image/generate', {
      poem_text: prompt,
      title: props.node.name,
      style: '水墨国风',
    }, { timeout: 120000 })

    generatedImage.value = data?.url || data?.image_url || ''
    if (!generatedImage.value) {
      imageError.value = '图片生成失败，请稍后再试'
    }
  } catch {
    imageError.value = '图片生成服务暂不可用'
  } finally {
    imageLoading.value = false
  }
}
</script>

<style scoped>
.detail-panel {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 20px;
  border: 0.5px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

/* 过渡动画 */
.slide-up-enter-active { transition: all 0.3s ease; }
.slide-up-leave-active { transition: all 0.2s ease; }
.slide-up-enter-from { opacity: 0; transform: translateY(16px); }
.slide-up-leave-to { opacity: 0; transform: translateY(8px); }

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.detail-node-name {
  font-family: 'Noto Serif SC', 'KaiTi', '楷体', serif;
  font-size: 20px;
  font-weight: 600;
  color: #1D1D1F;
}

.detail-category {
  font-size: 11px;
  font-weight: 500;
  color: #c8851a;
  padding: 2px 8px;
  background: rgba(200, 133, 26, 0.08);
  border-radius: 8px;
}

.close-btn {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: none;
  background: rgba(0, 0, 0, 0.04);
  color: #AEAEB2;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.08);
  color: #6E6E73;
}

/* Tab 栏 */
.tab-bar {
  display: flex;
  gap: 4px;
  padding: 3px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 10px;
  margin-bottom: 16px;
}

.tab-btn {
  flex: 1;
  padding: 7px 0;
  border-radius: 8px;
  font-size: 13px;
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
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

/* 内容区 */
.tab-content {
  min-height: 120px;
}

.meaning-content {
  font-family: 'Noto Serif SC', 'KaiTi', '楷体', serif;
}

/* 关联诗句卡片 */
.related-poem-card {
  padding: 12px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.02);
  border: 0.5px solid rgba(0, 0, 0, 0.04);
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.related-poem-card:hover {
  background: rgba(200, 133, 26, 0.05);
  border-color: rgba(200, 133, 26, 0.12);
}

.poem-quote {
  font-family: 'Noto Serif SC', 'KaiTi', '楷体', serif;
  font-size: 15px;
  color: #1D1D1F;
  line-height: 1.8;
  margin-bottom: 4px;
}

.poem-source {
  font-size: 12px;
  color: #6E6E73;
}

/* 配图区 */
.image-placeholder {
  text-align: center;
  padding: 24px 0;
}

.generate-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 22px;
  font-size: 14px;
  font-weight: 500;
  color: white;
  background: linear-gradient(135deg, #c8851a, #d4922e);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(200, 133, 26, 0.25);
}

.generate-btn:hover {
  background: linear-gradient(135deg, #b5760f, #c8851a);
}

.generate-btn:active {
  transform: scale(0.97);
}

.image-loading {
  text-align: center;
  padding: 32px 0;
}

.typing-dots {
  display: inline-flex;
  gap: 4px;
  align-items: center;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c8851a;
  opacity: 0.35;
  animation: bounce 1.2s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 60%, 100% { opacity: 0.35; transform: translateY(0); }
  30% { opacity: 1; transform: translateY(-4px); }
}

.generated-img {
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}
</style>

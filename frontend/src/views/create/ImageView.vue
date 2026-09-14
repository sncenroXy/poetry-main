<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- 页面标题 -->
    <div class="content-container pt-6 pb-4">
      <h1 class="text-[24px] lg:text-[32px] font-semibold text-ink tracking-tight">诗画互生</h1>
      <p class="text-ink-light text-[15px] mt-1">以诗绘画，以画赋诗</p>
    </div>

    <!-- Tab 切换 -->
    <div class="content-container pb-4">
      <div class="tab-bar">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'text2img' }"
          @click="activeTab = 'text2img'"
        >以诗绘画</button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'img2text' }"
          @click="activeTab = 'img2text'"
        >以画赋诗</button>
      </div>
    </div>

    <!-- 文生图 Tab -->
    <div v-show="activeTab === 'text2img'" class="content-container">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 左栏：输入 -->
        <div>
          <div class="glass-card p-5 mb-4">
            <h3 class="text-[15px] font-semibold text-ink mb-3">输入诗词</h3>
            <textarea
              v-model="t2i.poemText"
              rows="5"
              placeholder="输入或粘贴一首诗词…&#10;如：床前明月光，疑是地上霜。&#10;举头望明月，低头思故乡。"
              class="w-full bg-sys-bg-secondary rounded-apple p-3.5 text-[15px] text-ink placeholder:text-text-tertiary border-none outline-none resize-none poem-body"
            />
          </div>

          <div class="glass-card p-5 mb-4">
            <h3 class="text-[15px] font-semibold text-ink mb-3">配图设置</h3>

            <div class="mb-3">
              <label class="text-[13px] text-ink-light mb-2 block font-medium">诗词标题（可选）</label>
              <input
                v-model="t2i.title"
                placeholder="如：静夜思"
                class="w-full bg-sys-bg-secondary rounded-apple p-3 text-[15px] text-ink placeholder:text-text-tertiary border-none outline-none"
              />
            </div>

            <div>
              <label class="text-[13px] text-ink-light mb-2 block font-medium">画风</label>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="s in imageStyles"
                  :key="s"
                  class="tag-item"
                  :class="t2i.style === s ? 'tag-active' : ''"
                  @click="t2i.style = s"
                >{{ s }}</span>
              </div>
            </div>
          </div>

          <van-button
            block
            color="#c8851a"
            size="large"
            style="border-radius: 12px"
            :disabled="!t2i.poemText.trim()"
            :loading="t2i.loading"
            :loading-text="t2i.loadingText"
            @click="doGenerateImage"
          >
            生成配图
          </van-button>

          <!-- 其他入口 -->
          <div class="text-center mt-3 mb-4">
            <button class="text-[13px] text-primary font-medium cursor-pointer" @click="router.push('/create')">
              诗词创作 →
            </button>
            <span class="text-[13px] text-ink-light mx-2">|</span>
            <button class="text-[13px] text-primary font-medium cursor-pointer" @click="router.push('/create/mimic')">
              仿写工坊 →
            </button>
          </div>
        </div>

        <!-- 右栏：结果 -->
        <div v-if="t2i.result">
          <h2 class="text-[20px] font-semibold text-ink mb-4">生成配图</h2>

          <div class="glass-card-accent p-5 animate-slide-up">
            <!-- 图片展示 -->
            <div class="image-frame">
              <img :src="t2i.result.image_url" :alt="t2i.result.title || '诗词配图'" class="generated-image" />
            </div>

            <!-- 原诗 -->
            <div class="mt-4 pt-3 border-t border-sys-divider">
              <p v-if="t2i.result.title" class="poem-title text-[16px] text-ink text-center mb-2">
                《{{ t2i.result.title }}》
              </p>
              <p class="text-[13px] text-ink-light text-center leading-relaxed poem-body">
                {{ t2i.result.poem_text }}
              </p>
            </div>

            <!-- 操作按钮 -->
            <div class="flex gap-2 mt-4 pt-3 border-t border-sys-divider">
              <van-button plain size="small" style="border-radius: 10px" @click="downloadImage">
                下载图片
              </van-button>
              <van-button plain size="small" style="border-radius: 10px" @click="t2i.result = null">
                清除
              </van-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图生文 Tab -->
    <div v-show="activeTab === 'img2text'" class="content-container">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 左栏：上传图片 -->
        <div>
          <div class="glass-card p-5 mb-4">
            <h3 class="text-[15px] font-semibold text-ink mb-3">上传图片</h3>

            <!-- 上传区域 -->
            <div
              class="upload-zone"
              :class="{ 'has-image': i2t.preview }"
              @click="triggerUpload"
              @dragover.prevent
              @drop.prevent="handleDrop"
            >
              <img v-if="i2t.preview" :src="i2t.preview" alt="预览" class="upload-preview" />
              <div v-else class="upload-placeholder">
                <van-icon name="photograph" size="40" color="#AEAEB2" />
                <p class="text-[14px] text-ink-light mt-2">点击或拖拽上传图片</p>
                <p class="text-[12px] text-text-tertiary mt-1">支持 JPG、PNG 格式</p>
              </div>
            </div>
            <input
              ref="fileInput"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              class="hidden"
              @change="handleFileSelect"
            />

            <!-- 清除按钮 -->
            <div v-if="i2t.preview" class="text-right mt-2">
              <button class="text-[13px] text-ink-light cursor-pointer" @click="clearUpload">清除图片</button>
            </div>
          </div>

          <!-- 偏好设置 -->
          <div class="glass-card p-5 mb-4">
            <h3 class="text-[15px] font-semibold text-ink mb-3">创作偏好（可选）</h3>

            <div class="mb-3">
              <label class="text-[13px] text-ink-light mb-2 block font-medium">诗词风格</label>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="s in poemStyles"
                  :key="s"
                  class="tag-item"
                  :class="i2t.style === s ? 'tag-active' : ''"
                  @click="i2t.style = s"
                >{{ s }}</span>
              </div>
            </div>

            <div>
              <label class="text-[13px] text-ink-light mb-2 block font-medium">情感基调</label>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="e in emotions"
                  :key="e"
                  class="tag-item"
                  :class="i2t.emotion === e ? 'tag-active' : ''"
                  @click="i2t.emotion = i2t.emotion === e ? '' : e"
                >{{ e }}</span>
              </div>
            </div>
          </div>

          <van-button
            block
            color="#c8851a"
            size="large"
            style="border-radius: 12px"
            :disabled="!i2t.imageBase64"
            :loading="i2t.loading"
            :loading-text="i2t.loadingText"
            @click="doGeneratePoem"
          >
            以画赋诗
          </van-button>
        </div>

        <!-- 右栏：诗词结果 -->
        <div v-if="i2t.result">
          <h2 class="text-[20px] font-semibold text-ink mb-4">赋诗成果</h2>

          <div class="glass-card-accent p-5 animate-slide-up">
            <!-- 场景描述 -->
            <p v-if="i2t.result.scene_description" class="text-[13px] text-ink-light text-center mb-4 italic">
              「{{ i2t.result.scene_description }}」
            </p>

            <!-- 诗词展示 -->
            <PoemText :poem="i2t.result.poem" />

            <!-- 赏析 -->
            <div v-if="i2t.result.poem?.analysis" class="mt-4 pt-3 border-t border-sys-divider">
              <p v-if="i2t.result.poem.analysis.translation" class="text-[13px] text-ink-light mb-2">
                <span class="font-medium text-ink">译文：</span>{{ i2t.result.poem.analysis.translation }}
              </p>
              <p v-if="i2t.result.poem.analysis.appreciation" class="text-[13px] text-ink-light">
                <span class="font-medium text-ink">赏析：</span>{{ i2t.result.poem.analysis.appreciation }}
              </p>
            </div>

            <!-- 操作按钮 -->
            <div class="flex gap-2 mt-4 pt-3 border-t border-sys-divider">
              <van-button plain size="small" style="border-radius: 10px" @click="sharePoem">
                分享
              </van-button>
              <van-button plain size="small" style="border-radius: 10px" @click="i2t.result = null">
                清除
              </van-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部留白 -->
    <div class="h-12"></div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { generateImage, generatePoemFromImage } from '@/api/image'
import PoemText from '@/components/poetry/PoemText.vue'
import { showToast } from 'vant'

const router = useRouter()

const activeTab = ref('text2img')

const imageStyles = ['水墨国风', '工笔花鸟', '青绿山水', '写意泼墨']
const poemStyles = ['唐诗', '宋词', '古风']
const emotions = ['思乡', '喜悦', '豪迈', '惆怅', '婉约', '闲适']

// ===== 文生图 =====
const t2i = reactive({
  poemText: '',
  title: '',
  style: '水墨国风',
  loading: false,
  loadingText: '正在绘制…',
  result: null,
})

const t2iLoadingTexts = ['正在绘制…', '渲染意境中…', '水墨晕染中…', '即将呈现…']

async function doGenerateImage() {
  if (!t2i.poemText.trim()) return
  t2i.loading = true
  let idx = 0
  t2i.loadingText = t2iLoadingTexts[0]
  const timer = setInterval(() => {
    idx = (idx + 1) % t2iLoadingTexts.length
    t2i.loadingText = t2iLoadingTexts[idx]
  }, 2000)

  try {
    const data = await generateImage({
      poem_text: t2i.poemText.trim(),
      title: t2i.title.trim(),
      style: t2i.style,
    })
    t2i.result = data
  } catch {
    showToast('图片生成失败，请稍后再试')
  } finally {
    t2i.loading = false
    clearInterval(timer)
  }
}

function downloadImage() {
  if (!t2i.result?.image_url) return
  const a = document.createElement('a')
  a.href = t2i.result.image_url
  a.download = `${t2i.result.title || '诗词配图'}.png`
  a.target = '_blank'
  a.click()
}

// ===== 图生文 =====
const fileInput = ref(null)
const i2t = reactive({
  preview: '',
  imageBase64: '',
  style: '古风',
  emotion: '',
  loading: false,
  loadingText: '赋诗中…',
  result: null,
})

const i2tLoadingTexts = ['观画品意中…', '赋诗中…', '斟字酌句中…', '灵感涌现中…']

function triggerUpload() {
  fileInput.value?.click()
}

function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (file) processFile(file)
}

function handleDrop(e) {
  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) processFile(file)
}

function processFile(file) {
  if (file.size > 10 * 1024 * 1024) {
    showToast('图片大小不能超过 10MB')
    return
  }
  const reader = new FileReader()
  reader.onload = (e) => {
    i2t.preview = e.target.result
    i2t.imageBase64 = e.target.result
  }
  reader.readAsDataURL(file)
}

function clearUpload() {
  i2t.preview = ''
  i2t.imageBase64 = ''
  i2t.result = null
  if (fileInput.value) fileInput.value.value = ''
}

async function doGeneratePoem() {
  if (!i2t.imageBase64) return
  i2t.loading = true
  let idx = 0
  i2t.loadingText = i2tLoadingTexts[0]
  const timer = setInterval(() => {
    idx = (idx + 1) % i2tLoadingTexts.length
    i2t.loadingText = i2tLoadingTexts[idx]
  }, 1500)

  try {
    const data = await generatePoemFromImage({
      image: i2t.imageBase64,
      style: i2t.style,
      emotion: i2t.emotion,
    })
    i2t.result = data
  } catch {
    showToast('诗词生成失败，请稍后再试')
  } finally {
    i2t.loading = false
    clearInterval(timer)
  }
}

function sharePoem() {
  const poem = i2t.result?.poem
  if (!poem) return
  const text = `《${poem.title || '无题'}》\n${(poem.content || []).join('\n')}\n—— 来自诗词雅韵`
  if (navigator.share) {
    navigator.share({ title: poem.title, text })
  } else {
    navigator.clipboard?.writeText(text).then(() => showToast('已复制到剪贴板'))
  }
}
</script>

<style scoped>
/* Tab 切换栏 */
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

/* 上传区域 */
.upload-zone {
  border: 2px dashed rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-zone:hover {
  border-color: #c8851a;
  background: rgba(200, 133, 26, 0.03);
}

.upload-zone.has-image {
  padding: 8px;
  border-style: solid;
  border-color: rgba(0, 0, 0, 0.06);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-preview {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
  border-radius: 12px;
}

/* 生成图片展示 */
.image-frame {
  border-radius: 12px;
  overflow: hidden;
  background: #F2F1EF;
}

.generated-image {
  width: 100%;
  display: block;
  border-radius: 12px;
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

<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- 页面标题 -->
    <div class="content-container pt-6 pb-4">
      <h1 class="text-[24px] lg:text-[32px] font-semibold text-ink tracking-tight">仿写工坊</h1>
      <p class="text-ink-light text-[15px] mt-1">参考原诗，AI 仿写新篇</p>
    </div>

    <div class="content-container py-2">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 左栏：输入 -->
        <div>
          <!-- 输入原文 -->
          <div class="glass-card p-5 mb-4">
            <h3 class="text-[15px] font-semibold text-ink mb-3">输入参考诗词或草稿</h3>
            <textarea
              v-model="draft"
              rows="4"
              placeholder="粘贴一首诗词，或写下你的创作草稿…"
              class="w-full bg-sys-bg-secondary rounded-apple p-3.5 text-[15px] text-ink placeholder:text-text-tertiary border-none outline-none resize-none"
            />
          </div>

          <!-- 调整参数 -->
          <div class="glass-card p-5 mb-4">
            <h3 class="text-[15px] font-semibold text-ink mb-3">仿写风格（可选）</h3>

            <div class="mb-3">
              <label class="text-[13px] text-ink-light mb-2 block font-medium">情感</label>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="e in emotions"
                  :key="e"
                  class="tag-item"
                  :class="emotion === e ? 'tag-active' : ''"
                  @click="emotion = emotion === e ? '' : e"
                >{{ e }}</span>
              </div>
            </div>

            <div>
              <label class="text-[13px] text-ink-light mb-2 block font-medium">风格</label>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="s in styles"
                  :key="s"
                  class="tag-item"
                  :class="style === s ? 'tag-active' : ''"
                  @click="style = style === s ? '' : s"
                >{{ s }}</span>
              </div>
            </div>
          </div>

          <!-- 仿写按钮 -->
          <van-button
            block
            color="#c8851a"
            size="large"
            style="border-radius: 12px"
            :disabled="!draft.trim()"
            :loading="loading"
            @click="doMimic"
          >
            开始仿写
          </van-button>

          <!-- 其他入口 -->
          <div class="text-center mt-3 mb-4">
            <button class="text-[13px] text-primary font-medium cursor-pointer" @click="router.push('/create')">
              诗词创作 →
            </button>
            <span class="text-[13px] text-ink-light mx-2">|</span>
            <button class="text-[13px] text-primary font-medium cursor-pointer" @click="router.push('/create/image')">
              诗画互生 →
            </button>
          </div>
        </div>

        <!-- 右栏：仿写结果 -->
        <div v-if="result">
          <h2 class="text-[20px] font-semibold text-ink mb-4">仿写成果</h2>

          <div class="glass-card-accent p-5 animate-slide-up">
            <PoemText :poem="result" />

            <div class="flex gap-2 mt-4 pt-3 border-t border-sys-divider">
              <van-button plain size="small" style="border-radius: 10px" @click="sharePoem">分享</van-button>
              <van-button plain size="small" style="border-radius: 10px" @click="result = null">清除</van-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { mimicPoem } from '@/api/generate'
import PoemText from '@/components/poetry/PoemText.vue'
import { showToast } from 'vant'

const router = useRouter()

const emotions = ['思乡', '喜悦', '豪迈', '惆怅', '婉约', '闲适']
const styles = ['唐诗', '宋词', '古风']

const draft = ref('')
const emotion = ref('思乡')
const style = ref('唐诗')
const result = ref(null)
const loading = ref(false)

async function doMimic() {
  if (!draft.value.trim()) return
  loading.value = true
  try {
    const data = await mimicPoem({
      draft: draft.value.trim(),
      emotion: emotion.value,
      style: style.value
    })
    result.value = data
  } catch {
    showToast('仿写失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

function sharePoem() {
  if (!result.value) return
  const lines = Array.isArray(result.value.content) ? result.value.content.join('\n') : (result.value.content || '')
  const text = `《${result.value.title || '无题'}》\n${lines}\n—— 来自诗词雅韵`
  if (navigator.share) {
    navigator.share({ title: result.value.title, text })
  } else {
    navigator.clipboard?.writeText(text).then(() => showToast('已复制到剪贴板'))
  }
}
</script>

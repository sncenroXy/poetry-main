<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- 页面标题 -->
    <div class="content-container pt-4 pb-3 flex items-center gap-3">
      <button class="text-ink-light lg:hidden" @click="router.back()">
        <van-icon name="arrow-left" size="20" />
      </button>
      <h1 class="text-[17px] lg:text-[24px] font-semibold text-ink">{{ poem?.title || '鉴赏' }}</h1>
    </div>

    <Loading v-if="loading" text="正在加载…" />

    <div v-else-if="poem" class="animate-fade-in">
      <!-- 诗词正文 -->
      <div class="content-container py-4">
        <div class="reading-container">
          <div class="glass-card-accent p-6 lg:p-8">
            <PoemText :poem="poem" @author-click="goAuthor" />
          </div>
        </div>
      </div>

      <div class="reading-container">
        <div class="divider-brush mx-8" />
      </div>

      <!-- 赏析与文化拓展 -->
      <div class="content-container pb-6">
        <div class="reading-container">
          <AnalysisPanel :poem="poem" />
        </div>
      </div>

      <!-- 探索意境入口 -->
      <div class="content-container pb-20">
        <div class="reading-container">
          <button class="imagery-btn" @click="goImagery">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
              <circle cx="12" cy="12" r="10" /><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
            </svg>
            探索意境
            <span class="imagery-btn-sub">AI 解读诗词意象图谱</span>
          </button>
        </div>
      </div>
    </div>

    <EmptyState v-else message="诗词不存在" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPoemDetail } from '@/api/poem'
import { usePoemStore } from '@/stores/poem'
import PoemText from '@/components/poetry/PoemText.vue'
import AnalysisPanel from '@/components/poetry/AnalysisPanel.vue'
import Loading from '@/components/common/Loading.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const poemStore = usePoemStore()

const poem = ref(poemStore.currentPoem)
const loading = ref(false)

function goAuthor(name) {
  router.push(`/author/${encodeURIComponent(name)}`)
}

function goImagery() {
  const text = poem.value?.content?.join('\n') || ''
  const title = poem.value?.title || ''
  const author = poem.value?.author?.name || ''
  router.push({
    path: '/explore/imagery',
    query: { poem: text, title, author },
  })
}

onMounted(async () => {
  const id = route.params.id
  loading.value = !poem.value
  try {
    const data = await getPoemDetail(id)
    poem.value = data
    poemStore.setCurrentPoem(data)
  } catch {
    // 保持缓存数据
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.imagery-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 14px 20px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  color: #c8851a;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.8), rgba(245, 214, 138, 0.1));
  border: 1px solid rgba(200, 133, 26, 0.15);
  cursor: pointer;
  transition: all 0.2s ease;
}

.imagery-btn:hover {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.9), rgba(245, 214, 138, 0.18));
  box-shadow: 0 4px 16px rgba(200, 133, 26, 0.12);
}

.imagery-btn:active {
  transform: scale(0.99);
}

.imagery-btn-sub {
  font-size: 12px;
  font-weight: 400;
  color: #AEAEB2;
  margin-left: auto;
}
</style>

<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- 页面标题 -->
    <div class="content-container pt-4 pb-3 flex items-center gap-3">
      <button class="text-ink-light lg:hidden" @click="router.back()">
        <van-icon name="arrow-left" size="20" />
      </button>
      <h1 class="text-[17px] lg:text-[24px] font-semibold text-ink">{{ authorName }}</h1>
    </div>

    <div class="content-container">
      <!-- 作者卡片 -->
      <div class="pb-3">
        <div class="glass-card p-5 flex items-center gap-4 max-w-lg">
          <div class="w-14 h-14 rounded-full bg-gradient-to-br from-primary/20 to-accent/10 flex items-center justify-center text-[22px] font-kai font-bold text-primary flex-shrink-0">
            {{ authorName.charAt(0) }}
          </div>
          <div>
            <h2 class="font-kai text-[20px] text-ink">{{ authorName }}</h2>
            <p class="text-ink-light text-[14px] mt-0.5">共 {{ total }} 首</p>
          </div>
        </div>
      </div>

      <!-- 诗词列表 -->
      <div class="pb-8">
        <van-list
          v-model:loading="loading"
          v-model:error="error"
          :finished="finished"
          finished-text="已加载全部诗词"
          error-text="加载失败，点击重试"
          :offset="300"
          @load="onLoad"
        >
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            <PoemCard
              v-for="poem in poems"
              :key="poem.id"
              :poem="poem"
              @click="goDetail"
            />
          </div>
        </van-list>

        <EmptyState v-if="finished && !poems.length" message="暂无该作者的诗词" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPoemsByAuthor } from '@/api/poem'
import { usePoemStore } from '@/stores/poem'
import PoemCard from '@/components/poetry/PoemCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const poemStore = usePoemStore()

const authorName = computed(() => decodeURIComponent(route.params.name))
const poems = ref([])
const total = ref(0)
const page = ref(0)
const pageSize = 18
const loading = ref(false)
const finished = ref(false)
const error = ref(false)

function goDetail(poem) {
  poemStore.setCurrentPoem(poem)
  router.push(`/poem/${poem.id}`)
}

async function onLoad() {
  try {
    page.value++
    const data = await getPoemsByAuthor(authorName.value, page.value, pageSize)
    const items = Array.isArray(data) ? data : (data?.items || [])
    const serverTotal = Array.isArray(data) ? data.length : (data?.total || 0)

    poems.value.push(...items)
    total.value = serverTotal
    loading.value = false

    if (!items.length || poems.value.length >= serverTotal) {
      finished.value = true
    }
  } catch {
    loading.value = false
    error.value = true
  }
}
</script>

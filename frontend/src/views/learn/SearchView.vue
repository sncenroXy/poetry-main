<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- 搜索框 -->
    <div class="content-container pt-4 pb-3">
      <div class="flex items-center gap-3 bg-sys-bg-secondary rounded-apple px-4 py-2.5 max-w-lg">
        <van-icon name="search" color="#AEAEB2" size="18" />
        <input
          v-model="query"
          class="flex-1 bg-transparent border-none outline-none text-[15px] text-ink placeholder:text-text-tertiary"
          placeholder="搜诗句、作者、意象…"
          autofocus
          @keydown.enter="doSearch"
        />
        <van-icon v-if="query" name="clear" color="#AEAEB2" size="16" @click="clearSearch" />
      </div>
    </div>

    <!-- 搜索结果 -->
    <div class="content-container">
      <div v-if="searched">
        <p v-if="total" class="text-ink-light text-[13px] mb-3">
          共找到 {{ total }} 条结果
        </p>

        <van-list
          v-model:loading="loading"
          v-model:error="error"
          :finished="finished"
          finished-text="已加载全部结果"
          error-text="加载失败，点击重试"
          :offset="300"
          @load="onLoad"
        >
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            <PoemCard
              v-for="poem in results"
              :key="poem.id"
              :poem="poem"
              @click="goDetail"
            />
          </div>
        </van-list>

        <EmptyState
          v-if="finished && !results.length"
          message="未找到相关诗词"
        >
          <p class="text-[13px] text-ink-light mt-2">试试换个关键词？</p>
        </EmptyState>
      </div>

      <!-- 初始状态 - 热门搜索 -->
      <div v-else class="py-6">
        <p class="text-ink-light text-[14px] mb-3 font-medium">热门搜索</p>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="tag in hotTags"
            :key="tag"
            class="tag-item"
            @click="quickSearch(tag)"
          >
            {{ tag }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { searchPoems } from '@/api/poem'
import { usePoemStore } from '@/stores/poem'
import PoemCard from '@/components/poetry/PoemCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const poemStore = usePoemStore()

const query = ref('')
const results = ref([])
const total = ref(0)
const page = ref(0)
const pageSize = 18
const loading = ref(false)
const finished = ref(false)
const error = ref(false)
const searched = ref(false)

// 当前生效的搜索关键词（防止加载下一页时 query 已被用户修改）
let activeQuery = ''

const hotTags = ['明月', '春风', '思乡', '李白', '苏轼', '边塞', '送别', '田园']

function resetList() {
  results.value = []
  total.value = 0
  page.value = 0
  finished.value = false
  error.value = false
}

function doSearch() {
  if (!query.value.trim()) return
  activeQuery = query.value.trim()
  searched.value = true
  resetList()
  // van-list 检测到 finished=false 且在视口内会自动触发 onLoad
}

async function onLoad() {
  try {
    page.value++
    const data = await searchPoems(activeQuery, page.value, pageSize)
    const items = Array.isArray(data) ? data : (data?.items || [])
    const serverTotal = Array.isArray(data) ? data.length : (data?.total || 0)

    results.value.push(...items)
    total.value = serverTotal
    loading.value = false

    if (!items.length || results.value.length >= serverTotal) {
      finished.value = true
    }
  } catch {
    loading.value = false
    error.value = true
  }
}

function clearSearch() {
  query.value = ''
  activeQuery = ''
  searched.value = false
  resetList()
}

function quickSearch(tag) {
  query.value = tag
  doSearch()
}

function goDetail(poem) {
  poemStore.setCurrentPoem(poem)
  router.push(`/poem/${poem.id}`)
}

onMounted(() => {
  if (route.query.q) {
    query.value = route.query.q
    doSearch()
  }
})
</script>

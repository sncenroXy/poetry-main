<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- 页面标题 -->
    <div class="content-container pt-4 pb-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button class="text-ink-light lg:hidden" @click="router.back()">
          <van-icon name="arrow-left" size="20" />
        </button>
        <h1 class="text-[24px] lg:text-[32px] font-semibold text-ink tracking-tight">诗词库</h1>
      </div>
    </div>

    <div class="content-container pb-8">
      <!-- 筛选栏 -->
      <div class="filter-bar mb-4">
        <!-- 分类维度切换 -->
        <div class="filter-tabs mb-3">
          <button
            v-for="cat in categories"
            :key="cat.key"
            class="filter-tab"
            :class="{ active: activeCategory === cat.key }"
            @click="toggleCategory(cat.key)"
          >{{ cat.label }}</button>
        </div>

        <!-- 当前分类的选项 -->
        <div v-if="activeCategory" class="filter-options">
          <!-- 已选筛选条件提示 -->
          <div v-if="hasActiveFilters" class="flex items-center gap-2 mb-2">
            <span class="text-[12px] text-ink-light">已筛选：</span>
            <span
              v-for="(val, key) in activeFilterLabels"
              :key="key"
              class="active-filter-chip"
              @click="clearFilter(key)"
            >{{ val }} <span class="ml-1 opacity-60">&times;</span></span>
            <button class="text-[12px] text-primary font-medium ml-1" @click="clearAllFilters">清除全部</button>
          </div>

          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="opt in currentOptions"
              :key="opt"
              class="filter-option"
              :class="{ selected: isOptionSelected(opt) }"
              @click="selectOption(opt)"
            >{{ opt }}</button>
          </div>

          <!-- 展开/收起（当选项过多时） -->
          <button
            v-if="allCurrentOptions.length > visibleLimit"
            class="text-[12px] text-primary font-medium mt-2"
            @click="expanded = !expanded"
          >{{ expanded ? '收起' : `展开全部 (${allCurrentOptions.length})` }}</button>
        </div>
      </div>

      <!-- 统计 -->
      <p v-if="total" class="text-ink-light text-[13px] mb-3">
        {{ hasActiveFilters ? `筛选结果 ${total} 首` : `共收录 ${total} 首` }}
      </p>

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

      <EmptyState v-if="finished && !poems.length" :message="hasActiveFilters ? '没有符合条件的诗词' : '暂无诗词'" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getAllPoems, getFilterOptions } from '@/api/poem'
import { usePoemStore } from '@/stores/poem'
import PoemCard from '@/components/poetry/PoemCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const poemStore = usePoemStore()

// ===== 筛选状态 =====
const categories = [
  { key: 'dynasty', label: '朝代' },
  { key: 'genre', label: '体裁' },
  { key: 'author', label: '作者' },
  { key: 'tag', label: '主题' },
]

const activeCategory = ref('')
const expanded = ref(false)
const visibleLimit = 20

const filterOptions = reactive({
  dynasties: [],
  genres: [],
  authors: [],
  tags: [],
})

const filters = reactive({
  dynasty: '',
  genre: '',
  author: '',
  tag: '',
})

const hasActiveFilters = computed(() =>
  filters.dynasty || filters.genre || filters.author || filters.tag
)

const activeFilterLabels = computed(() => {
  const labels = {}
  if (filters.dynasty) labels.dynasty = filters.dynasty
  if (filters.genre) labels.genre = filters.genre
  if (filters.author) labels.author = filters.author
  if (filters.tag) labels.tag = filters.tag
  return labels
})

const allCurrentOptions = computed(() => {
  switch (activeCategory.value) {
    case 'dynasty': return filterOptions.dynasties
    case 'genre': return filterOptions.genres
    case 'author': return filterOptions.authors
    case 'tag': return filterOptions.tags
    default: return []
  }
})

const currentOptions = computed(() => {
  const all = allCurrentOptions.value
  return expanded.value ? all : all.slice(0, visibleLimit)
})

function toggleCategory(key) {
  if (activeCategory.value === key) {
    activeCategory.value = ''
  } else {
    activeCategory.value = key
    expanded.value = false
  }
}

function isOptionSelected(opt) {
  return filters[activeCategory.value] === opt
}

function selectOption(opt) {
  const key = activeCategory.value
  if (filters[key] === opt) {
    filters[key] = ''
  } else {
    filters[key] = opt
  }
}

function clearFilter(key) {
  filters[key] = ''
}

function clearAllFilters() {
  filters.dynasty = ''
  filters.genre = ''
  filters.author = ''
  filters.tag = ''
}

// ===== 列表状态 =====
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

function resetList() {
  poems.value = []
  total.value = 0
  page.value = 0
  finished.value = false
  error.value = false
  loading.value = true
}

async function onLoad() {
  try {
    page.value++
    const data = await getAllPoems(page.value, pageSize, {
      dynasty: filters.dynasty,
      genre: filters.genre,
      author: filters.author,
      tag: filters.tag,
    })
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

// 筛选条件变化时重新加载
watch(
  () => [filters.dynasty, filters.genre, filters.author, filters.tag],
  () => {
    resetList()
    onLoad()
  }
)

// 加载筛选选项
onMounted(async () => {
  try {
    const data = await getFilterOptions()
    filterOptions.dynasties = data.dynasties || []
    filterOptions.genres = data.genres || []
    filterOptions.authors = data.authors || []
    filterOptions.tags = data.tags || []
  } catch {
    // 筛选项加载失败不影响列表
  }
})
</script>

<style scoped>
/* 筛选栏 */
.filter-bar {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 14px;
  padding: 12px 16px;
  border: 0.5px solid rgba(0, 0, 0, 0.04);
}

/* 分类维度 Tab */
.filter-tabs {
  display: flex;
  gap: 4px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 10px;
  padding: 3px;
  width: fit-content;
}

.filter-tab {
  padding: 6px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #6E6E73;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.filter-tab.active {
  background: white;
  color: #1D1D1F;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.filter-tab:active {
  transform: scale(0.97);
}

/* 筛选选项 */
.filter-options {
  padding-top: 4px;
}

.filter-option {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 13px;
  color: #6E6E73;
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.filter-option:hover {
  background: rgba(0, 0, 0, 0.06);
  color: #1D1D1F;
}

.filter-option.selected {
  background: rgba(200, 133, 26, 0.10);
  color: #c8851a;
  border-color: rgba(200, 133, 26, 0.25);
  font-weight: 500;
}

/* 已选标签 */
.active-filter-chip {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(200, 133, 26, 0.10);
  color: #c8851a;
  cursor: pointer;
  transition: all 0.15s ease;
}

.active-filter-chip:hover {
  background: rgba(200, 133, 26, 0.18);
}
</style>

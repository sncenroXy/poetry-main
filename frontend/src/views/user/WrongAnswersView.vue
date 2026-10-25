<template>
  <div class="min-h-screen bg-sys-bg">
    <div class="content-container pt-6 pb-4">
      <div class="flex items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <button class="text-ink-light lg:hidden" @click="router.back()">
            <van-icon name="arrow-left" size="20" />
          </button>
          <h1 class="text-[24px] lg:text-[32px] font-semibold text-ink tracking-tight">错题本</h1>
        </div>
        <van-button v-if="items.length" plain size="small" style="border-radius: 10px" @click="clearAll">清空</van-button>
      </div>
      <p class="text-ink-light text-[14px] mt-1">答错的题目会收在这里，方便集中复习</p>
    </div>

    <div class="content-container py-4">
      <Loading v-if="loading" text="正在加载…" />

      <template v-else-if="items.length">
        <div class="space-y-3">
          <div v-for="item in items" :key="item.id" class="glass-card p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="type-badge" :class="item.type === 'chain' ? 'type-chain' : 'type-quiz'">
                {{ typeLabels[item.type] || '答题' }}
              </span>
              <span v-if="item.source" class="text-[12px] text-ink-light">{{ item.source }}</span>
              <button class="ml-auto text-[12px] text-ink-light" @click="remove(item)">删除</button>
            </div>

            <p class="text-[15px] text-ink leading-relaxed mb-2">{{ item.question }}</p>

            <div v-if="item.user_answer" class="text-[13px] mb-1">
              <span class="text-ink-light">我的答案：</span>
              <span class="text-accent">{{ item.user_answer }}</span>
            </div>
            <div v-if="item.correct_answer" class="text-[13px]">
              <span class="text-ink-light">正确答案：</span>
              <span class="text-success font-medium">{{ item.correct_answer }}</span>
            </div>
          </div>
        </div>
      </template>

      <EmptyState v-else message="还没有错题，继续加油！" />
    </div>

    <div class="h-12"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getWrongAnswers, removeWrongAnswer, clearWrongAnswers } from '@/api/user'
import Loading from '@/components/common/Loading.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { showToast, showConfirmDialog } from 'vant'

const router = useRouter()

const typeLabels = { quiz: '答题', chain: '飞花令' }

const items = ref([])
const loading = ref(true)

async function remove(item) {
  try {
    await removeWrongAnswer(item.id)
    items.value = items.value.filter(i => i.id !== item.id)
    showToast('已删除')
  } catch {
    showToast('操作失败，请重试')
  }
}

async function clearAll() {
  try {
    await showConfirmDialog({ title: '清空错题本', message: '确定清空所有错题吗？' })
  } catch {
    return
  }
  try {
    await clearWrongAnswers()
    items.value = []
    showToast('已清空')
  } catch {
    showToast('操作失败，请重试')
  }
}

onMounted(async () => {
  loading.value = true
  try {
    items.value = await getWrongAnswers()
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.type-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.type-quiz {
  background: rgba(200, 133, 26, 0.10);
  color: #c8851a;
}

.type-chain {
  background: rgba(52, 199, 89, 0.10);
  color: #34c759;
}
</style>

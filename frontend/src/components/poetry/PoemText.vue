<template>
  <div class="poem-text">
    <!-- 标题 -->
    <h1 class="poem-title text-[24px] text-ink text-center mb-2">
      {{ poem.title || '无题' }}
    </h1>

    <!-- 作者信息 -->
    <div class="flex justify-center items-center gap-2 text-ink-light text-[14px] mb-6">
      <span v-if="poem.author?.dynasty" class="text-[12px] bg-primary/8 text-primary px-2.5 py-0.5 rounded-full">
        {{ poem.author.dynasty }}
      </span>
      <span
        v-if="poem.author?.name"
        class="cursor-pointer hover:text-primary transition-colors"
        @click="$emit('author-click', poem.author.name)"
      >
        {{ poem.author.name }}
      </span>
    </div>

    <!-- 诗词正文 -->
    <div class="poem-body text-ink text-[18px] leading-relaxed text-center">
      <p
        v-for="(line, idx) in lines"
        :key="idx"
        class="mb-2"
      >
        {{ line }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  poem: { type: Object, required: true }
})

defineEmits(['author-click'])

const lines = computed(() => {
  const content = props.poem.content
  if (!content) return []
  if (Array.isArray(content)) return content
  return content.split(/[。\n]/).filter(line => line.trim())
})
</script>

<style scoped>
.poem-text {
  padding: 24px 20px;
}
</style>

<template>
  <div
    class="poem-card glass-card p-4 cursor-pointer active:scale-[0.98] transition-all duration-200"
    @click="$emit('click', poem)"
  >
    <h3 class="poem-title text-[17px] text-ink mb-1.5 tracking-tight font-bold">
      {{ poem.title || '无题' }}
    </h3>
    <div class="flex items-center gap-2 text-ink-light text-[13px] mb-2.5">
      <span v-if="poem.author?.name" class="flex items-center gap-1">
        {{ poem.author.name }}
      </span>
      <span v-if="poem.author?.dynasty" class="text-[11px] bg-primary/8 text-primary px-2 py-0.5 rounded-full">
        {{ poem.author.dynasty }}
      </span>
    </div>
    <p class="poem-body text-ink-light text-[14px] line-clamp-2 leading-relaxed">
      {{ previewContent }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  poem: { type: Object, required: true }
})

defineEmits(['click'])

const previewContent = computed(() => {
  const content = props.poem.content
  if (!content) return ''
  if (Array.isArray(content)) {
    return content.slice(0, 2).join('，') + '…'
  }
  return content.split(/[，。！？\n]/).filter(Boolean).slice(0, 2).join('，') + '…'
})
</script>

<style scoped>
.poem-card {
  position: relative;
  border-left: 2px solid rgba(200, 133, 26, 0.15);
}

@media (hover: hover) {
  .poem-card:hover {
    box-shadow:
      var(--shadow-card-lg),
      var(--inset-card);
    transform: translateY(-2px);
    border-left-color: #c8851a;
  }
}
</style>

<template>
  <div class="flex flex-col items-center justify-center py-16 text-ink-light">
    <div class="text-[40px] mb-4 opacity-20">{{ icon }}</div>
    <p class="text-[15px] font-medium">{{ message }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📄' },
  message: { type: String, default: '暂无内容' }
})
</script>

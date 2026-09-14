<template>
  <div class="flex flex-col items-center justify-center py-20 gap-3">
    <div class="spinner" />
    <p class="text-ink-light text-[14px]">{{ text }}</p>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: '加载中…' }
})
</script>

<style scoped>
.spinner {
  width: 28px;
  height: 28px;
  border: 2.5px solid rgba(0, 0, 0, 0.06);
  border-top-color: #c8851a;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>

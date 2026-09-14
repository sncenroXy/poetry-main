<template>
  <span
    class="author-tag inline-flex items-center gap-1 px-2 py-1 bg-paper-dark rounded text-sm text-ink cursor-pointer hover:bg-gold-light/30 transition-colors"
    @click="$emit('click', name)"
  >
    <van-icon name="user-o" size="12" />
    {{ name }}
  </span>
</template>

<script setup>
defineProps({
  name: { type: String, required: true }
})

defineEmits(['click'])
</script>

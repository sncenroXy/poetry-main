<template>
  <div class="analysis-panel mt-5">
    <!-- 白话译文 -->
    <section v-if="poem.analysis?.translation" class="mb-5">
      <div class="section-header">
        <span class="section-title">白话译文</span>
      </div>
      <p class="text-ink-light text-[14px] leading-relaxed mt-3">
        {{ poem.analysis.translation }}
      </p>
    </section>

    <!-- 赏析 -->
    <section v-if="poem.analysis" class="mb-5">
      <div class="section-header">
        <span class="section-title">诗词赏析</span>
      </div>
      <div class="mt-3 space-y-3">
        <p v-if="poem.analysis.appreciation" class="text-ink text-[14px] leading-relaxed">
          <span class="text-primary font-medium">赏析 · </span>
          {{ poem.analysis.appreciation }}
        </p>
        <p v-if="poem.analysis.cultural" class="text-ink text-[14px] leading-relaxed">
          <span class="text-primary font-medium">文化 · </span>
          {{ poem.analysis.cultural }}
        </p>
      </div>
    </section>

    <!-- 作者简介 -->
    <section v-if="poem.author?.brief" class="mb-5">
      <div class="section-header">
        <span class="section-title">作者简介</span>
      </div>
      <p class="text-ink-light text-[14px] leading-relaxed mt-3">
        {{ poem.author.brief }}
      </p>
    </section>

    <!-- 创作背景 -->
    <section v-if="poem.background" class="mb-5">
      <div class="section-header">
        <span class="section-title">创作背景</span>
      </div>
      <p class="text-ink-light text-[14px] leading-relaxed mt-3">
        {{ poem.background }}
      </p>
    </section>
  </div>
</template>

<script setup>
defineProps({
  poem: { type: Object, required: true }
})
</script>

<style scoped>
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-header::before {
  content: '';
  width: 3px;
  height: 16px;
  background: linear-gradient(180deg, #c8851a, #e54d42);
  border-radius: 2px;
}

.section-title {
  font-family: 'KaiTi', '楷体', serif;
  font-size: 17px;
  font-weight: 600;
  color: #1D1D1F;
}
</style>

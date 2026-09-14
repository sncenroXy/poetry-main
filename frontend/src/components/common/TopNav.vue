<template>
  <header class="top-nav lg:hidden">
    <div class="top-nav-inner">
      <!-- Logo -->
      <div class="nav-brand" @click="go('/')">
        <div class="brand-icon">诗</div>
        <span class="brand-text">诗词雅韵</span>
      </div>

      <!-- Tab 切换 -->
      <nav class="nav-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.name"
          class="nav-tab"
          :class="{ active: activeTab === tab.name }"
          @click="go(tab.path)"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const tabs = [
  { name: 'home', label: '鉴赏', path: '/' },
  { name: 'challenge', label: '挑战', path: '/challenge' },
  { name: 'create', label: '创作', path: '/create' }
]

const activeTab = computed(() => {
  if (route.path.startsWith('/challenge')) return 'challenge'
  if (route.path.startsWith('/create')) return 'create'
  return 'home'
})

function go(path) {
  router.push(path)
}
</script>

<style scoped>
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.top-nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 52px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.85) 0%, rgba(250, 247, 240, 0.82) 100%);
  backdrop-filter: blur(24px) saturate(1.2);
  -webkit-backdrop-filter: blur(24px) saturate(1.2);
  border-bottom: 1px solid rgba(200, 133, 26, 0.12);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.brand-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, #c8851a, #e54d42);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-family: 'Noto Serif SC', 'KaiTi', '楷体', serif;
  font-size: 14px;
  font-weight: 600;
}

.brand-text {
  font-family: 'Noto Serif SC', 'KaiTi', '楷体', serif;
  font-size: 16px;
  font-weight: 600;
  color: #1D1D1F;
}

.nav-tabs {
  display: flex;
  gap: 4px;
  background: rgba(200, 133, 26, 0.05);
  border: 1px solid rgba(200, 133, 26, 0.08);
  border-radius: 10px;
  padding: 3px;
}

.nav-tab {
  padding: 5px 16px;
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

.nav-tab.active {
  background: white;
  color: #1D1D1F;
  font-weight: 600;
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(200, 133, 26, 0.06);
}

.nav-tab:active {
  transform: scale(0.96);
}
</style>

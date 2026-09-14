<template>
  <aside class="side-nav">
    <!-- Brand -->
    <div class="side-brand" @click="go('/')">
      <div class="side-brand-icon">诗</div>
      <span class="side-brand-text">诗词雅韵</span>
    </div>

    <!-- Navigation -->
    <nav class="side-nav-links">
      <div
        v-for="section in sections"
        :key="section.name"
        class="side-section"
      >
        <p class="side-section-label">{{ section.label }}</p>
        <button
          v-for="item in section.items"
          :key="item.path"
          class="side-nav-item"
          :class="{ active: isActive(item.path) }"
          @click="go(item.path)"
        >
          <component :is="item.icon" class="side-nav-icon" />
          <span>{{ item.name }}</span>
        </button>
      </div>
    </nav>

    <!-- Footer -->
    <div class="side-footer">
      <p class="text-[12px] text-ink-light/60">学诗 · 练诗 · 创诗</p>
    </div>
  </aside>
</template>

<script setup>
import { computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// SVG icon components
const IconBook = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20' })]) }
const IconSearch = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('circle', { cx: '11', cy: '11', r: '8' }), h('path', { d: 'M21 21l-4.3-4.3' })]) }
const IconLibrary = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z' }), h('path', { d: 'M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z' })]) }
const IconFlower = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M12 7.5a4.5 4.5 0 1 1 4.5 4.5M12 7.5A4.5 4.5 0 1 0 7.5 12M12 7.5V9m-4.5 3a4.5 4.5 0 1 0 4.5 4.5M7.5 12H9m3 4.5a4.5 4.5 0 1 0 4.5-4.5M12 16.5V15m4.5-3a4.5 4.5 0 1 1-4.5-4.5M16.5 12H15' }), h('circle', { cx: '12', cy: '12', r: '3' })]) }
const IconQuiz = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M9 11l3 3L22 4' }), h('path', { d: 'M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11' })]) }
const IconPen = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M12 20h9' }), h('path', { d: 'M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z' })]) }
const IconWand = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M15 4V2' }), h('path', { d: 'M15 16v-2' }), h('path', { d: 'M8 9h2' }), h('path', { d: 'M20 9h2' }), h('path', { d: 'M17.8 11.8L19 13' }), h('path', { d: 'M15 9h0' }), h('path', { d: 'M17.8 6.2L19 5' }), h('path', { d: 'M3 21l9-9' }), h('path', { d: 'M12.2 6.2L11 5' })]) }
const IconImage = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('rect', { x: '3', y: '3', width: '18', height: '18', rx: '2', ry: '2' }), h('circle', { cx: '8.5', cy: '8.5', r: '1.5' }), h('polyline', { points: '21 15 16 10 5 21' })]) }
const IconVideo = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z' }), h('circle', { cx: '12', cy: '13', r: '3' })]) }

const IconCompass = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('circle', { cx: '12', cy: '12', r: '10' }), h('polygon', { points: '16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76' })]) }

const sections = [
  {
    name: 'learn',
    label: '鉴赏',
    items: [
      { name: '首页', path: '/', icon: IconBook },
      // { name: '搜索', path: '/search', icon: IconSearch },
      { name: '诗词库', path: '/poems', icon: IconLibrary },
      { name: '诗境漫游', path: '/explore/imagery', icon: IconCompass }
    ]
  },
  {
    name: 'challenge',
    label: '挑战',
    items: [
      { name: '飞花令', path: '/challenge/chain', icon: IconFlower },
      { name: '答题闯关', path: '/challenge/quiz', icon: IconQuiz }
    ]
  },
  {
    name: 'create',
    label: '创作',
    items: [
      { name: '诗词创作', path: '/create', icon: IconPen },
      { name: '仿写工坊', path: '/create/mimic', icon: IconWand },
      { name: '诗画互生', path: '/create/image', icon: IconImage },
      { name: '诗境动画', path: '/create/video', icon: IconVideo }
    ]
  }
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  // 精确匹配有子路由的路径（如 /create），避免 /create 和 /create/image 同时高亮
  if (route.path === path) return true
  // 只有当 path 本身不是其他导航项的前缀时才用 startsWith
  const allPaths = sections.flatMap(s => s.items.map(i => i.path))
  const hasChildNav = allPaths.some(p => p !== path && p.startsWith(path + '/'))
  if (hasChildNav) return route.path === path
  return route.path.startsWith(path)
}

function go(path) {
  router.push(path)
}
</script>

<style scoped>
.side-nav {
  position: fixed;
  top: 0;
  left: 0;
  width: 240px;
  height: 100vh;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.82) 0%, rgba(250, 247, 240, 0.85) 100%);
  backdrop-filter: blur(24px) saturate(1.2);
  -webkit-backdrop-filter: blur(24px) saturate(1.2);
  border-right: 1px solid rgba(200, 133, 26, 0.12);
  box-shadow: 1px 0 4px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  z-index: 100;
  overflow-y: auto;
}

.side-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 20px 16px;
  cursor: pointer;
}

.side-brand-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #c8851a, #e54d42);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-family: 'Noto Serif SC', 'KaiTi', '楷体', serif;
  font-size: 16px;
  font-weight: 600;
  flex-shrink: 0;
}

.side-brand-text {
  font-family: 'Noto Serif SC', 'KaiTi', '楷体', serif;
  font-size: 18px;
  font-weight: 600;
  color: #1D1D1F;
}

.side-nav-links {
  flex: 1;
  padding: 0 12px;
}

.side-section {
  margin-bottom: 8px;
}

.side-section-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.15em;
  color: #6E6E73;
  padding: 14px 12px 6px;
  margin: 0;
}

.side-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 9px 12px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #6E6E73;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.side-nav-item:hover {
  background: rgba(200, 133, 26, 0.04);
  color: #1D1D1F;
  border-color: rgba(200, 133, 26, 0.06);
}

.side-nav-item.active {
  background: rgba(200, 133, 26, 0.10);
  color: #c8851a;
  border-color: rgba(200, 133, 26, 0.15);
  box-shadow: inset 0 1px 2px rgba(200, 133, 26, 0.08);
  font-weight: 600;
}

.side-nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.side-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(200, 133, 26, 0.08);
}
</style>

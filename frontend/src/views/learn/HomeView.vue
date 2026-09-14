<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- Hero Section — 紧凑型，带装饰背景 -->
    <div class="hero-section">
      <div class="hero-bg-pattern"></div>
      <div class="content-container relative z-10 pt-6 pb-5 px-5 lg:px-0">
        <div class="flex items-end justify-between gap-4 flex-wrap">
          <div>
            <h1 class="poem-title text-[26px] lg:text-[32px] text-ink tracking-tight leading-tight">诗词雅韵</h1>
            <p class="text-ink-light text-[14px] mt-0.5">学诗 · 练诗 · 创诗</p>
          </div>
          <!-- 搜索框 — 内嵌到 hero 右侧 -->
          <div
            class="search-box flex items-center gap-2.5 px-4 py-2.5 rounded-full cursor-pointer transition-all hover:shadow-apple min-w-[220px] lg:min-w-[280px]"
            @click="onSearchFocus"
          >
            <van-icon name="search" color="#AEAEB2" size="16" />
            <span class="text-text-tertiary text-[13px]">搜诗句、作者、意象…</span>
          </div>
        </div>
      </div>
    </div>

    <div class="content-container">
      <!-- 功能入口 — 紧凑横向滚动(移动端) / 网格(桌面) -->
      <div class="py-3">
        <div class="feature-scroll lg:grid lg:grid-cols-8 lg:gap-2.5">
          <div
            v-for="item in featureCards"
            :key="item.name"
            class="feature-card"
            :class="item.cardClass"
            @click="router.push(item.path)"
          >
            <div class="feature-icon-wrap" :class="item.iconBg">
              <component :is="item.icon" class="w-[18px] h-[18px]" :class="item.iconClass" />
            </div>
            <span class="feature-label">{{ item.name }}</span>
          </div>
        </div>
      </div>

      <!-- 双栏布局：AI 助手 + 每日一诗 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 pb-6">
        <!-- AI 诗词助手 — 占 2 列 -->
        <div class="lg:col-span-2">
          <AiAssistant />
        </div>
        <!-- 侧边栏：每日诗句 + 快捷入口 -->
        <div class="flex flex-col gap-4">
          <!-- 每日诗句卡片 -->
          <div class="daily-poem-card">
            <div class="daily-poem-header">
              <span class="daily-label">每日一诗</span>
            </div>
            <p class="poem-body text-[16px] text-ink leading-[2.2] mt-3">{{ dailyPoem.lines[0] }}</p>
            <p class="poem-body text-[16px] text-ink leading-[2.2]">{{ dailyPoem.lines[1] }}</p>
            <div class="divider-brush my-2"></div>
            <div class="flex items-center justify-between">
              <span class="text-[13px] text-ink-light">{{ dailyPoem.source }}</span>
              <button
                class="text-[12px] text-primary font-medium cursor-pointer hover:underline"
                @click="router.push('/poems')"
              >探索更多</button>
            </div>
          </div>

          <!-- 学习统计 / 快捷卡片 -->
          <div class="quick-links-card">
            <h3 class="text-[14px] font-semibold text-ink mb-3">快捷入口</h3>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="link in quickLinks"
                :key="link.name"
                class="quick-link-item"
                @click="router.push(link.path)"
              >
                <component :is="link.icon" class="w-4 h-4" :class="link.iconClass" />
                <span>{{ link.name }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { h, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AiAssistant from '@/components/ai/AiAssistant.vue'

const router = useRouter()

// 每日诗句
const dailyPoems = [
  { lines: ['大漠孤烟直', '长河落日圆'], source: '王维《使至塞上》' },
  { lines: ['海上生明月', '天涯共此时'], source: '张九龄《望月怀远》' },
  { lines: ['落霞与孤鹜齐飞', '秋水共长天一色'], source: '王勃《滕王阁序》' },
  { lines: ['春风又绿江南岸', '明月何时照我还'], source: '王安石《泊船瓜洲》' },
  { lines: ['两个黄鹂鸣翠柳', '一行白鹭上青天'], source: '杜甫《绝句》' },
  { lines: ['千山鸟飞绝', '万径人踪灭'], source: '柳宗元《江雪》' },
  { lines: ['接天莲叶无穷碧', '映日荷花别样红'], source: '杨万里《晓出净慈寺送林子方》' },
]
const dailyPoem = ref(dailyPoems[0])

onMounted(() => {
  const dayIndex = new Date().getDate() % dailyPoems.length
  dailyPoem.value = dailyPoems[dayIndex]
})

// SVG icon components
const IconLibrary = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z' }), h('path', { d: 'M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z' })]) }
const IconFlower = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('circle', { cx: '12', cy: '12', r: '3' }), h('path', { d: 'M12 7.5a4.5 4.5 0 1 1 4.5 4.5M12 7.5A4.5 4.5 0 1 0 7.5 12M12 7.5V9m-4.5 3a4.5 4.5 0 1 0 4.5 4.5M7.5 12H9m3 4.5a4.5 4.5 0 1 0 4.5-4.5M12 16.5V15m4.5-3a4.5 4.5 0 1 1-4.5-4.5M16.5 12H15' })]) }
const IconPen = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M12 20h9' }), h('path', { d: 'M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z' })]) }
const IconQuiz = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: '9 11l3 3L22 4' }), h('path', { d: 'M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11' })]) }
const IconWand = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M15 4V2' }), h('path', { d: 'M15 16v-2' }), h('path', { d: 'M8 9h2' }), h('path', { d: 'M20 9h2' }), h('path', { d: 'M17.8 11.8L19 13' }), h('path', { d: 'M15 9h0' }), h('path', { d: 'M17.8 6.2L19 5' }), h('path', { d: 'M3 21l9-9' }), h('path', { d: 'M12.2 6.2L11 5' })]) }
const IconImage = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('rect', { x: '3', y: '3', width: '18', height: '18', rx: '2', ry: '2' }), h('circle', { cx: '8.5', cy: '8.5', r: '1.5' }), h('polyline', { points: '21 15 16 10 5 21' })]) }
const IconVideo = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z' }), h('circle', { cx: '12', cy: '13', r: '3' })]) }
const IconCompass = { render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('circle', { cx: '12', cy: '12', r: '10' }), h('polygon', { points: '16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76' })]) }

const featureCards = [
  { name: '诗词库', icon: IconLibrary, path: '/poems', iconBg: 'icon-bg-gold', iconClass: 'text-primary', cardClass: '' },
  { name: '诗境漫游', icon: IconCompass, path: '/explore/imagery', iconBg: 'icon-bg-vermilion', iconClass: 'text-accent', cardClass: '' },
  { name: '飞花令', icon: IconFlower, path: '/challenge/chain', iconBg: 'icon-bg-cyan', iconClass: 'text-success', cardClass: '' },
  { name: '答题闯关', icon: IconQuiz, path: '/challenge/quiz', iconBg: 'icon-bg-gold', iconClass: 'text-primary', cardClass: '' },
  { name: '诗词创作', icon: IconPen, path: '/create', iconBg: 'icon-bg-vermilion', iconClass: 'text-accent', cardClass: '' },
  { name: '仿写工坊', icon: IconWand, path: '/create/mimic', iconBg: 'icon-bg-cyan', iconClass: 'text-success', cardClass: '' },
  { name: '诗画互生', icon: IconImage, path: '/create/image', iconBg: 'icon-bg-gold', iconClass: 'text-primary', cardClass: '' },
  { name: '诗境动画', icon: IconVideo, path: '/create/video', iconBg: 'icon-bg-vermilion', iconClass: 'text-accent', cardClass: '' },
]

const quickLinks = [
  { name: '飞花令', path: '/challenge/chain', icon: IconFlower, iconClass: 'text-accent' },
  { name: '答题闯关', path: '/challenge/quiz', icon: IconQuiz, iconClass: 'text-success' },
  { name: '诗词创作', path: '/create', icon: IconPen, iconClass: 'text-primary' },
  { name: '诗画互生', path: '/create/image', icon: IconImage, iconClass: 'text-success' },
]

function onSearchFocus() {
  router.push('/search')
}
</script>

<style scoped>
/* ===== Hero Section ===== */
.hero-section {
  position: relative;
  background: linear-gradient(135deg,
    rgba(250, 247, 240, 0.6) 0%,
    rgba(240, 235, 225, 0.5) 50%,
    rgba(245, 238, 226, 0.4) 100%
  );
  border-bottom: 1px solid rgba(200, 133, 26, 0.12);
  overflow: hidden;
}

.hero-bg-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.04;
  background-image:
    radial-gradient(circle at 20% 50%, #c8851a 1px, transparent 1px),
    radial-gradient(circle at 80% 20%, #e54d42 1px, transparent 1px),
    radial-gradient(circle at 60% 80%, #12aa9c 1px, transparent 1px);
  background-size: 60px 60px, 80px 80px, 70px 70px;
}

.search-box {
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(200, 133, 26, 0.10);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.04);
}

/* ===== Feature Cards — 横向滚动 (移动端) ===== */
.feature-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom: 2px;
}

.feature-scroll::-webkit-scrollbar {
  display: none;
}

.feature-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(200, 133, 26, 0.08);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: all 0.2s ease;
  scroll-snap-align: start;
  flex-shrink: 0;
  white-space: nowrap;
}

@media (min-width: 1024px) {
  .feature-card {
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 14px 8px;
    gap: 6px;
  }
}

.feature-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.feature-card:active {
  transform: scale(0.97);
}

.feature-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

@media (min-width: 1024px) {
  .feature-icon-wrap {
    width: 36px;
    height: 36px;
    border-radius: 10px;
  }
}

.icon-bg-gold { background: rgba(200, 133, 26, 0.1); }
.icon-bg-vermilion { background: rgba(229, 77, 66, 0.1); }
.icon-bg-cyan { background: rgba(18, 170, 156, 0.1); }

.feature-label {
  font-size: 13px;
  font-weight: 500;
  color: #1D1D1F;
}

/* ===== 每日诗句卡片 ===== */
.daily-poem-card {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.75), rgba(245, 214, 138, 0.10));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(200, 133, 26, 0.12);
  box-shadow:
    0 2px 8px rgba(200, 133, 26, 0.06),
    inset 0 1px 2px rgba(0, 0, 0, 0.03);
}

.daily-poem-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.daily-label {
  font-size: 13px;
  font-weight: 600;
  color: #c8851a;
  padding: 2px 10px;
  background: rgba(200, 133, 26, 0.08);
  border-radius: 10px;
}

/* ===== 快捷入口卡片 ===== */
.quick-links-card {
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(200, 133, 26, 0.08);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.quick-link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  color: #6E6E73;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(200, 133, 26, 0.06);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  cursor: pointer;
  transition: all 0.15s ease;
  width: 100%;
  text-align: left;
}

.quick-link-item:hover {
  background: rgba(200, 133, 26, 0.05);
  color: #1D1D1F;
  border-color: rgba(200, 133, 26, 0.10);
}

.quick-link-item:active {
  transform: scale(0.97);
}
</style>

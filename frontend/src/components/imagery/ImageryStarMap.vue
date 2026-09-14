<template>
  <div class="star-map-container" ref="container">
    <!-- SVG 连线层 -->
    <svg class="connection-lines" :viewBox="svgViewBox" v-if="!isMobile">
      <line
        v-for="(line, idx) in connectionLines"
        :key="'line-' + idx"
        :x1="line.x1" :y1="line.y1"
        :x2="line.x2" :y2="line.y2"
        class="conn-line"
        :style="{ animationDelay: `${0.5 + idx * 0.1}s` }"
      />
    </svg>

    <!-- 中心节点：诗词标题 -->
    <div
      v-if="!isMobile"
      class="center-node"
      :style="centerStyle"
    >
      <span class="center-text">{{ title || '诗' }}</span>
    </div>

    <!-- 意象节点 — 桌面径向 / 移动竖向 -->
    <div :class="isMobile ? 'mobile-list' : 'radial-layout'">
      <div
        v-for="(node, idx) in nodes"
        :key="node.name"
        class="imagery-node"
        :class="[
          `node-color-${idx % 4}`,
          { 'node-selected': selectedNode === node.name },
        ]"
        :style="!isMobile ? getNodeStyle(idx) : {}"
        @click="$emit('select', node)"
      >
        <div class="node-inner">
          <span class="node-category">{{ node.category }}</span>
          <span class="node-name">{{ node.name }}</span>
        </div>
        <!-- 移动端连线指示 -->
        <div v-if="isMobile && node.connections?.length" class="mobile-connections">
          <span v-for="c in node.connections" :key="c" class="conn-tag">{{ c }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  nodes: { type: Array, required: true },
  title: { type: String, default: '' },
  selectedNode: { type: String, default: '' },
})

defineEmits(['select'])

const container = ref(null)
const isMobile = ref(false)
const mapSize = ref(360)

function checkMobile() {
  const w = container.value?.offsetWidth || window.innerWidth
  isMobile.value = w < 640
  mapSize.value = Math.min(w, 480)
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

const center = computed(() => mapSize.value / 2)
const radius = computed(() => mapSize.value * 0.35)

const svgViewBox = computed(() => `0 0 ${mapSize.value} ${mapSize.value}`)

const centerStyle = computed(() => ({
  left: `${center.value}px`,
  top: `${center.value}px`,
  transform: 'translate(-50%, -50%)',
}))

function getNodePosition(idx) {
  const count = props.nodes.length
  const angle = (2 * Math.PI * idx) / count - Math.PI / 2
  return {
    x: center.value + radius.value * Math.cos(angle),
    y: center.value + radius.value * Math.sin(angle),
  }
}

function getNodeStyle(idx) {
  const pos = getNodePosition(idx)
  return {
    left: `${pos.x}px`,
    top: `${pos.y}px`,
    transform: 'translate(-50%, -50%)',
    animationDelay: `${0.2 + idx * 0.15}s`,
  }
}

const connectionLines = computed(() => {
  const lines = []
  const nodeNames = props.nodes.map(n => n.name)

  props.nodes.forEach((node, idx) => {
    if (!node.connections) return
    node.connections.forEach(connName => {
      const targetIdx = nodeNames.indexOf(connName)
      if (targetIdx === -1 || targetIdx <= idx) return
      const from = getNodePosition(idx)
      const to = getNodePosition(targetIdx)
      lines.push({ x1: from.x, y1: from.y, x2: to.x, y2: to.y })
    })

    // 连到中心
    const pos = getNodePosition(idx)
    lines.push({ x1: center.value, y1: center.value, x2: pos.x, y2: pos.y })
  })

  return lines
})
</script>

<style scoped>
.star-map-container {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  max-width: 480px;
  margin: 0 auto;
}

/* SVG 连线 */
.connection-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.conn-line {
  stroke: rgba(200, 133, 26, 0.15);
  stroke-width: 1.5;
  stroke-dasharray: 4 3;
  opacity: 0;
  animation: lineAppear 0.5s ease forwards;
}

@keyframes lineAppear {
  to { opacity: 1; }
}

/* 中心节点 */
.center-node {
  position: absolute;
  z-index: 10;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #c8851a, #e54d42);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(200, 133, 26, 0.3);
  animation: nodeAppear 0.4s ease forwards;
  opacity: 0;
}

.center-text {
  font-family: 'Noto Serif SC', 'KaiTi', '楷体', serif;
  font-size: 16px;
  font-weight: 600;
  color: white;
}

/* 意象节点 — 径向布局 */
.radial-layout {
  position: relative;
  width: 100%;
  height: 100%;
}

.imagery-node {
  position: absolute;
  z-index: 10;
  cursor: pointer;
  opacity: 0;
  animation: nodeAppear 0.4s ease forwards;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.imagery-node:hover {
  transform: translate(-50%, -50%) scale(1.1) !important;
  z-index: 20;
}

.imagery-node.node-selected {
  transform: translate(-50%, -50%) scale(1.12) !important;
  z-index: 20;
}

.node-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 12px 16px;
  border-radius: 14px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1.5px solid transparent;
  min-width: 64px;
  text-align: center;
  transition: all 0.2s ease;
}

/* 4 色循环 */
.node-color-0 .node-inner {
  background: rgba(200, 133, 26, 0.12);
  border-color: rgba(200, 133, 26, 0.25);
}
.node-color-0.node-selected .node-inner,
.node-color-0:hover .node-inner {
  background: rgba(200, 133, 26, 0.2);
  box-shadow: 0 0 20px rgba(200, 133, 26, 0.2);
}

.node-color-1 .node-inner {
  background: rgba(229, 77, 66, 0.1);
  border-color: rgba(229, 77, 66, 0.25);
}
.node-color-1.node-selected .node-inner,
.node-color-1:hover .node-inner {
  background: rgba(229, 77, 66, 0.18);
  box-shadow: 0 0 20px rgba(229, 77, 66, 0.2);
}

.node-color-2 .node-inner {
  background: rgba(18, 170, 156, 0.1);
  border-color: rgba(18, 170, 156, 0.25);
}
.node-color-2.node-selected .node-inner,
.node-color-2:hover .node-inner {
  background: rgba(18, 170, 156, 0.18);
  box-shadow: 0 0 20px rgba(18, 170, 156, 0.2);
}

.node-color-3 .node-inner {
  background: rgba(91, 110, 75, 0.1);
  border-color: rgba(91, 110, 75, 0.25);
}
.node-color-3.node-selected .node-inner,
.node-color-3:hover .node-inner {
  background: rgba(91, 110, 75, 0.18);
  box-shadow: 0 0 20px rgba(91, 110, 75, 0.2);
}

.node-category {
  font-size: 10px;
  color: #AEAEB2;
  font-weight: 500;
}

.node-name {
  font-family: 'Noto Serif SC', 'KaiTi', '楷体', serif;
  font-size: 18px;
  font-weight: 600;
  color: #1D1D1F;
}

@keyframes nodeAppear {
  0% { opacity: 0; transform: translate(-50%, -50%) scale(0.6); }
  100% { opacity: 1; }
}

/* ===== 移动端列表模式 ===== */
.mobile-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mobile-list .imagery-node {
  position: relative;
  opacity: 0;
  animation: mobileNodeIn 0.3s ease forwards;
}

.mobile-list .imagery-node:hover {
  transform: scale(1.02) !important;
}

.mobile-list .imagery-node.node-selected {
  transform: scale(1.02) !important;
}

.mobile-list .node-inner {
  flex-direction: row;
  gap: 10px;
  padding: 14px 16px;
  justify-content: flex-start;
}

.mobile-list .node-category {
  font-size: 11px;
  min-width: 32px;
}

.mobile-list .node-name {
  font-size: 16px;
}

.mobile-connections {
  display: flex;
  gap: 4px;
  padding: 4px 16px 0;
}

.conn-tag {
  font-size: 11px;
  color: #AEAEB2;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.03);
}

@keyframes mobileNodeIn {
  0% { opacity: 0; transform: translateX(-12px); }
  100% { opacity: 1; transform: translateX(0); }
}

/* 移动端重置容器 */
@media (max-width: 639px) {
  .star-map-container {
    aspect-ratio: unset;
  }
}
</style>

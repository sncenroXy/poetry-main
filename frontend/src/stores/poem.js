import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePoemStore = defineStore('poem', () => {
  // 当前阅读的诗词（用于跨页面共享上下文）
  const currentPoem = ref(null)

  // 最近浏览历史
  const history = ref([])

  function setCurrentPoem(poem) {
    currentPoem.value = poem
    // 添加到历史记录，去重
    if (poem && poem.id) {
      history.value = [
        poem,
        ...history.value.filter(p => p.id !== poem.id)
      ].slice(0, 20) // 保留最近20条
    }
  }

  function clearHistory() {
    history.value = []
  }

  return {
    currentPoem,
    history,
    setCurrentPoem,
    clearHistory
  }
})

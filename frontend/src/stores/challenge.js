import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useChallengeStore = defineStore('challenge', () => {
  // 接龙游戏状态
  const chainScore = ref(0)
  const chainStreak = ref(0) // 连续正确数
  const chainMode = ref('classic') // 'classic' | 'ai'
  const chainHistory = ref([]) // AI 对战聊天记录

  // 答题游戏状态
  const quizScore = ref(0)
  const quizTotal = ref(0)
  const quizCorrect = ref(0)
  const quizResults = ref([]) // 每题答案记录，用于 AI 总结

  // 统计
  const totalChallenges = computed(() => chainScore.value + quizScore.value)

  // 接龙相关
  function addChainScore(points = 10) {
    chainScore.value += points
    chainStreak.value++
  }

  function resetChainStreak() {
    chainStreak.value = 0
  }

  function setChainMode(mode) {
    chainMode.value = mode
    chainHistory.value = []
  }

  function addChainMessage(msg) {
    // msg: { role: 'user'|'ai', content, title?, author?, type? }
    chainHistory.value.push(msg)
  }

  function clearChainHistory() {
    chainHistory.value = []
  }

  // 答题相关
  function recordQuizAnswer(isCorrect) {
    quizTotal.value++
    if (isCorrect) {
      quizCorrect.value++
      quizScore.value += 10
    }
  }

  function addQuizResult(result) {
    // result: { question, options, answer, user_answer, correct, type?, source? }
    quizResults.value.push(result)
  }

  function resetQuiz() {
    quizTotal.value = 0
    quizCorrect.value = 0
    quizResults.value = []
  }

  function resetAll() {
    chainScore.value = 0
    chainStreak.value = 0
    chainMode.value = 'classic'
    chainHistory.value = []
    quizScore.value = 0
    quizTotal.value = 0
    quizCorrect.value = 0
    quizResults.value = []
  }

  return {
    chainScore,
    chainStreak,
    chainMode,
    chainHistory,
    quizScore,
    quizTotal,
    quizCorrect,
    quizResults,
    totalChallenges,
    addChainScore,
    resetChainStreak,
    setChainMode,
    addChainMessage,
    clearChainHistory,
    recordQuizAnswer,
    addQuizResult,
    resetQuiz,
    resetAll
  }
})

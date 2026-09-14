import request from './index'

// ---------- 原有接口 ----------

/**
 * 获取接龙下句候选
 * @param {string} line 当前诗句
 */
export function getNextLines(line) {
  return request.get('/challenge/chain/next', { params: { line } })
}

/**
 * 校验接龙答案（精确匹配）
 * @param {string} current 当前诗句
 * @param {string} answer 用户答案
 */
export function validateChain(current, answer) {
  return request.post('/challenge/chain/validate', { current, answer })
}

/**
 * 生成答题题目（数据库）
 * @param {number} count 题目数量
 */
export function getQuiz(count = 3) {
  return request.get('/challenge/quiz', { params: { count } })
}

// ---------- AI 增强接口 ----------

/**
 * 飞花令 AI 渐进提示
 * @param {string} line 当前诗句
 * @param {number} level 提示级别 1-3
 */
export function getAIHint(line, level = 1) {
  return request.post('/challenge/chain/ai-hint', { line, level }, { timeout: 60000 })
}

/**
 * 飞花令 AI 语义校验
 * @param {string} current 当前诗句
 * @param {string} answer 用户答案
 */
export function aiValidateChain(current, answer) {
  return request.post('/challenge/chain/ai-validate', { current, answer }, { timeout: 60000 })
}

/**
 * 飞花令 AI 对战回合
 * @param {string} current 当前诗句
 */
export function aiChainTurn(current) {
  return request.post('/challenge/chain/ai-turn', { current }, { timeout: 60000 })
}

/**
 * AI 生成多种题型
 * @param {number} count 题目数量
 */
export function getAIQuiz(count = 5) {
  return request.post('/challenge/quiz/ai-generate', null, { params: { count }, timeout: 60000 })
}

/**
 * AI 解析单题
 * @param {object} question 题目对象
 * @param {number} userAnswer 用户选择的选项索引
 */
export function aiExplainAnswer(question, userAnswer) {
  return request.post('/challenge/quiz/ai-explain', { question, user_answer: userAnswer }, { timeout: 60000 })
}

/**
 * AI 答题总结分析
 * @param {Array} results 答题记录列表
 */
export function aiQuizSummary(results) {
  return request.post('/challenge/quiz/ai-summary', { results }, { timeout: 60000 })
}

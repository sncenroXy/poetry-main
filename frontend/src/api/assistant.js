import request from './index'

/**
 * AI 诗词助手对话
 * @param {string} message 用户消息
 * @param {Array<{role: string, content: string}>} history 对话历史
 * @returns {{ reply: string, fallback?: boolean }}
 */
export function chatWithAssistant(message, history = []) {
  return request.post('/assistant/chat', { message, history }, { timeout: 60000 })
}

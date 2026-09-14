import request from './index'

/**
 * 生成诗词
 * @param {Object} params
 * @param {string} params.scene 场景
 * @param {string} params.emotion 情感
 * @param {string} params.style 风格
 * @param {string[]} params.images 意象列表
 * @param {number} params.count 生成数量
 */
export function generatePoem(params) {
  return request.post('/generate', params, { timeout: 60000 })
}

/**
 * 轻度优化诗词
 * @param {string} id 诗词ID
 */
export function optimizePoem(id) {
  return request.post('/generate/optimize', { id }, { timeout: 60000 })
}

/**
 * 仿写诗词
 * @param {Object} params
 * @param {string} params.draft 草稿/原文
 * @param {string} params.scene 场景
 * @param {string} params.emotion 情感
 * @param {string} params.style 风格
 */
export function mimicPoem(params) {
  return request.post('/generate/mimic', params, { timeout: 60000 })
}

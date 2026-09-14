import request from './index'

/**
 * 文生图：诗词生成配图
 * @param {Object} params
 * @param {string} params.poem_text 诗词文本
 * @param {string} params.title 诗词标题
 * @param {string} params.style 图片风格
 */
export function generateImage(params) {
  return request.post('/image/generate', params, { timeout: 120000 })
}

/**
 * 图生文：图片生成诗词
 * @param {Object} params
 * @param {string} params.image base64 编码的图片
 * @param {string} params.style 诗词风格
 * @param {string} params.emotion 情感基调
 */
export function generatePoemFromImage(params) {
  return request.post('/image/poem', params, { timeout: 120000 })
}

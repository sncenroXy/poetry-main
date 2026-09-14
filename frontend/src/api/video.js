import request from './index'

/**
 * 提交视频生成任务
 * @param {Object} params
 * @param {string} params.poem_text 诗词文本
 * @param {string} params.title 诗词标题
 * @param {string} params.style 视频风格
 */
export function submitVideoTask(params) {
  return request.post('/video/generate', params, { timeout: 60000 })
}

/**
 * 查询视频生成状态
 * @param {string} taskId 任务 ID
 */
export function queryVideoStatus(taskId) {
  return request.get(`/video/status/${taskId}`, { timeout: 30000 })
}

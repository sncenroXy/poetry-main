import request from './index'

/**
 * 分析诗词意象
 * @param {{ poem_text: string, title?: string, author?: string, poem_id?: string }} params
 * @returns {{ poem_summary: string, imagery_nodes: Array }}
 */
export function analyzeImagery(params) {
  return request.post('/imagery/analyze', params, { timeout: 180000 })
}

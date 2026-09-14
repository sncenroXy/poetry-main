import request from './index'

/**
 * 通用检索（分页）
 * @param {string} q 关键词
 * @param {number} page 页码
 * @param {number} pageSize 每页条数
 * @returns {{ items: Array, total: number, page: number, page_size: number }}
 */
export function searchPoems(q, page = 1, pageSize = 18) {
  return request.get('/search', { params: { q, page, page_size: pageSize } })
}

/**
 * 获取所有诗词列表（分页，支持分类筛选）
 * @param {number} page 页码
 * @param {number} pageSize 每页条数
 * @param {Object} filters 筛选条件 { dynasty, genre, author, tag }
 * @returns {{ items: Array, total: number, page: number, page_size: number }}
 */
export function getAllPoems(page = 1, pageSize = 18, filters = {}) {
  const params = { page, page_size: pageSize }
  if (filters.dynasty) params.dynasty = filters.dynasty
  if (filters.genre) params.genre = filters.genre
  if (filters.author) params.author = filters.author
  if (filters.tag) params.tag = filters.tag
  return request.get('/poems', { params })
}

/**
 * 获取诗词筛选项（朝代、体裁、作者、标签）
 * @returns {{ dynasties: string[], genres: string[], authors: string[], tags: string[] }}
 */
export function getFilterOptions() {
  return request.get('/poems/filters')
}

/**
 * 获取诗词简洁详情
 * @param {string} id 诗词ID
 */
export function getPoemById(id) {
  return request.get(`/poems/${id}`)
}

/**
 * 获取诗词鉴赏详情（含原文、译文、赏析）
 * @param {string} id 诗词ID
 */
export function getPoemDetail(id) {
  return request.get(`/poem/${id}/detail`)
}

/**
 * 按作者名检索诗词（分页）
 * @param {string} name 作者名
 * @param {number} page 页码
 * @param {number} pageSize 每页条数
 * @returns {{ items: Array, total: number, page: number, page_size: number }}
 */
export function getPoemsByAuthor(name, page = 1, pageSize = 18) {
  return request.get(`/authors/${encodeURIComponent(name)}/poems`, { params: { page, page_size: pageSize } })
}

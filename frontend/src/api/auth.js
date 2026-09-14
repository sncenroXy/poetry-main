import request from './index'

/**
 * 用户登录（预留）
 * @param {string} username
 * @param {string} password
 */
export function login(username, password) {
  return request.post('/auth/login', { username, password })
}

/**
 * 用户注册（预留）
 * @param {Object} data
 */
export function register(data) {
  return request.post('/auth/register', data)
}

/**
 * 获取当前用户信息（预留）
 */
export function getUserInfo() {
  return request.get('/auth/user')
}

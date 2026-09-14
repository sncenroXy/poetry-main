import axios from 'axios'
import { getToken, removeToken } from '@/utils/storage'
import { showToast } from 'vant'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data
    // 后端统一返回格式 Result<T> { code, msg, data }
    if (res.code === 1) {
      return res.data
    }
    // 业务错误：不弹 toast，交给组件自行处理
    return Promise.reject(new Error(res.msg || '请求失败'))
  },
  (error) => {
    if (error.response) {
      const { status } = error.response
      if (status === 401) {
        removeToken()
        showToast('登录已过期，请重新登录')
      }
      // 其他 HTTP 错误（如 500）不弹 toast，交给组件处理
    }
    // 网络错误也不弹 toast，交给组件处理
    return Promise.reject(error)
  }
)

export default request

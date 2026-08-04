import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 优先读取 VITE_API_BASE_URL，默认使用同源 /api（生产环境由 nginx 代理到后端内网域名）
const http = axios.create({ baseURL: API_BASE_URL, timeout: 60000 })

// ---------- 标签 ----------
export const tagApi = {
  list: () => http.get('/tags').then((r) => r.data),
  create: (payload) => http.post('/tags', payload).then((r) => r.data),
  update: (id, payload) => http.put(`/tags/${id}`, payload).then((r) => r.data),
  remove: (id) => http.delete(`/tags/${id}`),
  toggle: (id) => http.post(`/tags/${id}/toggle`).then((r) => r.data),
  triggerFetch: (id) => http.post(`/tags/${id}/fetch`).then((r) => r.data),
}

// ---------- 热点 ----------
export const itemApi = {
  list: (params) => http.get('/hot-items', { params }).then((r) => r.data),
  resetData: () => http.delete('/admin/reset-data').then((r) => r.data),
}

// ---------- 趋势 ----------
export const trendApi = {
  trend: (tagId, days = 7) => http.get(`/tags/${tagId}/trend`, { params: { days } }).then((r) => r.data),
  distribution: (tagId) => http.get(`/tags/${tagId}/platform-distribution`).then((r) => r.data),
}

// ---------- 任务日志 ----------
export const jobApi = {
  list: (params) => http.get('/jobs', { params }).then((r) => r.data),
}

// ---------- 元信息 ----------
export const metaApi = {
  health: () => http.get('/health').then((r) => r.data),
}

/**
 * API 统一封装 — 全部对接 Django 后端
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const request = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

/** 短时间相同错误只提示一次，避免首屏并发 503 刷屏 */
let lastErrorKey = ''
let lastErrorAt = 0
function showErrorOnce(message, ttlMs = 2500) {
  const now = Date.now()
  const key = String(message || '')
  if (key && key === lastErrorKey && now - lastErrorAt < ttlMs) return
  lastErrorKey = key
  lastErrorAt = now
  ElMessage.error(key || '请求失败')
}

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== 200) {
      showErrorOnce(res.msg || '请求失败')
      return Promise.reject(new Error(res.msg))
    }
    return res
  },
  (error) => {
    const status = error.response?.status
    const msg = error.response?.data?.msg
    if (status === 403) {
      showErrorOnce(msg || '暂无操作权限')
    } else if (status === 409) {
      return Promise.reject(new Error(msg || '请求冲突'))
    } else if (status === 401) {
      showErrorOnce(msg || '登录已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 触发下次路由守卫重新鉴权；若已在登录页则不跳转
      if (!window.location.pathname.startsWith('/login')) {
        const redirect = encodeURIComponent(window.location.pathname + window.location.search)
        window.location.assign(`/login?redirect=${redirect}`)
      }
    } else if (status === 503) {
      showErrorOnce(msg || '服务暂时繁忙，请稍后重试')
    } else if (msg) {
      showErrorOnce(msg)
    } else if (error.code === 'ERR_NETWORK') {
      showErrorOnce('无法连接后端，请确认 Django 服务已启动（端口 8000）')
    } else {
      showErrorOnce(error.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

const api = {
  // ========== 认证 ==========
  createLoginTicket: () => request.post('/auth/login-ticket/'),
  pollLoginTicket: (ticketId) => request.get(`/auth/login-ticket/${ticketId}/`),
  simulateScanLogin: (ticketId, userId) =>
    request.post(`/auth/login-ticket/${ticketId}/simulate/`, userId ? { user_id: userId } : {}),
  logout: () => request.post('/auth/logout/'),
  getUserInfo: () => request.get('/auth/me/'),
  passwordLogin: (data) => request.post('/auth/login/', data),
  passwordRegister: (data) => request.post('/auth/register/', data),
  devLogin: (role) => request.post('/auth/dev/login/', { role }),
  getAdminUsers: (params) => request.get('/admin/users/', { params }),
  grantStaff: (userId) => request.post(`/admin/users/${userId}/grant-staff/`),
  revokeStaff: (userId) => request.post(`/admin/users/${userId}/revoke-staff/`),
  banUser: (userId, data) => request.post(`/admin/users/${userId}/ban/`, data),
  unbanUser: (userId) => request.post(`/admin/users/${userId}/unban/`),
  deleteUser: (userId, data) => request.post(`/admin/users/${userId}/delete/`, data),

  // ========== 入驻 / 上传 ==========
  uploadImage: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/uploads/image/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  submitApplication: (data) => request.post('/applications/', data),
  getMyApplication: () => request.get('/applications/my/'),
  getShopApplications: (params) => request.get('/admin/applications/', { params }),
  auditShop: (id, data) => request.post(`/admin/applications/${id}/audit/`, data),

  // ========== 品牌字典 ==========
  getBrands: () => request.get('/brands/'),
  getModels: (brandId) => request.get(`/brands/${brandId}/models/`),

  // ========== C 端商家 / 车源 ==========
  getBikeList: () => Promise.resolve({ code: 200, msg: 'success', data: { list: [], total: 0 } }),
  getBikeDetail: (id, params) => request.get(`/bikes/${id}/`, { params }),
  getShopDetail: (id, params) => request.get(`/shops/${id}/`, { params }),

  // ========== 收藏 ==========
  getFavorites: () => request.get('/favorites/'),
  addFavorite: (bikeId) => request.post('/favorites/', { bike_id: bikeId }),
  removeFavorite: (bikeId) => request.delete(`/favorites/${bikeId}/`),

  // ========== 留言 ==========
  getUserMessageThreads: () => request.get('/message-threads/'),
  getMyMessageThreads: (params) => request.get('/shop/message-threads/', { params }),
  getMyMessages: (params) => request.get('/shop/message-threads/', { params }),
  getMessageThread: (id) => request.get(`/message-threads/${id}/`),
  sendMessage: (id, data) => request.post(`/message-threads/${id}/messages/`, data),
  createMessageThread: (data) => request.post('/message-threads/', data),
  submitMessage: (data) => request.post('/message-threads/', data),
  replyMessage: (id, data) => request.post(`/message-threads/${id}/messages/`, data),
  markThreadRead: (id, role) => request.post(`/message-threads/${id}/read/`, { role }),
  getUnreadCount: (role = 'user') => request.get('/messages/unread-count/', { params: { role } }),
  getAllMessages: (params) => request.get('/admin/message-threads/', { params }),
  resolveShareLink: (code) => request.get(`/s/${code}/`),

  // ========== 最近访问 ==========
  getVisitedShops: () => request.get('/visits/'),
  recordVisit: (shopId) => request.post('/visits/', { shop_id: shopId }),

  // ========== 商家后台 ==========
  getMyBikes: (params) => request.get('/shop/bikes/', { params }),
  getShopBike: (id) => request.get(`/shop/bikes/${id}/`),
  createBike: (data) => request.post('/shop/bikes/', data),
  updateBike: (id, data) => request.put(`/shop/bikes/${id}/`, data),
  offShelfBike: (id) => request.post(`/shop/bikes/${id}/off-shelf/`),
  onShelfBike: (id) => request.post(`/shop/bikes/${id}/on-shelf/`),
  markSoldBike: (id) => request.post(`/shop/bikes/${id}/mark-sold/`),
  createBikeShareLink: (id) => request.post(`/shop/bikes/${id}/share-link/`),
  deleteBike: (id) => request.delete(`/shop/bikes/${id}/`),
  getShopProfile: () => request.get('/shop/profile/'),
  updateShopProfile: (data) => request.put('/shop/profile/', data),
  getShopStats: () => request.get('/shop/stats/'),

  // ========== 管理端 ==========
  getAllShops: (params) => request.get('/admin/shops/', { params }),
  banShop: (id) => request.post(`/admin/shops/${id}/ban/`),
  unbanShop: (id) => request.post(`/admin/shops/${id}/unban/`),
  deleteShop: (id) => request.delete(`/admin/shops/${id}/`),
  getAllBikes: (params) => request.get('/admin/bikes/', { params }),
  forceOffShelf: (id, data) => request.post(`/admin/bikes/${id}/force-off-shelf/`, data || {}),
  restoreBike: (id) => request.post(`/admin/bikes/${id}/restore/`),
  adminDeleteBike: (id) => request.delete(`/admin/bikes/${id}/`),
  getAdminStats: () => request.get('/admin/stats/'),
}

export default api

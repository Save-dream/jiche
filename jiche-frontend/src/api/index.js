/**
 * API 统一封装
 * 开发阶段使用 Mock 数据，生产环境替换 USE_MOCK = false 并配置 BASE_URL
 */
import axios from 'axios'
import { mockApi } from './mock'
import { ElMessage } from 'element-plus'

const USE_MOCK = true
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// ==================== Axios 实例 ====================
const request = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截：附加 token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截：统一错误处理
request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.msg || '请求失败')
      return Promise.reject(new Error(res.msg))
    }
    return res
  },
  (error) => {
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('token')
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      ElMessage.error('暂无操作权限')
    } else {
      ElMessage.error(error.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

// ==================== API 函数 ====================
// USE_MOCK = true 时使用 mock，false 时使用真实接口

const api = USE_MOCK
  ? mockApi
  : {
      // 真实接口（生产环境填写）
      getBikeList: (params) => request.get('/bikes/', { params }),
      getBikeDetail: (id) => request.get(`/bikes/${id}/`),
      getShopDetail: (id) => request.get(`/shops/${id}/`),
      getMyBikes: (params) => request.get('/shop/bikes/', { params }),
      getMyMessages: (params) => request.get('/shop/messages/', { params }),
      getAllMessages: (params) => request.get('/admin/messages/', { params }),
      getShopApplications: (params) => request.get('/admin/applications/', { params }),
      getAllShops: (params) => request.get('/admin/shops/', { params }),
      getAllBikes: (params) => request.get('/admin/bikes/', { params }),
      getBrands: () => request.get('/brands/'),
      getModels: (brandId) => request.get(`/brands/${brandId}/models/`),
      getShopStats: () => request.get('/shop/stats/'),
      getAdminStats: () => request.get('/admin/stats/'),

      // 用户认证
      login: (data) => request.post('/auth/login/', data),
      logout: () => request.post('/auth/logout/'),
      getUserInfo: () => request.get('/auth/me/'),

      // 商家入驻
      submitApplication: (data) => request.post('/applications/', data),
      getMyApplication: () => request.get('/applications/my/'),

      // 车辆操作
      createBike: (data) => request.post('/shop/bikes/', data),
      updateBike: (id, data) => request.put(`/shop/bikes/${id}/`, data),
      offShelfBike: (id) => request.post(`/shop/bikes/${id}/off-shelf/`),
      deleteBike: (id) => request.delete(`/shop/bikes/${id}/`),

      // 留言
      submitMessage: (data) => request.post('/messages/', data),
      replyMessage: (id, data) => request.post(`/messages/${id}/reply/`, data),

      // 收藏
      getFavorites: () => request.get('/favorites/'),
      addFavorite: (bikeId) => request.post('/favorites/', { bike_id: bikeId }),
      removeFavorite: (bikeId) => request.delete(`/favorites/${bikeId}/`),

      // 管理员
      auditShop: (id, data) => request.post(`/admin/applications/${id}/audit/`, data),
      banShop: (id) => request.post(`/admin/shops/${id}/ban/`),
      unbanShop: (id) => request.post(`/admin/shops/${id}/unban/`),
      forceOffShelf: (id) => request.post(`/admin/bikes/${id}/force-off-shelf/`),
      restoreBike: (id) => request.post(`/admin/bikes/${id}/restore/`),
    }

export default api

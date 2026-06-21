import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 状态枚举映射（仅做展示映射，枚举值来自后端）
export const SHOP_STATUS = {
  0: { label: '普通用户', type: 'info' },
  1: { label: '待审核', type: 'warning' },
  2: { label: '已入驻', type: 'success' },
  3: { label: '审核驳回', type: 'danger' },
  4: { label: '已封禁', type: 'danger' },
}

export const BIKE_STATUS = {
  1: { label: '在售', type: 'success' },
  2: { label: '已售', type: 'danger' },
  3: { label: '已下架', type: 'info' },
  4: { label: '违规下架', type: 'danger' },
}

export const MESSAGE_STATUS = {
  1: { label: '未读', type: 'danger' },
  2: { label: '已读未回复', type: 'warning' },
  3: { label: '已回复', type: 'success' },
}

export const useAuthStore = defineStore('auth', () => {
  // 用户信息（Mock 默认为已入驻商家，方便开发调试）
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null') || {
    id: 1,
    username: 'demo_shop',
    nickname: '极速摩托行老板',
    phone: '13800138001',
    shop_status: 2,    // 0普通 1待审核 2已入驻 3驳回 4封禁
    is_staff: false,   // 管理员标志
    shop_id: 1,
  })

  const isLoggedIn = computed(() => !!user.value)
  const isShop = computed(() => user.value?.shop_status === 2)
  const isAdmin = computed(() => user.value?.is_staff === true)
  const shopStatus = computed(() => user.value?.shop_status ?? 0)

  function setUser(userInfo) {
    user.value = userInfo
    localStorage.setItem('user', JSON.stringify(userInfo))
  }

  function logout() {
    user.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  // 切换角色（开发调试用）
  function switchRole(role) {
    if (role === 'user') {
      setUser({ id: 100, username: 'c_user', nickname: '普通用户', phone: '13600000001', shop_status: 0, is_staff: false })
    } else if (role === 'pending') {
      setUser({ id: 101, username: 'pending_user', nickname: '待审核商家', phone: '13600000002', shop_status: 1, is_staff: false })
    } else if (role === 'shop') {
      setUser({ id: 1, username: 'demo_shop', nickname: '极速摩托行老板', phone: '13800138001', shop_status: 2, is_staff: false, shop_id: 1 })
    } else if (role === 'admin') {
      setUser({ id: 999, username: 'admin', nickname: '平台管理员', phone: '13999999999', shop_status: 0, is_staff: true })
    }
  }

  // 收藏列表（本地缓存）
  const favorites = ref(new Set(JSON.parse(localStorage.getItem('favorites') || '[]')))

  function toggleFavorite(bikeId) {
    if (favorites.value.has(bikeId)) {
      favorites.value.delete(bikeId)
    } else {
      favorites.value.add(bikeId)
    }
    localStorage.setItem('favorites', JSON.stringify([...favorites.value]))
  }

  function isFavorite(bikeId) {
    return favorites.value.has(bikeId)
  }

  return {
    user, isLoggedIn, isShop, isAdmin, shopStatus,
    setUser, logout, switchRole,
    favorites, toggleFavorite, isFavorite,
  }
})

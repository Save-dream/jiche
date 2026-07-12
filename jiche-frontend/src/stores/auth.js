import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!user.value && !!token.value)
  const isShop = computed(() => user.value?.shop_status === 2)
  const isAdmin = computed(() => user.value?.is_staff === true)
  const shopStatus = computed(() => user.value?.shop_status ?? 0)

  // 多租户：当前访问的商家域（分享链接写入）
  const currentShopId = ref(Number(localStorage.getItem('currentShopId') || 0) || null)

  function setCurrentShopId(shopId) {
    if (!shopId) return
    currentShopId.value = Number(shopId)
    localStorage.setItem('currentShopId', String(shopId))
    recordVisitedShop(Number(shopId))
  }

  // 最近访问商家
  const visitedShops = ref(JSON.parse(localStorage.getItem('visitedShops') || '[]'))

  function recordVisitedShop(shopId) {
    const entry = { id: shopId, visited_at: new Date().toISOString() }
    visitedShops.value = [entry, ...visitedShops.value.filter(s => s.id !== shopId)].slice(0, 10)
    localStorage.setItem('visitedShops', JSON.stringify(visitedShops.value))
  }

  async function syncVisit(shopId, api) {
    if (!shopId) return
    recordVisitedShop(Number(shopId))
    if (!token.value || token.value.startsWith('mock_token_') || !api?.recordVisit) return
    try {
      await api.recordVisit(Number(shopId))
    } catch { /* 未登录或网络错误时保留本地记录 */ }
  }

  async function loadVisitedShops(api) {
    if (!token.value || token.value.startsWith('mock_token_') || !api?.getVisitedShops) {
      return visitedShops.value
    }
    try {
      const res = await api.getVisitedShops()
      const list = (res.data?.list || []).map((item) => ({
        id: item.id,
        name: item.name,
        visited_at: item.last_visited_at,
      }))
      if (list.length) {
        visitedShops.value = list
        localStorage.setItem('visitedShops', JSON.stringify(list))
      }
      return list
    } catch {
      return visitedShops.value
    }
  }

  function setToken(newToken) {
    token.value = newToken
    if (newToken) localStorage.setItem('token', newToken)
    else localStorage.removeItem('token')
  }

  function setUser(userInfo) {
    user.value = userInfo
    if (userInfo) localStorage.setItem('user', JSON.stringify(userInfo))
    else localStorage.removeItem('user')
  }

  function loginSession({ token: newToken, user: userInfo }) {
    setToken(newToken)
    setUser(userInfo)
  }

  async function restoreSession(api) {
    if (!token.value) return
    // 旧版前端 Dev 切换产生的假 token，后端 JWT 无法识别
    if (token.value.startsWith('mock_token_')) {
      logout()
      return
    }
    try {
      const res = await api.getUserInfo()
      setUser(res.data)
      await Promise.all([loadFavorites(api), loadUnreadMessages(api)])
    } catch {
      logout()
    }
  }

  async function refreshUser(api) {
    if (!token.value) return null
    if (token.value.startsWith('mock_token_')) {
      logout()
      return null
    }
    try {
      const res = await api.getUserInfo()
      setUser(res.data)
      await Promise.all([loadFavorites(api), loadUnreadMessages(api)])
      return res.data
    } catch {
      logout()
      return null
    }
  }

  async function switchRole(role, api) {
    if (!api?.devLogin) {
      throw new Error('开发登录接口不可用')
    }
    const res = await api.devLogin(role)
    loginSession({ token: res.data.token, user: res.data.user })
    await Promise.all([loadFavorites(api), loadUnreadMessages(api)])
  }

  const favorites = ref(new Set())

  async function loadFavorites(api) {
    if (!token.value || token.value.startsWith('mock_token_') || !api?.getFavorites) return
    try {
      const res = await api.getFavorites()
      favorites.value = new Set((res.data?.list || []).map((b) => b.id))
      persistFavorites()
    } catch { /* ignore */ }
  }

  async function toggleFavorite(bikeId, api) {
    if (favorites.value.has(bikeId)) {
      if (api?.removeFavorite) await api.removeFavorite(bikeId)
      favorites.value.delete(bikeId)
      persistFavorites()
      return 'removed'
    }
    try {
      if (api?.addFavorite) await api.addFavorite(bikeId)
      favorites.value.add(bikeId)
      persistFavorites()
      return 'added'
    } catch (err) {
      if (String(err.message || '').includes('已在收藏夹中')) {
        favorites.value.add(bikeId)
        persistFavorites()
        return 'already'
      }
      throw err
    }
  }

  async function removeFavorite(bikeId, api) {
    if (api?.removeFavorite) await api.removeFavorite(bikeId)
    favorites.value.delete(bikeId)
    persistFavorites()
  }

  function persistFavorites() {
    localStorage.setItem('favorites', JSON.stringify([...favorites.value]))
  }

  function isFavorite(bikeId) {
    return favorites.value.has(bikeId)
  }

  const favoriteIds = computed(() => [...favorites.value])

  const userUnreadMessages = ref(0)

  function syncUnreadFromThreads(threads, role = 'user') {
    const field = role === 'shop' ? 'unread_count_shop' : 'unread_count_user'
    userUnreadMessages.value = (threads || []).reduce((sum, t) => sum + (t[field] || 0), 0)
  }

  async function loadUnreadMessages(api, role = 'auto') {
    if (!token.value || token.value.startsWith('mock_token_')) {
      userUnreadMessages.value = 0
      return
    }
    // 已入驻商家：角标 = 我发起的未读 + 用户对我的未读
    const effectiveRole = role === 'auto'
      ? (isShop.value ? 'combined' : 'user')
      : role
    if (api?.getUnreadCount) {
      try {
        if (effectiveRole === 'combined') {
          const [mine, inbox] = await Promise.all([
            api.getUnreadCount('user'),
            api.getUnreadCount('shop'),
          ])
          userUnreadMessages.value =
            (mine.data?.unread_count || 0) + (inbox.data?.unread_count || 0)
          return
        }
        const res = await api.getUnreadCount(effectiveRole)
        userUnreadMessages.value = res.data?.unread_count || 0
        return
      } catch {
        /* fallback below */
      }
    }
    const fetcher = effectiveRole === 'shop' ? api?.getMyMessageThreads : api?.getUserMessageThreads
    if (!fetcher) {
      userUnreadMessages.value = 0
      return
    }
    try {
      const res = await fetcher()
      syncUnreadFromThreads(res.data?.list || [], effectiveRole === 'shop' ? 'shop' : 'user')
    } catch {
      userUnreadMessages.value = 0
    }
  }

  function logout() {
    user.value = null
    setToken('')
    localStorage.removeItem('user')
    userUnreadMessages.value = 0
  }

  return {
    user, token, isLoggedIn, isShop, isAdmin, shopStatus,
    currentShopId, visitedShops, favoriteIds, userUnreadMessages,
    setUser, setToken, loginSession, logout, restoreSession, refreshUser, switchRole,
    setCurrentShopId, recordVisitedShop, syncVisit, loadVisitedShops,
    favorites, toggleFavorite, removeFavorite, isFavorite, loadFavorites,
    loadUnreadMessages, syncUnreadFromThreads,
  }
})

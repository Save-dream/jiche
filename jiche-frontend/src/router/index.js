import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { guestOnly: true },
  },
  {
    // 短链解析页允许未登录访问，解析后再按目标页鉴权并带回跳
    path: '/s/:code',
    name: 'ShareRedirect',
    component: () => import('@/views/user/ShareRedirect.vue'),
    meta: { allowAnonymous: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/UserLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Home', component: () => import('@/views/user/Home.vue') },
      { path: 'bike/:id', name: 'BikeDetail', component: () => import('@/views/user/BikeDetail.vue') },
      { path: 'shop/:id', name: 'ShopHome', component: () => import('@/views/user/ShopHome.vue') },
      { path: 'favorites', name: 'Favorites', component: () => import('@/views/user/Favorites.vue') },
      { path: 'messages', name: 'UserMessages', component: () => import('@/views/user/MyMessages.vue') },
      { path: 'messages/:threadId', name: 'UserChat', component: () => import('@/views/user/ChatDetail.vue'), meta: { chatRole: 'user' } },
      { path: 'profile', name: 'Profile', component: () => import('@/views/user/Profile.vue') },
      { path: 'apply-shop', name: 'ApplyShop', component: () => import('@/views/user/ApplyShop.vue') },
    ],
  },
  {
    path: '/shop',
    component: () => import('@/layouts/ShopLayout.vue'),
    meta: { requiresShop: true, requiresAuth: true },
    children: [
      { path: '', redirect: '/shop/dashboard' },
      { path: 'dashboard', name: 'ShopDashboard', component: () => import('@/views/shop/Dashboard.vue') },
      { path: 'bikes', name: 'ShopBikeList', component: () => import('@/views/shop/BikeList.vue') },
      { path: 'bikes/new', name: 'ShopBikeNew', component: () => import('@/views/shop/BikeForm.vue') },
      { path: 'bikes/:id/edit', name: 'ShopBikeEdit', component: () => import('@/views/shop/BikeForm.vue') },
      { path: 'messages', name: 'ShopMessages', component: () => import('@/views/shop/Messages.vue') },
      { path: 'messages/:threadId', name: 'ShopChat', component: () => import('@/views/user/ChatDetail.vue'), meta: { chatRole: 'shop' } },
      { path: 'profile', name: 'ShopProfile', component: () => import('@/views/shop/ShopProfile.vue') },
    ],
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAdmin: true, requiresAuth: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'audit', name: 'AdminShopAudit', component: () => import('@/views/admin/ShopAudit.vue') },
      { path: 'shops', name: 'AdminShopManage', component: () => import('@/views/admin/ShopManage.vue') },
      { path: 'bikes', name: 'AdminBikeControl', component: () => import('@/views/admin/BikeControl.vue') },
      { path: 'messages', name: 'AdminMessages', component: () => import('@/views/admin/MessageView.vue') },
      { path: 'users', name: 'AdminUsers', component: () => import('@/views/admin/AdminUsers.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

function defaultHome(auth) {
  if (auth.isAdmin) return '/admin/dashboard'
  if (auth.isShop) return '/shop/dashboard'
  return '/'
}

/**
 * 进入受保护页面前，用服务端 /auth/me/ 校验 token。
 * 另一浏览器无 token → 登录页；token 无效/过期 → 清会话并登录；
 * 已登录但无管理员/商家权限 → 回用户首页。
 */
router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const needsAuth = to.matched.some((r) => r.meta.requiresAuth)
  const allowAnonymous = to.matched.some((r) => r.meta.allowAnonymous)
  const guestOnly = to.matched.some((r) => r.meta.guestOnly)
  const needsAdmin = to.matched.some((r) => r.meta.requiresAdmin)
  const needsShop = to.matched.some((r) => r.meta.requiresShop)

  if (guestOnly && auth.isLoggedIn) {
    const redirect = to.query.redirect
    if (redirect && typeof redirect === 'string' && redirect.startsWith('/')) {
      return redirect
    }
    return defaultHome(auth)
  }

  if (allowAnonymous && !needsAuth) {
    return true
  }

  // 需要登录：先确保服务端会话有效（localStorage 不能单独当真）
  if (needsAuth || needsAdmin || needsShop) {
    if (!auth.token) {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
    const user = await auth.refreshUser(api)
    if (!user) {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
  }

  if (to.name === 'ApplyShop' && auth.isAdmin) {
    return { path: '/admin/audit' }
  }

  if (needsAdmin && !auth.isAdmin) {
    if (!auth.isLoggedIn) {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
    return { path: '/', query: { msg: '需要管理员权限' } }
  }

  if (needsShop && !auth.isShop) {
    if (!auth.isLoggedIn) {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
    // 无商家权限：回用户首页（非商家后台）
    return { path: '/', query: { msg: '请先完成商家入驻审核' } }
  }

  if (to.name === 'ShopHome' && to.params.id) {
    auth.setCurrentShopId(to.params.id)
    auth.syncVisit(to.params.id, api)
  }
  if (to.name === 'BikeDetail' && to.query.shop_id) {
    auth.setCurrentShopId(to.query.shop_id)
    auth.syncVisit(to.query.shop_id, api)
  }
})

export default router

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
    path: '/s/:code',
    name: 'ShareRedirect',
    component: () => import('@/views/user/ShareRedirect.vue'),
  },
  {
    path: '/',
    component: () => import('@/layouts/UserLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('@/views/user/Home.vue') },
      { path: 'bike/:id', name: 'BikeDetail', component: () => import('@/views/user/BikeDetail.vue') },
      { path: 'shop/:id', name: 'ShopHome', component: () => import('@/views/user/ShopHome.vue') },
      { path: 'favorites', name: 'Favorites', component: () => import('@/views/user/Favorites.vue'), meta: { requiresAuth: true } },
      { path: 'messages', name: 'UserMessages', component: () => import('@/views/user/MyMessages.vue'), meta: { requiresAuth: true } },
      { path: 'messages/:threadId', name: 'UserChat', component: () => import('@/views/user/ChatDetail.vue'), meta: { requiresAuth: true, chatRole: 'user' } },
      { path: 'profile', name: 'Profile', component: () => import('@/views/user/Profile.vue') },
      { path: 'apply-shop', name: 'ApplyShop', component: () => import('@/views/user/ApplyShop.vue'), meta: { requiresAuth: true } },
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

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.guestOnly && auth.isLoggedIn) {
    const redirect = to.query.redirect
    return redirect && typeof redirect === 'string' ? redirect : '/'
  }

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (to.name === 'ApplyShop' && auth.isAdmin) {
    return { path: '/admin/audit' }
  }

  if (to.meta.requiresAdmin && !auth.isAdmin) {
    if (!auth.isLoggedIn) {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
    return { path: '/', query: { msg: '需要管理员权限' } }
  }
  if (to.meta.requiresShop && !auth.isShop) {
    if (!auth.isLoggedIn) {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
    return { path: '/profile', query: { msg: '请先完成商家入驻审核' } }
  }

  // 多租户：进入商家域页面时记录 shop_id
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

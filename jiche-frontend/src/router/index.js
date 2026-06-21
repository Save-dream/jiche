import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // ==================== C端用户区 ====================
  {
    path: '/',
    component: () => import('@/layouts/UserLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('@/views/user/Home.vue') },
      { path: 'bike/:id', name: 'BikeDetail', component: () => import('@/views/user/BikeDetail.vue') },
      { path: 'shop/:id', name: 'ShopHome', component: () => import('@/views/user/ShopHome.vue') },
      { path: 'favorites', name: 'Favorites', component: () => import('@/views/user/Favorites.vue'), meta: { requiresAuth: true } },
      { path: 'profile', name: 'Profile', component: () => import('@/views/user/Profile.vue'), meta: { requiresAuth: true } },
      { path: 'apply-shop', name: 'ApplyShop', component: () => import('@/views/user/ApplyShop.vue'), meta: { requiresAuth: true } },
    ],
  },

  // ==================== 商家后台 ====================
  {
    path: '/shop',
    component: () => import('@/layouts/ShopLayout.vue'),
    meta: { requiresShop: true },
    children: [
      { path: '', redirect: '/shop/dashboard' },
      { path: 'dashboard', name: 'ShopDashboard', component: () => import('@/views/shop/Dashboard.vue') },
      { path: 'bikes', name: 'ShopBikeList', component: () => import('@/views/shop/BikeList.vue') },
      { path: 'bikes/new', name: 'ShopBikeNew', component: () => import('@/views/shop/BikeForm.vue') },
      { path: 'bikes/:id/edit', name: 'ShopBikeEdit', component: () => import('@/views/shop/BikeForm.vue') },
      { path: 'messages', name: 'ShopMessages', component: () => import('@/views/shop/Messages.vue') },
      { path: 'profile', name: 'ShopProfile', component: () => import('@/views/shop/ShopProfile.vue') },
    ],
  },

  // ==================== 管理员后台 ====================
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAdmin: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'audit', name: 'AdminShopAudit', component: () => import('@/views/admin/ShopAudit.vue') },
      { path: 'shops', name: 'AdminShopManage', component: () => import('@/views/admin/ShopManage.vue') },
      { path: 'bikes', name: 'AdminBikeControl', component: () => import('@/views/admin/BikeControl.vue') },
      { path: 'messages', name: 'AdminMessages', component: () => import('@/views/admin/MessageView.vue') },
    ],
  },

  // 404
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// ==================== 权限守卫 ====================
router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { path: '/', query: { msg: '需要管理员权限' } }
  }
  if (to.meta.requiresShop && !auth.isShop) {
    return { path: '/profile', query: { msg: '请先完成商家入驻审核' } }
  }
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { path: '/', query: { msg: '请先登录' } }
  }
})

export default router

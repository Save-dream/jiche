<template>
  <div class="shop-layout">
    <aside class="shop-sidebar" :class="{ 'mobile-open': sidebarOpen }">
      <div class="sidebar-header">
        <router-link to="/" class="sidebar-logo">🏍 极车管理中心</router-link>
        <button v-if="isMobile" class="sidebar-close" @click="sidebarOpen = false"><el-icon><Close /></el-icon></button>
      </div>
      <div class="sidebar-user">
        <el-icon size="32"><UserFilled /></el-icon>
        <div>
          <div class="sidebar-username">{{ auth.user?.nickname }}</div>
          <el-tag size="small" type="danger">平台管理员</el-tag>
        </div>
      </div>
      <nav class="sidebar-nav">
        <router-link v-for="item in navItems" :key="item.path" :to="item.path" class="sidebar-nav-item" @click="sidebarOpen = false">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
          <el-badge v-if="item.badge" :value="item.badge" class="sidebar-badge" />
        </router-link>
      </nav>
      <div class="sidebar-bottom">
        <router-link to="/" class="sidebar-nav-item"><el-icon><ArrowLeft /></el-icon><span>返回前台</span></router-link>
        <button class="sidebar-nav-item logout-btn" @click="handleLogout"><el-icon><SwitchButton /></el-icon><span>退出登录</span></button>
      </div>
    </aside>

    <div v-if="isMobile && sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false" />

    <div class="shop-main">
      <div class="shop-topbar" v-if="isMobile">
        <button class="topbar-menu-btn" @click="sidebarOpen = true"><el-icon><Menu /></el-icon></button>
        <span class="topbar-title">{{ pageTitle }}</span>
      </div>
      <div class="shop-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const sidebarOpen = ref(false)
const isMobile = ref(false)
const pendingAuditCount = ref(0)

function checkMobile() { isMobile.value = window.innerWidth <= 768 }

async function loadPendingAuditCount() {
  try {
    const res = await api.getShopApplications({ status: 1 })
    pendingAuditCount.value = res.data?.total || 0
  } catch {
    pendingAuditCount.value = 0
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  window.addEventListener('admin:pending-audit-changed', loadPendingAuditCount)
  loadPendingAuditCount()
})
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  window.removeEventListener('admin:pending-audit-changed', loadPendingAuditCount)
})

watch(
  () => route.path,
  (path) => {
    if (path.startsWith('/admin')) loadPendingAuditCount()
  }
)

const navItems = computed(() => [
  { path: '/admin/dashboard', label: '数据概览', icon: 'DataBoard' },
  { path: '/admin/audit', label: '商家审核', icon: 'Checked', badge: pendingAuditCount.value },
  { path: '/admin/shops', label: '商户管理', icon: 'OfficeBuilding' },
  { path: '/admin/bikes', label: '车源管控', icon: 'List' },
  { path: '/admin/messages', label: '留言查看', icon: 'ChatDotRound' },
  { path: '/admin/users', label: '管理员管理', icon: 'UserFilled' },
])

const pageTitle = computed(() => {
  const item = navItems.value.find((entry) => route.path === entry.path || route.path.startsWith(`${entry.path}/`))
  return item?.label || '管理中心'
})

function handleLogout() { auth.logout(); router.push('/login') }
</script>

<style scoped>
.shop-layout { display: flex; height: 100vh; overflow: hidden; }
.shop-sidebar {
  width: 220px;
  background: #fff;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: transform 0.25s;
}
.sidebar-header { padding: 16px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; justify-content: space-between; }
.sidebar-logo { font-size: 15px; font-weight: 700; color: #222; text-decoration: none; }
.sidebar-close { background: none; border: none; cursor: pointer; font-size: 20px; color: #888; display: flex; align-items: center; }
.sidebar-user { display: flex; align-items: center; gap: 10px; padding: 16px; background: #f9fafb; border-bottom: 1px solid #f0f0f0; }
.sidebar-username { font-size: 13px; font-weight: 600; color: #333; margin-bottom: 4px; }
.sidebar-nav { flex: 1; padding: 12px 0; overflow-y: auto; }
.sidebar-nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 11px 20px; color: #555; text-decoration: none; font-size: 14px;
  transition: background 0.15s, color 0.15s; cursor: pointer; position: relative;
  border: none; background: none; width: 100%; text-align: left;
}
.sidebar-nav-item:hover, .router-link-active.sidebar-nav-item { background: #f0f7ff; color: #1890ff; }
.sidebar-nav-item .el-icon { font-size: 18px; }
.sidebar-badge { margin-left: auto; }
.sidebar-bottom { border-top: 1px solid #f0f0f0; padding: 8px 0; }
.logout-btn { color: #ff4d4f; }
.logout-btn:hover { background: #fff1f0; color: #ff4d4f; }
.shop-main { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: #f5f6fa; }
.shop-topbar { height: 52px; background: #fff; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; gap: 12px; padding: 0 16px; flex-shrink: 0; }
.topbar-menu-btn { background: none; border: none; cursor: pointer; font-size: 22px; color: #555; display: flex; align-items: center; }
.topbar-title { font-size: 16px; font-weight: 600; color: #333; }
.shop-content { flex: 1; overflow-y: auto; padding: 24px; }
.sidebar-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.35); z-index: 98; }
@media (max-width: 768px) {
  .shop-sidebar { position: fixed; left: 0; top: 0; height: 100vh; z-index: 99; transform: translateX(-100%); }
  .shop-sidebar.mobile-open { transform: translateX(0); }
  .shop-content { padding: 16px; }
}
</style>

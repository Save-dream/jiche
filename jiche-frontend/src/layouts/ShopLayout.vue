<template>
  <div class="shop-layout">
    <!-- 侧边栏 -->
    <aside class="shop-sidebar" :class="{ 'mobile-open': sidebarOpen }">
      <div class="sidebar-header">
        <router-link to="/" class="sidebar-logo">🏍 极车商家中心</router-link>
        <button v-if="isMobile" class="sidebar-close" @click="sidebarOpen = false">
          <el-icon><Close /></el-icon>
        </button>
      </div>

      <div class="sidebar-user">
        <el-icon size="32"><UserFilled /></el-icon>
        <div>
          <div class="sidebar-username">{{ auth.user?.nickname }}</div>
          <el-tag size="small" type="success">已入驻商家</el-tag>
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

    <!-- 移动端遮罩 -->
    <div v-if="isMobile && sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false" />

    <!-- 主内容区 -->
    <div class="shop-main">
      <!-- 移动端顶栏 -->
      <div class="shop-topbar" v-if="isMobile">
        <button class="topbar-menu-btn" @click="sidebarOpen = true"><el-icon><Menu /></el-icon></button>
        <span class="topbar-title">商家后台</span>
      </div>

      <div class="shop-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const router = useRouter()
const sidebarOpen = ref(false)
const isMobile = ref(false)
const unreadMessages = ref(0)

function checkMobile() { isMobile.value = window.innerWidth <= 768 }

async function loadUnread() {
  try {
    const res = await api.getUnreadCount('shop')
    unreadMessages.value = res.data?.unread_count || 0
  } catch {
    unreadMessages.value = 0
  }
}

let unreadTimer = null
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  loadUnread()
  unreadTimer = setInterval(loadUnread, 30000)
})
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  if (unreadTimer) clearInterval(unreadTimer)
})

const navItems = computed(() => [
  { path: '/shop/dashboard', label: '概览', icon: 'DataBoard' },
  { path: '/shop/bikes', label: '我的车源', icon: 'List' },
  { path: '/shop/messages', label: '留言管理', icon: 'ChatDotRound', badge: unreadMessages.value },
  { path: '/shop/profile', label: '商家资料', icon: 'Setting' },
])

function handleLogout() { auth.logout(); router.push('/login') }
</script>

<style scoped>
.shop-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}
.shop-sidebar {
  width: 220px;
  background: #fff;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: transform 0.25s;
}
.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.sidebar-logo {
  font-size: 15px;
  font-weight: 700;
  color: #222;
  text-decoration: none;
}
.sidebar-close { background: none; border: none; cursor: pointer; font-size: 20px; color: #888; display: flex; align-items: center; }
.sidebar-user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  background: #f9fafb;
  border-bottom: 1px solid #f0f0f0;
}
.sidebar-username { font-size: 13px; font-weight: 600; color: #333; margin-bottom: 4px; }
.sidebar-nav { flex: 1; padding: 12px 0; overflow-y: auto; }
.sidebar-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 20px;
  color: #555;
  text-decoration: none;
  font-size: 14px;
  transition: background 0.15s, color 0.15s;
  cursor: pointer;
  position: relative;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
}
.sidebar-nav-item:hover, .router-link-active.sidebar-nav-item {
  background: #f0f7ff;
  color: #1890ff;
}
.sidebar-nav-item .el-icon { font-size: 18px; }
.sidebar-badge { margin-left: auto; }
.sidebar-bottom { border-top: 1px solid #f0f0f0; padding: 8px 0; }
.logout-btn { color: #ff4d4f; }
.logout-btn:hover { background: #fff1f0; color: #ff4d4f; }

.shop-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f5f6fa;
}
.shop-topbar {
  height: 52px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  flex-shrink: 0;
}
.topbar-menu-btn { background: none; border: none; cursor: pointer; font-size: 22px; color: #555; display: flex; align-items: center; }
.topbar-title { font-size: 16px; font-weight: 600; color: #333; }
.shop-content { flex: 1; overflow-y: auto; padding: 24px; }

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.35);
  z-index: 98;
}

@media (max-width: 768px) {
  .shop-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 99;
    transform: translateX(-100%);
  }
  .shop-sidebar.mobile-open { transform: translateX(0); }
  .shop-content { padding: 16px; }
}
</style>

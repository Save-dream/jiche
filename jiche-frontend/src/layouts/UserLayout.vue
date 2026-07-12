<template>
  <div class="user-layout">
    <NavBar />
    <main class="user-main" :class="{ 'has-bottom-bar': hasBottomBar }">
      <div class="page-container page-content">
        <router-view />
      </div>
    </main>
    <!-- 移动端底部 Tab -->
    <nav class="mobile-tabbar" v-if="isMobile">
      <router-link to="/" class="tab-item" :class="{ active: isHomeActive }">
        <el-icon><House /></el-icon><span>首页</span>
      </router-link>
      <router-link to="/favorites" class="tab-item" :class="{ active: $route.path === '/favorites' }">
        <el-icon><Star /></el-icon><span>收藏</span>
      </router-link>
      <router-link to="/messages" class="tab-item" :class="{ active: $route.path.startsWith('/messages') }">
        <span class="tab-icon-wrap">
          <el-icon><ChatDotRound /></el-icon>
          <em v-if="auth.userUnreadMessages" class="tab-badge">{{ auth.userUnreadMessages }}</em>
        </span>
        <span>咨询</span>
      </router-link>
      <router-link to="/profile" class="tab-item" :class="{ active: $route.path === '/profile' }">
        <el-icon><User /></el-icon><span>我的</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const UNREAD_POLL_INTERVAL_MS = 30000

const route = useRoute()
const auth = useAuthStore()
const isMobile = ref(false)
let unreadPollTimer = null

function checkMobile() { isMobile.value = window.innerWidth <= 768 }

const isHomeActive = computed(() => {
  return route.path === '/' || route.path.startsWith('/shop/') || route.path.startsWith('/bike/')
})

const hasBottomBar = computed(() => {
  return isMobile.value && route.name === 'BikeDetail'
})

function startUnreadPolling() {
  stopUnreadPolling()
  unreadPollTimer = setInterval(() => {
    if (auth.isLoggedIn && document.visibilityState === 'visible') {
      auth.loadUnreadMessages(api, 'auto')
    }
  }, UNREAD_POLL_INTERVAL_MS)
}

function stopUnreadPolling() {
  if (unreadPollTimer) {
    clearInterval(unreadPollTimer)
    unreadPollTimer = null
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  if (auth.isLoggedIn) {
    auth.loadUnreadMessages(api, 'auto')
    startUnreadPolling()
  }
})
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  stopUnreadPolling()
})
</script>

<style scoped>
.user-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.user-main {
  flex: 1;
  background: #f5f6fa;
}
.page-content {
  padding-top: 12px;
  padding-bottom: 20px;
}
.mobile-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: calc(56px + env(safe-area-inset-bottom, 0px));
  padding-bottom: env(safe-area-inset-bottom, 0px);
  background: #fff;
  border-top: 1px solid #f0f0f0;
  display: flex;
  align-items: stretch;
  z-index: 99;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
}
.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  font-size: 10px;
  color: #888;
  text-decoration: none;
  transition: color 0.15s;
  position: relative;
}
.tab-item .el-icon { font-size: 22px; }
.tab-item.active { color: #1890ff; }
.tab-icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.tab-badge {
  position: absolute;
  top: -4px;
  right: -10px;
  font-style: normal;
  background: #ff4d4f;
  color: #fff;
  font-size: 10px;
  min-width: 16px;
  height: 16px;
  line-height: 16px;
  text-align: center;
  border-radius: 8px;
  padding: 0 4px;
}

@media (max-width: 768px) {
  .page-content {
    padding-bottom: calc(68px + env(safe-area-inset-bottom, 0px));
  }
  .user-main.has-bottom-bar .page-content {
    padding-bottom: calc(128px + env(safe-area-inset-bottom, 0px));
  }
}
</style>

<template>
  <div class="user-layout">
    <NavBar />
    <main class="user-main">
      <div class="page-container" style="padding-top: clamp(12px, 2vw, 20px); padding-bottom: clamp(40px, 5vw, 60px);">
        <router-view />
      </div>
    </main>
    <!-- 移动端底部 Tab -->
    <nav class="mobile-tabbar" v-if="isMobile">
      <router-link to="/" class="tab-item" :class="{ active: $route.path === '/' }">
        <el-icon><House /></el-icon><span>首页</span>
      </router-link>
      <router-link to="/favorites" class="tab-item" :class="{ active: $route.path === '/favorites' }">
        <el-icon><Star /></el-icon><span>收藏</span>
      </router-link>
      <router-link to="/profile" class="tab-item" :class="{ active: $route.path === '/profile' }">
        <el-icon><User /></el-icon><span>我的</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import NavBar from '@/components/NavBar.vue'

const isMobile = ref(false)
function checkMobile() { isMobile.value = window.innerWidth <= 768 }
onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })
onUnmounted(() => window.removeEventListener('resize', checkMobile))
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
.mobile-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
  display: flex;
  align-items: stretch;
  z-index: 99;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.06);
}
.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  font-size: 11px;
  color: #888;
  text-decoration: none;
  transition: color 0.15s;
}
.tab-item .el-icon { font-size: 20px; }
.tab-item.active, .tab-item:hover { color: #1890ff; }
@media (max-width: 768px) {
  .user-main { padding-bottom: 60px; } /* 给底部Tab留空间 */
}
</style>

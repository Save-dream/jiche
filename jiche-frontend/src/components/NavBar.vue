<template>
  <header class="navbar">
    <div class="navbar__inner page-container">
      <!-- Logo -->
      <router-link to="/" class="navbar__logo">
        <span class="logo-icon">🏍</span>
        <span class="logo-text">极车</span>
      </router-link>

      <!-- PC 导航菜单 -->
      <nav class="navbar__nav" v-if="!isMobile">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">首页</router-link>
        <router-link to="/messages" class="nav-link" :class="{ active: $route.path.startsWith('/messages') }">
          我的咨询
          <el-badge v-if="auth.userUnreadMessages" :value="auth.userUnreadMessages" class="nav-badge" />
        </router-link>
        <router-link v-if="auth.isShop" to="/shop/dashboard" class="nav-link">商家后台</router-link>
        <router-link v-if="auth.isAdmin" to="/admin/dashboard" class="nav-link">管理中心</router-link>
      </nav>

      <!-- 右侧操作区 -->
      <div class="navbar__actions">
        <!-- 收藏（移动端在下拉菜单里） -->
        <router-link v-if="!isMobile" to="/favorites" class="navbar__icon-btn" title="我的收藏">
          <el-icon><Star /></el-icon>
        </router-link>

        <!-- 用户头像/登录 -->
        <template v-if="auth.isLoggedIn">
          <el-dropdown v-if="!isMobile" @command="handleUserCommand">
            <div class="navbar__avatar">
              <el-icon><UserFilled /></el-icon>
              <span v-if="!isMobile" class="navbar__username">{{ auth.user?.nickname }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item v-if="auth.isShop" command="shop">商家后台</el-dropdown-item>
                <el-dropdown-item v-if="auth.isAdmin" command="admin">管理中心</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <router-link v-if="isMobile" to="/profile" class="navbar__avatar mobile-avatar">
            <el-icon><UserFilled /></el-icon>
          </router-link>
        </template>
        <router-link v-else to="/login" class="navbar__login-btn">
          <el-button type="primary" size="small" round>登录</el-button>
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const isMobile = ref(false)

function checkMobile() {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })
onUnmounted(() => window.removeEventListener('resize', checkMobile))

function handleUserCommand(cmd) {
  if (cmd === 'profile') router.push('/profile')
  else if (cmd === 'shop') router.push('/shop/dashboard')
  else if (cmd === 'admin') router.push('/admin/dashboard')
  else if (cmd === 'logout') { auth.logout(); router.push('/login') }
}
</script>

<style scoped>
.navbar {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.navbar__inner {
  height: 56px;
  display: flex;
  align-items: center;
  gap: clamp(8px, 3vw, 24px);
  overflow: hidden;
}
.navbar__logo {
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  flex-shrink: 0;
}
.logo-icon { font-size: 24px; }
.logo-text { font-size: 18px; font-weight: 700; color: #222; }

.navbar__nav {
  display: flex;
  gap: 4px;
  flex: 1;
}
.nav-link {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 14px;
  color: #555;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.nav-link:hover, .nav-link.active {
  background: #f0f7ff;
  color: #1890ff;
}

.navbar__actions {
  display: flex;
  align-items: center;
  gap: clamp(4px, 1.5vw, 12px);
  margin-left: auto;
  flex-shrink: 0;
}
.navbar__icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #555;
  font-size: 20px;
  padding: 4px;
}
.navbar__icon-btn:hover { color: #1890ff; }

.navbar__avatar {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #555;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.15s;
}
.navbar__avatar:hover { background: #f5f5f5; }
.navbar__username { max-width: 80px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.mobile-avatar {
  text-decoration: none;
  color: #555;
}

.navbar__login-btn { text-decoration: none; }

@media (max-width: 768px) {
  .navbar__nav { display: none; }
  .navbar__icon-btn { display: none; }
  .navbar__username { display: none; }
}
</style>

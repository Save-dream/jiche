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
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">车源广场</router-link>
        <router-link v-if="auth.isShop" to="/shop/dashboard" class="nav-link">商家后台</router-link>
        <router-link v-if="auth.isAdmin" to="/admin/dashboard" class="nav-link">管理中心</router-link>
      </nav>

      <!-- 右侧操作区 -->
      <div class="navbar__actions">
        <!-- 调试角色切换（开发用） -->
        <el-dropdown v-if="showDevTools && !isMobile" @command="auth.switchRole" class="dev-switcher">
          <el-button size="small" type="warning" plain>
            [Dev] {{ roleLabel }} <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="user">普通用户</el-dropdown-item>
              <el-dropdown-item command="pending">待审核商家</el-dropdown-item>
              <el-dropdown-item command="shop">已入驻商家</el-dropdown-item>
              <el-dropdown-item command="admin">管理员</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 收藏（移动端在下拉菜单里） -->
        <router-link v-if="!isMobile" to="/favorites" class="navbar__icon-btn" title="我的收藏">
          <el-icon><Star /></el-icon>
        </router-link>

        <!-- 用户头像/登录 -->
        <el-dropdown @command="handleUserCommand">
          <div class="navbar__avatar">
            <el-icon><UserFilled /></el-icon>
            <span v-if="!isMobile" class="navbar__username">{{ auth.user?.nickname || '登录' }}</span>
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

        <!-- 移动端菜单按钮 -->
        <button v-if="isMobile" class="navbar__menu-btn" @click="mobileMenuOpen = !mobileMenuOpen">
          <el-icon><Menu /></el-icon>
        </button>
      </div>
    </div>

    <!-- 移动端菜单 -->
    <div v-if="isMobile && mobileMenuOpen" class="navbar__mobile-menu">
      <router-link to="/" class="mobile-nav-link" @click="mobileMenuOpen = false">车源广场</router-link>
      <router-link to="/favorites" class="mobile-nav-link" @click="mobileMenuOpen = false">我的收藏</router-link>
      <router-link to="/profile" class="mobile-nav-link" @click="mobileMenuOpen = false">个人中心</router-link>
      <router-link v-if="auth.isShop" to="/shop/dashboard" class="mobile-nav-link" @click="mobileMenuOpen = false">商家后台</router-link>
      <router-link v-if="auth.isAdmin" to="/admin/dashboard" class="mobile-nav-link" @click="mobileMenuOpen = false">管理中心</router-link>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, SHOP_STATUS } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const mobileMenuOpen = ref(false)
const isMobile = ref(false)
const showDevTools = ref(true) // 开发调试用，生产关闭

function checkMobile() {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })
onUnmounted(() => window.removeEventListener('resize', checkMobile))

const roleLabel = computed(() => {
  if (auth.isAdmin) return '管理员'
  if (auth.isShop) return '商家'
  return SHOP_STATUS[auth.shopStatus]?.label || '用户'
})

function handleUserCommand(cmd) {
  if (cmd === 'profile') router.push('/profile')
  else if (cmd === 'shop') router.push('/shop/dashboard')
  else if (cmd === 'admin') router.push('/admin/dashboard')
  else if (cmd === 'logout') { auth.logout(); router.push('/') }
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

.navbar__menu-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 22px;
  color: #555;
  display: flex;
  align-items: center;
}

.navbar__mobile-menu {
  display: flex;
  flex-direction: column;
  border-top: 1px solid #f0f0f0;
  background: #fff;
}
.mobile-nav-link {
  padding: 14px 20px;
  font-size: 14px;
  color: #333;
  text-decoration: none;
  border-bottom: 1px solid #f5f5f5;
}
.mobile-nav-link:hover { background: #f5f5f5; color: #1890ff; }
.dev-switcher { display: flex; }

/* CSS媒体查询备份：即使JS isMobile未触发，CSS也保证不溢出 */
@media (max-width: 768px) {
  .navbar__nav { display: none; }
  .dev-switcher { display: none !important; }
  .navbar__icon-btn { display: none; }
  .navbar__username { display: none; }
  .navbar__menu-btn { display: flex; }
}
@media (min-width: 769px) {
  .navbar__menu-btn { display: none; }
}
</style>

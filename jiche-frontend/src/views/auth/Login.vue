<template>
  <div class="login-page">
    <div class="login-card">
      <router-link to="/" class="login-logo">
        <span class="logo-icon">🏍</span>
        <span class="logo-text">极车</span>
      </router-link>

      <h1 class="login-title">账号登录</h1>
      <p class="login-desc">请使用管理员分配的账号密码登录</p>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="login-form"
        @submit.prevent
      >
        <el-form-item label="账号" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入账号"
            size="large"
            clearable
            autocomplete="username"
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            autocomplete="current-password"
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          class="login-btn"
          :loading="loading"
          @click="onSubmit"
        >
          登录
        </el-button>
      </el-form>

      <ul class="login-tips">
        <li>请使用管理员分配的账号，暂不支持自助注册</li>
        <li>商家账号登录后可进入「商家后台」配置店铺与车源</li>
        <li>管理员账号可进入「管理中心」审核与管控</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function onSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    const res = await api.passwordLogin({
      username: form.username.trim(),
      password: form.password,
    })
    auth.loginSession({ token: res.data.token, user: res.data.user })
    await auth.loadUnreadMessages(api)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect
    if (typeof redirect === 'string' && redirect.startsWith('/')) {
      router.replace(redirect)
      return
    }
    if (auth.isAdmin) {
      router.replace('/admin/dashboard')
    } else if (auth.isShop) {
      router.replace('/shop/dashboard')
    } else {
      router.replace('/')
    }
  } catch {
    /* 错误由 axios 拦截器提示 */
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(160deg, #f0f7ff 0%, #f5f6fa 50%, #fff 100%);
  padding: 24px 16px;
}
.login-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 32px 28px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}
.login-logo {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  margin-bottom: 24px;
}
.logo-icon { font-size: 28px; }
.logo-text { font-size: 20px; font-weight: 700; color: #222; }
.login-title {
  font-size: 22px;
  font-weight: 700;
  color: #222;
  margin: 0 0 8px;
}
.login-desc {
  font-size: 14px;
  color: #888;
  margin: 0 0 24px;
}
.login-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #555;
}
.login-btn {
  width: 100%;
  margin-top: 8px;
}
.login-tips {
  margin: 28px 0 0;
  padding-left: 18px;
  font-size: 12px;
  color: #999;
  line-height: 1.8;
}
</style>

<template>
  <div class="login-page">
    <div class="login-card">
      <router-link to="/" class="login-logo">
        <span class="logo-icon">🏍</span>
        <span class="logo-text">极车</span>
      </router-link>

      <h1 class="login-title">{{ mode === 'login' ? '账号登录' : '注册账号' }}</h1>
      <p class="login-desc">
        {{ mode === 'login'
          ? '微信登录未接通前，请使用账号密码（注册即视为授权登录）'
          : '注册后即可浏览商品/店铺详情，等同微信授权建号' }}
      </p>

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
        <el-form-item v-if="mode === 'register'" label="昵称" prop="nickname">
          <el-input
            v-model="form.nickname"
            placeholder="选填，默认与账号相同"
            size="large"
            clearable
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-form-item v-if="mode === 'register'" label="手机号" prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="选填"
            size="large"
            clearable
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
          {{ mode === 'login' ? '登录' : '注册并登录' }}
        </el-button>
      </el-form>

      <p class="login-switch">
        <template v-if="mode === 'login'">
          还没有账号？
          <button type="button" class="link-btn" @click="switchMode('register')">去注册</button>
        </template>
        <template v-else>
          已有账号？
          <button type="button" class="link-btn" @click="switchMode('login')">去登录</button>
        </template>
      </p>

      <ul class="login-tips">
        <li>普通用户可自助注册；封禁后将无法登录进入系统</li>
        <li>商家账号登录后可进入「商家后台」</li>
        <li>管理员账号可进入「管理中心」</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const mode = ref('login')
const formRef = ref(null)
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
  nickname: '',
  phone: '',
})

const rules = computed(() => ({
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    ...(mode.value === 'register'
      ? [{ min: 6, message: '密码至少 6 位', trigger: 'blur' }]
      : []),
  ],
  phone: [
    {
      validator: (_r, v, cb) => {
        if (!v) return cb()
        if (!/^1[3-9]\d{9}$/.test(v)) return cb(new Error('手机号格式不正确'))
        cb()
      },
      trigger: 'blur',
    },
  ],
}))

function switchMode(next) {
  mode.value = next
  formRef.value?.clearValidate()
}

async function afterAuth(res) {
  auth.loginSession({ token: res.data.token, user: res.data.user })
  await auth.loadUnreadMessages(api)
  ElMessage.success(mode.value === 'login' ? '登录成功' : '注册成功')
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
    if (mode.value === 'login') {
      const res = await api.passwordLogin({
        username: form.username.trim(),
        password: form.password,
      })
      await afterAuth(res)
    } else {
      const res = await api.passwordRegister({
        username: form.username.trim(),
        password: form.password,
        nickname: form.nickname.trim(),
        phone: form.phone.trim() || undefined,
      })
      await afterAuth(res)
    }
  } catch {
    /* interceptor */
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
  padding: 24px 16px;
  background:
    radial-gradient(ellipse at 20% 0%, rgba(255, 107, 53, 0.12), transparent 50%),
    radial-gradient(ellipse at 80% 100%, rgba(30, 60, 90, 0.08), transparent 45%),
    linear-gradient(165deg, #f7f4ef 0%, #eef2f6 55%, #f3efe8 100%);
}
.login-card {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  padding: 36px 28px 28px;
  box-shadow: 0 12px 40px rgba(20, 30, 50, 0.08);
}
.login-logo {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: #1a1a1a;
  margin-bottom: 28px;
}
.logo-icon { font-size: 22px; }
.logo-text { font-size: 20px; font-weight: 800; letter-spacing: 0.04em; }
.login-title {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
}
.login-desc {
  margin: 0 0 24px;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
}
.login-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: #374151;
}
.login-btn {
  width: 100%;
  margin-top: 8px;
  font-weight: 600;
}
.login-switch {
  margin: 16px 0 0;
  text-align: center;
  font-size: 13px;
  color: #6b7280;
}
.link-btn {
  border: none;
  background: none;
  color: #2563eb;
  cursor: pointer;
  padding: 0;
  font-size: 13px;
}
.login-tips {
  margin: 20px 0 0;
  padding: 12px 12px 12px 28px;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.7;
  background: #f8fafc;
  border-radius: 10px;
}
</style>

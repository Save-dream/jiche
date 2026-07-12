<template>
  <div class="login-page">
    <div class="login-card">
      <router-link to="/" class="login-logo">
        <span class="logo-icon">🏍</span>
        <span class="logo-text">极车</span>
      </router-link>

      <h1 class="login-title">微信扫码登录</h1>
      <p class="login-desc">使用微信扫码，与小程序账号互通，无需注册</p>

      <div class="qr-wrap" v-loading="creating">
        <template v-if="ticket">
          <img :src="ticket.qr_url" alt="微信登录二维码" class="qr-image" />
          <p class="qr-status">
            <el-icon v-if="status === 'pending'" class="is-loading"><Loading /></el-icon>
            {{ statusText }}
          </p>
          <p class="qr-expire" v-if="ticket">二维码 {{ expireMinutes }} 分钟内有效</p>
        </template>
      </div>

      <div class="login-actions">
        <el-button v-if="status === 'expired'" type="primary" @click="initTicket">刷新二维码</el-button>
        <el-button v-if="showDevTools && ticket" type="warning" plain @click="simulateScan">
          [Dev] 模拟扫码成功
        </el-button>
      </div>

      <ul class="login-tips">
        <li>电脑端与微信小程序使用同一微信账号，数据自动同步</li>
        <li>收藏、咨询记录、最近访问商家在多端共享</li>
        <li>平台不支持前台注册，管理员由后台预置或授权</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const showDevTools = ref(true)
const creating = ref(false)
const ticket = ref(null)
const status = ref('pending')
let pollTimer = null

const expireMinutes = 5

const statusText = computed(() => {
  if (status.value === 'pending') return '请使用微信扫描二维码'
  if (status.value === 'scanned') return '扫码成功，请在手机上确认'
  if (status.value === 'expired') return '二维码已过期，请刷新'
  return '登录中...'
})

async function initTicket() {
  stopPoll()
  creating.value = true
  status.value = 'pending'
  try {
    const res = await api.createLoginTicket()
    ticket.value = res.data
    startPoll()
  } catch {
    ElMessage.error('获取登录二维码失败')
  } finally {
    creating.value = false
  }
}

function startPoll() {
  stopPoll()
  pollTimer = setInterval(pollOnce, 2000)
}

function stopPoll() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function pollOnce() {
  if (!ticket.value?.ticket_id) return
  try {
    const res = await api.pollLoginTicket(ticket.value.ticket_id)
    const data = res.data
    status.value = data.status
    if (data.status === 'confirmed') {
      stopPoll()
      auth.loginSession({ token: data.token, user: data.user })
      await auth.loadUnreadMessages(api)
      ElMessage.success('登录成功')
      const redirect = route.query.redirect || '/'
      router.replace(typeof redirect === 'string' ? redirect : '/')
    }
    if (data.status === 'expired') stopPoll()
  } catch { /* ignore */ }
}

async function simulateScan() {
  if (!ticket.value?.ticket_id) return
  try {
    await api.simulateScanLogin(ticket.value.ticket_id)
    await pollOnce()
  } catch {
    ElMessage.error('模拟扫码失败')
  }
}

onMounted(initTicket)
onUnmounted(stopPoll)
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
.qr-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 280px;
  justify-content: center;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  padding: 24px;
  background: #fafafa;
}
.qr-image {
  width: 220px;
  height: 220px;
  border-radius: 8px;
  border: 1px solid #eee;
}
.qr-status {
  margin: 16px 0 4px;
  font-size: 14px;
  color: #07c160;
  display: flex;
  align-items: center;
  gap: 6px;
}
.qr-expire {
  font-size: 12px;
  color: #aaa;
  margin: 0;
}
.login-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}
.login-tips {
  margin: 28px 0 0;
  padding-left: 18px;
  font-size: 12px;
  color: #999;
  line-height: 1.8;
}
</style>

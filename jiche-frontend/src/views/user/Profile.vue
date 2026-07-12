<template>
  <div>
    <!-- 未登录引导 -->
    <div v-if="!auth.isLoggedIn" class="card">
      <div class="card-body login-prompt">
        <el-icon size="56" color="#07c160"><UserFilled /></el-icon>
        <h3>登录后使用完整功能</h3>
        <p>微信扫码登录，与小程序账号互通，收藏与咨询数据多端同步</p>
        <el-button type="primary" size="large" @click="goLogin">微信扫码登录</el-button>
      </div>
    </div>

    <!-- 商家账号已封禁：专属页 -->
    <div v-else-if="auth.shopStatus === 4" class="banned-page">
      <div class="banned-card">
        <div class="banned-icon-wrap">
          <el-icon :size="64" color="#ff4d4f"><CircleCloseFilled /></el-icon>
        </div>
        <h2 class="banned-title">账号已封禁</h2>
        <p class="banned-subtitle">您的商户账号因违反平台规则已被封禁，暂时无法使用商家相关功能。</p>

        <div class="banned-info">
          <div class="banned-info-row">
            <span class="label">账号昵称</span>
            <span>{{ auth.user?.nickname }}</span>
          </div>
          <div class="banned-info-row">
            <span class="label">绑定手机</span>
            <span>{{ auth.user?.phone || '未绑定' }}</span>
          </div>
          <div class="banned-info-row">
            <span class="label">封禁状态</span>
            <el-tag type="danger" size="small">永久封禁</el-tag>
          </div>
        </div>

        <div class="banned-notice">
          <div class="notice-title">封禁期间您将无法：</div>
          <ul>
            <li>登录商家后台发布或管理车源</li>
            <li>回复用户咨询留言</li>
            <li>修改商家资料或重新申请入驻</li>
          </ul>
          <div class="notice-title mt-3">您仍可：</div>
          <ul>
            <li>以普通用户身份浏览分享链接中的车源</li>
            <li>收藏车辆、发起咨询（面向其他商家）</li>
          </ul>
        </div>

        <div class="banned-contact">
          <p>如您认为封禁有误，请联系平台客服申诉：</p>
          <div class="contact-actions">
            <el-button type="danger" plain @click="copyContact">复制客服电话 400-888-0000</el-button>
            <el-button @click="$router.push('/')">返回首页</el-button>
          </div>
        </div>
      </div>
    </div>

    <template v-else>
    <!-- 个人信息卡 -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="profile-header">
          <div class="profile-avatar">
            <el-icon size="48"><UserFilled /></el-icon>
          </div>
          <div class="profile-info">
            <div class="profile-name">{{ auth.user?.nickname || '未登录' }}</div>
            <div class="profile-phone">{{ auth.user?.phone }}</div>
            <el-tag :type="shopStatusInfo.type" size="small">{{ shopStatusInfo.label }}</el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 商家/管理员快捷入口（底部 Tab 未覆盖的功能） -->
    <div class="func-grid" v-if="auth.isShop || auth.isAdmin" :class="{ 'admin-grid': auth.isAdmin && !auth.isShop }">
      <div class="func-item" v-if="auth.isShop" @click="$router.push('/shop/dashboard')">
        <div class="func-icon" style="background:#e3f2fd;"><el-icon color="#1565c0"><OfficeBuilding /></el-icon></div>
        <span>商家后台</span>
      </div>
      <div class="func-item" v-if="auth.isAdmin" @click="$router.push('/admin/dashboard')">
        <div class="func-icon" style="background:#fce4ec;"><el-icon color="#c62828"><Setting /></el-icon></div>
        <span>管理中心</span>
      </div>
      <div class="func-item" v-if="auth.isAdmin" @click="$router.push('/admin/audit')">
        <div class="func-icon" style="background:#fff3e0;"><el-icon color="#e65100"><Checked /></el-icon></div>
        <span class="func-label">
          商家审核
          <el-badge v-if="pendingAuditCount" :value="pendingAuditCount" class="func-badge" />
        </span>
      </div>
    </div>

    <!-- 入驻状态区（管理员不展示） -->
    <div v-if="!auth.isAdmin" class="card" :class="{ 'mt-4': auth.isShop }">
      <div class="card-header">商家入驻状态</div>
      <div class="card-body">
        <!-- 普通用户：引导入驻 -->
        <div v-if="auth.shopStatus === 0" class="apply-prompt">
          <el-icon size="48" color="#1890ff"><OfficeBuilding /></el-icon>
          <p>成为入驻商家，发布您的二手摩托车</p>
          <el-button type="primary" @click="$router.push('/apply-shop')">立即申请入驻</el-button>
        </div>

        <!-- 待审核 -->
        <div v-else-if="auth.shopStatus === 1" class="status-prompt">
          <el-result icon="warning" title="申请待审核" sub-title="您的入驻申请正在审核中，请耐心等待。审核结果将在1-3个工作日内反馈。">
            <template #extra>
              <el-button type="primary" @click="$router.push('/apply-shop')">查看申请详情</el-button>
            </template>
          </el-result>
          <div v-if="myApplication" class="application-summary">
            <div class="summary-title">已提交信息摘要</div>
            <div class="summary-grid">
              <div><span class="label">入驻类型</span>{{ myApplication.shop_type }}</div>
              <div><span class="label">联系人</span>{{ myApplication.contact_name }}</div>
              <div><span class="label">联系电话</span>{{ myApplication.phone }}</div>
              <div><span class="label">提交时间</span>{{ myApplication.applied_at }}</div>
            </div>
          </div>
        </div>

        <!-- 已入驻 -->
        <div v-else-if="auth.shopStatus === 2" class="status-prompt">
          <el-result icon="success" title="已入驻商家" sub-title="您已成为平台认证商家，可发布车源、管理留言。">
            <template #extra>
              <el-button type="primary" @click="$router.push('/shop/dashboard')">进入商家后台</el-button>
            </template>
          </el-result>
        </div>

        <!-- 驳回 -->
        <div v-else-if="auth.shopStatus === 3" class="status-prompt">
          <el-result icon="error" title="申请已驳回" sub-title="请修改申请信息后重新提交。">
            <template #extra>
              <el-button type="primary" @click="$router.push('/apply-shop')">重新提交申请</el-button>
            </template>
          </el-result>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore, SHOP_STATUS } from '@/stores/auth'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const myApplication = ref(null)
const pendingAuditCount = ref(0)
const shopStatusInfo = computed(() => SHOP_STATUS[auth.shopStatus] || SHOP_STATUS[0])

function goLogin() {
  router.push({ path: '/login', query: { redirect: route.fullPath } })
}

async function copyContact() {
  const phone = '400-888-0000'
  try {
    await navigator.clipboard.writeText(phone)
    ElMessage.success('客服电话已复制')
  } catch {
    ElMessage.info(phone)
  }
}

async function refreshUser() {
  if (!auth.isLoggedIn) return
  await auth.refreshUser(api)
}

async function loadMyApplication() {
  if (!auth.isLoggedIn || auth.shopStatus !== 1) {
    myApplication.value = null
    return
  }
  try {
    const res = await api.getMyApplication()
    myApplication.value = res.data
  } catch {
    myApplication.value = null
  }
}

async function loadPendingAuditCount() {
  if (!auth.isAdmin) {
    pendingAuditCount.value = 0
    return
  }
  try {
    const res = await api.getShopApplications({ status: 1 })
    pendingAuditCount.value = res.data?.total || 0
  } catch {
    pendingAuditCount.value = 0
  }
}

onMounted(async () => {
  await refreshUser()
  await Promise.all([loadMyApplication(), loadPendingAuditCount()])
})
</script>

<style scoped>
.banned-page {
  display: flex;
  justify-content: center;
  padding: 8px 0 24px;
}
.banned-card {
  width: 100%;
  max-width: 520px;
  background: #fff;
  border-radius: 12px;
  padding: 32px 28px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  text-align: center;
  border-top: 4px solid #ff4d4f;
}
.banned-icon-wrap { margin-bottom: 12px; }
.banned-title {
  font-size: 22px;
  font-weight: 700;
  color: #222;
  margin: 0 0 8px;
}
.banned-subtitle {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0 0 24px;
}
.banned-info {
  text-align: left;
  background: #fafafa;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 20px;
}
.banned-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
  border-bottom: 1px solid #f0f0f0;
}
.banned-info-row:last-child { border-bottom: none; }
.banned-info-row .label { color: #888; }
.banned-notice {
  text-align: left;
  background: #fff7f7;
  border: 1px solid #ffccc7;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  font-size: 13px;
  color: #555;
}
.notice-title { font-weight: 600; color: #333; margin-bottom: 8px; }
.banned-notice ul { margin: 0; padding-left: 18px; line-height: 1.8; }
.banned-contact p { font-size: 13px; color: #888; margin: 0 0 12px; }
.contact-actions { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }

.profile-header { display: flex; gap: 16px; align-items: center; }
.profile-avatar {
  width: 72px; height: 72px;
  background: #f0f7ff;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #1890ff;
  flex-shrink: 0;
}
.profile-name { font-size: 18px; font-weight: 700; color: #222; margin-bottom: 4px; }
.profile-phone { font-size: 13px; color: #888; margin-bottom: 8px; }

.func-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}
.admin-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.func-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.func-badge :deep(.el-badge__content) {
  transform: none;
  position: static;
}
.func-item {
  background: #fff;
  border-radius: 10px;
  padding: 20px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s, transform 0.2s;
  font-size: 13px;
  color: #555;
}
.func-item:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); transform: translateY(-2px); }
.func-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
}
.func-icon .el-icon { font-size: 22px; }

.apply-prompt { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 24px; }
.apply-prompt p { color: #666; font-size: 14px; }

.login-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 24px;
  text-align: center;
}
.login-prompt h3 { margin: 0; font-size: 18px; color: #222; }
.login-prompt p { margin: 0; font-size: 14px; color: #888; max-width: 280px; }

.application-summary {
  margin-top: 8px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}
.summary-title { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 12px; }
.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 16px;
  font-size: 13px;
  color: #555;
}
.summary-grid .label {
  display: inline-block;
  min-width: 64px;
  color: #888;
  margin-right: 8px;
}
@media (max-width: 768px) {
  .summary-grid { grid-template-columns: 1fr; }
  .banned-card { padding: 24px 16px; }
}
</style>

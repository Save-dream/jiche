<template>
  <div>
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

    <!-- 功能导航 -->
    <div class="func-grid">
      <div class="func-item" @click="$router.push('/favorites')">
        <div class="func-icon" style="background:#fff3e0;"><el-icon color="#e65100"><Star /></el-icon></div>
        <span>我的收藏</span>
      </div>
      <div class="func-item" v-if="auth.isShop" @click="$router.push('/shop/dashboard')">
        <div class="func-icon" style="background:#e3f2fd;"><el-icon color="#1565c0"><OfficeBuilding /></el-icon></div>
        <span>商家后台</span>
      </div>
      <div class="func-item" v-if="auth.isAdmin" @click="$router.push('/admin/dashboard')">
        <div class="func-icon" style="background:#fce4ec;"><el-icon color="#c62828"><Setting /></el-icon></div>
        <span>管理中心</span>
      </div>
    </div>

    <!-- 入驻状态区 -->
    <div class="card mt-4">
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
              <el-button @click="$router.push('/apply-shop')">查看申请详情</el-button>
            </template>
          </el-result>
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

        <!-- 封禁 -->
        <div v-else-if="auth.shopStatus === 4" class="status-prompt">
          <el-result icon="error" title="账号已封禁" sub-title="您的商户账号因违规已被永久封禁，如有疑问请联系平台客服。" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore, SHOP_STATUS } from '@/stores/auth'

const auth = useAuthStore()
const shopStatusInfo = computed(() => SHOP_STATUS[auth.shopStatus] || SHOP_STATUS[0])
</script>

<style scoped>
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
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
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

@media (max-width: 768px) {
  .func-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>

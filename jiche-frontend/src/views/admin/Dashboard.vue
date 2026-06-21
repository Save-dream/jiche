<template>
  <div>
    <h2 class="page-title mb-4">平台数据概览</h2>

    <div class="stats-grid mb-4">
      <div class="stat-card" v-for="s in statCards" :key="s.label">
        <div class="stat-icon" :style="`background:${s.bg}`"><el-icon :color="s.color" size="28"><component :is="s.icon" /></el-icon></div>
        <div class="stat-info">
          <div class="stat-value">{{ stats[s.key] }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>

    <!-- 待审核提醒 -->
    <el-alert v-if="stats.pending_applications > 0" type="warning" :closable="false" show-icon class="mb-4"
      :title="`有 ${stats.pending_applications} 个商家申请待审核`">
      <template #default>
        <el-button size="small" type="warning" @click="$router.push('/admin/audit')" style="margin-top:4px">立即处理</el-button>
      </template>
    </el-alert>

    <el-row :gutter="20">
      <!-- 最新商家申请 -->
      <el-col :span="12" :xs="24">
        <div class="card">
          <div class="card-header flex-between">
            <span>最新申请</span>
            <router-link to="/admin/audit" style="font-size:13px;color:#1890ff">查看全部 ›</router-link>
          </div>
          <div class="card-body" style="padding:0">
            <el-table :data="recentApplications" size="small">
              <el-table-column prop="contact_name" label="联系人" width="80" />
              <el-table-column prop="shop_type" label="类型" width="90" />
              <el-table-column prop="applied_at" label="申请时间" />
              <el-table-column label="状态" width="80" align="center">
                <template #default="{ row }">
                  <el-tag type="warning" size="small">待审核</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-col>
      <!-- 最新车源 -->
      <el-col :span="12" :xs="24">
        <div class="card">
          <div class="card-header flex-between">
            <span>最新车源</span>
            <router-link to="/admin/bikes" style="font-size:13px;color:#1890ff">查看全部 ›</router-link>
          </div>
          <div class="card-body" style="padding:0">
            <el-table :data="recentBikes" size="small">
              <el-table-column label="车辆" min-width="120">
                <template #default="{ row }"><span>{{ row.brand }} {{ row.model }}</span></template>
              </el-table-column>
              <el-table-column label="价格" width="80">
                <template #default="{ row }"><span style="color:#ff4d4f">¥{{ (row.price/10000).toFixed(1) }}万</span></template>
              </el-table-column>
              <el-table-column label="状态" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="BIKE_STATUS[row.bike_status]?.type" size="small">{{ BIKE_STATUS[row.bike_status]?.label }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { BIKE_STATUS } from '@/stores/auth'
import api from '@/api'

const stats = ref({ total_shops: 0, pending_applications: 0, total_bikes: 0, total_messages: 0 })
const recentApplications = ref([])
const recentBikes = ref([])

const statCards = [
  { key: 'total_shops', label: '入驻商家', icon: 'OfficeBuilding', bg: '#e3f2fd', color: '#1565c0' },
  { key: 'pending_applications', label: '待审核申请', icon: 'Checked', bg: '#fff3e0', color: '#e65100' },
  { key: 'total_bikes', label: '全平台车源', icon: 'List', bg: '#e8f5e9', color: '#2e7d32' },
  { key: 'total_messages', label: '全部留言', icon: 'ChatDotRound', bg: '#fce4ec', color: '#c62828' },
]

onMounted(async () => {
  const [statsRes, appsRes, bikesRes] = await Promise.all([
    api.getAdminStats(),
    api.getShopApplications({ status: 1 }),
    api.getAllBikes(),
  ])
  stats.value = statsRes.data
  recentApplications.value = appsRes.data.list.slice(0, 5)
  recentBikes.value = bikesRes.data.list.slice(0, 5)
})
</script>

<style scoped>
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
@media (max-width: 768px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
</style>

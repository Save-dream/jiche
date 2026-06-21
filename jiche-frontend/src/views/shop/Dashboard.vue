<template>
  <div>
    <h2 class="page-title mb-4">商家概览</h2>

    <!-- 统计卡片 -->
    <div class="stats-grid mb-4">
      <div class="stat-card">
        <div class="stat-icon" style="background:#e3f2fd"><el-icon color="#1565c0" size="28"><List /></el-icon></div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.on_sale }}</div>
          <div class="stat-label">在售车辆</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#fce4ec"><el-icon color="#c62828" size="28"><Checked /></el-icon></div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.sold }}</div>
          <div class="stat-label">已售车辆</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#fff3e0"><el-icon color="#e65100" size="28"><ChatDotRound /></el-icon></div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.unread_messages }}</div>
          <div class="stat-label">未读留言</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#e8f5e9"><el-icon color="#2e7d32" size="28"><View /></el-icon></div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_views }}</div>
          <div class="stat-label">总浏览量</div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions card mb-4">
      <div class="card-header">快捷操作</div>
      <div class="card-body">
        <div class="quick-grid">
          <el-button type="primary" size="large" @click="$router.push('/shop/bikes/new')">
            <el-icon><Plus /></el-icon> 发布新车
          </el-button>
          <el-button size="large" @click="$router.push('/shop/messages')">
            <el-icon><ChatDotRound /></el-icon>
            查看留言
            <el-badge v-if="stats.unread_messages" :value="stats.unread_messages" style="margin-left:8px" />
          </el-button>
          <el-button size="large" @click="$router.push('/shop/profile')">
            <el-icon><Setting /></el-icon> 编辑资料
          </el-button>
          <el-button size="large" @click="$router.push('/shop/bikes')">
            <el-icon><List /></el-icon> 管理车源
          </el-button>
        </div>
      </div>
    </div>

    <!-- 最新车源 -->
    <div class="card">
      <div class="card-header flex-between">
        <span>最新车源（最近3辆）</span>
        <router-link to="/shop/bikes" style="font-size:13px;color:#1890ff">查看全部 ›</router-link>
      </div>
      <div class="card-body">
        <el-table :data="recentBikes" size="small">
          <el-table-column label="车辆" min-width="180">
            <template #default="{ row }">
              <div class="flex" style="gap:10px;align-items:center">
                <img :src="row.cover_image" style="width:50px;height:38px;object-fit:cover;border-radius:4px" />
                <span>{{ row.brand }} {{ row.model }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="售价" width="100">
            <template #default="{ row }">
              <span style="color:#ff4d4f;font-weight:600">¥{{ (row.price/10000).toFixed(1) }}万</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="BIKE_STATUS[row.bike_status]?.type" size="small">{{ BIKE_STATUS[row.bike_status]?.label }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="view_count" label="浏览" width="70" align="center" />
          <el-table-column label="操作" width="120" align="center">
            <template #default="{ row }">
              <el-button size="small" @click="$router.push(`/shop/bikes/${row.id}/edit`)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { BIKE_STATUS } from '@/stores/auth'
import api from '@/api'

const stats = ref({ on_sale: 0, sold: 0, unread_messages: 0, total_views: 0 })
const recentBikes = ref([])

onMounted(async () => {
  const [statsRes, bikesRes] = await Promise.all([api.getShopStats(), api.getMyBikes()])
  stats.value = statsRes.data
  recentBikes.value = bikesRes.data.list.slice(0, 3)
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.quick-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .quick-grid .el-button { flex: 1; min-width: 140px; }
}
</style>

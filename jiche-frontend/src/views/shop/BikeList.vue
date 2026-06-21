<template>
  <div>
    <div class="page-header-bar">
      <h2 class="page-title">我的车源</h2>
      <el-button type="primary" @click="$router.push('/shop/bikes/new')">
        <el-icon><Plus /></el-icon> 发布新车
      </el-button>
    </div>

    <!-- 筛选 -->
    <div class="filter-row mb-3">
      <el-radio-group v-model="activeStatus" @change="loadBikes">
        <el-radio-button :value="0">全部</el-radio-button>
        <el-radio-button :value="1">在售</el-radio-button>
        <el-radio-button :value="2">已售</el-radio-button>
        <el-radio-button :value="3">已下架</el-radio-button>
      </el-radio-group>
    </div>

    <!-- PC端表格 -->
    <div class="card pc-table">
      <el-table :data="bikes" v-loading="loading" empty-text="暂无车源">
        <el-table-column label="车辆信息" min-width="220">
          <template #default="{ row }">
            <div class="flex" style="gap:12px;align-items:center">
              <img :src="row.cover_image" style="width:64px;height:48px;object-fit:cover;border-radius:6px;flex-shrink:0" />
              <div>
                <div style="font-weight:600;color:#222">{{ row.brand }} {{ row.model }}</div>
                <div style="font-size:12px;color:#888;margin-top:2px">{{ row.year }}年 · {{ row.displacement }} · {{ (row.mileage/10000).toFixed(1) }}万km</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="售价" width="100">
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
        <el-table-column prop="created_at" label="发布时间" width="110" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/shop/bikes/${row.id}/edit`)">编辑</el-button>
            <el-button size="small" type="warning" v-if="row.bike_status === 1" @click="offShelf(row)">下架</el-button>
            <el-button size="small" type="success" v-if="row.bike_status === 3" @click="reOnShelf(row)">重新上架</el-button>
            <el-popconfirm title="确认删除此车辆？删除后不可恢复。" @confirm="deleteBike(row)">
              <template #reference>
                <el-button size="small" type="danger" v-if="row.bike_status !== 4">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 移动端卡片列表 -->
    <div class="mobile-list" v-loading="loading">
      <el-empty v-if="!loading && !bikes.length" description="暂无车源" />
      <div v-for="row in bikes" :key="row.id" class="mobile-bike-card">
        <div class="mobile-bike-info">
          <img :src="row.cover_image" class="mobile-bike-img" />
          <div class="mobile-bike-detail">
            <div class="mobile-bike-name">{{ row.brand }} {{ row.model }}</div>
            <div class="mobile-bike-meta">{{ row.year }}年 · {{ row.displacement }} · {{ (row.mileage/10000).toFixed(1) }}万km</div>
            <div class="mobile-bike-footer">
              <span class="mobile-bike-price">¥{{ (row.price/10000).toFixed(1) }}万</span>
              <el-tag :type="BIKE_STATUS[row.bike_status]?.type" size="small">{{ BIKE_STATUS[row.bike_status]?.label }}</el-tag>
            </div>
          </div>
        </div>
        <div class="mobile-bike-actions">
          <el-button size="small" @click="$router.push(`/shop/bikes/${row.id}/edit`)">编辑</el-button>
          <el-button size="small" type="warning" v-if="row.bike_status === 1" @click="offShelf(row)">下架</el-button>
          <el-button size="small" type="success" v-if="row.bike_status === 3" @click="reOnShelf(row)">上架</el-button>
          <el-popconfirm title="确认删除？" @confirm="deleteBike(row)">
            <template #reference>
              <el-button size="small" type="danger" v-if="row.bike_status !== 4">删除</el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { BIKE_STATUS } from '@/stores/auth'
import api from '@/api'

const bikes = ref([])
const loading = ref(false)
const activeStatus = ref(0)

async function loadBikes() {
  loading.value = true
  try {
    const res = await api.getMyBikes()
    const list = res.data.list
    bikes.value = activeStatus.value === 0 ? list : list.filter(b => b.bike_status === activeStatus.value)
  } finally {
    loading.value = false
  }
}

async function offShelf(bike) {
  await new Promise(r => setTimeout(r, 300))
  bike.bike_status = 3
  ElMessage.success('已下架')
}
async function reOnShelf(bike) {
  await new Promise(r => setTimeout(r, 300))
  bike.bike_status = 1
  ElMessage.success('已重新上架')
}
async function deleteBike(bike) {
  await new Promise(r => setTimeout(r, 300))
  bikes.value = bikes.value.filter(b => b.id !== bike.id)
  ElMessage.success('已删除（逻辑删除）')
}

onMounted(loadBikes)
</script>

<style scoped>
.page-header-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.filter-row { display: flex; flex-wrap: wrap; gap: 8px; }

/* 移动端卡片列表默认隐藏 */
.mobile-list { display: none; }

.mobile-bike-card {
  background: #fff;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 10px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
.mobile-bike-info { display: flex; gap: 12px; margin-bottom: 10px; }
.mobile-bike-img { width: 80px; height: 60px; object-fit: cover; border-radius: 6px; flex-shrink: 0; }
.mobile-bike-detail { flex: 1; min-width: 0; }
.mobile-bike-name { font-weight: 600; color: #222; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mobile-bike-meta { font-size: 12px; color: #888; margin: 4px 0; }
.mobile-bike-footer { display: flex; align-items: center; gap: 8px; }
.mobile-bike-price { font-size: 15px; font-weight: 700; color: #ff4d4f; }
.mobile-bike-actions { display: flex; gap: 6px; flex-wrap: wrap; }

@media (max-width: 768px) {
  .pc-table { display: none; }
  .mobile-list { display: block; }
}
</style>

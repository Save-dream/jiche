<template>
  <div>
    <h2 class="page-title mb-4">车源管控</h2>

    <div class="filter-row mb-3">
      <el-radio-group v-model="statusFilter" @change="loadData">
        <el-radio-button :value="0">全部</el-radio-button>
        <el-radio-button :value="1">在售</el-radio-button>
        <el-radio-button :value="2">已售</el-radio-button>
        <el-radio-button :value="3">已下架</el-radio-button>
        <el-radio-button :value="4">违规下架</el-radio-button>
      </el-radio-group>
    </div>

    <div class="card">
      <el-table :data="bikes" v-loading="loading" empty-text="暂无车源">
        <el-table-column label="车辆信息" min-width="220">
          <template #default="{ row }">
            <div class="flex" style="gap:10px;align-items:center">
              <img :src="row.cover_image" style="width:60px;height:45px;object-fit:cover;border-radius:6px;flex-shrink:0" />
              <div>
                <div style="font-weight:600;color:#222">{{ row.brand }} {{ row.model }}</div>
                <div style="font-size:12px;color:#888">{{ row.year }}年 · {{ row.displacement }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="shop_name" label="所属商家" width="130" />
        <el-table-column label="售价" width="100">
          <template #default="{ row }">
            <span style="color:#ff4d4f;font-weight:600">¥{{ (row.price/10000).toFixed(1) }}万</span>
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="浏览" width="70" align="center" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="BIKE_STATUS[row.bike_status]?.type" size="small">{{ BIKE_STATUS[row.bike_status]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发布时间" width="110" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/bike/${row.id}`)">查看</el-button>
            <el-popconfirm v-if="row.bike_status === 1" title="确认强制下架该车辆？" @confirm="forceOffShelf(row)">
              <template #reference>
                <el-button size="small" type="danger">强制下架</el-button>
              </template>
            </el-popconfirm>
            <el-popconfirm v-if="row.bike_status === 4" title="确认恢复该车辆为在售状态？" @confirm="restoreBike(row)">
              <template #reference>
                <el-button size="small" type="success">恢复上架</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
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
const statusFilter = ref(0)

async function loadData() {
  loading.value = true
  try {
    const res = await api.getAllBikes()
    const list = res.data.list
    bikes.value = statusFilter.value === 0 ? list : list.filter(b => b.bike_status === statusFilter.value)
  } finally { loading.value = false }
}

async function forceOffShelf(row) {
  await new Promise(r => setTimeout(r, 400))
  row.bike_status = 4
  ElMessage.success('已强制下架')
}
async function restoreBike(row) {
  await new Promise(r => setTimeout(r, 400))
  row.bike_status = 1
  ElMessage.success('已恢复上架')
}

onMounted(loadData)
</script>

<style scoped>
.filter-row { display: flex; flex-wrap: wrap; gap: 8px; }
</style>

<template>
  <div>
    <h2 class="page-title mb-4">商户管理</h2>

    <div class="card">
      <el-table :data="shops" v-loading="loading" empty-text="暂无商户">
        <el-table-column label="商家信息" min-width="200">
          <template #default="{ row }">
            <div class="flex" style="gap:10px;align-items:center">
              <img :src="row.avatar" style="width:40px;height:40px;border-radius:8px;object-fit:cover;border:1px solid #eee" />
              <div>
                <div style="font-weight:600;color:#222">{{ row.name }}</div>
                <div style="font-size:12px;color:#888">{{ row.contact_name }} · {{ row.phone }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="经营地址" min-width="160" show-overflow-tooltip />
        <el-table-column prop="main_models" label="主营车型" min-width="130" show-overflow-tooltip />
        <el-table-column prop="bike_count" label="车源数" width="80" align="center" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="SHOP_STATUS[row.shop_status]?.type" size="small">{{ SHOP_STATUS[row.shop_status]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/shop/${row.id}`)">查看主页</el-button>
            <el-popconfirm v-if="row.shop_status !== 4" title="确认封禁该商户？封禁后商家将无法操作任何数据。" @confirm="banShop(row)">
              <template #reference>
                <el-button size="small" type="danger">封禁</el-button>
              </template>
            </el-popconfirm>
            <el-popconfirm v-else title="确认解除封禁？" @confirm="unbanShop(row)">
              <template #reference>
                <el-button size="small" type="success">解封</el-button>
              </template>
            </el-popconfirm>
            <el-popconfirm title="确认删除该商户？删除后前台不可见（逻辑删除）。" @confirm="deleteShop(row)">
              <template #reference>
                <el-button size="small" type="danger" plain>删除</el-button>
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
import { SHOP_STATUS } from '@/stores/auth'
import api from '@/api'

const shops = ref([])
const loading = ref(false)

async function loadData() {
  loading.value = true
  try {
    const res = await api.getAllShops()
    shops.value = res.data.list
  } finally { loading.value = false }
}

async function banShop(row) {
  const res = await api.banShop(row.id)
  row.shop_status = res.data.shop_status
  ElMessage.success('商户已封禁')
}
async function unbanShop(row) {
  const res = await api.unbanShop(row.id)
  row.shop_status = res.data.shop_status
  ElMessage.success('封禁已解除')
}
async function deleteShop(row) {
  await api.deleteShop(row.id)
  shops.value = shops.value.filter((s) => s.id !== row.id)
  ElMessage.success('商户已删除')
}

onMounted(loadData)
</script>

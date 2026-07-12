<template>
  <div>
    <h2 class="page-title mb-4">管理员管理</h2>
    <p class="text-muted mb-4" style="font-size:13px">
      授予或撤销平台管理员权限。预置超级管理员不可撤销；不支持前台自助注册。
    </p>

    <div class="card">
      <el-table :data="users" v-loading="loading" empty-text="暂无用户">
        <el-table-column label="用户" min-width="180">
          <template #default="{ row }">
            <div class="flex" style="gap:10px;align-items:center">
              <img v-if="row.avatar" :src="row.avatar" style="width:36px;height:36px;border-radius:50%;object-fit:cover" />
              <div>
                <div style="font-weight:600;color:#222">{{ row.nickname }}</div>
                <div style="font-size:12px;color:#888">ID: {{ row.id }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column label="商家状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="SHOP_STATUS[row.shop_status]?.type" size="small">
              {{ SHOP_STATUS[row.shop_status]?.label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="管理员" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_super_staff" type="danger" size="small">超级管理员</el-tag>
            <el-tag v-else-if="row.is_staff" type="warning" size="small">管理员</el-tag>
            <span v-else class="text-muted" style="font-size:12px">普通用户</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              v-if="!row.is_staff && !row.is_super_staff"
              title="确认授予该用户管理员权限？"
              @confirm="grant(row)"
            >
              <template #reference>
                <el-button size="small" type="primary">授予管理员</el-button>
              </template>
            </el-popconfirm>
            <el-popconfirm
              v-else-if="row.is_staff && !row.is_super_staff"
              title="确认撤销该用户的管理员权限？"
              @confirm="revoke(row)"
            >
              <template #reference>
                <el-button size="small" type="danger">撤销权限</el-button>
              </template>
            </el-popconfirm>
            <span v-else class="text-muted" style="font-size:12px">不可操作</span>
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

const users = ref([])
const loading = ref(false)

async function loadData() {
  loading.value = true
  try {
    const res = await api.getAdminUsers()
    users.value = res.data.list
  } finally {
    loading.value = false
  }
}

async function grant(row) {
  try {
    const res = await api.grantStaff(row.id)
    Object.assign(row, res.data)
    ElMessage.success('已授予管理员权限')
  } catch { /* handled by interceptor */ }
}

async function revoke(row) {
  try {
    const res = await api.revokeStaff(row.id)
    Object.assign(row, res.data)
    ElMessage.success('已撤销管理员权限')
  } catch { /* handled by interceptor */ }
}

onMounted(loadData)
</script>

<template>
  <div>
    <h2 class="page-title mb-4">用户管理</h2>
    <p class="text-muted mb-4" style="font-size:13px">
      展示全部用户；可封禁、解封、删除、授予/撤销管理员。正常用户须先封禁后才可删除；封禁与删除需填写理由。
    </p>

    <div class="card mb-4" style="padding:12px 16px">
      <el-radio-group v-model="statusFilter" @change="loadData">
        <el-radio-button label="active">正常</el-radio-button>
        <el-radio-button label="banned">已封禁</el-radio-button>
        <el-radio-button label="deleted">已删除</el-radio-button>
        <el-radio-button label="all">全部</el-radio-button>
      </el-radio-group>
    </div>

    <div class="card">
      <el-table :data="users" v-loading="loading" empty-text="暂无用户">
        <el-table-column label="用户" min-width="180">
          <template #default="{ row }">
            <div class="flex" style="gap:10px;align-items:center">
              <img v-if="row.avatar" :src="row.avatar" style="width:36px;height:36px;border-radius:50%;object-fit:cover" />
              <div>
                <div style="font-weight:600;color:#222">{{ row.nickname || '未命名' }}</div>
                <div style="font-size:12px;color:#888">ID: {{ row.id }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column label="账户状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="accountStatusMeta(row).type" size="small">
              {{ accountStatusMeta(row).label }}
            </el-tag>
          </template>
        </el-table-column>
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
        <el-table-column label="理由 / 备注" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.account_status === 'banned'" style="font-size:12px;color:#666">
              {{ row.ban_reason || '—' }}
            </span>
            <span v-else-if="row.account_status === 'deleted'" style="font-size:12px;color:#666">
              {{ row.delete_reason || '—' }}
            </span>
            <span v-else class="text-muted" style="font-size:12px">—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <template v-if="row.account_status === 'active' && !row.is_super_staff && row.id !== auth.user?.id">
              <el-button size="small" type="warning" @click="openReason('ban', row)">封禁</el-button>
              <el-popconfirm
                v-if="!row.is_staff"
                title="确认授予该用户管理员权限？"
                @confirm="grant(row)"
              >
                <template #reference>
                  <el-button size="small" type="primary">授予管理员</el-button>
                </template>
              </el-popconfirm>
              <el-popconfirm
                v-else
                title="确认撤销该用户的管理员权限？"
                @confirm="revoke(row)"
              >
                <template #reference>
                  <el-button size="small">撤销权限</el-button>
                </template>
              </el-popconfirm>
            </template>
            <template v-else-if="row.account_status === 'banned' && !row.is_super_staff">
              <el-button size="small" type="success" @click="unban(row)">解封</el-button>
              <el-button size="small" type="danger" @click="openReason('delete', row)">删除</el-button>
            </template>
            <span v-else class="text-muted" style="font-size:12px">不可操作</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="reasonVisible"
      :title="reasonMode === 'ban' ? '封禁用户' : '删除用户'"
      width="420px"
      destroy-on-close
    >
      <p style="font-size:13px;color:#666;margin-bottom:12px">
        将对「{{ reasonTarget?.nickname || reasonTarget?.id }}」执行
        {{ reasonMode === 'ban' ? '封禁' : '删除' }}，请填写理由。
      </p>
      <el-input
        v-model="reasonText"
        type="textarea"
        :rows="3"
        maxlength="200"
        show-word-limit
        placeholder="请输入理由（至少 2 个字）"
      />
      <template #footer>
        <el-button @click="reasonVisible = false">取消</el-button>
        <el-button type="danger" :loading="submitting" @click="submitReason">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { SHOP_STATUS, useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const users = ref([])
const loading = ref(false)
const statusFilter = ref('active')

const reasonVisible = ref(false)
const reasonMode = ref('ban')
const reasonTarget = ref(null)
const reasonText = ref('')
const submitting = ref(false)

function accountStatusMeta(row) {
  const status = row.account_status || (row.is_deleted ? 'deleted' : row.is_active === false ? 'banned' : 'active')
  if (status === 'deleted') return { label: '已删除', type: 'info' }
  if (status === 'banned') return { label: '已封禁', type: 'danger' }
  return { label: '正常', type: 'success' }
}

async function loadData() {
  loading.value = true
  try {
    const res = await api.getAdminUsers({ status: statusFilter.value })
    users.value = res.data.list
  } finally {
    loading.value = false
  }
}

function openReason(mode, row) {
  reasonMode.value = mode
  reasonTarget.value = row
  reasonText.value = ''
  reasonVisible.value = true
}

async function submitReason() {
  const reason = reasonText.value.trim()
  if (reason.length < 2) {
    ElMessage.warning('请填写操作理由（至少 2 个字）')
    return
  }
  submitting.value = true
  try {
    if (reasonMode.value === 'ban') {
      const res = await api.banUser(reasonTarget.value.id, { reason })
      ElMessage.success('用户已封禁')
      if (statusFilter.value === 'active') {
        users.value = users.value.filter((u) => u.id !== reasonTarget.value.id)
      } else {
        Object.assign(reasonTarget.value, res.data)
      }
    } else {
      const res = await api.deleteUser(reasonTarget.value.id, { reason })
      ElMessage.success('用户已删除')
      if (statusFilter.value === 'banned') {
        users.value = users.value.filter((u) => u.id !== reasonTarget.value.id)
      } else {
        Object.assign(reasonTarget.value, res.data)
      }
    }
    reasonVisible.value = false
  } catch { /* interceptor */ } finally {
    submitting.value = false
  }
}

async function unban(row) {
  try {
    const res = await api.unbanUser(row.id)
    ElMessage.success('已解除封禁')
    if (statusFilter.value === 'banned') {
      users.value = users.value.filter((u) => u.id !== row.id)
    } else {
      Object.assign(row, res.data)
    }
  } catch { /* interceptor */ }
}

async function grant(row) {
  try {
    const res = await api.grantStaff(row.id)
    Object.assign(row, res.data)
    ElMessage.success('已授予管理员权限')
  } catch { /* interceptor */ }
}

async function revoke(row) {
  try {
    const res = await api.revokeStaff(row.id)
    Object.assign(row, res.data)
    ElMessage.success('已撤销管理员权限')
  } catch { /* interceptor */ }
}

onMounted(loadData)
</script>

<template>
  <div>
    <h2 class="page-title mb-4">用户管理</h2>
    <p class="text-muted mb-4" style="font-size:13px">
      列表展示全部用户。普通用户可封禁/解封/删除、授予管理员；
      <strong>平台管理员不可封禁、不可删除</strong>。封禁后无法登录进入系统。
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
        <el-table-column label="用户" min-width="200">
          <template #default="{ row }">
            <div class="flex" style="gap:10px;align-items:center">
              <img
                v-if="row.avatar"
                :src="row.avatar"
                style="width:36px;height:36px;border-radius:50%;object-fit:cover"
              />
              <div
                v-else
                style="width:36px;height:36px;border-radius:50%;background:#eee;display:flex;align-items:center;justify-content:center;font-size:12px;color:#999"
              >
                {{ (row.nickname || '?').slice(0, 1) }}
              </div>
              <div>
                <div style="font-weight:600;color:#222">{{ row.nickname || '未命名' }}</div>
                <div style="font-size:12px;color:#888">ID: {{ row.id }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="120">
          <template #default="{ row }">{{ row.phone || '—' }}</template>
        </el-table-column>
        <el-table-column label="注册时间" width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="最后登录" width="160">
          <template #default="{ row }">{{ formatTime(row.last_login_at) }}</template>
        </el-table-column>
        <el-table-column label="账户状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="accountStatusMeta(row).type" size="small">
              {{ accountStatusMeta(row).label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="商家状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag
              v-if="isMerchant(row)"
              :type="SHOP_STATUS[row.shop_status]?.type"
              size="small"
            >
              {{ SHOP_STATUS[row.shop_status]?.label }}
            </el-tag>
            <span v-else class="text-muted" style="font-size:12px">—</span>
          </template>
        </el-table-column>
        <el-table-column label="是否管理员" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_super_staff" type="danger" size="small">超级管理员</el-tag>
            <el-tag v-else-if="row.is_staff" type="warning" size="small">管理员</el-tag>
            <span v-else class="text-muted" style="font-size:12px">否</span>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="140" show-overflow-tooltip>
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
            <!-- 平台管理员：不可封禁/删除；仅超管可展示为不可操作；普通管理员可撤销 -->
            <template v-if="isPlatformAdminRow(row)">
              <el-popconfirm
                v-if="row.is_staff && !row.is_super_staff && row.account_status === 'active'"
                title="确认撤销该用户的管理员权限？"
                @confirm="revoke(row)"
              >
                <template #reference>
                  <el-button size="small">撤销管理员</el-button>
                </template>
              </el-popconfirm>
              <span v-else class="text-muted" style="font-size:12px">不可封禁/删除</span>
            </template>
            <template v-else-if="row.account_status === 'active'">
              <el-button size="small" type="warning" @click="openReason('ban', row)">封禁</el-button>
              <el-button size="small" type="danger" plain @click="openReason('delete', row)">删除</el-button>
              <el-popconfirm
                v-if="!row.is_staff"
                title="确认授予该用户与平台管理员一致的权限？"
                @confirm="grant(row)"
              >
                <template #reference>
                  <el-button size="small" type="primary">授予管理员</el-button>
                </template>
              </el-popconfirm>
            </template>
            <template v-else-if="row.account_status === 'banned'">
              <el-button size="small" type="success" @click="unban(row)">解封</el-button>
              <el-button size="small" type="danger" @click="openReason('delete', row)">删除</el-button>
            </template>
            <span v-else class="text-muted" style="font-size:12px">已删除</span>
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
        {{ reasonMode === 'ban' ? '封禁（封禁后无法登录）' : '逻辑删除' }}，请填写理由。
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
import { SHOP_STATUS } from '@/stores/auth'
import api from '@/api'

const users = ref([])
const loading = ref(false)
const statusFilter = ref('active')

const reasonVisible = ref(false)
const reasonMode = ref('ban')
const reasonTarget = ref(null)
const reasonText = ref('')
const submitting = ref(false)

function isPlatformAdminRow(row) {
  return !!(row.is_staff || row.is_super_staff)
}

function isMerchant(row) {
  // 已入驻 / 待审核 / 驳回 / 商家封禁 均展示商家状态；纯普通用户不展示
  return row.shop_status !== 0 && row.shop_status != null
}

function accountStatusMeta(row) {
  const status = row.account_status || (row.is_deleted ? 'deleted' : row.is_active === false ? 'banned' : 'active')
  if (status === 'deleted') return { label: '已删除', type: 'info' }
  if (status === 'banned') return { label: '已封禁', type: 'danger' }
  return { label: '正常', type: 'success' }
}

function formatTime(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value).replace('T', ' ').slice(0, 19)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
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
  if (isPlatformAdminRow(row)) {
    ElMessage.warning('平台管理员不可封禁或删除')
    return
  }
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
      ElMessage.success('用户已封禁，将无法登录')
      if (statusFilter.value === 'active') {
        users.value = users.value.filter((u) => u.id !== reasonTarget.value.id)
      } else {
        Object.assign(reasonTarget.value, res.data)
      }
    } else {
      const res = await api.deleteUser(reasonTarget.value.id, { reason })
      ElMessage.success('用户已删除')
      if (statusFilter.value === 'active' || statusFilter.value === 'banned') {
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

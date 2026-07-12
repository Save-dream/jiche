<template>
  <div>
    <div class="page-header-bar mb-4">
      <h2 class="page-title">商家审核</h2>
      <el-radio-group v-model="statusFilter" @change="loadData" class="status-filter">
        <el-radio-button :value="1">待审核 <el-badge v-if="pendingCount" :value="pendingCount" /></el-radio-button>
        <el-radio-button :value="2">已通过</el-radio-button>
        <el-radio-button :value="3">已驳回</el-radio-button>
        <el-radio-button :value="0">全部</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 桌面端表格 -->
    <div class="card desktop-only">
      <el-table :data="list" v-loading="loading" empty-text="暂无申请记录">
        <el-table-column label="申请人" width="100">
          <template #default="{ row }">
            <div>{{ row.user_name || row.contact_name }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="商家名称" min-width="120" show-overflow-tooltip />
        <el-table-column prop="shop_type" label="类型" width="90" />
        <el-table-column prop="contact_name" label="联系人" width="90" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="address" label="经营地址" min-width="140" show-overflow-tooltip />
        <el-table-column prop="main_models" label="主营车型" min-width="120" show-overflow-tooltip />
        <el-table-column label="微信二维码" width="90" align="center">
          <template #default="{ row }">
            <el-image :src="mediaUrl(row.wechat_qrcode)" style="width:40px;height:40px;border-radius:4px" fit="contain"
              :preview-src-list="[mediaUrl(row.wechat_qrcode)]" preview-teleported />
          </template>
        </el-table-column>
        <el-table-column label="资质照片" width="90" align="center">
          <template #default="{ row }">
            <el-image v-if="row.qualification_photo" :src="mediaUrl(row.qualification_photo)" style="width:40px;height:40px;border-radius:4px"
              :preview-src-list="[mediaUrl(row.qualification_photo)]" preview-teleported />
            <span v-else class="text-muted" style="font-size:12px">未上传</span>
          </template>
        </el-table-column>
        <el-table-column prop="applied_at" label="申请时间" width="140" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="SHOP_STATUS[row.shop_status]?.type" size="small">{{ SHOP_STATUS[row.shop_status]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <template v-if="row.shop_status === 1">
              <el-button size="small" type="success" :loading="operating" @click="approve(row)">通过</el-button>
              <el-button size="small" type="danger" @click="openReject(row)">驳回</el-button>
            </template>
            <span v-else class="text-muted" style="font-size:12px">已处理</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 手机端卡片 -->
    <div class="mobile-only" v-loading="loading">
      <el-empty v-if="!list.length" description="暂无申请记录" />
      <div v-for="row in list" :key="row.id" class="audit-card">
        <div class="audit-card-header">
          <div>
            <div class="audit-name">{{ row.user_name || row.contact_name }}</div>
            <div class="audit-meta">{{ row.shop_type }} · {{ row.applied_at }}</div>
          </div>
          <el-tag :type="SHOP_STATUS[row.shop_status]?.type" size="small">
            {{ SHOP_STATUS[row.shop_status]?.label }}
          </el-tag>
        </div>

        <div class="audit-info">
          <div class="audit-row" v-if="row.name"><span class="label">商家</span><span>{{ row.name }}</span></div>
          <div class="audit-row"><span class="label">联系人</span><span>{{ row.contact_name }}</span></div>
          <div class="audit-row"><span class="label">电话</span>
            <a :href="`tel:${row.phone}`" class="phone-link">{{ row.phone }}</a>
          </div>
          <div class="audit-row" v-if="row.address"><span class="label">地址</span><span>{{ row.address }}</span></div>
          <div class="audit-row" v-if="row.main_models"><span class="label">主营</span><span>{{ row.main_models }}</span></div>
          <div class="audit-row" v-if="row.description"><span class="label">说明</span><span>{{ row.description }}</span></div>
        </div>

        <div class="audit-images">
          <div class="image-item">
            <div class="image-label">微信二维码</div>
            <el-image :src="mediaUrl(row.wechat_qrcode)" fit="contain" class="audit-image"
              :preview-src-list="[mediaUrl(row.wechat_qrcode)]" preview-teleported />
          </div>
          <div class="image-item" v-if="row.qualification_photo">
            <div class="image-label">资质照片</div>
            <el-image :src="mediaUrl(row.qualification_photo)" fit="contain" class="audit-image"
              :preview-src-list="[mediaUrl(row.qualification_photo)]" preview-teleported />
          </div>
        </div>

        <div v-if="row.shop_status === 1" class="audit-actions">
          <el-button type="success" :loading="operating" @click="approve(row)">通过</el-button>
          <el-button type="danger" plain @click="openReject(row)">驳回</el-button>
        </div>
        <div v-else class="audit-done text-muted">已处理</div>
      </div>
    </div>

    <el-dialog
      v-model="rejectVisible"
      title="驳回申请"
      :width="isMobile ? '92%' : '440px'"
      :close-on-click-modal="false"
    >
      <el-form ref="rejectFormRef" :model="rejectForm" :rules="rejectRules" label-width="80px">
        <el-form-item label="驳回原因" prop="reason">
          <el-input v-model="rejectForm.reason" type="textarea" :rows="3" placeholder="请填写驳回原因，将通知申请人" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="danger" :loading="operating" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { SHOP_STATUS } from '@/stores/auth'
import api from '@/api'

const list = ref([])
const loading = ref(false)
const statusFilter = ref(1)
const operating = ref(false)
const rejectVisible = ref(false)
const currentRow = ref(null)
const pendingCount = ref(0)
const isMobile = ref(false)
const rejectFormRef = ref()
const rejectForm = reactive({ reason: '' })
const rejectRules = { reason: [{ required: true, message: '请填写驳回原因', trigger: 'blur' }] }

function checkMobile() {
  isMobile.value = window.innerWidth <= 768
}

function mediaUrl(url) {
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('data:')) return url
  return url
}

async function loadPendingCount() {
  try {
    const res = await api.getShopApplications({ status: 1 })
    pendingCount.value = res.data.total
  } catch {
    pendingCount.value = 0
  }
}

async function loadData() {
  loading.value = true
  try {
    const params = statusFilter.value !== 0 ? { status: statusFilter.value } : {}
    const res = await api.getShopApplications(params)
    list.value = res.data.list
    if (statusFilter.value === 1) pendingCount.value = res.data.total
  } finally {
    loading.value = false
  }
}

function notifyPendingChanged() {
  window.dispatchEvent(new CustomEvent('admin:pending-audit-changed'))
}

async function approve(row) {
  operating.value = true
  try {
    await api.auditShop(row.id, { action: 'approve' })
    ElMessage.success('已通过，商家权限已开通')
    await loadData()
    await loadPendingCount()
    notifyPendingChanged()
  } finally {
    operating.value = false
  }
}

function openReject(row) {
  currentRow.value = row
  rejectForm.reason = ''
  rejectVisible.value = true
}

async function confirmReject() {
  const valid = await rejectFormRef.value?.validate().catch(() => false)
  if (!valid) return
  operating.value = true
  try {
    await api.auditShop(currentRow.value.id, {
      action: 'reject',
      reject_reason: rejectForm.reason,
    })
    rejectVisible.value = false
    ElMessage.success('已驳回')
    await loadData()
    await loadPendingCount()
    notifyPendingChanged()
  } finally {
    operating.value = false
  }
}

onMounted(async () => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  await loadPendingCount()
  await loadData()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.page-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.status-filter {
  flex-wrap: wrap;
}
.desktop-only { display: block; }
.mobile-only { display: none; }

.audit-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
}
.audit-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}
.audit-name {
  font-size: 16px;
  font-weight: 600;
  color: #222;
  margin-bottom: 4px;
}
.audit-meta {
  font-size: 12px;
  color: #888;
}
.audit-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}
.audit-row {
  display: flex;
  gap: 10px;
  font-size: 13px;
  color: #444;
  line-height: 1.5;
}
.audit-row .label {
  flex-shrink: 0;
  width: 52px;
  color: #888;
}
.phone-link {
  color: #1890ff;
  text-decoration: none;
}
.audit-images {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}
.image-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.image-label {
  font-size: 12px;
  color: #888;
}
.audit-image {
  width: 88px;
  height: 88px;
  border-radius: 8px;
  border: 1px solid #eee;
  background: #fafafa;
}
.audit-actions {
  display: flex;
  gap: 10px;
}
.audit-actions .el-button {
  flex: 1;
}
.audit-done {
  font-size: 13px;
  text-align: center;
  padding-top: 4px;
}

@media (max-width: 768px) {
  .desktop-only { display: none; }
  .mobile-only { display: block; }
  .page-title { font-size: 18px; }
  .status-filter {
    width: 100%;
    display: flex;
  }
  .status-filter :deep(.el-radio-button) {
    flex: 1;
  }
  .status-filter :deep(.el-radio-button__inner) {
    width: 100%;
    padding: 8px 6px;
    font-size: 12px;
  }
}
</style>

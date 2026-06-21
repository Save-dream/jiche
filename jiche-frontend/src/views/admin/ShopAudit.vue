<template>
  <div>
    <div class="page-header-bar mb-4">
      <h2 class="page-title">商家审核</h2>
      <el-radio-group v-model="statusFilter" @change="loadData">
        <el-radio-button :value="1">待审核 <el-badge v-if="pendingCount" :value="pendingCount" /></el-radio-button>
        <el-radio-button :value="2">已通过</el-radio-button>
        <el-radio-button :value="3">已驳回</el-radio-button>
        <el-radio-button :value="0">全部</el-radio-button>
      </el-radio-group>
    </div>

    <div class="card">
      <el-table :data="list" v-loading="loading" empty-text="暂无申请记录">
        <el-table-column label="联系人" width="90">
          <template #default="{ row }"><span>{{ row.contact_name }}</span></template>
        </el-table-column>
        <el-table-column prop="shop_type" label="类型" width="90" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="address" label="经营地址" min-width="140" show-overflow-tooltip />
        <el-table-column prop="main_models" label="主营车型" min-width="120" show-overflow-tooltip />
        <el-table-column label="微信二维码" width="90" align="center">
          <template #default="{ row }">
            <el-image :src="row.wechat_qrcode" style="width:40px;height:40px;border-radius:4px" fit="contain"
              :preview-src-list="[row.wechat_qrcode]" preview-teleported />
          </template>
        </el-table-column>
        <el-table-column label="资质照片" width="90" align="center">
          <template #default="{ row }">
            <el-image v-if="row.qualification_photo" :src="row.qualification_photo" style="width:40px;height:40px;border-radius:4px"
              :preview-src-list="[row.qualification_photo]" preview-teleported />
            <span v-else class="text-muted" style="font-size:12px">未上传</span>
          </template>
        </el-table-column>
        <el-table-column prop="applied_at" label="申请时间" width="140" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="SHOP_STATUS[row.shop_status]?.type" size="small">{{ SHOP_STATUS[row.shop_status]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right" v-if="statusFilter === 1 || statusFilter === 0">
          <template #default="{ row }">
            <template v-if="row.shop_status === 1">
              <el-button size="small" type="success" @click="approve(row)">通过</el-button>
              <el-button size="small" type="danger" @click="openReject(row)">驳回</el-button>
            </template>
            <span v-else class="text-muted" style="font-size:12px">已处理</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 驳回弹窗 -->
    <el-dialog v-model="rejectVisible" title="驳回申请" width="440px" :close-on-click-modal="false">
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { SHOP_STATUS } from '@/stores/auth'
import api from '@/api'

const list = ref([])
const loading = ref(false)
const statusFilter = ref(1)
const operating = ref(false)
const rejectVisible = ref(false)
const currentRow = ref(null)
const rejectFormRef = ref()
const rejectForm = reactive({ reason: '' })
const rejectRules = { reason: [{ required: true, message: '请填写驳回原因', trigger: 'blur' }] }

const pendingCount = computed(() => list.value.filter(r => r.shop_status === 1).length)

async function loadData() {
  loading.value = true
  try {
    const params = statusFilter.value !== 0 ? { status: statusFilter.value } : {}
    const res = await api.getShopApplications(params)
    list.value = res.data.list
  } finally {
    loading.value = false
  }
}

async function approve(row) {
  operating.value = true
  try {
    await new Promise(r => setTimeout(r, 500))
    row.shop_status = 2
    ElMessage.success('已通过，商家权限已开通')
  } finally {
    operating.value = false
  }
}

function openReject(row) { currentRow.value = row; rejectForm.reason = ''; rejectVisible.value = true }

async function confirmReject() {
  const valid = await rejectFormRef.value?.validate().catch(() => false)
  if (!valid) return
  operating.value = true
  try {
    await new Promise(r => setTimeout(r, 500))
    currentRow.value.shop_status = 3
    currentRow.value.reject_reason = rejectForm.reason
    rejectVisible.value = false
    ElMessage.success('已驳回')
  } finally {
    operating.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-header-bar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
</style>

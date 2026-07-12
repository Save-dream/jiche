<template>
  <div>
    <el-breadcrumb separator="/" class="mb-3">
      <el-breadcrumb-item :to="{ path: '/profile' }">个人中心</el-breadcrumb-item>
      <el-breadcrumb-item>{{ pageTitle }}</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 待审核提示 -->
    <el-alert v-if="auth.shopStatus === 1" type="warning" show-icon :closable="false" class="mb-4"
      title="您的申请正在审核中" description="请耐心等待，审核结果将在1-3个工作日内反馈。审核期间无法修改或重新提交。" />

    <!-- 驳回提示 -->
    <el-alert v-if="auth.shopStatus === 3 && rejectReason" type="error" show-icon :closable="false" class="mb-4"
      title="申请已被驳回" :description="`驳回原因：${rejectReason}，请修改后重新提交。`" />

    <!-- 已入驻提示 -->
    <el-alert v-if="auth.shopStatus === 2" type="success" show-icon :closable="false" class="mb-4"
      title="您已是入驻商家" description="可进入商家后台发布车源。" />

    <div class="card" v-if="auth.shopStatus !== 2">
      <div class="card-header flex-between">
        <span>{{ pageTitle }}</span>
        <span v-if="appliedAt" class="applied-at">提交时间：{{ appliedAt }}</span>
      </div>
      <div class="card-body" v-loading="pageLoading">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" :disabled="isReadOnly">

          <div class="form-section-title">基本信息</div>

          <el-form-item label="商家名称" prop="name">
            <el-input v-model="form.name" placeholder="2-64 字，如：极速机车行" maxlength="64" style="width:400px" show-word-limit />
          </el-form-item>

          <el-form-item label="入驻类型" prop="shop_type">
            <el-select v-model="form.shop_type" placeholder="请选择入驻类型" style="width:200px">
              <el-option label="个人商户" value="个人商户" />
              <el-option label="企业商户" value="企业商户" />
            </el-select>
          </el-form-item>

          <el-form-item label="联系人姓名" prop="contact_name">
            <el-input v-model="form.contact_name" placeholder="2-10位中文姓名" maxlength="10" style="width:260px" />
          </el-form-item>

          <el-form-item label="联系电话" prop="phone">
            <el-input v-model="form.phone" placeholder="11位手机号" maxlength="11" style="width:260px" />
          </el-form-item>

          <el-form-item label="经营地址" prop="address">
            <el-input v-model="form.address" placeholder="选填，最多100字" maxlength="100" style="width:400px" />
          </el-form-item>

          <el-form-item label="主营车型" prop="main_models">
            <el-input v-model="form.main_models" placeholder="选填，如：本田、雅马哈中大排量" maxlength="50" style="width:400px" />
          </el-form-item>

          <el-form-item label="入驻说明" prop="description">
            <el-input v-model="form.description" type="textarea" :rows="3" placeholder="选填，简述您的经营情况，最多200字" maxlength="200" show-word-limit style="width:500px" />
          </el-form-item>

          <div class="form-section-title">资质证明</div>

          <el-form-item label="微信二维码" prop="wechat_qrcode" required>
            <div class="upload-area">
              <div v-if="form.wechat_qrcode_preview" class="preview-wrap">
                <img :src="form.wechat_qrcode_preview" class="upload-image-preview" />
                <el-button v-if="!isReadOnly" size="small" type="danger" plain @click="clearQR">删除</el-button>
              </div>
              <label v-else-if="!isReadOnly" class="upload-btn">
                <input type="file" accept="image/jpeg,image/png" @change="handleQRUpload" hidden />
                <el-icon><Plus /></el-icon>
                <span>上传微信二维码</span>
              </label>
              <div v-if="!isReadOnly" class="upload-tip">格式：jpg/png，大小≤5M</div>
            </div>
          </el-form-item>

          <el-form-item label="资质照片" :prop="form.shop_type === '企业商户' ? 'qualification_photo' : ''">
            <div class="upload-area">
              <div v-if="form.qualification_photo_preview" class="preview-wrap">
                <img :src="form.qualification_photo_preview" class="upload-image-preview" />
                <el-button v-if="!isReadOnly" size="small" type="danger" plain @click="clearQual">删除</el-button>
              </div>
              <label v-else-if="!isReadOnly" class="upload-btn">
                <input type="file" accept="image/jpeg,image/png" @change="handleQualUpload" hidden />
                <el-icon><Plus /></el-icon>
                <span>上传资质照片</span>
              </label>
              <div v-if="!isReadOnly" class="upload-tip">
                {{ form.shop_type === '企业商户' ? '企业商户必填（营业执照等）' : '个人商户选填' }}
              </div>
            </div>
          </el-form-item>

          <el-form-item v-if="!isReadOnly">
            <el-button
              type="primary"
              size="large"
              :loading="submitting"
              :disabled="auth.shopStatus === 4"
              @click="submit"
            >
              提交申请
            </el-button>
          </el-form-item>

        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const router = useRouter()
const formRef = ref()
const submitting = ref(false)
const pageLoading = ref(false)
const rejectReason = ref('')
const appliedAt = ref('')

const form = reactive({
  name: '',
  shop_type: '',
  contact_name: '',
  phone: '',
  address: '',
  main_models: '',
  description: '',
  wechat_qrcode: null,
  wechat_qrcode_preview: '',
  wechat_qrcode_url: '',
  qualification_photo: null,
  qualification_photo_preview: '',
  qualification_photo_url: '',
})

const rules = {
  name: [
    { required: true, message: '请填写商家名称', trigger: 'blur' },
    { min: 2, max: 64, message: '商家名称长度为 2-64 字', trigger: 'blur' },
  ],
  shop_type: [{ required: true, message: '请选择入驻类型', trigger: 'change' }],
  contact_name: [
    { required: true, message: '请填写联系人姓名', trigger: 'blur' },
    { pattern: /^[\u4e00-\u9fa5]{2,10}$/, message: '姓名须为2-10位中文', trigger: 'blur' },
  ],
  phone: [
    { required: true, message: '请填写联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请填写正确的手机号', trigger: 'blur' },
  ],
}

const isReadOnly = computed(() => auth.shopStatus === 1 || auth.shopStatus === 4)

const pageTitle = computed(() => {
  if (auth.shopStatus === 1) return '申请详情（审核中）'
  if (auth.shopStatus === 3) return '修改入驻申请'
  return '商家入驻申请'
})

function mediaUrl(url) {
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('blob:') || url.startsWith('data:')) return url
  return url.startsWith('/') ? url : `/${url}`
}

function fillFromApplication(app) {
  if (!app) return
  form.name = app.name || form.name
  form.shop_type = app.shop_type || form.shop_type
  form.contact_name = app.contact_name || form.contact_name
  form.phone = app.phone || form.phone
  form.address = app.address || ''
  form.main_models = app.main_models || ''
  form.description = app.description || ''
  appliedAt.value = app.applied_at || ''
  if (app.wechat_qrcode) {
    form.wechat_qrcode_url = app.wechat_qrcode
    form.wechat_qrcode_preview = mediaUrl(app.wechat_qrcode)
  }
  if (app.qualification_photo) {
    form.qualification_photo_url = app.qualification_photo
    form.qualification_photo_preview = mediaUrl(app.qualification_photo)
  }
  rejectReason.value = app.reject_reason || ''
}

async function loadMyApplication() {
  try {
    const res = await api.getMyApplication()
    if (res.data) {
      fillFromApplication(res.data)
      // 以申请记录同步入驻状态，避免本地缓存滞后
      if (auth.user && res.data.shop_status != null && auth.user.shop_status !== res.data.shop_status) {
        auth.setUser({ ...auth.user, shop_status: res.data.shop_status })
      }
    }
  } catch { /* ignore */ }
}

async function initPage() {
  if (!auth.isLoggedIn) return
  if (auth.isAdmin) {
    router.replace('/admin/audit')
    return
  }
  pageLoading.value = true
  try {
    await auth.refreshUser(api)
    await loadMyApplication()
  } finally {
    pageLoading.value = false
  }
}

function handleFile(e, previewKey, fileKey) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) { ElMessage.error('图片大小不能超过5M'); return }
  form[fileKey] = file
  form[previewKey] = URL.createObjectURL(file)
}
function handleQRUpload(e) { handleFile(e, 'wechat_qrcode_preview', 'wechat_qrcode') }
function handleQualUpload(e) { handleFile(e, 'qualification_photo_preview', 'qualification_photo') }

function clearQR() {
  form.wechat_qrcode = null
  form.wechat_qrcode_preview = ''
  form.wechat_qrcode_url = ''
}
function clearQual() {
  form.qualification_photo = null
  form.qualification_photo_preview = ''
  form.qualification_photo_url = ''
}

async function uploadIfNeeded(file, existingUrl) {
  if (file) {
    const res = await api.uploadImage(file)
    return res.data.url
  }
  return existingUrl || ''
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  if (!form.wechat_qrcode && !form.wechat_qrcode_url) {
    ElMessage.error('请上传微信二维码')
    return
  }
  if (form.shop_type === '企业商户' && !form.qualification_photo && !form.qualification_photo_url) {
    ElMessage.error('企业商户必须上传资质照片')
    return
  }

  submitting.value = true
  try {
    const wechat_qrcode = await uploadIfNeeded(form.wechat_qrcode, form.wechat_qrcode_url)
    const qualification_photo = await uploadIfNeeded(form.qualification_photo, form.qualification_photo_url)
    const res = await api.submitApplication({
      name: form.name.trim(),
      shop_type: form.shop_type,
      contact_name: form.contact_name,
      phone: form.phone,
      address: form.address,
      main_models: form.main_models,
      description: form.description,
      wechat_qrcode,
      qualification_photo: qualification_photo || '',
    })
    auth.setUser(res.data.user)
    fillFromApplication(res.data.application)
    rejectReason.value = ''
    ElMessage.success('申请提交成功！请等待平台审核。')
  } finally {
    submitting.value = false
  }
}

onMounted(initPage)
</script>

<style scoped>
.flex-between { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.applied-at { font-size: 12px; color: #888; font-weight: normal; }
.upload-area { display: flex; flex-direction: column; gap: 8px; }
.preview-wrap { display: flex; align-items: center; gap: 10px; }
.upload-image-preview { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; border: 1px solid #eee; }
.upload-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100px;
  height: 100px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  color: #999;
  font-size: 12px;
  transition: border-color 0.2s, color 0.2s;
}
.upload-btn:hover { border-color: #1890ff; color: #1890ff; }
.upload-btn .el-icon { font-size: 24px; }
.upload-tip { font-size: 12px; color: #999; }
</style>

<template>
  <div>
    <h2 class="page-title mb-4">商家资料</h2>

    <el-row :gutter="20" v-loading="loading">
      <!-- 左：基本信息编辑 -->
      <el-col :span="16" :xs="24">
        <div class="card">
          <div class="card-header">基本信息</div>
          <div class="card-body">
            <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
              <el-form-item label="商家名称" prop="name">
                <el-input v-model="form.name" maxlength="30" />
              </el-form-item>
              <el-form-item label="联系人" prop="contact_name">
                <el-input v-model="form.contact_name" maxlength="10" />
              </el-form-item>
              <el-form-item label="联系电话" prop="phone">
                <el-input v-model="form.phone" maxlength="11" />
              </el-form-item>
              <el-form-item label="经营地址">
                <el-input v-model="form.address" maxlength="100" />
              </el-form-item>
              <el-form-item label="主营车型">
                <el-input v-model="form.main_models" maxlength="50" />
              </el-form-item>
              <el-form-item label="商家简介">
                <el-input v-model="form.description" type="textarea" :rows="3" maxlength="200" show-word-limit />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="saving" @click="saveProfile">保存修改</el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </el-col>

      <!-- 右：店铺 Logo + 微信二维码 -->
      <el-col :span="8" :xs="24">
        <div class="card">
          <div class="card-header">店铺 Logo</div>
          <div class="card-body">
            <div class="qr-section">
              <div class="qr-current">
                <img v-if="previewAvatar" :src="previewAvatar" class="logo-img" />
                <div v-else class="qr-empty logo-empty">
                  <el-icon size="40" color="#ddd"><Shop /></el-icon>
                  <span>未上传 Logo</span>
                </div>
              </div>
              <div class="qr-tip">展示在商家主页头部与商品详情的商家信息区。上传后立即生效。</div>
              <label class="upload-btn" style="width:100%;justify-content:center;height:44px;border-radius:6px" :class="{ disabled: uploadingAvatar }">
                <input type="file" accept="image/jpeg,image/png" @change="handleAvatarUpload" hidden :disabled="uploadingAvatar" />
                <el-icon><Upload /></el-icon>
                <span>{{ uploadingAvatar ? '上传中…' : (form.avatar ? '更换 Logo' : '上传 Logo') }}</span>
              </label>
              <div class="upload-tip">建议方形图，jpg/png，≤5M · 上传后自动保存</div>
            </div>
          </div>
        </div>

        <div class="card mt-3">
          <div class="card-header">微信二维码</div>
          <div class="card-body">
            <div class="qr-section">
              <div class="qr-current">
                <img v-if="previewQr" :src="previewQr" class="qrcode-img" />
                <div v-else class="qr-empty"><el-icon size="40" color="#ddd"><Picture /></el-icon><span>未上传二维码</span></div>
              </div>
              <div class="qr-tip">此二维码将展示在您的商家主页和每辆车的详情页底部，供用户扫码咨询。上传后立即生效，无需再点左侧保存。</div>
              <label class="upload-btn" style="width:100%;justify-content:center;height:44px;border-radius:6px" :class="{ disabled: uploadingQr }">
                <input type="file" accept="image/jpeg,image/png" @change="handleQRUpload" hidden :disabled="uploadingQr" />
                <el-icon><Upload /></el-icon>
                <span>{{ uploadingQr ? '上传中…' : (form.wechat_qrcode ? '更换二维码' : '上传二维码') }}</span>
              </label>
              <div class="upload-tip">格式：jpg/png，大小≤5M · 上传后自动保存</div>
            </div>
          </div>
        </div>

        <!-- 店铺分享 -->
        <div class="card mt-3">
          <div class="card-header">店铺分享链接</div>
          <div class="card-body">
            <p class="qr-tip mb-3">分享此链接，客户将直接进入您的店铺主页</p>
            <el-button type="primary" style="width:100%" @click="copyShopLink">复制店铺分享链接</el-button>
          </div>
        </div>

        <!-- 入驻信息（只读展示） -->
        <div class="card mt-3" v-if="profile">
          <div class="card-header">入驻信息</div>
          <div class="card-body">
            <div class="info-row"><span class="info-l">入驻类型：</span><span>个人商户</span></div>
            <div class="info-row"><span class="info-l">入驻状态：</span><el-tag type="success" size="small">已审核通过</el-tag></div>
            <div class="info-row" v-if="profile.created_at"><span class="info-l">入驻时间：</span><span>{{ profile.created_at }}</span></div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { getShopShareLink } from '@/utils/bikeSort'
import api from '@/api'

const auth = useAuthStore()
const formRef = ref()
const saving = ref(false)
const uploadingQr = ref(false)
const uploadingAvatar = ref(false)
const loading = ref(true)
const profile = ref(null)

const form = reactive({
  name: '',
  contact_name: '',
  phone: '',
  address: '',
  main_models: '',
  description: '',
  avatar: '',
  wechat_qrcode: '',
})

function withCacheBust(url) {
  if (!url) return ''
  const base = url.startsWith('http') || url.startsWith('/') ? url : `/${url}`
  const key = profile.value?.updated_at || Date.now()
  return `${base}${base.includes('?') ? '&' : '?'}v=${encodeURIComponent(key)}`
}

const previewQr = computed(() => withCacheBust(form.wechat_qrcode))
const previewAvatar = computed(() => withCacheBust(form.avatar))

const rules = {
  name: [{ required: true, message: '请填写商家名称', trigger: 'blur' }],
  contact_name: [{ required: true, message: '请填写联系人', trigger: 'blur' }],
  phone: [
    { required: true, message: '请填写联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请填写正确的手机号', trigger: 'blur' },
  ],
}

async function uploadAndSaveImage(file, field, successMsg) {
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过5M')
    return null
  }
  const res = await api.uploadImage(file)
  const url = res.data.url
  form[field] = url
  const saved = await api.updateShopProfile({ [field]: url })
  fillForm(saved.data)
  ElMessage.success(successMsg)
  return url
}

async function handleAvatarUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  uploadingAvatar.value = true
  try {
    await uploadAndSaveImage(file, 'avatar', '店铺 Logo 已更新并生效')
  } catch { /* interceptor */ }
  finally {
    uploadingAvatar.value = false
    e.target.value = ''
  }
}

async function handleQRUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  uploadingQr.value = true
  try {
    await uploadAndSaveImage(file, 'wechat_qrcode', '微信二维码已更新并生效')
  } catch { /* interceptor */ }
  finally {
    uploadingQr.value = false
    e.target.value = ''
  }
}

async function copyShopLink() {
  const shopId = auth.user?.shop_id
  if (!shopId) { ElMessage.warning('商家信息不存在'); return }
  const link = getShopShareLink(shopId)
  try {
    await navigator.clipboard.writeText(link)
    ElMessage.success('店铺分享链接已复制')
  } catch {
    ElMessage.info(link)
  }
}

function fillForm(data) {
  profile.value = data
  Object.assign(form, {
    name: data.name || '',
    contact_name: data.contact_name || '',
    phone: data.phone || '',
    address: data.address || '',
    main_models: data.main_models || '',
    description: data.description || '',
    avatar: data.avatar || '',
    wechat_qrcode: data.wechat_qrcode || '',
  })
}

async function saveProfile() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const res = await api.updateShopProfile({ ...form })
    fillForm(res.data)
    ElMessage.success('资料已保存')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const res = await api.getShopProfile()
    fillForm(res.data)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.qr-section { display: flex; flex-direction: column; gap: 12px; align-items: center; }
.qr-current { width: 100%; display: flex; justify-content: center; }
.qrcode-img { width: 160px; height: 160px; object-fit: contain; border: 1px solid #eee; border-radius: 8px; }
.logo-img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border: 1px solid #eee;
  border-radius: 12px;
  background: #fafafa;
}
.qr-empty {
  width: 160px; height: 160px;
  border: 2px dashed #eee; border-radius: 8px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 8px; color: #bbb; font-size: 13px;
}
.logo-empty { width: 120px; height: 120px; border-radius: 12px; }
.qr-tip { font-size: 12px; color: #999; text-align: center; line-height: 1.5; }
.upload-btn {
  display: flex; align-items: center; gap: 6px;
  border: 1px solid #d9d9d9; border-radius: 6px; padding: 0 12px;
  cursor: pointer; color: #555; font-size: 13px; width: 100%;
  background: #fff; transition: border-color 0.2s, color 0.2s;
}
.upload-btn:hover { border-color: #1890ff; color: #1890ff; }
.upload-btn.disabled { opacity: 0.6; pointer-events: none; }
.upload-tip { font-size: 12px; color: #999; text-align: center; }
.info-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.info-row:last-child { border-bottom: none; }
.info-l { color: #888; flex-shrink: 0; }
</style>

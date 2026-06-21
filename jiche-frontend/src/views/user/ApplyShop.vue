<template>
  <div>
    <el-breadcrumb separator="/" class="mb-3">
      <el-breadcrumb-item :to="{ path: '/profile' }">个人中心</el-breadcrumb-item>
      <el-breadcrumb-item>商家入驻申请</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 待审核提示 -->
    <el-alert v-if="auth.shopStatus === 1" type="warning" show-icon :closable="false" class="mb-4"
      title="您的申请正在审核中" description="请耐心等待，审核结果将在1-3个工作日内反馈。审核期间无法重新提交。" />

    <!-- 驳回提示 -->
    <el-alert v-if="auth.shopStatus === 3 && rejectReason" type="error" show-icon :closable="false" class="mb-4"
      title="申请已被驳回" :description="`驳回原因：${rejectReason}，请修改后重新提交。`" />

    <div class="card">
      <div class="card-header">商家入驻申请</div>
      <div class="card-body">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" :disabled="auth.shopStatus === 1 || auth.shopStatus === 4">

          <div class="form-section-title">基本信息</div>

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
                <el-button size="small" type="danger" plain @click="form.wechat_qrcode_preview = ''; form.wechat_qrcode = null">删除</el-button>
              </div>
              <label v-else class="upload-btn">
                <input type="file" accept="image/jpeg,image/png" @change="handleQRUpload" hidden />
                <el-icon><Plus /></el-icon>
                <span>上传微信二维码</span>
              </label>
              <div class="upload-tip">格式：jpg/png，大小≤5M</div>
            </div>
          </el-form-item>

          <el-form-item label="资质照片" :prop="form.shop_type === '企业商户' ? 'qualification_photo' : ''">
            <div class="upload-area">
              <div v-if="form.qualification_photo_preview" class="preview-wrap">
                <img :src="form.qualification_photo_preview" class="upload-image-preview" />
                <el-button size="small" type="danger" plain @click="form.qualification_photo_preview = ''; form.qualification_photo = null">删除</el-button>
              </div>
              <label v-else class="upload-btn">
                <input type="file" accept="image/jpeg,image/png" @change="handleQualUpload" hidden />
                <el-icon><Plus /></el-icon>
                <span>上传资质照片</span>
              </label>
              <div class="upload-tip">
                {{ form.shop_type === '企业商户' ? '企业商户必填（营业执照等）' : '个人商户选填' }}
              </div>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="submitting"
              :disabled="auth.shopStatus === 1 || auth.shopStatus === 4"
              @click="submit"
            >
              {{ auth.shopStatus === 1 ? '审核中（不可重复提交）' : '提交申请' }}
            </el-button>
          </el-form-item>

        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const formRef = ref()
const submitting = ref(false)
const rejectReason = ref('资质材料不清晰，请重新上传')

const form = reactive({
  shop_type: '',
  contact_name: '',
  phone: '',
  address: '',
  main_models: '',
  description: '',
  wechat_qrcode: null,
  wechat_qrcode_preview: '',
  qualification_photo: null,
  qualification_photo_preview: '',
})

const rules = {
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

function handleFile(e, previewKey, fileKey) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) { ElMessage.error('图片大小不能超过5M'); return }
  form[fileKey] = file
  form[previewKey] = URL.createObjectURL(file)
}
function handleQRUpload(e) { handleFile(e, 'wechat_qrcode_preview', 'wechat_qrcode') }
function handleQualUpload(e) { handleFile(e, 'qualification_photo_preview', 'qualification_photo') }

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  if (!form.wechat_qrcode) { ElMessage.error('请上传微信二维码'); return }
  if (form.shop_type === '企业商户' && !form.qualification_photo) { ElMessage.error('企业商户必须上传资质照片'); return }
  submitting.value = true
  try {
    await new Promise(r => setTimeout(r, 800))
    auth.switchRole('pending')
    ElMessage.success('申请提交成功！请等待平台审核。')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.upload-area { display: flex; flex-direction: column; gap: 8px; }
.preview-wrap { display: flex; align-items: center; gap: 10px; }
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

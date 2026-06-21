<template>
  <div>
    <h2 class="page-title mb-4">商家资料</h2>

    <el-row :gutter="20">
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

      <!-- 右：微信二维码 -->
      <el-col :span="8" :xs="24">
        <div class="card">
          <div class="card-header">微信二维码</div>
          <div class="card-body">
            <div class="qr-section">
              <div class="qr-current">
                <img v-if="form.wechat_qrcode" :src="form.wechat_qrcode" class="qrcode-img" />
                <div v-else class="qr-empty"><el-icon size="40" color="#ddd"><Picture /></el-icon><span>未上传二维码</span></div>
              </div>
              <div class="qr-tip">此二维码将展示在您的商家主页和每辆车的详情页底部，供用户扫码咨询</div>
              <label class="upload-btn" style="width:100%;justify-content:center;height:44px;border-radius:6px">
                <input type="file" accept="image/jpeg,image/png" @change="handleQRUpload" hidden />
                <el-icon><Upload /></el-icon>
                <span>{{ form.wechat_qrcode ? '更换二维码' : '上传二维码' }}</span>
              </label>
              <div class="upload-tip">格式：jpg/png，大小≤5M</div>
            </div>
          </div>
        </div>

        <!-- 入驻信息（只读展示） -->
        <div class="card mt-3">
          <div class="card-header">入驻信息</div>
          <div class="card-body">
            <div class="info-row"><span class="info-l">入驻类型：</span><span>个人商户</span></div>
            <div class="info-row"><span class="info-l">入驻状态：</span><el-tag type="success" size="small">已审核通过</el-tag></div>
            <div class="info-row"><span class="info-l">入驻时间：</span><span>2024-01-01</span></div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const formRef = ref()
const saving = ref(false)

const form = reactive({
  name: '极速摩托行',
  contact_name: '张老板',
  phone: '13800138001',
  address: '广州市天河区车陂路168号',
  main_models: '本田、雅马哈中大排量',
  description: '专业二手摩托车商家，10年经验',
  wechat_qrcode: 'https://placehold.co/200x200?text=微信二维码',
})

const rules = {
  name: [{ required: true, message: '请填写商家名称', trigger: 'blur' }],
  contact_name: [{ required: true, message: '请填写联系人', trigger: 'blur' }],
  phone: [
    { required: true, message: '请填写联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请填写正确的手机号', trigger: 'blur' },
  ],
}

function handleQRUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) { ElMessage.error('图片大小不能超过5M'); return }
  form.wechat_qrcode = URL.createObjectURL(file)
  ElMessage.success('二维码已更新（请保存）')
  e.target.value = ''
}

async function saveProfile() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    await new Promise(r => setTimeout(r, 600))
    ElMessage.success('资料已保存')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.qr-section { display: flex; flex-direction: column; gap: 12px; align-items: center; }
.qr-current { width: 100%; display: flex; justify-content: center; }
.qrcode-img { width: 160px; height: 160px; object-fit: contain; border: 1px solid #eee; border-radius: 8px; }
.qr-empty {
  width: 160px; height: 160px;
  border: 2px dashed #eee; border-radius: 8px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 8px; color: #bbb; font-size: 13px;
}
.qr-tip { font-size: 12px; color: #999; text-align: center; line-height: 1.5; }
.upload-btn {
  display: flex; align-items: center; gap: 6px;
  border: 1px solid #d9d9d9; border-radius: 6px; padding: 0 12px;
  cursor: pointer; color: #555; font-size: 13px; width: 100%;
  background: #fff; transition: border-color 0.2s, color 0.2s;
}
.upload-btn:hover { border-color: #1890ff; color: #1890ff; }
.upload-tip { font-size: 12px; color: #999; text-align: center; }
.info-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.info-row:last-child { border-bottom: none; }
.info-l { color: #888; flex-shrink: 0; }
</style>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="在线留言"
    width="500px"
    :close-on-click-modal="false"
    @close="resetForm"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="留言内容" prop="content">
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="4"
          placeholder="请留下您的问题或联系方式，商家会尽快回复您..."
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="联系电话" prop="contact_phone">
        <el-input v-model="form.contact_phone" placeholder="选填，方便商家主动联系您" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">提交留言</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  bikeId: { type: Number, required: true },
})

const dialogVisible = defineModel({ default: false })

const formRef = ref()
const submitting = ref(false)

const form = reactive({
  content: '',
  contact_phone: '',
})

const rules = {
  content: [
    { required: true, message: '请填写留言内容', trigger: 'blur' },
    { min: 5, message: '留言内容至少5个字', trigger: 'blur' },
  ],
  contact_phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请填写正确的手机号格式', trigger: 'blur' },
  ],
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    // 真实环境: await api.submitMessage({ bike_id: props.bikeId, ...form })
    await new Promise(r => setTimeout(r, 500))
    ElMessage.success('留言提交成功，商家会尽快回复您！')
    dialogVisible.value = false
    resetForm()
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  form.content = ''
  form.contact_phone = ''
  formRef.value?.resetFields()
}
</script>

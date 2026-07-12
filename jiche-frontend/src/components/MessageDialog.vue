<template>
  <el-dialog
    v-model="dialogVisible"
    title="发起咨询"
    width="500px"
    :close-on-click-modal="false"
    @close="resetForm"
  >
    <p class="dialog-tip">发送后将进入对话页，支持与商家多轮沟通；新回复会收到消息提醒</p>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="留言内容" prop="content">
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="4"
          placeholder="请留下您的问题..."
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
      <el-button type="primary" :loading="submitting" @click="submit">发送并进入对话</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const props = defineProps({
  bikeId: { type: Number, required: true },
})

const emit = defineEmits(['created'])
const dialogVisible = defineModel({ default: false })

const auth = useAuthStore()
const formRef = ref()
const submitting = ref(false)

const form = reactive({
  content: '',
  contact_phone: '',
})

const rules = {
  content: [
    { required: true, message: '请填写留言内容', trigger: 'blur' },
    { min: 2, message: '留言内容至少2个字', trigger: 'blur' },
  ],
  contact_phone: [
    { pattern: /^$|^1[3-9]\d{9}$/, message: '请填写正确的手机号格式', trigger: 'blur' },
  ],
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const res = await api.createMessageThread({
      bike_id: props.bikeId,
      content: form.content,
      contact_phone: form.contact_phone,
      user_id: auth.user?.id,
      user_name: auth.user?.nickname,
    })
    ElMessage.success('发送成功，商家回复后将收到提醒')
    dialogVisible.value = false
    resetForm()
    emit('created', res.data)
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

<style scoped>
.dialog-tip { font-size: 13px; color: #888; margin-bottom: 16px; line-height: 1.5; }
</style>

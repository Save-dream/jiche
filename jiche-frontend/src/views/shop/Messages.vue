<template>
  <div>
    <div class="page-header-bar mb-4">
      <h2 class="page-title">留言管理</h2>
      <el-radio-group v-model="statusFilter" @change="loadMessages">
        <el-radio-button :value="0">全部</el-radio-button>
        <el-radio-button :value="1">
          未读 <el-badge v-if="unreadCount" :value="unreadCount" class="ml-1" />
        </el-radio-button>
        <el-radio-button :value="2">已读未回复</el-radio-button>
        <el-radio-button :value="3">已回复</el-radio-button>
      </el-radio-group>
    </div>

    <div class="card">
      <div v-loading="loading">
        <div v-if="messages.length === 0" style="padding:40px"><el-empty description="暂无留言" /></div>
        <div v-for="msg in messages" :key="msg.id" class="msg-item" :class="{ unread: msg.message_status === 1 }">
          <div class="msg-header">
            <div class="msg-meta">
              <el-tag :type="MESSAGE_STATUS[msg.message_status]?.type" size="small">{{ MESSAGE_STATUS[msg.message_status]?.label }}</el-tag>
              <span class="msg-bike">{{ msg.bike_info }}</span>
              <span class="msg-time">{{ msg.created_at }}</span>
            </div>
            <span class="msg-user">{{ msg.user_name }}</span>
          </div>

          <!-- 用户留言内容 -->
          <div class="msg-content">{{ msg.content }}</div>
          <div v-if="msg.contact_phone" class="msg-phone">
            <el-icon><Phone /></el-icon> 联系电话：{{ msg.contact_phone }}
          </div>

          <!-- 已回复内容 -->
          <div v-if="msg.reply_content" class="reply-box">
            <div class="reply-header"><el-icon><ChatDotRound /></el-icon> 商家回复 · {{ msg.replied_at }}</div>
            <div class="reply-content">{{ msg.reply_content }}</div>
          </div>

          <!-- 回复输入框 -->
          <div v-if="msg.message_status !== 3" class="reply-input-area">
            <el-input
              v-model="replyTexts[msg.id]"
              type="textarea"
              :rows="2"
              placeholder="输入回复内容..."
              maxlength="500"
            />
            <el-button type="primary" size="small" :loading="replyingId === msg.id" @click="submitReply(msg)">
              发送回复
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { MESSAGE_STATUS } from '@/stores/auth'
import api from '@/api'

const messages = ref([])
const loading = ref(false)
const statusFilter = ref(0)
const replyTexts = reactive({})
const replyingId = ref(null)

const unreadCount = computed(() => messages.value.filter(m => m.message_status === 1).length)

async function loadMessages() {
  loading.value = true
  try {
    const params = statusFilter.value !== 0 ? { status: statusFilter.value } : {}
    const res = await api.getMyMessages(params)
    messages.value = res.data.list
  } finally {
    loading.value = false
  }
}

async function submitReply(msg) {
  const content = replyTexts[msg.id]?.trim()
  if (!content) { ElMessage.warning('请输入回复内容'); return }
  replyingId.value = msg.id
  try {
    await new Promise(r => setTimeout(r, 500))
    msg.reply_content = content
    msg.message_status = 3
    msg.replied_at = new Date().toLocaleString()
    replyTexts[msg.id] = ''
    ElMessage.success('回复已发送')
  } finally {
    replyingId.value = null
  }
}

onMounted(loadMessages)
</script>

<style scoped>
.page-header-bar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }

.msg-item {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.15s;
}
.msg-item:last-child { border-bottom: none; }
.msg-item.unread { background: #fffbf0; }

.msg-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; flex-wrap: wrap; gap: 8px; }
.msg-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.msg-bike { font-size: 13px; color: #555; }
.msg-time { font-size: 12px; color: #aaa; }
.msg-user { font-size: 13px; color: #888; }

.msg-content { font-size: 14px; color: #333; line-height: 1.6; margin-bottom: 8px; }
.msg-phone { font-size: 12px; color: #888; display: flex; align-items: center; gap: 4px; margin-bottom: 8px; }

.reply-box {
  background: #f9fafb;
  border-radius: 8px;
  padding: 12px;
  margin: 8px 0;
  border-left: 3px solid #1890ff;
}
.reply-header { font-size: 12px; color: #888; display: flex; align-items: center; gap: 4px; margin-bottom: 6px; }
.reply-content { font-size: 13px; color: #555; line-height: 1.5; }

.reply-input-area { display: flex; flex-direction: column; gap: 8px; margin-top: 10px; align-items: flex-end; }
</style>

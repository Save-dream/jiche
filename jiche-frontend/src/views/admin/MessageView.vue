<template>
  <div>
    <div class="page-header-bar mb-4">
      <h2 class="page-title">全平台留言记录</h2>
      <el-tag type="info">只读视图，不可代为回复</el-tag>
    </div>

    <div class="card">
      <div v-loading="loading">
        <div v-if="messages.length === 0" style="padding:40px"><el-empty description="暂无留言记录" /></div>
        <div v-for="msg in messages" :key="msg.id" class="msg-item">
          <div class="msg-header">
            <div class="msg-meta">
              <el-tag :type="MESSAGE_STATUS[msg.message_status]?.type" size="small">{{ MESSAGE_STATUS[msg.message_status]?.label }}</el-tag>
              <span class="msg-bike-link" @click="$router.push(`/bike/${msg.bike_id}`)">{{ msg.bike_info }}</span>
              <span class="msg-time">{{ msg.created_at }}</span>
            </div>
            <div class="msg-user-info">
              <span class="msg-user">{{ msg.user_name }}</span>
              <span v-if="msg.contact_phone" class="msg-phone"><el-icon><Phone /></el-icon>{{ msg.contact_phone }}</span>
            </div>
          </div>

          <div class="msg-content">{{ msg.content }}</div>

          <div v-if="msg.reply_content" class="reply-box">
            <div class="reply-header"><el-icon><ChatDotRound /></el-icon> 商家回复 · {{ msg.replied_at }}</div>
            <div class="reply-content">{{ msg.reply_content }}</div>
          </div>
          <div v-else class="no-reply">
            <el-tag type="warning" size="small">待商家回复</el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { MESSAGE_STATUS } from '@/stores/auth'
import api from '@/api'

const messages = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.getAllMessages()
    messages.value = res.data.list
  } finally { loading.value = false }
})
</script>

<style scoped>
.page-header-bar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.msg-item { padding: 16px 20px; border-bottom: 1px solid #f0f0f0; }
.msg-item:last-child { border-bottom: none; }
.msg-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 10px; flex-wrap: wrap; gap: 8px; }
.msg-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.msg-bike-link { font-size: 13px; color: #1890ff; cursor: pointer; }
.msg-bike-link:hover { text-decoration: underline; }
.msg-time { font-size: 12px; color: #aaa; }
.msg-user-info { display: flex; align-items: center; gap: 10px; }
.msg-user { font-size: 13px; color: #666; }
.msg-phone { display: flex; align-items: center; gap: 4px; font-size: 12px; color: #888; }
.msg-content { font-size: 14px; color: #333; line-height: 1.6; margin-bottom: 8px; }
.reply-box { background: #f9fafb; border-radius: 8px; padding: 10px 12px; border-left: 3px solid #1890ff; }
.reply-header { font-size: 12px; color: #888; display: flex; align-items: center; gap: 4px; margin-bottom: 4px; }
.reply-content { font-size: 13px; color: #555; }
.no-reply { margin-top: 6px; }
</style>

<template>
  <div>
    <div class="page-header-bar mb-4">
      <h2 class="page-title">全平台留言记录</h2>
      <el-tag type="info">只读视图，不可代为回复</el-tag>
    </div>

    <div class="card" v-loading="loading">
      <div v-if="threads.length">
        <div v-for="thread in threads" :key="thread.id" class="thread-item">
          <div class="thread-header">
            <div class="thread-meta">
              <el-tag :type="MESSAGE_STATUS[thread.thread_status]?.type" size="small">
                {{ MESSAGE_STATUS[thread.thread_status]?.label }}
              </el-tag>
              <span class="thread-bike">{{ thread.bike_info }}</span>
              <span class="thread-user">{{ thread.user_name }}</span>
              <span v-if="thread.contact_phone" class="thread-phone">{{ thread.contact_phone }}</span>
            </div>
            <span class="thread-time">{{ thread.updated_at }}</span>
          </div>

          <div class="message-list">
            <div
              v-for="msg in thread.messages"
              :key="msg.id"
              class="message-row"
              :class="msg.sender_type === 1 ? 'from-user' : 'from-shop'"
            >
              <span class="sender-label">{{ msg.sender_type === 1 ? '用户' : '商家' }}</span>
              <span class="message-text">{{ msg.content }}</span>
              <span class="message-time">{{ msg.created_at }}</span>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无留言记录" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { MESSAGE_STATUS } from '@/stores/auth'
import api from '@/api'

const threads = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.getAllMessages()
    threads.value = res.data.list
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-header-bar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.thread-item { padding: 16px 20px; border-bottom: 1px solid #f0f0f0; }
.thread-item:last-child { border-bottom: none; }
.thread-header { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.thread-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.thread-bike { font-size: 13px; color: #333; font-weight: 600; }
.thread-user { font-size: 13px; color: #666; }
.thread-phone { font-size: 12px; color: #888; }
.thread-time { font-size: 12px; color: #aaa; }
.message-list { display: flex; flex-direction: column; gap: 8px; background: #fafafa; border-radius: 8px; padding: 12px; }
.message-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: baseline; font-size: 13px; }
.sender-label { font-weight: 600; color: #555; min-width: 36px; }
.from-user .sender-label { color: #1890ff; }
.from-shop .sender-label { color: #52c41a; }
.message-text { flex: 1; color: #333; line-height: 1.5; }
.message-time { font-size: 11px; color: #bbb; }
</style>

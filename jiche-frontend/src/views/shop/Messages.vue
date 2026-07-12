<template>
  <div>
    <div class="page-header-bar mb-4">
      <h2 class="page-title">留言管理</h2>
      <el-radio-group v-model="statusFilter" @change="loadThreads">
        <el-radio-button :value="0">全部</el-radio-button>
        <el-radio-button :value="1">
          未读 <el-badge v-if="unreadCount" :value="unreadCount" class="ml-1" />
        </el-radio-button>
        <el-radio-button :value="2">已读未回复</el-radio-button>
        <el-radio-button :value="3">已回复</el-radio-button>
      </el-radio-group>
    </div>

    <div class="card" v-loading="loading">
      <div v-if="threads.length">
        <div
          v-for="thread in threads"
          :key="thread.id"
          class="thread-item"
          :class="{ unread: thread.unread_count_shop > 0 }"
          @click="$router.push(`/shop/messages/${thread.id}`)"
        >
          <div class="thread-main">
            <div class="thread-title">
              {{ thread.bike_info }} · {{ thread.user_name }}
              <el-badge v-if="thread.unread_count_shop" :value="thread.unread_count_shop" class="ml-2" />
            </div>
            <div class="thread-preview">{{ lastMessage(thread) }}</div>
            <div v-if="thread.contact_phone" class="thread-phone">
              <el-icon><Phone /></el-icon> {{ thread.contact_phone }}
            </div>
          </div>
          <div class="thread-meta">
            <el-tag :type="MESSAGE_STATUS[thread.thread_status]?.type" size="small">
              {{ MESSAGE_STATUS[thread.thread_status]?.label }}
            </el-tag>
            <span class="thread-time">{{ thread.updated_at }}</span>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无留言" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { MESSAGE_STATUS } from '@/stores/auth'
import api from '@/api'

const threads = ref([])
const loading = ref(false)
const statusFilter = ref(0)

const unreadCount = computed(() =>
  threads.value.reduce((s, t) => s + (t.unread_count_shop || 0), 0)
)

function lastMessage(thread) {
  const msgs = thread.messages || []
  return msgs.length ? msgs[msgs.length - 1].content : ''
}

async function loadThreads() {
  loading.value = true
  try {
    const params = statusFilter.value !== 0 ? { status: statusFilter.value } : {}
    const res = await api.getMyMessageThreads(params)
    threads.value = res.data.list
  } finally {
    loading.value = false
  }
}

onMounted(loadThreads)
</script>

<style scoped>
.page-header-bar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.thread-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}
.thread-item:last-child { border-bottom: none; }
.thread-item.unread { background: #fffbf0; }
.thread-item:hover { background: #fafafa; }
.thread-title { font-size: 14px; font-weight: 600; color: #222; margin-bottom: 6px; display: flex; align-items: center; flex-wrap: wrap; }
.thread-preview { font-size: 13px; color: #666; margin-bottom: 4px; }
.thread-phone { font-size: 12px; color: #888; display: flex; align-items: center; gap: 4px; }
.thread-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; }
.thread-time { font-size: 12px; color: #aaa; }
</style>

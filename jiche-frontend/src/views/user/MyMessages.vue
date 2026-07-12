<template>
  <div>
    <div class="page-header-bar mb-4">
      <h2 class="page-title">我的咨询</h2>
      <span class="text-muted" style="font-size:13px">新回复将收到消息提醒</span>
    </div>

    <el-radio-group v-if="auth.isShop" v-model="activeTab" class="mb-3" @change="onTabChange">
      <el-radio-button value="mine">
        我的咨询
        <el-badge v-if="mineUnread" :value="mineUnread" class="tab-badge" />
      </el-radio-button>
      <el-radio-button value="inbox">
        用户咨询
        <el-badge v-if="inboxUnread" :value="inboxUnread" class="tab-badge" />
      </el-radio-button>
    </el-radio-group>

    <p v-if="auth.isShop" class="tab-hint mb-3">
      {{ activeTab === 'mine'
        ? '您作为买家向其他商家发起的咨询'
        : '其他用户向您的店铺发起的咨询（与商家后台「留言管理」数据同步）' }}
    </p>

    <div class="card" v-loading="loading">
      <div v-if="threads.length">
        <div
          v-for="thread in threads"
          :key="thread.id"
          class="thread-item"
          :class="{ unread: isUnread(thread) }"
          @click="openThread(thread)"
        >
          <div class="thread-main">
            <div class="thread-title">
              <template v-if="isInbox">
                {{ thread.bike_info }} · {{ thread.user_name }}
              </template>
              <template v-else>
                {{ thread.bike_info }}
              </template>
              <el-badge v-if="unreadOf(thread)" :value="unreadOf(thread)" class="ml-2" />
            </div>
            <div class="thread-preview">{{ lastMessage(thread) }}</div>
            <div v-if="isInbox && thread.contact_phone" class="thread-phone">
              联系电话：{{ thread.contact_phone }}
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
      <el-empty v-else :description="isInbox ? '暂无用户咨询' : '暂无咨询记录'" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MESSAGE_STATUS } from '@/stores/auth'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const POLL_INTERVAL_MS = 5000

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const threads = ref([])
const loading = ref(false)
const mineUnread = ref(0)
const inboxUnread = ref(0)
const activeTab = ref(route.query.tab === 'inbox' && auth.isShop ? 'inbox' : 'mine')
let pollTimer = null

const isInbox = computed(() => auth.isShop && activeTab.value === 'inbox')

function lastMessage(thread) {
  const msgs = thread.messages || []
  if (msgs.length) return msgs[msgs.length - 1].content
  return thread.last_message_preview || '暂无消息'
}

function unreadOf(thread) {
  return isInbox.value ? (thread.unread_count_shop || 0) : (thread.unread_count_user || 0)
}

function isUnread(thread) {
  return unreadOf(thread) > 0
}

async function refreshUnreadBadges() {
  if (!auth.isShop) {
    mineUnread.value = 0
    inboxUnread.value = 0
    return
  }
  try {
    const [mine, inbox] = await Promise.all([
      api.getUnreadCount('user'),
      api.getUnreadCount('shop'),
    ])
    mineUnread.value = mine.data?.unread_count || 0
    inboxUnread.value = inbox.data?.unread_count || 0
    auth.userUnreadMessages = mineUnread.value + inboxUnread.value
  } catch { /* ignore */ }
}

async function loadThreads({ silent = false } = {}) {
  if (!silent) loading.value = true
  try {
    if (isInbox.value) {
      const res = await api.getMyMessageThreads()
      threads.value = res.data.list || []
    } else {
      const res = await api.getUserMessageThreads()
      threads.value = res.data.list || []
    }
    await refreshUnreadBadges()
    if (!auth.isShop) {
      auth.syncUnreadFromThreads(threads.value, 'user')
    }
  } finally {
    if (!silent) loading.value = false
  }
}

function onTabChange(tab) {
  router.replace({ path: '/messages', query: tab === 'inbox' ? { tab: 'inbox' } : {} })
  loadThreads()
}

function openThread(thread) {
  if (isInbox.value) {
    router.push({ path: `/messages/${thread.id}`, query: { role: 'shop', from: 'inbox' } })
  } else {
    router.push(`/messages/${thread.id}`)
  }
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(() => {
    if (document.visibilityState === 'visible') loadThreads({ silent: true })
  }, POLL_INTERVAL_MS)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function onVisibilityChange() {
  if (document.visibilityState === 'visible') loadThreads({ silent: true })
}

watch(
  () => route.query.tab,
  (tab) => {
    const next = tab === 'inbox' && auth.isShop ? 'inbox' : 'mine'
    if (next !== activeTab.value) {
      activeTab.value = next
      loadThreads()
    }
  }
)

onMounted(() => {
  loadThreads()
  startPolling()
  document.addEventListener('visibilitychange', onVisibilityChange)
})

onUnmounted(() => {
  stopPolling()
  document.removeEventListener('visibilitychange', onVisibilityChange)
})
</script>

<style scoped>
.page-header-bar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
.tab-hint { font-size: 13px; color: #888; margin: 0; }
.tab-badge { margin-left: 6px; vertical-align: middle; }
.thread-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.15s;
}
.thread-item:last-child { border-bottom: none; }
.thread-item:hover { background: #fafafa; }
.thread-item.unread { background: #fffbf0; }
.thread-title { font-size: 15px; font-weight: 600; color: #222; margin-bottom: 6px; display: flex; align-items: center; flex-wrap: wrap; }
.thread-preview { font-size: 13px; color: #888; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 400px; }
.thread-phone { font-size: 12px; color: #888; margin-top: 4px; }
.thread-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; }
.thread-time { font-size: 12px; color: #aaa; }
</style>

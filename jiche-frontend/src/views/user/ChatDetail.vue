<template>
  <div v-if="thread">
    <el-breadcrumb separator="/" class="mb-3">
      <el-breadcrumb-item :to="backPath">{{ backLabel }}</el-breadcrumb-item>
      <el-breadcrumb-item>{{ thread.bike_info }}</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="card mb-3">
      <div class="card-body chat-header">
        <div>
          <div class="chat-title">{{ thread.bike_info }}</div>
          <div class="text-muted" style="font-size:12px">
            {{ chatRole === 'shop' ? `咨询用户：${thread.user_name}` : '与商家对话' }}
            <span v-if="thread.contact_phone"> · {{ thread.contact_phone }}</span>
          </div>
        </div>
        <el-button v-if="chatRole === 'user'" size="small" @click="goBike">查看商品</el-button>
      </div>
    </div>

    <MessageChatPanel
      :messages="thread.messages"
      :my-sender-type="chatRole === 'shop' ? 2 : 1"
      :on-send="handleSend"
    />
  </div>
  <el-empty v-else-if="!loading" description="会话不存在" />
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MessageChatPanel from '@/components/MessageChatPanel.vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const POLL_INTERVAL_MS = 3000

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const thread = ref(null)
const loading = ref(true)
let pollTimer = null

const chatRole = computed(() => {
  // 商家后台留言管理
  if (route.meta.chatRole === 'shop') return 'shop'
  // 用户侧「我的咨询 · 用户咨询」入口
  if (route.query.role === 'shop' && auth.isShop) return 'shop'
  return 'user'
})
const fromInbox = computed(() => route.query.from === 'inbox' || route.query.role === 'shop')
const backPath = computed(() => {
  if (route.meta.chatRole === 'shop') return '/shop/messages'
  if (fromInbox.value && auth.isShop) return { path: '/messages', query: { tab: 'inbox' } }
  return '/messages'
})
const backLabel = computed(() => {
  if (route.meta.chatRole === 'shop') return '留言管理'
  if (fromInbox.value && auth.isShop) return '用户咨询'
  return '我的咨询'
})

function lastMessageId(messages = []) {
  return messages.length ? messages[messages.length - 1].id : 0
}

async function loadThread({ silent = false } = {}) {
  if (!silent) loading.value = true
  try {
    const res = await api.getMessageThread(route.params.threadId)
    const prevLastId = lastMessageId(thread.value?.messages)
    const nextLastId = lastMessageId(res.data?.messages)
    thread.value = res.data
    if (!silent || nextLastId !== prevLastId) {
      await api.markThreadRead(route.params.threadId, chatRole.value)
      await auth.loadUnreadMessages(api, 'auto')
    }
  } finally {
    if (!silent) loading.value = false
  }
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(() => {
    if (document.visibilityState === 'visible') {
      loadThread({ silent: true })
    }
  }, POLL_INTERVAL_MS)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function handleSend(content) {
  const sender_type = chatRole.value === 'shop' ? 2 : 1
  const res = await api.sendMessage(route.params.threadId, { content, sender_type })
  thread.value = res.data.thread
}

function goBike() {
  router.push({ path: `/bike/${thread.value.bike_id}`, query: { shop_id: thread.value.shop_id } })
}

onMounted(() => {
  loadThread()
  startPolling()
})

onUnmounted(stopPolling)

watch(
  () => route.params.threadId,
  () => {
    thread.value = null
    loadThread()
  }
)
</script>

<style scoped>
.chat-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.chat-title { font-size: 16px; font-weight: 600; color: #222; margin-bottom: 4px; }
</style>

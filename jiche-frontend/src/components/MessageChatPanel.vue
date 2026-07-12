<template>
  <div class="chat-panel">
    <div ref="listRef" class="chat-messages">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="chat-bubble-row"
        :class="msg.sender_type === mySenderType ? 'mine' : 'other'"
      >
        <div class="chat-bubble">
          <div class="chat-text">{{ msg.content }}</div>
          <div class="chat-time">{{ msg.created_at }}</div>
        </div>
      </div>
      <el-empty v-if="!messages.length" description="暂无消息，发送第一条咨询吧" :image-size="60" />
      <div ref="bottomRef" class="chat-bottom-anchor" aria-hidden="true" />
    </div>

    <div class="chat-input-bar">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入消息..."
        maxlength="500"
        show-word-limit
        @keydown.enter.exact.prevent="send"
      />
      <el-button type="primary" :loading="sending" :disabled="!inputText.trim()" @click="send">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  mySenderType: { type: Number, required: true }, // 1=用户 2=商家
  onSend: { type: Function, required: true },
})

const inputText = ref('')
const sending = ref(false)
const listRef = ref(null)
const bottomRef = ref(null)

const lastMessageId = computed(() => {
  const msgs = props.messages
  return msgs.length ? msgs[msgs.length - 1].id : 0
})

function scrollToBottom(smooth = false) {
  nextTick(() => {
    requestAnimationFrame(() => {
      if (bottomRef.value) {
        bottomRef.value.scrollIntoView({ block: 'end', behavior: smooth ? 'smooth' : 'auto' })
        return
      }
      if (listRef.value) {
        listRef.value.scrollTop = listRef.value.scrollHeight
      }
    })
  })
}

async function send() {
  const content = inputText.value.trim()
  if (!content) return
  sending.value = true
  try {
    await props.onSend(content)
    inputText.value = ''
    ElMessage.success('发送成功')
    scrollToBottom(true)
  } finally {
    sending.value = false
  }
}

watch(lastMessageId, () => scrollToBottom(), { immediate: true })
</script>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: calc(100dvh - 220px);
  min-height: 360px;
  max-height: 720px;
  background: #f5f5f5;
  border-radius: 8px;
  overflow: hidden;
}
.chat-messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scroll-behavior: smooth;
}
.chat-bottom-anchor {
  flex-shrink: 0;
  width: 100%;
  height: 1px;
}
.chat-bubble-row { display: flex; }
.chat-bubble-row.mine { justify-content: flex-end; }
.chat-bubble-row.other { justify-content: flex-start; }
.chat-bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}
.mine .chat-bubble { background: #95ec69; }
.chat-text { font-size: 14px; color: #333; line-height: 1.5; word-break: break-word; }
.chat-time { font-size: 11px; color: #999; margin-top: 4px; text-align: right; }
.chat-input-bar {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: #fff;
  border-top: 1px solid #eee;
  align-items: flex-end;
}
.chat-input-bar .el-textarea { flex: 1; }
</style>

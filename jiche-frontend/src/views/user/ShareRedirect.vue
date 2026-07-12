<template>
  <div class="share-redirect">
    <el-result v-if="error" icon="warning" :title="error" sub-title="请联系商家获取最新分享链接">
      <template #extra>
        <el-button type="primary" @click="$router.replace('/')">返回首页</el-button>
      </template>
    </el-result>
    <div v-else class="loading-wrap">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>正在打开分享内容…</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const error = ref('')

onMounted(async () => {
  const code = route.params.code
  if (!code) {
    error.value = '链接无效'
    return
  }
  try {
    const res = await api.resolveShareLink(code)
    const data = res.data
    if (data.type === 'bike' && data.bike_id) {
      await router.replace({
        path: `/bike/${data.bike_id}`,
        query: {
          shop_id: data.shop_id,
          timestamp: data.timestamp,
          sign: data.sign,
        },
      })
      return
    }
    if (data.shop_id) {
      await router.replace(`/shop/${data.shop_id}`)
      return
    }
    error.value = '链接无效'
  } catch (e) {
    error.value = e?.message || '链接已过期或无效'
  }
})
</script>

<style scoped>
.share-redirect { min-height: 50vh; display: flex; align-items: center; justify-content: center; }
.loading-wrap { text-align: center; color: #666; }
.loading-wrap p { margin-top: 12px; font-size: 14px; }
</style>

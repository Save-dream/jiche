<template>
  <div>
    <div class="hero-banner">
      <div class="hero-content">
        <h1 class="hero-title">极车 · 私域看车</h1>
        <p class="hero-sub">通过商家分享的商品链接进入详情，或通过店铺链接进入商家主页</p>
        <p class="hero-tip">无分享链接时，可通过下方「最近访问商家」快速返回</p>
      </div>
    </div>

    <div class="quick-entries mb-4">
      <div class="quick-card" @click="goFavorites">
        <el-icon :size="22"><Star /></el-icon>
        <div>
          <div class="quick-title">我的收藏</div>
          <div class="quick-desc">查看收藏的车源</div>
        </div>
      </div>
      <div class="quick-card" @click="goMessages">
        <el-icon :size="22"><ChatDotRound /></el-icon>
        <div>
          <div class="quick-title">我的咨询</div>
          <div class="quick-desc">{{ auth.isShop ? '我发起的 / 用户咨询我的' : '查看留言与回复' }}</div>
        </div>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-header flex-between">
        <span>最近访问商家</span>
        <span class="text-muted" style="font-size:12px">最近 10 条 · 通过分享链接访问后自动记录</span>
      </div>
      <div class="card-body">
        <div v-if="visitedShops.length" class="visited-list">
          <div
            v-for="item in visitedShops"
            :key="item.id"
            class="visited-item"
            @click="goShop(item.id)"
          >
            <div class="visited-name">{{ item.name || shopNames[item.id] || `商家 #${item.id}` }}</div>
            <div class="visited-time">{{ formatTime(item.visited_at) }}</div>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
        <el-empty v-else description="暂无访问记录，请打开商家分享链接" :image-size="80" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const router = useRouter()
const auth = useAuthStore()
const shopNames = ref({})
const visitedShops = ref([])

async function loadVisits() {
  const list = await auth.loadVisitedShops(api)
  visitedShops.value = list
  const ids = [...new Set(list.map((s) => s.id))]
  for (const id of ids) {
    const item = list.find((s) => s.id === id)
    if (item?.name) shopNames.value[id] = item.name
    else if (!shopNames.value[id]) {
      try {
        const res = await api.getShopDetail(id)
        shopNames.value[id] = res.data.shop?.name || res.data.name
      } catch { /* ignore */ }
    }
  }
}

function goFavorites() {
  router.push('/favorites')
}

function goMessages() {
  router.push('/messages')
}

function goShop(shopId) {
  router.push(`/shop/${shopId}`)
}

function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('zh-CN')
}

onMounted(loadVisits)
</script>

<style scoped>
.hero-banner {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border-radius: clamp(8px, 2vw, 12px);
  padding: clamp(24px, 4vw, 40px) clamp(16px, 3vw, 32px);
  margin-bottom: clamp(12px, 2vw, 24px);
}
.hero-title { font-size: clamp(20px, 4vw, 28px); font-weight: 700; color: #fff; margin-bottom: 8px; }
.hero-sub { font-size: clamp(13px, 2vw, 15px); color: rgba(255,255,255,0.85); line-height: 1.6; }
.hero-tip { font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 8px; }

.quick-entries {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.quick-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.quick-card:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.1); }
.quick-title { font-weight: 600; font-size: 14px; color: #222; }
.quick-desc { font-size: 12px; color: #999; margin-top: 2px; }

.visited-list { display: flex; flex-direction: column; gap: 0; }
.visited-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 4px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}
.visited-item:last-child { border-bottom: none; }
.visited-item:hover .visited-name { color: #1890ff; }
.visited-name { flex: 1; font-weight: 500; color: #222; }
.visited-time { font-size: 12px; color: #aaa; }
</style>

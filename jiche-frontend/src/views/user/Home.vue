<template>
  <div>
    <!-- 引导区：多租户私域，无全平台广场 -->
    <div class="hero-banner">
      <div class="hero-content">
        <h1 class="hero-title">极车 · 私域看车</h1>
        <p class="hero-sub">商品分享链接 → 进入商品详情；店铺分享链接 → 进入商家主页</p>
        <p class="hero-tip">无分享链接时，可通过下方「最近访问商家」快速返回</p>
      </div>
    </div>

    <!-- 快捷入口 -->
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

    <!-- 最近访问商家 -->
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

    <!-- 开发调试：模拟分享入口 -->
    <div class="card dev-entry" v-if="showDevTools">
      <div class="card-header">开发调试 · 模拟分享进入</div>
      <div class="card-body">
        <p class="text-muted mb-3" style="font-size:13px">正式环境通过商家短链 /s/xxx 或带签 URL 进入</p>
        <div class="dev-links">
          <el-button
            v-for="bike in demoBikes"
            :key="bike.id"
            @click="goShareDemo(demoShopId, bike.id)"
          >
            商品链 · {{ bike.brand }} {{ bike.model }}
          </el-button>
          <el-button @click="goShopDemo(demoShopId)">店铺链 · {{ demoShopName }}</el-button>
        </div>
        <p v-if="!demoBikes.length" class="text-muted" style="font-size:12px;margin-top:8px">
          暂无演示车源，请在后端运行 <code>python manage.py seed_demo_data</code>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const router = useRouter()
const auth = useAuthStore()
const showDevTools = ref(true)
const shopNames = ref({})
const demoBikes = ref([])
const demoShopId = ref(1)
const demoShopName = ref('极速摩托行')

const visitedShops = ref([])

async function loadDemoBikes() {
  if (!showDevTools.value) return
  try {
    const res = await api.getShopDetail(demoShopId.value)
    demoShopName.value = res.data.shop?.name || demoShopName.value
    demoBikes.value = (res.data.bikes || [])
      .filter((b) => b.bike_status === 1 && !b.is_deleted)
      .slice(0, 3)
  } catch {
    demoBikes.value = []
  }
}

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

function requireLogin(path) {
  if (!auth.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push({ path: '/login', query: { redirect: path } })
    return false
  }
  return true
}

function goFavorites() {
  if (!requireLogin('/favorites')) return
  router.push('/favorites')
}

function goMessages() {
  if (!requireLogin('/messages')) return
  router.push('/messages')
}

function goShop(shopId) {
  router.push(`/shop/${shopId}`)
}

function goShareDemo(shopId, bikeId) {
  auth.setCurrentShopId(shopId)
  router.push({ path: `/bike/${bikeId}`, query: { shop_id: shopId } })
}

function goShopDemo(shopId) {
  auth.setCurrentShopId(shopId)
  router.push(`/shop/${shopId}`)
}

function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('zh-CN')
}

onMounted(async () => {
  await loadVisits()
  await loadDemoBikes()
})

onActivated(loadDemoBikes)
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
  padding: 14px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}
.visited-item:last-child { border-bottom: none; }
.visited-item:hover { color: #1890ff; }
.visited-name { flex: 1; font-weight: 600; font-size: 14px; }
.visited-time { font-size: 12px; color: #999; }

.dev-links { display: flex; flex-wrap: wrap; gap: 8px; }

@media (max-width: 480px) {
  .quick-entries { grid-template-columns: 1fr; }
}
</style>

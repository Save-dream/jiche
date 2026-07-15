<template>
  <div v-if="shop">
    <div class="shop-header card mb-4">
      <div class="shop-cover"></div>
      <div class="shop-header-body">
        <div class="shop-top">
          <div class="shop-avatar-wrap">
            <img v-if="shop.avatar" :src="avatarSrc" class="shop-avatar" alt="店铺 Logo" />
            <div v-else class="shop-avatar shop-avatar--placeholder">
              <el-icon :size="28"><Shop /></el-icon>
            </div>
          </div>
          <div class="shop-info">
            <h1 class="shop-title">{{ shop.name }}</h1>
            <p class="shop-desc">{{ shop.description }}</p>
            <div class="shop-meta">
              <span><el-icon><Location /></el-icon> {{ shop.address }}</span>
              <span><el-icon><Cpu /></el-icon> 主营：{{ shop.main_models }}</span>
              <span><el-icon><List /></el-icon> 在售 {{ onSaleCount }} 辆</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="flex-between mb-3">
      <h2 class="section-title">商家车源</h2>
      <el-radio-group v-model="activeStatus" size="small" @change="loadBikes">
        <el-radio-button :value="1">在售</el-radio-button>
        <el-radio-button :value="2">已售</el-radio-button>
        <el-radio-button :value="0">全部</el-radio-button>
      </el-radio-group>
    </div>

    <FilterBar v-if="activeStatus !== 2" @change="onFilterChange" class="mb-3" />

    <div v-if="loading" class="bikes-grid">
      <el-skeleton v-for="i in 6" :key="i" animated />
    </div>

    <div v-else>
      <div class="bikes-grid">
        <BikeCard v-for="bike in filteredBikes" :key="bike.id" :bike="bike" />
      </div>
      <el-empty v-if="!filteredBikes.length" description="暂无车辆" />
    </div>
  </div>
  <div v-else-if="loading" class="flex-center" style="height:300px"><el-loading /></div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import BikeCard from '@/components/BikeCard.vue'
import FilterBar from '@/components/FilterBar.vue'
import { sortShopBikes, applyBikeFilters } from '@/utils/bikeSort'
import api from '@/api'

const route = useRoute()
const shop = ref(null)
const allBikes = ref([])
const loading = ref(true)
const activeStatus = ref(1)
const localFilters = ref({})

const onSaleCount = computed(() => allBikes.value.filter(b => b.bike_status === 1).length)

const avatarSrc = computed(() => {
  const url = shop.value?.avatar
  if (!url) return ''
  const base = url.startsWith('http') || url.startsWith('/') ? url : `/${url}`
  const key = shop.value?.updated_at || shop.value?.id || ''
  return key ? `${base}${base.includes('?') ? '&' : '?'}v=${encodeURIComponent(key)}` : base
})

const filteredBikes = computed(() => {
  const list = applyBikeFilters(allBikes.value, localFilters.value)
  return sortShopBikes(list, { cEndOnly: true })
})

async function loadBikes() {
  loading.value = true
  try {
    const res = await api.getShopDetail(route.params.id, { status: activeStatus.value || undefined })
    shop.value = res.data.shop
    allBikes.value = res.data.bikes
  } finally {
    loading.value = false
  }
}

function onFilterChange(filters) {
  localFilters.value = { ...filters }
}

onMounted(loadBikes)
</script>

<style scoped>
.shop-header { overflow: visible; }
.shop-cover {
  height: 100px;
  background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
  border-radius: 10px 10px 0 0;
}
.shop-header-body {
  padding: 0 16px 16px;
}
.shop-top {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  margin-top: -32px;
  margin-bottom: 14px;
}
.shop-avatar-wrap { flex-shrink: 0; }
.shop-avatar {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  object-fit: cover;
  background: #f0f2f5;
}
.shop-avatar--placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bbb;
}
.shop-info { flex: 1; min-width: 0; padding-top: 36px; }
.shop-title {
  font-size: 18px;
  font-weight: 700;
  color: #222;
  margin: 0 0 4px;
  line-height: 1.3;
}
.shop-desc {
  font-size: 12px;
  color: #888;
  margin: 0 0 8px;
  line-height: 1.5;
}
.shop-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #666;
}
.shop-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
  line-height: 1.4;
}
.section-title { font-size: 16px; font-weight: 600; color: #222; }

@media (min-width: 769px) {
  .shop-header-body { padding: 0 24px 20px; }
  .shop-cover { height: 120px; }
  .shop-top { margin-top: -36px; gap: 20px; }
  .shop-avatar { width: 72px; height: 72px; }
  .shop-info { padding-top: 40px; }
  .shop-meta { flex-direction: row; flex-wrap: wrap; gap: 12px; }
  .shop-title { font-size: 20px; }
  .shop-desc { font-size: 13px; }
  .shop-meta { font-size: 13px; }
}
</style>

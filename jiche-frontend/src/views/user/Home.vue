<template>
  <div>
    <!-- 横幅 -->
    <div class="hero-banner">
      <div class="hero-content">
        <h1 class="hero-title">发现你的下一辆摩托车</h1>
        <p class="hero-sub">汇聚全国优质商家，透明信息，放心选购</p>
      </div>
    </div>

    <!-- 筛选区 -->
    <FilterBar @change="onFilterChange" />

    <!-- 列表区 -->
    <div class="list-header flex-between mb-3">
      <span class="list-count">共 <b>{{ total }}</b> 辆在售车辆</span>
      <el-radio-group v-model="viewMode" size="small">
        <el-radio-button value="grid"><el-icon><Grid /></el-icon></el-radio-button>
        <el-radio-button value="list"><el-icon><List /></el-icon></el-radio-button>
      </el-radio-group>
    </div>

    <!-- 加载骨架 -->
    <div v-if="loading" class="bikes-grid">
      <el-skeleton v-for="i in 9" :key="i" animated>
        <template #template>
          <el-skeleton-item variant="image" style="height: 180px; border-radius: 10px 10px 0 0;" />
          <div style="padding: 12px;">
            <el-skeleton-item variant="text" style="width: 70%;" />
            <el-skeleton-item variant="text" style="width: 50%; margin-top: 8px;" />
            <el-skeleton-item variant="text" style="width: 40%; margin-top: 8px;" />
          </div>
        </template>
      </el-skeleton>
    </div>

    <!-- 车辆列表 -->
    <div v-else>
      <!-- 网格模式 -->
      <div v-if="viewMode === 'grid'" class="bikes-grid">
        <BikeCard v-for="bike in bikes" :key="bike.id" :bike="bike" />
      </div>

      <!-- 列表模式 -->
      <div v-else class="bikes-list">
        <div v-for="bike in bikes" :key="bike.id" class="bike-list-item" @click="$router.push(`/bike/${bike.id}`)">
          <img :src="bike.cover_image" :alt="bike.brand + bike.model" class="bike-list-img" />
          <div class="bike-list-body">
            <div class="bike-list-title">{{ bike.brand }} {{ bike.model }}</div>
            <div class="bike-list-meta">{{ bike.year }}年 · {{ bike.displacement }} · {{ (bike.mileage/10000).toFixed(1) }}万公里</div>
            <div class="bike-list-footer">
              <span class="bike-list-price">¥{{ formatPrice(bike.price) }}</span>
              <span class="text-muted" style="font-size:12px">{{ bike.shop_name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="!bikes.length" description="暂无符合条件的车辆" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import BikeCard from '@/components/BikeCard.vue'
import FilterBar from '@/components/FilterBar.vue'
import api from '@/api'

const bikes = ref([])
const total = ref(0)
const loading = ref(false)
const viewMode = ref('grid')
let currentFilters = {}

async function loadBikes(filters = {}) {
  loading.value = true
  try {
    const res = await api.getBikeList(filters)
    bikes.value = res.data.list
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function onFilterChange(filters) {
  currentFilters = filters
  loadBikes(filters)
}

function formatPrice(price) {
  if (price >= 10000) return (price / 10000).toFixed(1) + '万'
  return price.toLocaleString()
}

onMounted(() => loadBikes())
</script>

<style scoped>
.hero-banner {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border-radius: clamp(8px, 2vw, 12px);
  padding: clamp(20px, 4vw, 40px) clamp(16px, 3vw, 32px);
  margin-bottom: clamp(12px, 2vw, 24px);
  position: relative;
  overflow: hidden;
}
.hero-banner::before {
  content: '🏍';
  position: absolute;
  right: 32px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 80px;
  opacity: 0.15;
}
.hero-title {
  font-size: clamp(18px, 4vw, 28px);
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
}
.hero-sub { font-size: clamp(12px, 2vw, 14px); color: rgba(255,255,255,0.7); }

.list-header { margin-bottom: 12px; }
.list-count { font-size: 14px; color: #666; }
.list-count b { color: #1890ff; }

.bikes-list { display: flex; flex-direction: column; gap: 12px; }
.bike-list-item {
  background: #fff;
  border-radius: 10px;
  display: flex;
  gap: 16px;
  padding: 12px;
  cursor: pointer;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}
.bike-list-item:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
.bike-list-img { width: clamp(90px, 25vw, 140px); aspect-ratio: 4/3; object-fit: cover; border-radius: 8px; flex-shrink: 0; }
.bike-list-body { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.bike-list-title { font-size: clamp(13px, 2vw, 16px); font-weight: 600; color: #222; }
.bike-list-meta { font-size: 12px; color: #888; margin: 4px 0; }
.bike-list-footer { display: flex; align-items: center; justify-content: space-between; }
.bike-list-price { font-size: clamp(15px, 2.5vw, 18px); font-weight: 700; color: #ff4d4f; }

@media (max-width: 768px) {
  .hero-banner::before { font-size: 50px; right: 16px; }
  .bike-list-img { width: 100px; }
}
</style>

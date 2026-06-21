<template>
  <div v-if="shop">
    <!-- 商家头部 -->
    <div class="shop-header card mb-4">
      <div class="shop-cover"></div>
      <div class="shop-header-body">
        <div class="shop-avatar-wrap">
          <img :src="shop.avatar" class="shop-avatar" />
        </div>
        <div class="shop-info">
          <h1 class="shop-title">{{ shop.name }}</h1>
          <p class="shop-desc">{{ shop.description }}</p>
          <div class="shop-meta">
            <span><el-icon><Location /></el-icon> {{ shop.address }}</span>
            <span><el-icon><Cpu /></el-icon> 主营：{{ shop.main_models }}</span>
            <span><el-icon><List /></el-icon> 在售 {{ shop.bike_count }} 辆</span>
          </div>
        </div>
        <div class="shop-qrcode">
          <QRCodeViewer :src="shop.wechat_qrcode" />
        </div>
      </div>
    </div>

    <!-- 车辆列表 -->
    <div class="flex-between mb-3">
      <h2 class="section-title">全部车源</h2>
      <el-radio-group v-model="activeStatus" size="small" @change="filterBikes">
        <el-radio-button :value="0">全部</el-radio-button>
        <el-radio-button :value="1">在售</el-radio-button>
        <el-radio-button :value="2">已售</el-radio-button>
      </el-radio-group>
    </div>

    <div v-if="loading" class="bikes-grid">
      <el-skeleton v-for="i in 6" :key="i" animated>
        <template #template>
          <el-skeleton-item variant="image" style="height: 160px; border-radius: 10px 10px 0 0;" />
          <div style="padding: 10px;"><el-skeleton-item variant="text" /></div>
        </template>
      </el-skeleton>
    </div>

    <div v-else>
      <div class="bikes-grid">
        <BikeCard v-for="bike in filteredBikes" :key="bike.id" :bike="bike" />
      </div>
      <el-empty v-if="!filteredBikes.length" description="暂无车辆" />
    </div>
  </div>
  <div v-else-if="loading" class="flex-center" style="height:300px">
    <el-loading />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import BikeCard from '@/components/BikeCard.vue'
import QRCodeViewer from '@/components/QRCodeViewer.vue'
import api from '@/api'

const route = useRoute()
const shop = ref(null)
const allBikes = ref([])
const loading = ref(true)
const activeStatus = ref(0)

const filteredBikes = computed(() => {
  if (activeStatus.value === 0) return allBikes.value
  return allBikes.value.filter(b => b.bike_status === activeStatus.value)
})

onMounted(async () => {
  try {
    const res = await api.getShopDetail(route.params.id)
    shop.value = res.data.shop
    allBikes.value = res.data.bikes
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.shop-header { overflow: visible; }
.shop-cover {
  height: 120px;
  background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
  border-radius: 10px 10px 0 0;
}
.shop-header-body {
  padding: 0 24px 20px;
  display: flex;
  gap: 20px;
  align-items: flex-end;
  flex-wrap: wrap;
}
.shop-avatar-wrap {
  margin-top: -36px;
  flex-shrink: 0;
}
.shop-avatar {
  width: 72px;
  height: 72px;
  border-radius: 12px;
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  object-fit: cover;
}
.shop-info { flex: 1; min-width: 0; }
.shop-title { font-size: 20px; font-weight: 700; color: #222; margin: 4px 0; }
.shop-desc { font-size: 13px; color: #888; margin: 4px 0 8px; }
.shop-meta { display: flex; flex-wrap: wrap; gap: 12px; font-size: 13px; color: #666; }
.shop-meta span { display: flex; align-items: center; gap: 4px; }
.shop-qrcode { flex-shrink: 0; }
.section-title { font-size: 16px; font-weight: 600; color: #222; }

@media (max-width: 768px) {
  .shop-header-body { flex-direction: column; align-items: flex-start; padding: 0 16px 16px; }
  .shop-qrcode { align-self: center; }
}
</style>

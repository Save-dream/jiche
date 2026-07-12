<template>
  <div class="bike-card" @click="goDetail">
    <!-- 封面图 -->
    <div class="bike-card__image-wrap">
      <img :src="bike.cover_image" :alt="bike.brand + bike.model" class="bike-card__image" loading="lazy" />
      <!-- 状态遮罩 -->
      <div v-if="bike.bike_status !== 1" class="bike-card__mask">
        <span>{{ BIKE_STATUS[bike.bike_status]?.label }}</span>
      </div>
      <!-- 收藏按钮 -->
      <button class="bike-card__fav" @click.stop="handleFavorite" :title="isFav ? '取消收藏' : '收藏'">
        <el-icon :color="isFav ? '#ff4d4f' : '#fff'"><StarFilled v-if="isFav" /><Star v-else /></el-icon>
      </button>
    </div>

    <!-- 车辆信息 -->
    <div class="bike-card__body">
      <div class="bike-card__title">{{ bike.brand }} {{ bike.model }}</div>
      <div class="bike-card__meta">
        <span>{{ bike.year }}年</span>
        <span>{{ bike.displacement }}</span>
        <span>{{ (bike.mileage / 10000).toFixed(1) }}万公里</span>
      </div>
      <div class="bike-card__footer">
        <span class="bike-card__price">¥{{ formatPrice(bike.price) }}</span>
        <div class="bike-card__tags">
          <el-tag v-if="bike.can_transfer" size="small" type="info">可过户</el-tag>
          <el-tag v-if="bike.negotiable" size="small" type="warning">可议价</el-tag>
        </div>
      </div>
      <div class="bike-card__shop" @click.stop="router.push(`/shop/${bike.shop_id}`)">
        <el-icon><Shop /></el-icon>
        <span>{{ bike.shop_name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore, BIKE_STATUS } from '@/stores/auth'
import api from '@/api'

const props = defineProps({
  bike: { type: Object, required: true },
})

const router = useRouter()
const auth = useAuthStore()
const isFav = computed(() => auth.isFavorite(props.bike.id))

function goDetail() {
  router.push({ path: `/bike/${props.bike.id}`, query: { shop_id: props.bike.shop_id } })
}

async function handleFavorite() {
  if (!auth.isLoggedIn) {
    ElMessage.warning('请先登录后收藏')
    router.push({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }
  if (auth.isFavorite(props.bike.id)) {
    try {
      await auth.toggleFavorite(props.bike.id, api)
      ElMessage.success('已取消收藏')
    } catch { /* ignore */ }
    return
  }
  try {
    const result = await auth.toggleFavorite(props.bike.id, api)
    if (result === 'already') {
      ElMessage.warning('已在收藏夹中')
    } else {
      ElMessage.success('已加入收藏')
    }
  } catch { /* ignore */ }
}

function formatPrice(price) {
  if (price >= 10000) return (price / 10000).toFixed(1) + '万'
  return price.toLocaleString()
}
</script>

<style scoped>
.bike-card {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}
.bike-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}

.bike-card__image-wrap {
  position: relative;
  aspect-ratio: 4/3;
  overflow: hidden;
  background: #f5f5f5;
}
.bike-card__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s;
}
.bike-card:hover .bike-card__image {
  transform: scale(1.04);
}

.bike-card__mask {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 2px;
}

.bike-card__fav {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0,0,0,0.3);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}
.bike-card__fav:hover { background: rgba(0,0,0,0.5); }

.bike-card__body {
  padding: 12px;
}

.bike-card__title {
  font-size: 15px;
  font-weight: 600;
  color: #222;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bike-card__meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: #888;
  margin-bottom: 8px;
}
.bike-card__meta span::after {
  content: '·';
  margin-left: 8px;
}
.bike-card__meta span:last-child::after { content: ''; }

.bike-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.bike-card__price {
  font-size: 18px;
  font-weight: 700;
  color: #ff4d4f;
}

.bike-card__tags {
  display: flex;
  gap: 4px;
}

.bike-card__shop {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
}
.bike-card__shop:hover { color: #1890ff; }

@media (max-width: 768px) {
  .bike-card__image-wrap { aspect-ratio: 16/10; }
  .bike-card__body { padding: 8px; }
  .bike-card__title { font-size: 13px; margin-bottom: 4px; }
  .bike-card__meta { font-size: 11px; gap: 4px; margin-bottom: 6px; }
  .bike-card__price { font-size: 15px; }
  .bike-card__tags { display: none; } /* 移动端双列时隐藏标签避免拥挚 */
  .bike-card__shop { font-size: 11px; }
  .bike-card__fav { width: 28px; height: 28px; }
}
</style>

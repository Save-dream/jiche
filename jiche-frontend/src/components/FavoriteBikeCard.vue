<template>
  <div class="fav-card" :class="{ disabled: isUnavailable }">
    <div class="fav-card__image-wrap" @click="goDetail">
      <img :src="bike.cover_image" :alt="bike.brand + bike.model" class="fav-card__image" />
      <div v-if="isUnavailable" class="fav-card__mask">
        <span>{{ unavailableLabel }}</span>
      </div>
    </div>
    <div class="fav-card__body">
      <div class="fav-card__title" @click="goDetail">{{ bike.brand }} {{ bike.model }}</div>
      <div class="fav-card__meta">{{ bike.year }}年 · {{ bike.displacement }}</div>
      <div class="fav-card__footer">
        <span v-if="!isUnavailable" class="fav-card__price">¥{{ formatPrice(bike.price) }}</span>
        <span v-else class="fav-card__unavailable">{{ unavailableLabel }}</span>
        <el-button type="danger" link size="small" @click.stop="$emit('remove', bike.id)">
          删除收藏
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const props = defineProps({
  bike: { type: Object, required: true },
})
defineEmits(['remove'])

const router = useRouter()

const isUnavailable = computed(() => props.bike.is_deleted || props.bike.unavailable)
const unavailableLabel = computed(() =>
  props.bike.is_deleted ? '商家已删除' : '暂不可查看'
)

function goDetail() {
  if (isUnavailable.value) {
    ElMessage.warning(unavailableLabel.value)
    return
  }
  router.push({ path: `/bike/${props.bike.id}`, query: { shop_id: props.bike.shop_id } })
}

function formatPrice(price) {
  if (!price) return '-'
  if (price >= 10000) return (price / 10000).toFixed(1) + '万'
  return price.toLocaleString()
}
</script>

<style scoped>
.fav-card {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
}
.fav-card.disabled { opacity: 0.85; }
.fav-card__image-wrap {
  position: relative;
  aspect-ratio: 4/3;
  cursor: pointer;
  background: #f5f5f5;
}
.fav-card__image { width: 100%; height: 100%; object-fit: cover; display: block; }
.fav-card__mask {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: not-allowed;
}
.fav-card__body { padding: 12px; }
.fav-card__title {
  font-size: 15px;
  font-weight: 600;
  color: #222;
  margin-bottom: 4px;
  cursor: pointer;
}
.fav-card.disabled .fav-card__title { cursor: not-allowed; color: #999; }
.fav-card__meta { font-size: 12px; color: #888; margin-bottom: 8px; }
.fav-card__footer { display: flex; align-items: center; justify-content: space-between; }
.fav-card__price { font-size: 16px; font-weight: 700; color: #ff4d4f; }
.fav-card__unavailable { font-size: 13px; color: #999; }
</style>

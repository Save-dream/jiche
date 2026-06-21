<template>
  <div>
    <h2 class="page-title mb-4">我的收藏</h2>

    <div v-if="favorites.length" class="bikes-grid">
      <BikeCard v-for="bike in favorites" :key="bike.id" :bike="bike" />
    </div>
    <el-empty v-else description="暂无收藏车辆，去首页逛逛吧">
      <el-button type="primary" @click="$router.push('/')">浏览车源</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import BikeCard from '@/components/BikeCard.vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const allBikes = ref([])

const favorites = computed(() =>
  allBikes.value.filter(b => auth.isFavorite(b.id))
)

onMounted(async () => {
  const res = await api.getBikeList()
  allBikes.value = [...res.data.list]
  // 也获取已售车辆
  const res2 = await api.getAllBikes?.()
  if (res2) allBikes.value = res2.data.list
})
</script>

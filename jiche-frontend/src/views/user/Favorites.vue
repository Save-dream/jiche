<template>
  <div>
    <h2 class="page-title mb-4">我的收藏</h2>
    <p class="page-desc mb-4">支持删除收藏；商家已删除的商品将显示失效状态，不可进入详情</p>

    <div v-if="loading" class="bikes-grid">
      <el-skeleton v-for="i in 3" :key="i" animated />
    </div>

    <div v-else-if="favorites.length" class="bikes-grid">
      <FavoriteBikeCard
        v-for="bike in favorites"
        :key="bike.id"
        :bike="bike"
        @remove="removeFavorite"
      />
    </div>

    <el-empty v-else description="暂无收藏，请通过商家分享链接浏览车源">
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import FavoriteBikeCard from '@/components/FavoriteBikeCard.vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const favorites = ref([])
const loading = ref(true)

async function loadFavorites() {
  loading.value = true
  try {
    const res = await api.getFavorites()
    favorites.value = res.data.list || []
  } finally {
    loading.value = false
  }
}

async function removeFavorite(bikeId) {
  await api.removeFavorite(bikeId)
  auth.removeFavorite(bikeId)
  favorites.value = favorites.value.filter(b => b.id !== bikeId)
  ElMessage.success('已删除收藏')
}

onMounted(loadFavorites)
</script>

<style scoped>
.page-desc { font-size: 13px; color: #888; }
</style>

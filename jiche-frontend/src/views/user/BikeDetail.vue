<template>
  <div v-if="bike">
    <!-- 面包屑 -->
    <el-breadcrumb separator="/" class="mb-3">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>{{ bike.brand }} {{ bike.model }}</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="detail-layout">
      <!-- 左侧内容 -->
      <div class="detail-main">

        <!-- 图片轮播 -->
        <div class="card mb-3">
          <el-carousel :height="carouselHeight" :autoplay="false" indicator-position="outside" class="bike-carousel">
            <el-carousel-item v-for="(img, i) in bike.images" :key="i">
              <img :src="img" class="carousel-img" @click="previewImages(i)" />
            </el-carousel-item>
          </el-carousel>
        </div>

        <!-- 移动端：操作区（仅移动端显示，在基础信息前） -->
        <div class="card mb-3 action-card mobile-action-card">
          <div class="card-body">
            <div class="price-display">¥{{ formatPrice(bike.price) }}</div>
            <div class="action-btns">
              <el-button type="primary" size="large" class="action-btn" @click="msgVisible = true" :disabled="bike.bike_status !== 1">
                <el-icon><ChatDotRound /></el-icon>&nbsp;在线留言咨询
              </el-button>
              <el-button size="large" class="action-btn" :type="isFav ? 'danger' : 'default'" @click="toggleFav">
                <el-icon><StarFilled v-if="isFav" /><Star v-else /></el-icon>
                &nbsp;{{ isFav ? '已收藏' : '收藏' }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- 基础信息 -->
        <div class="card mb-3">
          <div class="card-header flex-between">
            <div>
              <span class="bike-name">{{ bike.brand }} {{ bike.model }}</span>
              <el-tag :type="bikeStatusMap[bike.bike_status]?.type" class="ml-2" size="small">
                {{ bikeStatusMap[bike.bike_status]?.label }}
              </el-tag>
            </div>
            <span class="price-big">¥{{ formatPrice(bike.price) }}</span>
          </div>
          <div class="card-body">
            <div class="info-grid">
              <div class="info-item"><span class="info-label">品牌</span><span>{{ bike.brand }}</span></div>
              <div class="info-item"><span class="info-label">车型</span><span>{{ bike.model }}</span></div>
              <div class="info-item"><span class="info-label">上牌年份</span><span>{{ bike.year }}年</span></div>
              <div class="info-item"><span class="info-label">排量</span><span>{{ bike.displacement }}</span></div>
              <div class="info-item"><span class="info-label">行驶里程</span><span>{{ bike.mileage.toLocaleString() }} km</span></div>
              <div class="info-item"><span class="info-label">是否可过户</span><span>{{ bike.can_transfer ? '✅ 可过户' : '❌ 不可过户' }}</span></div>
              <div class="info-item"><span class="info-label">是否可议价</span><span>{{ bike.negotiable ? '✅ 可议价' : '❌ 不可议价' }}</span></div>
              <div class="info-item"><span class="info-label">过户次数</span><span>{{ bike.transfer_count ?? 0 }} 次</span></div>
              <div class="info-item"><span class="info-label">交付方式</span><span>{{ bike.delivery_method }}</span></div>
              <div class="info-item"><span class="info-label">浏览次数</span><span>{{ bike.view_count }} 次</span></div>
            </div>
          </div>
        </div>

        <!-- 车况与零部件 -->
        <div class="card mb-3">
          <div class="card-header">车况 & 零部件状态</div>
          <div class="card-body">
            <div class="condition-section">
              <div class="condition-item" v-for="item in conditionItems" :key="item.key">
                <div class="condition-label"><el-icon><component :is="item.icon" /></el-icon>{{ item.label }}</div>
                <div class="condition-value">{{ bike[item.key] || '未填写' }}</div>
              </div>
            </div>
            <!-- 车况图片 -->
            <div v-if="bike.condition_images && bike.condition_images.length" class="condition-images">
              <div class="condition-images-title">零部件实拍图</div>
              <div class="condition-images-grid">
                <img
                  v-for="(img, i) in bike.condition_images"
                  :key="i"
                  :src="img"
                  class="condition-img"
                  @click="previewConditionImages(i)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 改装与瑕疵 -->
        <div class="card mb-3">
          <div class="card-header">改装 & 瑕疵说明</div>
          <div class="card-body">
            <div class="text-row"><span class="text-label">改装配件：</span><span>{{ bike.modification }}</span></div>
            <div class="text-row mt-2"><span class="text-label">车况瑕疵：</span><span>{{ bike.defects }}</span></div>
            <div class="text-row mt-2"><span class="text-label">维保记录：</span><span>{{ bike.maintenance }}</span></div>
          </div>
        </div>

        <!-- 补充说明 -->
        <div class="card mb-3" v-if="bike.fee_note || bike.after_sale">
          <div class="card-header">费用 & 售后说明</div>
          <div class="card-body">
            <div class="text-row" v-if="bike.fee_note"><span class="text-label">费用说明：</span><span>{{ bike.fee_note }}</span></div>
            <div class="text-row mt-2" v-if="bike.after_sale"><span class="text-label">售后说明：</span><span>{{ bike.after_sale }}</span></div>
          </div>
        </div>

        <!-- 移动端：商家信息 -->
        <div class="card mb-3 mobile-shop-card" v-if="bike.shop">
          <div class="card-header">商家信息</div>
          <div class="card-body">
            <div class="shop-info-row" @click="$router.push(`/shop/${bike.shop.id}`)" style="cursor:pointer">
              <img :src="bike.shop.avatar" class="shop-avatar" />
              <div>
                <div class="shop-name">{{ bike.shop.name }}</div>
                <div class="text-muted" style="font-size:12px">{{ bike.shop.address }}</div>
              </div>
            </div>
            <div class="mt-3">
              <div class="text-muted mb-2" style="font-size:12px; text-align:center">扫码联系商家微信</div>
              <QRCodeViewer :src="bike.shop.wechat_qrcode" />
            </div>
            <el-button type="default" size="small" style="width:100%; margin-top:12px" @click="$router.push(`/shop/${bike.shop.id}`)">
              查看商家全部车源
            </el-button>
          </div>
        </div>

      </div>

      <!-- 右侧：商家信息 + 操作（PC端显示） -->
      <div class="detail-sidebar">

        <!-- 操作区 -->
        <div class="card mb-3 action-card">
          <div class="card-body">
            <div class="price-display">¥{{ formatPrice(bike.price) }}</div>
            <el-button type="primary" size="large" block class="mb-2" @click="msgVisible = true" :disabled="bike.bike_status !== 1">
              <el-icon><ChatDotRound /></el-icon>&nbsp;在线留言咨询
            </el-button>
            <el-button size="large" block :type="isFav ? 'danger' : 'default'" @click="toggleFav">
              <el-icon><StarFilled v-if="isFav" /><Star v-else /></el-icon>
              &nbsp;{{ isFav ? '已收藏' : '加入收藏' }}
            </el-button>
          </div>
        </div>

        <!-- 商家信息 -->
        <div class="card mb-3" v-if="bike.shop">
          <div class="card-header">商家信息</div>
          <div class="card-body">
            <div class="shop-info-row" @click="$router.push(`/shop/${bike.shop.id}`)" style="cursor:pointer">
              <img :src="bike.shop.avatar" class="shop-avatar" />
              <div>
                <div class="shop-name">{{ bike.shop.name }}</div>
                <div class="text-muted" style="font-size:12px">{{ bike.shop.address }}</div>
              </div>
            </div>
            <div class="mt-3">
              <div class="text-muted mb-2" style="font-size:12px; text-align:center">扫码联系商家微信</div>
              <QRCodeViewer :src="bike.shop.wechat_qrcode" />
            </div>
            <el-button type="default" size="small" style="width:100%; margin-top:12px" @click="$router.push(`/shop/${bike.shop.id}`)">
              查看商家全部车源
            </el-button>
          </div>
        </div>

      </div>
    </div>

    <!-- 留言弹窗 -->
    <MessageDialog v-model="msgVisible" :bikeId="bike.id" />

    <!-- 图片预览 -->
    <el-image-viewer v-if="imgViewerVisible" :url-list="bike.images" :initial-index="imgViewerIndex" @close="imgViewerVisible = false" />
    <el-image-viewer v-if="condImgViewerVisible" :url-list="bike.condition_images" :initial-index="condImgViewerIndex" @close="condImgViewerVisible = false" />
  </div>

  <div v-else-if="loading" class="flex-center" style="height:300px"><el-loading /></div>
  <el-empty v-else description="车辆不存在或已下架" />
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore, BIKE_STATUS } from '@/stores/auth'
import QRCodeViewer from '@/components/QRCodeViewer.vue'
import MessageDialog from '@/components/MessageDialog.vue'
import api from '@/api'

const route = useRoute()
const auth = useAuthStore()

const bike = ref(null)
const loading = ref(true)
const msgVisible = ref(false)
const imgViewerVisible = ref(false)
const imgViewerIndex = ref(0)
const condImgViewerVisible = ref(false)
const condImgViewerIndex = ref(0)

// 流式轮播高度：随窗口宽度平滑缩放 200~380px
const winW = ref(typeof window !== 'undefined' ? window.innerWidth : 1200)
function onResize() { winW.value = window.innerWidth }
const carouselHeight = computed(() => {
  const h = Math.max(200, Math.min(380, winW.value * 0.42))
  return `${Math.round(h)}px`
})

const bikeStatusMap = BIKE_STATUS
const isFav = computed(() => auth.isFavorite(bike.value?.id))

function toggleFav() { auth.toggleFavorite(bike.value.id) }
function previewImages(index) { imgViewerIndex.value = index; imgViewerVisible.value = true }
function previewConditionImages(index) { condImgViewerIndex.value = index; condImgViewerVisible.value = true }
function formatPrice(price) {
  if (price >= 10000) return (price / 10000).toFixed(1) + '万'
  return price.toLocaleString()
}

const conditionItems = [
  { key: 'engine_status', label: '发动机', icon: 'Setting' },
  { key: 'suspension_status', label: '减震', icon: 'Share' },
  { key: 'brake_status', label: '刹车', icon: 'Remove' },
  { key: 'electrical_status', label: '电控', icon: 'Lightning' },
  { key: 'frame_status', label: '车架', icon: 'Grid' },
]

onMounted(async () => {
  window.addEventListener('resize', onResize)
  try {
    const res = await api.getBikeDetail(route.params.id)
    bike.value = res.data
  } finally {
    loading.value = false
  }
})
onUnmounted(() => window.removeEventListener('resize', onResize))
</script>

<style scoped>
.detail-layout {
  display: flex;
  gap: clamp(12px, 2vw, 20px);
  align-items: flex-start;
}
.detail-main { flex: 1; min-width: 0; }
.detail-sidebar { width: clamp(240px, 22vw, 280px); flex-shrink: 0; position: sticky; top: 76px; }

/* 移动端操作卡片和商家信息默认隐藏（PC由侧边栏显示） */
.mobile-action-card { display: none; }
.mobile-shop-card { display: none; }

/* 轮播：高度由 JS carouselHeight 控制，CSS 只管图片填满 */
.bike-carousel :deep(.el-carousel__container) {
  overflow: hidden;
}
.carousel-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
}

.bike-name { font-size: clamp(16px, 3vw, 20px); font-weight: 700; color: #222; }
.price-big { font-size: clamp(18px, 3vw, 24px); font-weight: 700; color: #ff4d4f; }

/* 参数网格：自动列数，窄屏1列，宽屏2+列 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 200px), 1fr));
  gap: clamp(8px, 1.5vw, 12px);
}
.info-item { display: flex; gap: 8px; font-size: clamp(12px, 1.5vw, 14px); min-width: 0; }
.info-label { color: #888; flex-shrink: 0; white-space: nowrap; }

.condition-section { display: flex; flex-direction: column; gap: clamp(8px, 1.5vw, 12px); }
.condition-item { display: flex; gap: clamp(8px, 1.5vw, 12px); }
.condition-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
  color: #444;
  width: clamp(60px, 10vw, 80px);
  flex-shrink: 0;
  font-size: clamp(12px, 1.5vw, 13px);
}
.condition-value { flex: 1; font-size: clamp(12px, 1.5vw, 13px); color: #555; line-height: 1.5; min-width: 0; }

.condition-images { margin-top: clamp(12px, 2vw, 16px); border-top: 1px solid #f0f0f0; padding-top: clamp(10px, 1.5vw, 12px); }
.condition-images-title { font-size: 13px; font-weight: 600; color: #444; margin-bottom: 10px; }
.condition-images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 100px), 1fr));
  gap: 8px;
}
.condition-img {
  width: 100%;
  aspect-ratio: 4/3;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #eee;
  cursor: pointer;
  transition: opacity 0.2s;
}
.condition-img:hover { opacity: 0.85; }

.text-row { font-size: clamp(13px, 1.5vw, 14px); color: #555; line-height: 1.6; }
.text-label { font-weight: 600; color: #444; }

.action-card .price-display { font-size: clamp(22px, 4vw, 28px); font-weight: 700; color: #ff4d4f; margin-bottom: clamp(10px, 2vw, 16px); text-align: center; }

.shop-info-row { display: flex; gap: 12px; align-items: center; }
.shop-avatar { width: clamp(40px, 8vw, 48px); height: clamp(40px, 8vw, 48px); border-radius: 8px; object-fit: cover; border: 1px solid #eee; }
.shop-name { font-size: 14px; font-weight: 600; color: #222; margin-bottom: 4px; }

/* 布局切换：窄屏改为单列纵向 */
@media (max-width: 900px) {
  .detail-layout { flex-direction: column; align-items: stretch; }
  .detail-main { width: 100%; }
  .detail-sidebar { display: none; }
  .mobile-action-card { display: block; }
  .mobile-shop-card { display: block; }
  .action-btns { display: flex; gap: 8px; }
  .action-btn { flex: 1; }
}
</style>

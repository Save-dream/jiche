<template>
  <div class="share-guide">
    <div class="share-guide__card">
      <div class="share-guide__icon">
        <el-icon :size="56" color="#1890ff"><Link /></el-icon>
      </div>
      <h2 class="share-guide__title">请通过商家分享链接访问</h2>
      <p class="share-guide__desc">
        极车是<strong>私域看车</strong>平台，不支持公开搜索或随意浏览车源。
        您只能通过商家微信分享的<strong>商品链接</strong>或<strong>店铺链接</strong>进入对应商家域。
      </p>

      <div class="share-guide__tips">
        <div class="tip-item">
          <span class="tip-num">1</span>
          <div>
            <div class="tip-title">获取分享链接</div>
            <div class="tip-text">向商家索取商品或店铺分享链接，在微信中打开即可自动携带商家信息</div>
          </div>
        </div>
        <div class="tip-item">
          <span class="tip-num">2</span>
          <div>
            <div class="tip-title">链接格式说明</div>
            <div class="tip-text">商品链接包含 <code>shop_id</code> 参数，确保您访问的是该商家授权的车源</div>
          </div>
        </div>
        <div class="tip-item">
          <span class="tip-num">3</span>
          <div>
            <div class="tip-title">曾访问过的商家</div>
            <div class="tip-text">若您之前通过分享链接访问过，可在首页「最近访问商家」快速返回</div>
          </div>
        </div>
      </div>

      <div v-if="recentShops.length" class="share-guide__recent">
        <div class="recent-title">最近访问的商家</div>
        <div
          v-for="item in recentShops"
          :key="item.id"
          class="recent-item"
          @click="goShop(item.id)"
        >
          <span>{{ item.name || `商家 #${item.id}` }}</span>
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="share-guide__actions">
        <el-button type="primary" size="large" @click="$router.push('/')">返回首页</el-button>
        <el-button size="large" @click="$router.back()">返回上一页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineProps({
  bikeId: { type: [String, Number], default: '' },
})

const router = useRouter()
const auth = useAuthStore()

const recentShops = computed(() => auth.visitedShops.slice(0, 5))

function goShop(shopId) {
  router.push(`/shop/${shopId}`)
}
</script>

<style scoped>
.share-guide {
  display: flex;
  justify-content: center;
  padding: clamp(16px, 4vw, 40px) 0;
}
.share-guide__card {
  width: 100%;
  max-width: 560px;
  background: #fff;
  border-radius: 12px;
  padding: clamp(24px, 4vw, 40px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  text-align: center;
}
.share-guide__icon { margin-bottom: 16px; }
.share-guide__title {
  font-size: clamp(18px, 3vw, 22px);
  font-weight: 700;
  color: #222;
  margin: 0 0 12px;
}
.share-guide__desc {
  font-size: 14px;
  color: #666;
  line-height: 1.7;
  margin: 0 0 24px;
  text-align: left;
}
.share-guide__desc strong { color: #333; }

.share-guide__tips {
  text-align: left;
  background: #f8fafc;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 20px;
}
.tip-item {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #eef2f6;
}
.tip-item:last-child { border-bottom: none; }
.tip-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #1890ff;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.tip-title { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 4px; }
.tip-text { font-size: 13px; color: #888; line-height: 1.5; }
.tip-text code {
  background: #e8f4ff;
  color: #1890ff;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.share-guide__recent {
  text-align: left;
  margin-bottom: 24px;
}
.recent-title { font-size: 13px; color: #888; margin-bottom: 8px; }
.recent-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  transition: border-color 0.2s, color 0.2s;
}
.recent-item:hover { border-color: #1890ff; color: #1890ff; }

.share-guide__actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}
</style>

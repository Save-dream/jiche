<template>
  <div class="qrcode-wrap" :class="`qrcode-wrap--${variant}`">
    <!-- 按钮模式：点击后弹窗展示 -->
    <button v-if="variant === 'button'" type="button" class="qrcode-btn" @click="visible = true">
      <span class="qrcode-btn-icon">
        <el-icon><ChatDotRound /></el-icon>
      </span>
      <span class="qrcode-btn-text">
        <span class="qrcode-btn-title">{{ buttonText }}</span>
        <span class="qrcode-btn-sub">{{ buttonSub }}</span>
      </span>
      <el-icon class="qrcode-btn-arrow"><ArrowRight /></el-icon>
    </button>

    <!-- 紧凑模式：小缩略图 -->
    <template v-else-if="variant === 'compact'">
      <img
        v-if="displaySrc"
        :src="displaySrc"
        alt="商家微信二维码"
        class="qrcode-compact"
        @click="visible = true"
        title="点击放大查看"
      />
      <div v-else class="qrcode-empty compact">暂无二维码</div>
    </template>

    <!-- 默认：大图展示 -->
    <template v-else>
      <img
        v-if="displaySrc"
        :src="displaySrc"
        alt="商家微信二维码"
        class="qrcode-thumb"
        @click="visible = true"
        title="点击放大查看"
      />
      <div v-else class="qrcode-empty">商家暂未上传微信二维码</div>
      <p v-if="displaySrc" class="qrcode-hint">点击扫码咨询商家</p>
    </template>

    <el-dialog v-model="visible" title="商家微信二维码" width="320px" align-center class="qrcode-dialog">
      <div class="qrcode-dialog-body">
        <img v-if="displaySrc" :src="displaySrc" alt="商家微信二维码" class="qrcode-full" />
        <p v-else class="qrcode-dialog-tip">商家暂未上传微信二维码</p>
        <p v-if="displaySrc" class="qrcode-dialog-tip">长按图片识别二维码，添加商家微信</p>
      </div>
      <template #footer>
        <el-button @click="visible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  /** 用于破坏浏览器缓存，如 shop.updated_at */
  cacheKey: { type: [String, Number], default: '' },
  variant: { type: String, default: 'default' }, // default | compact | button
  buttonText: { type: String, default: '微信咨询' },
  buttonSub: { type: String, default: '点击扫码添加商家微信' },
})

const visible = ref(false)

function normalizeMediaUrl(url) {
  if (!url) return ''
  const raw = String(url).trim()
  if (!raw) return ''
  if (
    raw.startsWith('http://') ||
    raw.startsWith('https://') ||
    raw.startsWith('data:') ||
    raw.startsWith('blob:')
  ) {
    return raw
  }
  return raw.startsWith('/') ? raw : `/${raw}`
}

const displaySrc = computed(() => {
  const base = normalizeMediaUrl(props.src)
  if (!base) return ''
  if (!props.cacheKey) return base
  const sep = base.includes('?') ? '&' : '?'
  return `${base}${sep}v=${encodeURIComponent(String(props.cacheKey))}`
})
</script>

<style scoped>
.qrcode-wrap--button { width: 100%; }

.qrcode-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid #e8f0fe;
  border-radius: 10px;
  background: linear-gradient(135deg, #f8fbff 0%, #f0f7ff 100%);
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  text-align: left;
}
.qrcode-btn:active { opacity: 0.85; }
.qrcode-btn:hover {
  border-color: #91caff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.12);
}
.qrcode-btn-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #1890ff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
}
.qrcode-btn-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.qrcode-btn-title {
  font-size: 14px;
  font-weight: 600;
  color: #222;
}
.qrcode-btn-sub {
  font-size: 12px;
  color: #888;
}
.qrcode-btn-arrow {
  color: #bbb;
  flex-shrink: 0;
}

.qrcode-compact {
  width: 56px;
  height: 56px;
  object-fit: contain;
  border: 1px solid #eee;
  border-radius: 8px;
  cursor: pointer;
}

.qrcode-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.qrcode-thumb {
  width: 120px;
  height: 120px;
  object-fit: contain;
  border: 1px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: box-shadow 0.2s;
}
.qrcode-thumb:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.15); }
.qrcode-hint { font-size: 12px; color: #888; }
.qrcode-empty {
  width: 120px;
  height: 120px;
  border: 1px dashed #ddd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #bbb;
  text-align: center;
  padding: 8px;
}
.qrcode-empty.compact {
  width: 56px;
  height: 56px;
  font-size: 10px;
  padding: 4px;
}

.qrcode-dialog-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}
.qrcode-full {
  width: 240px;
  height: 240px;
  object-fit: contain;
  border: 1px solid #eee;
  border-radius: 8px;
}
.qrcode-dialog-tip {
  font-size: 13px;
  color: #666;
  text-align: center;
}
</style>

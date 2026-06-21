<template>
  <!-- 二维码缩略展示 -->
  <div class="qrcode-wrap">
    <img
      :src="src"
      alt="商家微信二维码"
      class="qrcode-thumb"
      @click="visible = true"
      title="点击放大查看"
    />
    <p class="qrcode-hint">点击扫码咨询商家</p>

    <!-- 放大弹窗 -->
    <el-dialog v-model="visible" title="商家微信二维码" width="320px" align-center>
      <div class="qrcode-dialog-body">
        <img :src="src" alt="商家微信二维码" class="qrcode-full" />
        <p class="qrcode-dialog-tip">长按图片识别二维码，添加商家微信</p>
      </div>
      <template #footer>
        <el-button @click="visible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
defineProps({ src: { type: String, required: true } })
const visible = ref(false)
</script>

<style scoped>
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
.qrcode-hint {
  font-size: 12px;
  color: #888;
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

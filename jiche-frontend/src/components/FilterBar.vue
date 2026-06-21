<template>
  <div class="filter-bar">
    <div class="filter-bar__inner">
      <!-- 搜索框 -->
      <el-input
        v-model="localFilters.keyword"
        placeholder="搜索品牌、型号..."
        clearable
        class="filter-search"
        @change="emitChange"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>

      <!-- 价格区间 -->
      <div class="filter-item filter-item--price">
        <span class="filter-label">价格</span>
        <el-input v-model.number="localFilters.min_price" placeholder="最低价" class="filter-input-sm" @change="emitChange" />
        <span class="filter-sep">-</span>
        <el-input v-model.number="localFilters.max_price" placeholder="最高价" class="filter-input-sm" @change="emitChange" />
      </div>

      <!-- 排量 -->
      <div class="filter-item">
        <span class="filter-label">排量</span>
        <el-select v-model="localFilters.displacement" placeholder="不限" clearable @change="emitChange">
          <el-option label="150cc及以下" value="150" />
          <el-option label="151-250cc" value="250" />
          <el-option label="251-400cc" value="400" />
          <el-option label="401-600cc" value="600" />
          <el-option label="600cc以上" value="600+" />
        </el-select>
      </div>

      <!-- 年份 -->
      <div class="filter-item">
        <span class="filter-label">年份</span>
        <el-select v-model="localFilters.year" placeholder="不限" clearable @change="emitChange">
          <el-option v-for="y in years" :key="y" :label="`${y}年及以上`" :value="y" />
        </el-select>
      </div>

      <!-- 可过户 -->
      <div class="filter-item">
        <span class="filter-label">过户</span>
        <el-select v-model="localFilters.can_transfer" placeholder="不限" clearable @change="emitChange">
          <el-option label="可过户" value="true" />
          <el-option label="不可过户" value="false" />
        </el-select>
      </div>

      <!-- 重置 -->
      <el-button @click="reset" plain>重置</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'

const emit = defineEmits(['change'])

const localFilters = reactive({
  keyword: '',
  min_price: '',
  max_price: '',
  displacement: '',
  year: '',
  can_transfer: '',
})

const years = computed(() => {
  const now = new Date().getFullYear()
  const result = []
  for (let y = now; y >= now - 15; y--) result.push(y)
  return result
})

function emitChange() {
  emit('change', { ...localFilters })
}

function reset() {
  Object.keys(localFilters).forEach(k => localFilters[k] = '')
  emitChange()
}
</script>

<style scoped>
.filter-bar {
  background: #fff;
  border-radius: 10px;
  padding: clamp(10px, 2vw, 14px) clamp(12px, 2vw, 16px);
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
  margin-bottom: clamp(12px, 2vw, 20px);
}
.filter-bar__inner {
  display: flex;
  flex-wrap: wrap;
  gap: clamp(6px, 1.5vw, 12px);
  align-items: center;
}
.filter-search {
  width: clamp(140px, 20vw, 200px);
  flex-shrink: 0;
}
.filter-item {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
}
.filter-label {
  font-size: 13px;
  color: #666;
  white-space: nowrap;
  flex-shrink: 0;
}
/* el-select 默认占满剩余宽度，不溢出 */
.filter-item .el-select {
  flex: 1;
  min-width: 100px;
}
.filter-input-sm {
  width: clamp(70px, 12vw, 90px);
  min-width: 60px;
}
.filter-sep { color: #ccc; font-size: 12px; flex-shrink: 0; }

/* 移动端：搜索框和价格占满整行，其余两项一行 */
@media (max-width: 768px) {
  .filter-search {
    width: 100%;
    flex-basis: 100%;
  }
  .filter-item--price {
    flex-basis: 100%;
  }
  .filter-item--price .filter-input-sm {
    flex: 1;
    width: auto;
  }
  .filter-bar__inner > .el-button {
    flex-basis: 100%;
  }
}
</style>

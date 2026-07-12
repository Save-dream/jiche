<template>
  <div class="filter-shell">
    <!-- 搜索 + 筛选入口 -->
    <div class="filter-top">
      <div class="search-box">
        <el-icon class="search-icon"><Search /></el-icon>
        <input
          v-model="localFilters.keyword"
          type="search"
          class="search-input"
          placeholder="搜索品牌、型号"
          @input="debouncedEmit"
        />
        <button v-if="localFilters.keyword" class="search-clear" @click="clearKeyword">×</button>
      </div>
      <button
        type="button"
        class="filter-toggle"
        :class="{ active: panelOpen || activeFilterCount > 0 }"
        @click="panelOpen = !panelOpen"
      >
        <el-icon><Operation /></el-icon>
        <span>筛选</span>
        <em v-if="activeFilterCount" class="filter-badge">{{ activeFilterCount }}</em>
      </button>
    </div>

    <!-- 已选条件标签 -->
    <div v-if="activeFilterCount && !panelOpen" class="active-tags">
      <span v-for="tag in activeTags" :key="tag.key" class="active-tag" @click="clearTag(tag.key)">
        {{ tag.label }} ×
      </span>
      <button type="button" class="clear-all" @click="reset">清空</button>
    </div>

    <!-- 展开面板 -->
    <transition name="panel-slide">
      <div v-show="panelOpen" class="filter-panel">
        <div class="filter-group">
          <div class="group-label">价格区间</div>
          <div class="chip-row">
            <button
              v-for="p in pricePresets"
              :key="p.label"
              type="button"
              class="chip"
              :class="{ selected: isPriceSelected(p) }"
              @click="selectPrice(p)"
            >{{ p.label }}</button>
          </div>
          <div class="range-inputs">
            <input v-model.number="localFilters.min_price" type="number" placeholder="最低价" @input="debouncedEmit" @change="emitChange" />
            <span>—</span>
            <input v-model.number="localFilters.max_price" type="number" placeholder="最高价" @input="debouncedEmit" @change="emitChange" />
          </div>
        </div>

        <div class="filter-group">
          <div class="group-label">排量</div>
          <div class="chip-row">
            <button
              v-for="d in displacementOptions"
              :key="d.value"
              type="button"
              class="chip"
              :class="{ selected: localFilters.displacement === d.value }"
              @click="toggleField('displacement', d.value)"
            >{{ d.label }}</button>
          </div>
        </div>

        <div class="filter-group">
          <div class="group-label">上牌年份</div>
          <div class="chip-row">
            <button
              v-for="y in yearOptions"
              :key="y"
              type="button"
              class="chip"
              :class="{ selected: localFilters.year === y }"
              @click="toggleField('year', y)"
            >{{ y }}年起</button>
          </div>
        </div>

        <div class="filter-group">
          <div class="group-label">过户</div>
          <div class="chip-row">
            <button type="button" class="chip" :class="{ selected: !localFilters.can_transfer }" @click="toggleField('can_transfer', '')">不限</button>
            <button type="button" class="chip" :class="{ selected: localFilters.can_transfer === 'true' }" @click="toggleField('can_transfer', 'true')">可过户</button>
            <button type="button" class="chip" :class="{ selected: localFilters.can_transfer === 'false' }" @click="toggleField('can_transfer', 'false')">不可过户</button>
          </div>
        </div>

        <div class="panel-actions">
          <button type="button" class="btn-reset" @click="reset">重置</button>
          <button type="button" class="btn-confirm" @click="confirmPanel">确定</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { reactive, computed, ref } from 'vue'

const emit = defineEmits(['change'])

const panelOpen = ref(false)
const localFilters = reactive({
  keyword: '',
  min_price: '',
  max_price: '',
  displacement: '',
  year: '',
  can_transfer: '',
})

const pricePresets = [
  { label: '3万以下', min: '', max: 30000 },
  { label: '3-6万', min: 30000, max: 60000 },
  { label: '6-10万', min: 60000, max: 100000 },
  { label: '10万以上', min: 100000, max: '' },
]

const displacementOptions = [
  { label: '150以下', value: '150' },
  { label: '150-400', value: '400' },
  { label: '400-600', value: '600' },
  { label: '600+', value: '600+' },
]

const now = new Date().getFullYear()
const yearOptions = [now, now - 1, now - 2, now - 3, now - 5]

let debounceTimer
function debouncedEmit() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(emitChange, 300)
}

function emitChange() {
  emit('change', { ...localFilters })
}

function confirmPanel() {
  emitChange()
  panelOpen.value = false
}

function toggleField(field, value) {
  localFilters[field] = localFilters[field] === value ? '' : value
  emitChange()
}

function isPriceSelected(p) {
  return localFilters.min_price === p.min && localFilters.max_price === p.max
}

function selectPrice(p) {
  if (isPriceSelected(p)) {
    localFilters.min_price = ''
    localFilters.max_price = ''
  } else {
    localFilters.min_price = p.min
    localFilters.max_price = p.max
  }
  emitChange()
}

function clearKeyword() {
  localFilters.keyword = ''
  emitChange()
}

function clearTag(key) {
  if (key === 'price') {
    localFilters.min_price = ''
    localFilters.max_price = ''
  } else {
    localFilters[key] = ''
  }
  emitChange()
}

function reset() {
  Object.keys(localFilters).forEach(k => { localFilters[k] = '' })
  emitChange()
}

const activeFilterCount = computed(() => {
  let n = 0
  if (localFilters.keyword) n++
  if (localFilters.min_price || localFilters.max_price) n++
  if (localFilters.displacement) n++
  if (localFilters.year) n++
  if (localFilters.can_transfer) n++
  return n
})

const activeTags = computed(() => {
  const tags = []
  if (localFilters.keyword) tags.push({ key: 'keyword', label: localFilters.keyword })
  if (localFilters.min_price || localFilters.max_price) {
    tags.push({ key: 'price', label: `${localFilters.min_price || 0}-${localFilters.max_price || '∞'}` })
  }
  if (localFilters.displacement) {
    const d = displacementOptions.find(o => o.value === localFilters.displacement)
    tags.push({ key: 'displacement', label: d?.label || localFilters.displacement })
  }
  if (localFilters.year) tags.push({ key: 'year', label: `${localFilters.year}年起` })
  if (localFilters.can_transfer === 'true') tags.push({ key: 'can_transfer', label: '可过户' })
  if (localFilters.can_transfer === 'false') tags.push({ key: 'can_transfer', label: '不可过户' })
  return tags
})
</script>

<style scoped>
.filter-shell {
  margin-bottom: 16px;
}

.filter-top {
  display: flex;
  gap: 10px;
  align-items: stretch;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border-radius: 22px;
  padding: 0 14px;
  height: 40px;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
}
.search-icon { color: #bbb; font-size: 16px; flex-shrink: 0; }
.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  background: transparent;
  min-width: 0;
}
.search-input::placeholder { color: #bbb; }
.search-clear {
  border: none;
  background: #eee;
  color: #888;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  flex-shrink: 0;
}

.filter-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 40px;
  padding: 0 14px;
  border-radius: 22px;
  border: 1px solid #f0f0f0;
  background: #fff;
  font-size: 13px;
  color: #555;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}
.filter-toggle.active,
.filter-toggle:hover {
  border-color: #1890ff;
  color: #1890ff;
  background: #f0f7ff;
}
.filter-badge {
  font-style: normal;
  background: #1890ff;
  color: #fff;
  font-size: 11px;
  min-width: 16px;
  height: 16px;
  line-height: 16px;
  text-align: center;
  border-radius: 8px;
  padding: 0 4px;
}

.active-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
  align-items: center;
}
.active-tag {
  font-size: 12px;
  color: #1890ff;
  background: #e6f4ff;
  padding: 4px 10px;
  border-radius: 14px;
  cursor: pointer;
}
.clear-all {
  border: none;
  background: none;
  color: #999;
  font-size: 12px;
  cursor: pointer;
}

.filter-panel {
  margin-top: 12px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
}

.filter-group { margin-bottom: 16px; }
.filter-group:last-of-type { margin-bottom: 12px; }
.group-label {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chip {
  border: 1px solid #e8e8e8;
  background: #fafafa;
  color: #666;
  font-size: 12px;
  padding: 6px 14px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.15s;
}
.chip.selected {
  background: #e6f4ff;
  border-color: #1890ff;
  color: #1890ff;
  font-weight: 500;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}
.range-inputs input {
  flex: 1;
  min-width: 0;
  height: 34px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 0 10px;
  font-size: 13px;
  outline: none;
}
.range-inputs input:focus { border-color: #1890ff; }
.range-inputs span { color: #ccc; }

.panel-actions {
  display: flex;
  gap: 10px;
  padding-top: 4px;
}
.btn-reset,
.btn-confirm {
  flex: 1;
  height: 38px;
  border-radius: 19px;
  font-size: 14px;
  cursor: pointer;
  border: none;
}
.btn-reset { background: #f5f5f5; color: #666; }
.btn-confirm { background: #1890ff; color: #fff; }

.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}
.panel-slide-enter-from,
.panel-slide-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
}
.panel-slide-enter-to,
.panel-slide-leave-from {
  opacity: 1;
  max-height: 600px;
}
</style>

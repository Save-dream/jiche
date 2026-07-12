<template>
  <div>
    <el-breadcrumb separator="/" class="mb-4">
      <el-breadcrumb-item :to="{ path: '/shop/bikes' }">我的车源</el-breadcrumb-item>
      <el-breadcrumb-item>{{ isEdit ? '编辑车辆' : '发布新车' }}</el-breadcrumb-item>
    </el-breadcrumb>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="130px" label-position="top" class="bike-form">

      <!-- 基础参数区 -->
      <div class="card mb-4">
        <div class="card-header">基础参数（全部必填）</div>
        <div class="card-body">
          <el-row :gutter="20">
            <el-col :span="12" :xs="24">
              <el-form-item label="车辆品牌" prop="brand">
                <el-select
                  v-model="form.brand"
                  placeholder="选择或输入品牌"
                  filterable
                  allow-create
                  default-first-option
                  @change="onBrandChange"
                  style="width:100%"
                >
                  <el-option v-for="b in brands" :key="b.id" :label="b.name" :value="b.name" />
                </el-select>
                <div class="field-tip">可从列表选择，或直接输入自定义品牌</div>
              </el-form-item>
            </el-col>
            <el-col :span="12" :xs="24">
              <el-form-item label="车辆车型" prop="model">
                <el-select
                  v-model="form.model"
                  placeholder="选择或输入车型"
                  filterable
                  allow-create
                  default-first-option
                  style="width:100%"
                >
                  <el-option v-for="m in models" :key="m" :label="m" :value="m" />
                </el-select>
                <div class="field-tip">可从列表选择，或直接输入自定义车型</div>
              </el-form-item>
            </el-col>
            <el-col :span="12" :xs="24">
              <el-form-item label="上牌年份" prop="year">
                <el-select v-model="form.year" placeholder="请选择年份" style="width:100%">
                  <el-option v-for="y in years" :key="y" :label="`${y}年`" :value="y" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12" :xs="24">
              <el-form-item label="排量" prop="displacement">
                <el-input v-model="form.displacement" placeholder="如：400cc / 689cc" />
              </el-form-item>
            </el-col>
            <el-col :span="12" :xs="24">
              <el-form-item label="行驶里程(km)" prop="mileage">
                <el-input-number v-model="form.mileage" :min="2" :max="999999" :controls="true" style="width:100%" placeholder="须大于1" />
              </el-form-item>
            </el-col>
            <el-col :span="12" :xs="24">
              <el-form-item label="过户次数" prop="transfer_count">
                <el-input-number v-model="form.transfer_count" :min="0" :max="99" style="width:100%" placeholder="必填，可为0" />
              </el-form-item>
            </el-col>
            <el-col :span="12" :xs="24">
              <el-form-item label="售价(元)" prop="price">
                <el-input-number v-model="form.price" :min="1.01" :precision="2" :step="1000" style="width:100%" placeholder="须大于1" />
              </el-form-item>
            </el-col>
            <el-col :span="12" :xs="24">
              <el-form-item label="是否可过户" prop="can_transfer">
                <el-radio-group v-model="form.can_transfer">
                  <el-radio :value="true">是</el-radio>
                  <el-radio :value="false">否</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12" :xs="24">
              <el-form-item label="是否可议价" prop="negotiable">
                <el-radio-group v-model="form.negotiable">
                  <el-radio :value="true">是</el-radio>
                  <el-radio :value="false">否</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="商品首图" required>
                <div>
                  <div class="image-upload-grid">
                    <div v-for="(img, i) in form.images" :key="i" class="img-item">
                      <img :src="img.preview || img" class="img-preview" />
                      <span v-if="i === 0" class="img-cover-tag">封面</span>
                      <button class="img-del" @click.prevent="removeImage(i)"><el-icon><Close /></el-icon></button>
                    </div>
                    <label v-if="form.images.length < 20" class="img-add">
                      <input type="file" accept="image/jpeg,image/png" multiple @change="handleImageUpload" hidden />
                      <el-icon><Plus /></el-icon>
                      <span>添加图片</span>
                    </label>
                  </div>
                  <div class="field-tip">至少 3 张，最多 20 张；第一张为封面。格式 jpg/png，每张 ≤5M。已上传 {{ form.images.length }}/20 张</div>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 车况与零部件 -->
      <div class="card mb-4">
        <div class="card-header">车况 & 零部件介绍（必填）</div>
        <div class="card-body">
          <el-form-item v-for="item in conditionFields" :key="item.key" :label="item.label" :prop="item.key">
            <el-input v-model="form[item.key]" type="textarea" :rows="2" :placeholder="item.placeholder" />
          </el-form-item>
          <!-- 车况图片 -->
          <el-form-item label="车况图片" style="margin-top:4px">
            <div>
              <div class="image-upload-grid">
                <div v-for="(img, i) in form.condition_images" :key="i" class="img-item">
                  <img :src="img.preview || img" class="img-preview" />
                  <button class="img-del" @click.prevent="removeConditionImage(i)"><el-icon><Close /></el-icon></button>
                </div>
                <label v-if="form.condition_images.length < 10" class="img-add">
                  <input type="file" accept="image/jpeg,image/png" multiple @change="handleConditionImageUpload" hidden />
                  <el-icon><Plus /></el-icon>
                  <span>添加</span>
                </label>
              </div>
              <div style="font-size:12px;color:#999;margin-top:6px">可上传发动机、减震、刹车等零部件实拍图，最多10张（选填）</div>
            </div>
          </el-form-item>
        </div>
      </div>

      <!-- 改装与瑕疵 -->
      <div class="card mb-4">
        <div class="card-header">改装 & 瑕疵（必填，无则填"无"）</div>
        <div class="card-body">
          <el-form-item label="改装配件明细" prop="modification">
            <el-input v-model="form.modification" type="textarea" :rows="2" placeholder="无改装填写'无'，有改装请填写品牌、部位" />
          </el-form-item>
          <el-form-item label="车况瑕疵说明" prop="defects">
            <el-input v-model="form.defects" type="textarea" :rows="2" placeholder="无瑕疵填写'无'，禁止空提交" />
          </el-form-item>
          <el-form-item label="整车维保记录" prop="maintenance">
            <el-input v-model="form.maintenance" type="textarea" :rows="2" placeholder="如：每5000km换机油，大保养已做" />
          </el-form-item>
        </div>
      </div>

      <!-- 补充说明（选填） -->
      <div class="card mb-4">
        <div class="card-header">补充说明（选填）</div>
        <div class="card-body">
          <el-form-item label="交付方式">
            <el-checkbox-group v-model="form.delivery_methods">
              <el-checkbox label="自提">自提</el-checkbox>
              <el-checkbox label="物流">物流配送</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="费用说明">
            <el-input v-model="form.fee_note" placeholder="如：含过户 / 过户费买方承担" />
          </el-form-item>
          <el-form-item label="售后说明">
            <el-input v-model="form.after_sale" placeholder="如：7天质量问题退换 / 无售后" />
          </el-form-item>
        </div>
      </div>

      <!-- 提交 -->
      <div class="form-actions">
        <el-button size="large" @click="$router.back()">取消</el-button>
        <el-button type="primary" size="large" :loading="submitting" @click="submit">
          {{ isEdit ? '保存修改' : '发布车辆' }}
        </el-button>
      </div>

    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const formRef = ref()
const submitting = ref(false)

const brands = ref([])
const models = ref([])
const selectedBrandId = ref(null)

const years = computed(() => {
  const now = new Date().getFullYear()
  return Array.from({ length: 30 }, (_, i) => now - i)
})

const form = reactive({
  brand: '', model: '', year: null, displacement: '', mileage: null,
  transfer_count: null, price: null, can_transfer: true, negotiable: true,
  engine_status: '', suspension_status: '', brake_status: '', electrical_status: '', frame_status: '',
  modification: '', defects: '', maintenance: '',
  images: [],
  condition_images: [],
  delivery_methods: ['自提'],
  fee_note: '', after_sale: '',
})

const conditionFields = [
  { key: 'engine_status', label: '发动机状态', placeholder: '原厂运转正常，无异响...' },
  { key: 'suspension_status', label: '减震状态', placeholder: '前后减震原厂，无漏油...' },
  { key: 'brake_status', label: '刹车状态', placeholder: '刹车片剩余70%...' },
  { key: 'electrical_status', label: '电控系统', placeholder: '电控正常，无报警灯...' },
  { key: 'frame_status', label: '车架状态', placeholder: '无变形，无事故记录...' },
]

function gtOne(_rule, value, callback) {
  if (value === null || value === undefined || value === '') {
    callback(new Error('此项必填'))
    return
  }
  if (Number(value) <= 1) {
    callback(new Error('须大于 1'))
    return
  }
  callback()
}

function transferRequired(_rule, value, callback) {
  if (value === null || value === undefined || value === '') {
    callback(new Error('请填写过户次数，可为 0'))
    return
  }
  if (Number(value) < 0) {
    callback(new Error('过户次数不能为负数'))
    return
  }
  callback()
}

const required = [{ required: true, message: '此项必填', trigger: 'blur' }]
const rules = {
  brand: [{ required: true, message: '请选择或输入品牌', trigger: 'change' }],
  model: [{ required: true, message: '请选择或输入车型', trigger: 'change' }],
  year: [{ required: true, message: '请选择年份', trigger: 'change' }],
  displacement: required,
  mileage: [{ validator: gtOne, trigger: 'change' }],
  transfer_count: [{ validator: transferRequired, trigger: 'change' }],
  price: [{ validator: gtOne, trigger: 'change' }],
  engine_status: required, suspension_status: required,
  brake_status: required, electrical_status: required, frame_status: required,
  modification: required, defects: required, maintenance: required,
}

async function loadBrands() {
  const res = await api.getBrands()
  brands.value = res.data || []
}

async function onBrandChange(brandName, { clearModel = true } = {}) {
  if (clearModel) form.model = ''
  const name = String(brandName || '').trim()
  form.brand = name
  const brand = brands.value.find(b => b.name === name)
  selectedBrandId.value = brand?.id || null
  if (brand) {
    const res = await api.getModels(brand.id)
    models.value = (res.data || []).map((m) => (typeof m === 'string' ? m : m.name || m.model || String(m)))
  } else {
    models.value = []
  }
}

function handleImageUpload(e) {
  const files = [...e.target.files]
  const remaining = 20 - form.images.length
  files.slice(0, remaining).forEach(file => {
    if (file.size > 5 * 1024 * 1024) { ElMessage.error(`${file.name} 超过5M`); return }
    form.images.push({ file, preview: URL.createObjectURL(file) })
  })
  e.target.value = ''
}
function removeImage(index) { form.images.splice(index, 1) }

function handleConditionImageUpload(e) {
  const files = [...e.target.files]
  const remaining = 10 - form.condition_images.length
  files.slice(0, remaining).forEach(file => {
    if (file.size > 5 * 1024 * 1024) { ElMessage.error(`${file.name} 超过5M`); return }
    form.condition_images.push({ file, preview: URL.createObjectURL(file) })
  })
  e.target.value = ''
}
function removeConditionImage(index) { form.condition_images.splice(index, 1) }

async function resolveImageUrls(items) {
  const urls = []
  for (const item of items) {
    if (typeof item === 'string') {
      urls.push(item)
    } else if (item.file) {
      const res = await api.uploadImage(item.file)
      urls.push(res.data.url)
    } else if (item.preview && !String(item.preview).startsWith('blob:')) {
      urls.push(item.preview)
    }
  }
  return urls
}

async function submit() {
  form.brand = String(form.brand || '').trim()
  form.model = String(form.model || '').trim()
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  if (form.images.length < 3) { ElMessage.error('请至少上传 3 张商品首图'); return }
  submitting.value = true
  try {
    const images = await resolveImageUrls(form.images)
    const condition_images = await resolveImageUrls(form.condition_images)
    const catalogBrand = brands.value.find(b => b.name === form.brand)
    const payload = {
      brand_id: catalogBrand?.id || selectedBrandId.value || null,
      brand: form.brand,
      model: form.model,
      year: form.year,
      displacement: form.displacement,
      mileage: form.mileage,
      transfer_count: form.transfer_count,
      price: form.price,
      can_transfer: form.can_transfer,
      negotiable: form.negotiable,
      engine_status: form.engine_status,
      suspension_status: form.suspension_status,
      brake_status: form.brake_status,
      electrical_status: form.electrical_status,
      frame_status: form.frame_status,
      modification: form.modification,
      defects: form.defects,
      maintenance: form.maintenance,
      delivery_method: form.delivery_methods.join('/'),
      fee_note: form.fee_note,
      after_sale: form.after_sale,
      cover_image: images[0],
      images,
      condition_images,
    }
    if (isEdit.value) {
      await api.updateBike(route.params.id, payload)
      ElMessage.success('修改已保存')
    } else {
      await api.createBike(payload)
      ElMessage.success('车辆发布成功！')
    }
    router.push('/shop/bikes')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await loadBrands()
  if (isEdit.value) {
    const res = await api.getShopBike(route.params.id)
    const bike = res.data
    Object.assign(form, {
      brand: bike.brand,
      model: bike.model,
      year: bike.year,
      displacement: bike.displacement,
      mileage: bike.mileage,
      transfer_count: bike.transfer_count,
      price: bike.price,
      can_transfer: bike.can_transfer,
      negotiable: bike.negotiable,
      engine_status: bike.engine_status,
      suspension_status: bike.suspension_status,
      brake_status: bike.brake_status,
      electrical_status: bike.electrical_status,
      frame_status: bike.frame_status,
      modification: bike.modification,
      defects: bike.defects,
      maintenance: bike.maintenance,
      fee_note: bike.fee_note || '',
      after_sale: bike.after_sale || '',
      images: (bike.images || []).map(url => url),
      condition_images: (bike.condition_images || []).map(url => url),
      delivery_methods: bike.delivery_method?.split('/').filter(Boolean) || ['自提'],
    })
    await onBrandChange(bike.brand, { clearModel: false })
    form.model = bike.model
  }
})
</script>

<style scoped>
.bike-form { max-width: 900px; }
.field-tip { font-size: 12px; color: #999; margin-top: 4px; line-height: 1.4; }
.form-actions { display: flex; gap: 12px; justify-content: flex-end; padding: 8px 0 24px; }
.image-upload-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.img-item {
  position: relative;
  width: 100px;
  height: 100px;
}
.img-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #eee;
}
.img-cover-tag {
  position: absolute;
  left: 0;
  bottom: 0;
  background: rgba(24, 144, 255, 0.9);
  color: #fff;
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 0 6px 0 6px;
}
.img-del {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #ff4d4f;
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
}
.img-add {
  width: 100px;
  height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  color: #999;
  font-size: 12px;
  transition: border-color 0.2s, color 0.2s;
}
.img-add:hover { border-color: #1890ff; color: #1890ff; }
.img-add .el-icon { font-size: 24px; }
</style>

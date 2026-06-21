// Mock 数据模块 - 模拟后端接口返回数据
// 真实对接时替换 mockXxx 函数为 axios 请求即可

// ==================== 本地 SVG 占位图 ====================
function placeholder(text, w = 400, h = 300, bg = '#e8e8e8', fg = '#888') {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><rect fill="${bg}" width="${w}" height="${h}"/><text x="50%" y="50%" font-size="${Math.min(w, h) / 6}" text-anchor="middle" fill="${fg}" dy=".3em" font-family="sans-serif" font-weight="bold">${text}</text></svg>`
  return `data:image/svg+xml,${encodeURIComponent(svg)}`
}

// ==================== Mock 基础数据 ====================

export const mockBrands = [
  { id: 1, name: '本田' },
  { id: 2, name: '雅马哈' },
  { id: 3, name: '铃木' },
  { id: 4, name: '川崎' },
  { id: 5, name: '宝马' },
  { id: 6, name: '哈雷' },
  { id: 7, name: '杜卡迪' },
  { id: 8, name: '春风' },
  { id: 9, name: '钱江' },
  { id: 10, name: '贝纳利' },
]

export const mockModels = {
  1: ['CB400', 'CB500F', 'CBR600RR', 'NC750X', 'CRF1100L'],
  2: ['MT-07', 'MT-09', 'YZF-R1', 'NMAX155', 'XMAX300'],
  3: ['GSX-R750', 'V-STROM650', 'BOULEVARD'],
  4: ['Z900', 'Ninja 400', 'Versys 650', 'Z H2'],
  5: ['R1250GS', 'S1000RR', 'F850GS'],
  6: ['Sportster', 'Fat Boy', 'Road King'],
  7: ['Panigale V4', 'Monster', 'Multistrada'],
  8: ['450SR', '800MT', 'NK800'],
  9: ['QJ900GS', 'SR500'],
  10: ['502C', 'Leoncino500'],
}

export const mockShops = [
  {
    id: 1,
    name: '极速摩托行',
    contact_name: '张老板',
    phone: '13800138001',
    address: '广州市天河区车陂路168号',
    main_models: '本田、雅马哈中大排量',
    shop_status: 2,
    wechat_qrcode: placeholder('微信二维码', 200, 200),
    avatar: placeholder('极速', 80, 80),
    bike_count: 12,
    description: '专业二手摩托车商家，10年经验',
  },
  {
    id: 2,
    name: '骑行天堂',
    contact_name: '李老板',
    phone: '13900139002',
    address: '深圳市南山区科技园',
    main_models: '川崎、宝马进口车',
    shop_status: 2,
    wechat_qrcode: placeholder('微信二维码', 200, 200),
    avatar: placeholder('骑行', 80, 80),
    bike_count: 8,
    description: '进口车专卖，品质保证',
  },
]

export const mockBikes = [
  {
    id: 1,
    shop_id: 1,
    shop_name: '极速摩托行',
    brand: '本田',
    model: 'CB400',
    year: 2021,
    displacement: '400cc',
    mileage: 8500,
    price: 28000,
    can_transfer: true,
    negotiable: true,
    bike_status: 1,
    cover_image: placeholder('CB400', 400, 300),
    images: [
      placeholder('CB400 全景', 800, 600),
      placeholder('CB400 发动机', 800, 600),
      placeholder('CB400 仪表', 800, 600),
    ],
    condition_images: [
      placeholder('发动机实拍', 400, 300),
      placeholder('减震实拍', 400, 300),
      placeholder('刹车实拍', 400, 300),
    ],
    engine_status: '原厂，运转正常，无异响',
    suspension_status: '前后减震原厂，无漏油',
    brake_status: '刹车片剩余70%，刹车力度正常',
    electrical_status: '电控系统正常，无报警灯',
    frame_status: '车架无变形，无事故记录',
    modification: '无',
    defects: '左侧小磕碰，不影响使用',
    maintenance: '定期更换机油，大保养已做',
    delivery_method: '支持自提/物流',
    after_sale: '7天质量问题退换',
    fee_note: '过户费买方承担',
    created_at: '2024-01-15',
    view_count: 256,
  },
  {
    id: 2,
    shop_id: 1,
    shop_name: '极速摩托行',
    brand: '雅马哈',
    model: 'MT-07',
    year: 2022,
    displacement: '689cc',
    mileage: 12000,
    price: 58000,
    can_transfer: true,
    negotiable: false,
    bike_status: 1,
    cover_image: placeholder('MT-07', 400, 300),
    images: [
      placeholder('MT07 全景', 800, 600),
      placeholder('MT07 细节', 800, 600),
    ],
    engine_status: '原厂，动力强劲',
    suspension_status: '减震正常',
    brake_status: '刹车灵敏',
    electrical_status: '全部正常',
    frame_status: '无事故',
    modification: 'Akrapovic排气，美观提升音效',
    defects: '无',
    maintenance: '每5000km保养一次',
    delivery_method: '支持自提',
    after_sale: '包过户',
    fee_note: '含过户',
    created_at: '2024-01-20',
    view_count: 189,
  },
  {
    id: 3,
    shop_id: 2,
    shop_name: '骑行天堂',
    brand: '川崎',
    model: 'Z900',
    year: 2020,
    displacement: '948cc',
    mileage: 22000,
    price: 75000,
    can_transfer: true,
    negotiable: true,
    bike_status: 1,
    cover_image: placeholder('Z900', 400, 300),
    images: [placeholder('Z900', 800, 600)],
    engine_status: '原厂发动机',
    suspension_status: '前倒置减震，状态良好',
    brake_status: '对向卡钳，制动有力',
    electrical_status: '多骑行模式，正常',
    frame_status: '无变形',
    modification: '无',
    defects: '左侧脚踏轻微磨损',
    maintenance: '有完整保养记录',
    delivery_method: '支持自提/物流',
    after_sale: '协商',
    fee_note: '过户另算',
    created_at: '2024-02-01',
    view_count: 312,
  },
  {
    id: 4,
    shop_id: 1,
    shop_name: '极速摩托行',
    brand: '宝马',
    model: 'R1250GS',
    year: 2019,
    displacement: '1254cc',
    mileage: 35000,
    price: 120000,
    can_transfer: false,
    negotiable: true,
    bike_status: 2,
    cover_image: placeholder('R1250GS', 400, 300),
    images: [placeholder('R1250GS', 800, 600)],
    engine_status: '水平对卧发动机，运转良好',
    suspension_status: 'Telelever前减震，状态正常',
    brake_status: '有ABS，制动正常',
    electrical_status: '多模式，ICC正常',
    frame_status: '无事故',
    modification: '加装防摔杠、手把套',
    defects: '前风挡轻微划痕',
    maintenance: '宝马官方保养记录',
    delivery_method: '仅自提',
    after_sale: '无',
    fee_note: '无过户',
    created_at: '2024-01-05',
    view_count: 520,
  },
]

export const mockMessages = [
  {
    id: 1,
    bike_id: 1,
    bike_info: 'CB400 2021年',
    user_id: 101,
    user_name: '用户张三',
    content: '请问这辆车可以试驾吗？',
    contact_phone: '13512345678',
    message_status: 3,
    reply_content: '可以的，请提前预约，地址：广州天河区车陂路168号',
    created_at: '2024-02-10 14:30',
    replied_at: '2024-02-10 16:00',
  },
  {
    id: 2,
    bike_id: 1,
    bike_info: 'CB400 2021年',
    user_id: 102,
    user_name: '用户李四',
    content: '车子还在吗？价格可以再优惠一点吗？',
    contact_phone: '',
    message_status: 1,
    reply_content: '',
    created_at: '2024-02-12 09:15',
    replied_at: '',
  },
  {
    id: 3,
    bike_id: 2,
    bike_info: 'MT-07 2022年',
    user_id: 103,
    user_name: '用户王五',
    content: '改装排气有没有影响保险？',
    contact_phone: '13987654321',
    message_status: 2,
    reply_content: '',
    created_at: '2024-02-11 20:00',
    replied_at: '',
  },
]

export const mockShopApplications = [
  {
    id: 1,
    user_id: 201,
    user_name: '赵六',
    shop_type: '个人商户',
    contact_name: '赵六',
    phone: '13711111111',
    address: '北京朝阳区',
    main_models: '日系中排量',
    wechat_qrcode: placeholder('二维码', 200, 200),
    qualification_photo: '',
    description: '专注二手摩托5年',
    shop_status: 1,
    applied_at: '2024-02-13 10:00',
    reject_reason: '',
  },
  {
    id: 2,
    user_id: 202,
    user_name: '孙七',
    shop_type: '企业商户',
    contact_name: '孙七',
    phone: '13822222222',
    address: '上海徐汇区',
    main_models: '欧系大排量',
    wechat_qrcode: placeholder('二维码', 200, 200),
    qualification_photo: placeholder('营业执照', 400, 300),
    description: '合法注册企业',
    shop_status: 1,
    applied_at: '2024-02-14 08:30',
    reject_reason: '',
  },
]

// ==================== 模拟延迟 ====================
const delay = (ms = 300) => new Promise(resolve => setTimeout(resolve, ms))

// ==================== API 模拟函数 ====================
// 生产环境替换为真实 axios 调用

const mockResponse = (data) => ({ code: 200, msg: 'success', data })

export const mockApi = {
  // 车辆列表（含筛选）
  async getBikeList(params = {}) {
    await delay()
    let list = mockBikes.filter(b => b.bike_status === 1)
    if (params.brand) list = list.filter(b => b.brand === params.brand)
    if (params.min_price) list = list.filter(b => b.price >= params.min_price)
    if (params.max_price) list = list.filter(b => b.price <= params.max_price)
    if (params.can_transfer !== undefined && params.can_transfer !== '') {
      list = list.filter(b => b.can_transfer === (params.can_transfer === 'true'))
    }
    if (params.year) list = list.filter(b => b.year >= params.year)
    return mockResponse({ list, total: list.length })
  },

  // 车辆详情
  async getBikeDetail(id) {
    await delay()
    const bike = mockBikes.find(b => b.id === Number(id))
    if (!bike) return { code: 404, msg: '车辆不存在', data: null }
    const shop = mockShops.find(s => s.id === bike.shop_id)
    return mockResponse({ ...bike, shop })
  },

  // 商家信息
  async getShopDetail(id) {
    await delay()
    const shop = mockShops.find(s => s.id === Number(id))
    const bikes = mockBikes.filter(b => b.shop_id === Number(id))
    return mockResponse({ shop, bikes })
  },

  // 商家自己的车源列表
  async getMyBikes() {
    await delay()
    return mockResponse({ list: mockBikes.filter(b => b.shop_id === 1), total: mockBikes.filter(b => b.shop_id === 1).length })
  },

  // 留言列表（商家）
  async getMyMessages(params = {}) {
    await delay()
    let list = mockMessages
    if (params.status) list = list.filter(m => m.message_status === Number(params.status))
    return mockResponse({ list, total: list.length })
  },

  // 所有留言（管理员）
  async getAllMessages() {
    await delay()
    return mockResponse({ list: mockMessages, total: mockMessages.length })
  },

  // 所有商家申请（管理员）
  async getShopApplications(params = {}) {
    await delay()
    let list = mockShopApplications
    if (params.status) list = list.filter(s => s.shop_status === Number(params.status))
    return mockResponse({ list, total: list.length })
  },

  // 所有商家（管理员）
  async getAllShops() {
    await delay()
    return mockResponse({ list: mockShops, total: mockShops.length })
  },

  // 全平台车源（管理员）
  async getAllBikes() {
    await delay()
    return mockResponse({ list: mockBikes, total: mockBikes.length })
  },

  // 品牌列表
  async getBrands() {
    await delay(100)
    return mockResponse(mockBrands)
  },

  // 品牌下的车型
  async getModels(brandId) {
    await delay(100)
    return mockResponse(mockModels[brandId] || [])
  },

  // 统计数据（商家）
  async getShopStats() {
    await delay()
    return mockResponse({
      on_sale: 3,
      sold: 1,
      unread_messages: 2,
      total_views: 1277,
    })
  },

  // 统计数据（管理员）
  async getAdminStats() {
    await delay()
    return mockResponse({
      total_shops: 2,
      pending_applications: 2,
      total_bikes: 4,
      total_messages: 3,
    })
  },
}

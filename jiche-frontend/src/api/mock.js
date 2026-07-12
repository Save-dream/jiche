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
    published_at: '2024-02-10',
    created_at: '2024-01-15',
    is_deleted: 0,
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
    published_at: '2024-02-08',
    created_at: '2024-01-20',
    is_deleted: 0,
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
    published_at: '2024-01-28',
    created_at: '2024-02-01',
    is_deleted: 0,
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
    published_at: '2024-01-05',
    created_at: '2024-01-05',
    is_deleted: 0,
    view_count: 520,
  },
  {
    id: 5,
    shop_id: 1,
    shop_name: '极速摩托行',
    brand: '春风',
    model: '450SR',
    year: 2023,
    displacement: '450cc',
    mileage: 5000,
    price: 32000,
    can_transfer: true,
    negotiable: true,
    bike_status: 1,
    cover_image: placeholder('450SR', 400, 300),
    images: [placeholder('450SR', 800, 600)],
    engine_status: '原厂',
    suspension_status: '正常',
    brake_status: '正常',
    electrical_status: '正常',
    frame_status: '无事故',
    modification: '无',
    defects: '无',
    maintenance: '保养良好',
    delivery_method: '自提',
    after_sale: '',
    fee_note: '',
    published_at: '2024-01-10',
    created_at: '2024-01-10',
    is_deleted: 1,
    view_count: 88,
  },
  {
    id: 6,
    shop_id: 1,
    shop_name: '极速摩托行',
    brand: '杜卡迪',
    model: 'Monster',
    year: 2020,
    displacement: '821cc',
    mileage: 15000,
    price: 68000,
    can_transfer: true,
    negotiable: false,
    bike_status: 4,
    cover_image: placeholder('Monster', 400, 300),
    images: [placeholder('Monster', 800, 600)],
    engine_status: '原厂',
    suspension_status: '正常',
    brake_status: '正常',
    electrical_status: '正常',
    frame_status: '无事故',
    modification: '无',
    defects: '无',
    maintenance: '有记录',
    delivery_method: '自提',
    after_sale: '',
    fee_note: '',
    published_at: '2024-01-08',
    created_at: '2024-01-08',
    is_deleted: 0,
    view_count: 45,
  },
]

// 多轮留言会话
export const mockMessageThreads = [
  {
    id: 1,
    bike_id: 1,
    shop_id: 1,
    user_id: 100,
    user_name: '普通用户',
    bike_info: '本田 CB400 2021年',
    thread_status: 1,
    unread_count_user: 1,
    unread_count_shop: 0,
    contact_phone: '13600000001',
    updated_at: '2024-02-14 10:30',
    messages: [
      { id: 1, sender_type: 1, content: '请问这辆车可以试驾吗？', created_at: '2024-02-10 14:30' },
      { id: 2, sender_type: 2, content: '可以的，请提前预约，地址：广州天河区车陂路168号', created_at: '2024-02-10 16:00' },
      { id: 3, sender_type: 1, content: '好的，这周末方便吗？', created_at: '2024-02-14 10:30' },
    ],
  },
  {
    id: 2,
    bike_id: 1,
    shop_id: 1,
    user_id: 102,
    user_name: '用户李四',
    bike_info: '本田 CB400 2021年',
    thread_status: 1,
    unread_count_user: 0,
    unread_count_shop: 1,
    contact_phone: '',
    updated_at: '2024-02-12 09:15',
    messages: [
      { id: 4, sender_type: 1, content: '车子还在吗？价格可以再优惠一点吗？', created_at: '2024-02-12 09:15' },
    ],
  },
  {
    id: 3,
    bike_id: 2,
    shop_id: 1,
    user_id: 103,
    user_name: '用户王五',
    bike_info: '雅马哈 MT-07 2022年',
    thread_status: 2,
    unread_count_user: 0,
    unread_count_shop: 0,
    contact_phone: '13987654321',
    updated_at: '2024-02-11 20:00',
    messages: [
      { id: 5, sender_type: 1, content: '改装排气有没有影响保险？', created_at: '2024-02-11 20:00' },
    ],
  },
]

// 兼容旧引用
export const mockMessages = mockMessageThreads

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

// ==================== 用户与登录 Mock（V1.2 多端微信登录） ====================

export const mockUsers = [
  { id: 100, nickname: '普通用户', phone: '13600000001', shop_status: 0, is_staff: false, is_super_staff: false, shop_id: null, unionid: 'union_100', mp_openid: 'mp_100', web_openid: null, avatar: placeholder('用户', 80, 80) },
  { id: 101, nickname: '待审核商家', phone: '13600000002', shop_status: 1, is_staff: false, is_super_staff: false, shop_id: null, unionid: 'union_101', mp_openid: 'mp_101', web_openid: null, avatar: placeholder('待审', 80, 80) },
  { id: 1, nickname: '极速摩托行老板', phone: '13800138001', shop_status: 2, is_staff: false, is_super_staff: false, shop_id: 1, unionid: 'union_1', mp_openid: 'mp_1', web_openid: null, avatar: placeholder('商家', 80, 80) },
  { id: 999, nickname: '平台管理员', phone: '13999999999', shop_status: 0, is_staff: true, is_super_staff: true, shop_id: null, unionid: 'union_999', mp_openid: 'mp_999', web_openid: null, avatar: placeholder('管理', 80, 80) },
  { id: 102, nickname: '用户李四', phone: '13700000002', shop_status: 0, is_staff: false, is_super_staff: false, shop_id: null, unionid: 'union_102', mp_openid: 'mp_102', web_openid: null, avatar: placeholder('李四', 80, 80) },
]

const loginTickets = new Map()
let ticketSeq = 1

function issueToken(userId) {
  return `mock_token_${userId}_${Date.now()}`
}

function findUserByToken(token) {
  if (!token) return null
  const match = token.match(/^mock_token_(\d+)_/)
  if (!match) return null
  return mockUsers.find(u => u.id === Number(match[1])) || null
}

function sanitizeUser(u) {
  if (!u) return null
  const { unionid, mp_openid, web_openid, ...rest } = u
  return rest
}

// ==================== 模拟延迟 ====================
const delay = (ms = 300) => new Promise(resolve => setTimeout(resolve, ms))

const mockResponse = (data) => ({ code: 200, msg: 'success', data })

function getVisibleShopBikes(shopId, { cEndOnly = false, statusFilter = 0 } = {}) {
  let list = mockBikes.filter(b => b.shop_id === Number(shopId) && !b.is_deleted)
  if (cEndOnly) {
    list = list.filter(b => b.bike_status === 1 || b.bike_status === 2)
  } else if (statusFilter !== 0) {
    list = list.filter(b => b.bike_status === statusFilter)
  }
  return list.sort((a, b) => {
    const order = (s) => (s === 1 ? 0 : s === 2 ? 1 : 2)
    const diff = order(a.bike_status) - order(b.bike_status)
    if (diff !== 0) return diff
    return new Date(b.published_at || b.created_at) - new Date(a.published_at || a.created_at)
  })
}

export const mockApi = {
  // C 端不再提供全平台列表（多租户）
  async getBikeList() {
    await delay()
    return mockResponse({ list: [], total: 0 })
  },

  async getBikeDetail(id, params = {}) {
    await delay()
    const bike = mockBikes.find(b => b.id === Number(id))
    if (!bike || bike.is_deleted) return { code: 404, msg: '车辆不存在或已删除', data: null }
    if (params.shop_id && bike.shop_id !== Number(params.shop_id)) {
      return { code: 403, msg: '无权查看该商家商品', data: null }
    }
    const shop = mockShops.find(s => s.id === bike.shop_id)
    return mockResponse({ ...bike, shop })
  },

  async getShopDetail(id, params = {}) {
    await delay()
    const shop = mockShops.find(s => s.id === Number(id))
    if (!shop) return { code: 404, msg: '商家不存在', data: null }
    const statusFilter = params.status ? Number(params.status) : 0
    const bikes = getVisibleShopBikes(id, { cEndOnly: true, statusFilter })
    return mockResponse({ shop, bikes })
  },

  async getMyBikes(params = {}) {
    await delay()
    let list = mockBikes.filter(b => b.shop_id === 1 && !b.is_deleted)
    const statusFilter = params.status ? Number(params.status) : 0
    if (statusFilter !== 0) list = list.filter(b => b.bike_status === statusFilter)
    list = list.sort((a, b) => {
      const order = (s) => (s === 1 ? 0 : s === 2 ? 1 : 2)
      const diff = order(a.bike_status) - order(b.bike_status)
      if (diff !== 0) return diff
      return new Date(b.published_at || b.created_at) - new Date(a.published_at || a.created_at)
    })
    return mockResponse({ list, total: list.length })
  },

  async getMyMessageThreads(params = {}) {
    await delay()
    let list = mockMessageThreads.filter(t => t.shop_id === 1)
    if (params.status) {
      list = list.filter(t => t.thread_status === Number(params.status))
    }
    return mockResponse({ list, total: list.length })
  },

  async getMyMessages(params = {}) {
    return this.getMyMessageThreads(params)
  },

  async getUserMessageThreads(userId = 100) {
    await delay()
    const list = mockMessageThreads.filter(t => t.user_id === userId)
    return mockResponse({ list, total: list.length })
  },

  async getMessageThread(threadId) {
    await delay()
    const thread = mockMessageThreads.find(t => t.id === Number(threadId))
    if (!thread) return { code: 404, msg: '会话不存在', data: null }
    return mockResponse(thread)
  },

  async sendMessage(threadId, { content, sender_type }) {
    await delay()
    const thread = mockMessageThreads.find(t => t.id === Number(threadId))
    if (!thread) return { code: 404, msg: '会话不存在', data: null }
    const msg = {
      id: Date.now(),
      sender_type,
      content,
      created_at: new Date().toLocaleString('zh-CN', { hour12: false }),
    }
    thread.messages.push(msg)
    thread.updated_at = msg.created_at
    if (sender_type === 1) {
      thread.unread_count_shop = (thread.unread_count_shop || 0) + 1
      thread.thread_status = 1
    } else {
      thread.unread_count_user = (thread.unread_count_user || 0) + 1
      thread.thread_status = 3
    }
    return mockResponse({ message: msg, thread })
  },

  async createMessageThread({ bike_id, content, contact_phone, user_id = 100, user_name = '普通用户' }) {
    await delay()
    const bike = mockBikes.find(b => b.id === Number(bike_id))
    if (!bike) return { code: 404, msg: '车辆不存在', data: null }
    let thread = mockMessageThreads.find(t => t.bike_id === bike.id && t.user_id === user_id)
    if (thread) {
      await this.sendMessage(thread.id, { content, sender_type: 1 })
      return mockResponse(thread)
    }
    thread = {
      id: mockMessageThreads.length + 1,
      bike_id: bike.id,
      shop_id: bike.shop_id,
      user_id,
      user_name,
      bike_info: `${bike.brand} ${bike.model} ${bike.year}年`,
      thread_status: 1,
      unread_count_user: 0,
      unread_count_shop: 1,
      contact_phone: contact_phone || '',
      updated_at: new Date().toLocaleString('zh-CN', { hour12: false }),
      messages: [{ id: Date.now(), sender_type: 1, content, created_at: new Date().toLocaleString('zh-CN', { hour12: false }) }],
    }
    mockMessageThreads.push(thread)
    return mockResponse(thread)
  },

  async markThreadRead(threadId, role = 'user') {
    await delay()
    const thread = mockMessageThreads.find(t => t.id === Number(threadId))
    if (!thread) return { code: 404, msg: '会话不存在', data: null }
    if (role === 'user') thread.unread_count_user = 0
    else thread.unread_count_shop = 0
    return mockResponse(thread)
  },

  async getFavorites(favoriteIds = []) {
    await delay()
    const list = favoriteIds.map(id => {
      const bike = mockBikes.find(b => b.id === id)
      if (!bike) return { id, unavailable: true, brand: '未知', model: '车辆', is_deleted: 1 }
      return { ...bike }
    })
    return mockResponse({ list, total: list.length })
  },

  async getAllMessages() {
    await delay()
    return mockResponse({ list: mockMessageThreads, total: mockMessageThreads.length })
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
    const shopBikes = mockBikes.filter(b => b.shop_id === 1 && !b.is_deleted)
    return mockResponse({
      on_sale: shopBikes.filter(b => b.bike_status === 1).length,
      sold: shopBikes.filter(b => b.bike_status === 2).length,
      unread_messages: mockMessageThreads.filter(t => t.shop_id === 1).reduce((s, t) => s + (t.unread_count_shop || 0), 0),
      total_views: shopBikes.reduce((s, b) => s + b.view_count, 0),
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

  // ==================== 认证（V1.2） ====================

  async createLoginTicket() {
    await delay(200)
    const ticketId = `T${String(ticketSeq++).padStart(6, '0')}`
    const ticket = {
      ticket_id: ticketId,
      status: 'pending',
      qr_url: placeholder('微信扫码\n登录', 220, 220, '#ffffff', '#07c160'),
      expires_at: Date.now() + 5 * 60 * 1000,
      user_id: null,
    }
    loginTickets.set(ticketId, ticket)
    return mockResponse(ticket)
  },

  async pollLoginTicket(ticketId) {
    await delay(80)
    const ticket = loginTickets.get(ticketId)
    if (!ticket) return { code: 404, msg: '登录票据不存在', data: null }
    if (Date.now() > ticket.expires_at && ticket.status !== 'confirmed') {
      ticket.status = 'expired'
    }
    if (ticket.status === 'confirmed') {
      const user = mockUsers.find(u => u.id === ticket.user_id)
      if (!user) return { code: 500, msg: '用户不存在', data: null }
      user.web_openid = user.web_openid || `web_${user.id}`
      user.last_login_platform = 'web'
      const token = issueToken(user.id)
      loginTickets.delete(ticketId)
      return mockResponse({ status: 'confirmed', token, user: sanitizeUser(user) })
    }
    return mockResponse({ status: ticket.status })
  },

  async simulateScanLogin(ticketId, userId = 100) {
    await delay(400)
    const ticket = loginTickets.get(ticketId)
    if (!ticket) return { code: 404, msg: '登录票据不存在', data: null }
    if (ticket.status === 'expired') return { code: 410, msg: '二维码已过期', data: null }
    ticket.status = 'scanned'
    await delay(300)
    ticket.status = 'confirmed'
    ticket.user_id = Number(userId)
    return mockResponse({ ok: true })
  },

  async getUserInfo() {
    await delay(100)
    const token = localStorage.getItem('token')
    const user = findUserByToken(token)
    if (!user) return { code: 401, msg: '未登录或登录已过期', data: null }
    return mockResponse(sanitizeUser(user))
  },

  async logout() {
    await delay(100)
    return mockResponse(null)
  },

  async getAdminUsers() {
    await delay()
    return mockResponse({ list: mockUsers.map(sanitizeUser), total: mockUsers.length })
  },

  async grantStaff(userId) {
    await delay()
    const user = mockUsers.find(u => u.id === Number(userId))
    if (!user) return { code: 404, msg: '用户不存在', data: null }
    user.is_staff = true
    user.staff_granted_at = new Date().toISOString()
    return mockResponse(sanitizeUser(user))
  },

  async revokeStaff(userId) {
    await delay()
    const user = mockUsers.find(u => u.id === Number(userId))
    if (!user) return { code: 404, msg: '用户不存在', data: null }
    if (user.is_super_staff) return { code: 403, msg: '预置超级管理员不可撤销', data: null }
    user.is_staff = false
    return mockResponse(sanitizeUser(user))
  },
}

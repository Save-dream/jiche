/** 从排量字符串解析 cc 数值，如 "400cc" → 400 */
export function parseDisplacementCc(displacement) {
  if (!displacement) return null
  const match = String(displacement).match(/(\d+)/)
  return match ? Number(match[1]) : null
}

/** 排量筛选项匹配 */
export function matchDisplacement(cc, filterValue) {
  if (!filterValue) return true
  if (cc == null) return false
  if (filterValue === '150') return cc < 150
  if (filterValue === '400') return cc >= 150 && cc <= 400
  if (filterValue === '600') return cc > 400 && cc <= 600
  if (filterValue === '600+') return cc > 600
  return true
}

/** 前端车源列表筛选（商家主页 / C 端私域） */
export function applyBikeFilters(list, filters = {}) {
  let result = [...(list || [])]
  if (filters.keyword) {
    const kw = String(filters.keyword).toLowerCase()
    result = result.filter((b) =>
      `${b.brand}${b.model}`.toLowerCase().includes(kw) ||
      b.brand.toLowerCase().includes(kw) ||
      b.model.toLowerCase().includes(kw)
    )
  }
  const minPrice = Number(filters.min_price)
  if (filters.min_price !== '' && filters.min_price != null && !Number.isNaN(minPrice)) {
    result = result.filter((b) => Number(b.price) >= minPrice)
  }
  const maxPrice = Number(filters.max_price)
  if (filters.max_price !== '' && filters.max_price != null && !Number.isNaN(maxPrice)) {
    result = result.filter((b) => Number(b.price) <= maxPrice)
  }
  if (filters.can_transfer !== undefined && filters.can_transfer !== '') {
    result = result.filter((b) => b.can_transfer === (filters.can_transfer === 'true'))
  }
  if (filters.year) {
    result = result.filter((b) => b.year >= Number(filters.year))
  }
  if (filters.displacement) {
    result = result.filter((b) =>
      matchDisplacement(parseDisplacementCc(b.displacement), filters.displacement)
    )
  }
  return result
}

/** 商家域内车源排序：在售优先，同状态按上架时间倒序 */
export function sortShopBikes(list, { cEndOnly = false } = {}) {
  let filtered = (list || []).filter((b) => !b.is_deleted)
  if (cEndOnly) {
    filtered = filtered.filter((b) => b.bike_status === 1 || b.bike_status === 2)
  }
  const statusOrder = (s) => (s === 1 ? 0 : s === 2 ? 1 : 2)
  return [...filtered].sort((a, b) => {
    const diff = statusOrder(a.bike_status) - statusOrder(b.bike_status)
    if (diff !== 0) return diff
    const ta = new Date(a.published_at || a.created_at).getTime()
    const tb = new Date(b.published_at || b.created_at).getTime()
    return tb - ta
  })
}

export function getShareLink(bike) {
  const origin = typeof window !== 'undefined' ? window.location.origin : ''
  return `${origin}/bike/${bike.id}?shop_id=${bike.shop_id}`
}

export function getShopShareLink(shopId) {
  const origin = typeof window !== 'undefined' ? window.location.origin : ''
  return `${origin}/shop/${shopId}`
}

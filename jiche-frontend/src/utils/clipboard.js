/**
 * 兼容非 HTTPS（如 http://公网IP）下的复制。
 * clipboard API 仅在 secure context 可用，HTTP 下走 fallback。
 */
import { ElMessage } from 'element-plus'

export async function copyText(text, { successMsg = '已复制到剪贴板' } = {}) {
  const value = String(text || '')
  if (!value) {
    ElMessage.warning('没有可复制的内容')
    return false
  }

  try {
    if (typeof navigator !== 'undefined'
      && window.isSecureContext
      && navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(value)
      ElMessage.success(successMsg)
      return true
    }
  } catch {
    /* fall through */
  }

  try {
    const ta = document.createElement('textarea')
    ta.value = value
    ta.setAttribute('readonly', '')
    ta.style.position = 'fixed'
    ta.style.left = '-9999px'
    ta.style.top = '0'
    document.body.appendChild(ta)
    ta.focus()
    ta.select()
    ta.setSelectionRange(0, value.length)
    const ok = document.execCommand('copy')
    document.body.removeChild(ta)
    if (ok) {
      ElMessage.success(successMsg)
      return true
    }
  } catch {
    /* fall through */
  }

  ElMessage({
    type: 'warning',
    duration: 8000,
    message: `自动复制失败，请手动复制：${value}`,
  })
  return false
}

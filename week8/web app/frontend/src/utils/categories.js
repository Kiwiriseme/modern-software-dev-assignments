export const CATEGORY_COLORS = {
  '工作': '#5b7f95',
  '学习': '#5a8a6a',
  '生活': '#b08a7a',
  '想法': '#c4a05a',
}

export const CATEGORY_BG_COLORS = {
  '工作': '#e8eff4',
  '学习': '#e6f0e9',
  '生活': '#f5ede9',
  '想法': '#f9f2e3',
}

export const DEFAULT_CATEGORY_COLOR = '#8b7e6a'
export const DEFAULT_CATEGORY_BG = '#f0ede6'

export const PRESET_CATEGORIES = ['全部', '工作', '学习', '生活', '想法']

export function categoryColor(cat) {
  return CATEGORY_COLORS[cat] || DEFAULT_CATEGORY_COLOR
}

export function categoryBgColor(cat) {
  return CATEGORY_BG_COLORS[cat] || DEFAULT_CATEGORY_BG
}

export function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return ''
  return date.toISOString().split('T')[0]
}

export function formatRelativeDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return ''
  const now = new Date()
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const diff = date.getTime() - todayStart
  const days = Math.round(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天'
  if (days === 1) return '明天'
  if (days === -1) return '昨天'
  if (days < -1 && days >= -6) {
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return weekdays[date.getDay()]
  }
  return date.toISOString().split('T')[0]
}

export function getTodayDateString() {
  const d = new Date()
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function hashString(str) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
    hash = hash & hash
  }
  return Math.abs(hash)
}

export function generateCategoryColor(name) {
  const hue = hashString(name) % 360
  return `hsl(${hue}, 30%, 40%)`
}

export function generateCategoryBgColor(name) {
  const hue = hashString(name) % 360
  return `hsl(${hue}, 30%, 92%)`
}

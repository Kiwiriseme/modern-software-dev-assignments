export const CATEGORY_COLORS = {
  '工作': '#3b82f6',
  '学习': '#22c55e',
  '生活': '#a855f7',
  '想法': '#f59e0b',
}

export const DEFAULT_CATEGORY_COLOR = '#6b7280'

export const PRESET_CATEGORIES = ['全部', '工作', '学习', '生活', '想法']

export function categoryColor(cat) {
  return CATEGORY_COLORS[cat] || DEFAULT_CATEGORY_COLOR
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
  const diff = date.getTime() - new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const days = Math.round(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天'
  if (days === 1) return '明天'
  if (days === -1) return '昨天'
  return date.toISOString().split('T')[0]
}

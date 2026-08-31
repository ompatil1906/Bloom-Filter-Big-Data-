export function formatBytes(bytes) {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${units[i]}`
}

export function formatPercent(value, digits = 1) {
  return `${value.toFixed(digits)}%`
}

export function truncateUrl(url, max = 50) {
  if (url.length <= max) return url
  return url.slice(0, max - 3) + '...'
}

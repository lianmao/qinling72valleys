const BASE = import.meta.env.BASE_URL

async function getJSON(path) {
  const res = await fetch(`${BASE}data/${path}`, { cache: 'no-cache' })
  if (!res.ok) throw new Error(`${path} 载入失败 (${res.status})`)
  return res.json()
}

export const loadValleys = () => getJSON('valleys.json')
export const loadTop10 = () => getJSON('top10_details.json')

/** 状态语义：1 开放(绿) / 0 管制(红) / null 未核实(灰) */
export const STATUS_META = {
  1: { label: '开放通行', tone: 'open', dot: 'bg-emerald-600' },
  0: { label: '管制封山', tone: 'closed', dot: 'bg-red-600' },
  null: { label: '状态未核实', tone: 'unknown', dot: 'bg-slate-400' },
}
export const statusMeta = (v) => STATUS_META[v.status ?? null]

export const DASH_LEGEND = {
  yes: { label: '具备', tone: 'text-emerald-700 bg-emerald-50' },
  partial: { label: '有条件', tone: 'text-amber-700 bg-amber-50' },
  no: { label: '不具备', tone: 'text-red-700 bg-red-50' },
  unknown: { label: '待核实', tone: 'text-slate-600 bg-slate-100' },
}

/** 营地类型 → 中文标签（top10_details.json 的 around.campsites[].type） */
export const CAMPSITE_TYPE = { commercial: '收费营地', wild: '野营地', rv: '房车营地' }

/** 列表筛选：全部条件彼此取交集，条件为空即放行 */
export function filterValleys(list, { q = '', city = '', status = '', top10Only = false } = {}) {
  const needle = q.trim().toLowerCase()
  return list.filter((v) => {
    if (city && v.city !== city) return false
    if (status === 'open' && v.status !== 1) return false
    if (status === 'closed' && v.status !== 0) return false
    if (status === 'unknown' && v.status !== null) return false
    if (top10Only && !v.is_top10) return false
    if (!needle) return true
    return `${v.name}${v.district}${v.city}${v.summary}`.toLowerCase().includes(needle)
  })
}

export function cityCounts(list) {
  return list.reduce((acc, v) => ({ ...acc, [v.city]: (acc[v.city] || 0) + 1 }), {})
}

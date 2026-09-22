/**
 * 高德 JS API v2.0 懒加载 + 降级。
 * 未配置 VITE_AMAP_KEY 时不抛错：hasKey() 为 false，界面走纯列表模式。
 */
const KEY = import.meta.env.VITE_AMAP_KEY || ''
const SECURITY = import.meta.env.VITE_AMAP_SECURITY || ''

export const hasKey = () => Boolean(KEY)

let pending = null

export function loadAMap() {
  if (pending) return pending
  pending = new Promise((resolve, reject) => {
    if (window.AMap) return resolve(window.AMap)
    if (!KEY) return reject(new Error('未配置高德 Key'))
    window._AMapSecurityConfig = { securityJsCode: SECURITY }
    const s = document.createElement('script')
    s.src = `https://webapi.amap.com/maps?v=2.0&key=${KEY}&plugin=AMap.MarkerCluster`
    s.async = true
    s.onload = () => (window.AMap ? resolve(window.AMap) : reject(new Error('高德 SDK 未挂载')))
    s.onerror = () => reject(new Error('高德 SDK 加载失败（网络或 Key 域名白名单）'))
    document.head.appendChild(s)
  })
  return pending
}

const markerClass = (v) =>
  `marker marker--${v.status === 1 ? 'open' : v.status === 0 ? 'closed' : 'unknown'}` +
  (v.is_top10 ? ' marker--top' : '')

const markerHTML = (v) =>
  `<div class="${markerClass(v)}" title="${v.name}"><span class="marker__ring"></span><span class="marker__dot"></span></div>`

/** 初始化地图：全部点交给 MarkerCluster，近景自动散开 */
export async function initMap(el, valleys, onPick) {
  const AMap = await loadAMap()
  const map = new AMap.Map(el, {
    zoom: 9,
    center: [108.9, 34.15],
    viewMode: '2D',
    resizeEnable: true,
    mapStyle: 'amap://styles/whitesmoke',
  })
  const markers = []
  for (const v of valleys) {
    const m = new AMap.Marker({
      position: [v.lng, v.lat],
      content: markerHTML(v),
      offset: new AMap.Pixel(-11, -11),
      extData: { id: v.id },
      zIndex: v.is_top10 ? 120 : 100,
    })
    m.on('click', () => onPick?.(v))
    markers.push(m)
  }
  const cluster = new AMap.MarkerCluster(map, markers, {
    gridSize: 60,
    maxZoom: 14,
    renderClusterMarker: (ctx) => {
      const n = ctx.count
      ctx.marker.setContent(
        `<div style="width:34px;height:34px;border-radius:9999px;background:#0f2a1dcc;color:#fff;
          display:grid;place-items:center;font:600 13px/1 system-ui;border:2px solid #fff;
          box-shadow:0 2px 8px rgb(0 0 0 / .3)">${n}</div>`,
      )
    },
  })
  map.on('complete', () => map.setFitView(null, false, [40, 40, 40, 40]))
  return { map, markers, cluster }
}

/** 行政区聚焦：只对目标城市的点做 fitView */
export function focusCity(handle, valleys, city) {
  if (!handle) return
  const target = city ? handle.markers.filter((_, i) => valleys[i]?.city === city) : handle.markers
  if (target.length) handle.map.setFitView(target, false, [60, 60, 60, 60])
}

export function focusValley(handle, v, zoom = 14) {
  handle?.map.setZoomAndCenter(zoom, [v.lng, v.lat])
}

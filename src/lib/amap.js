/**
 * 高德 JS API v2.0 懒加载 + 打点聚合 + 降级。
 *
 * ★ v2.0 的 AMap.MarkerCluster(map, data, options) 接的是**点数据数组**（每项需 lnglat），
 *   由插件自己创建 Marker，用 renderMarker/renderClusterMarker 定制；
 *   v1 的 MarkerClusterer(map, markers, ...) 才吃 Marker 实例。
 *   传 Marker 实例进 v2.0 不会报错，但也一个点都不渲染 —— 实测踩过。
 *
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
    s.onerror = () => reject(new Error('高德 SDK 加载失败（网络、Key 类型或域名白名单）'))
    document.head.appendChild(s)
  })
  return pending
}

const tone = (v) => (v.status === 1 ? 'open' : v.status === 0 ? 'closed' : 'unknown')

const markerHTML = (v) =>
  `<div class="marker marker--${tone(v)}${v.is_top10 ? ' marker--top' : ''}" title="${v.name}">` +
  `<span class="marker__ring"></span><span class="marker__dot"></span></div>`

const bubbleHTML = (count) =>
  `<div style="width:34px;height:34px;border-radius:9999px;background:#0f2a1dcc;color:#fff;display:grid;
    place-items:center;font:600 13px/1 system-ui;border:2px solid #fff;box-shadow:0 2px 8px rgb(0 0 0 / .3)">${count}</div>`

const boundsOf = (AMap, list) =>
  new AMap.Bounds(
    [Math.min(...list.map((v) => v.lng)), Math.min(...list.map((v) => v.lat))],
    [Math.max(...list.map((v) => v.lng)), Math.max(...list.map((v) => v.lat))],
  )

/** ★ setBounds 只认 (bounds, immediately)；传 duration/padding 数组会让视野变成 NaN —— 实测踩过 */
const fitBounds = (map, AMap, list) => {
  if (list.length) map.setBounds(boundsOf(AMap, list), true)
}

/** 初始化地图：远景时点自动聚合为数字泡，近景散开为呼吸灯 Marker */
export async function initMap(el, valleys, onPick) {
  const AMap = await loadAMap()
  const map = new AMap.Map(el, {
    zoom: 9,
    center: [108.9, 34.15],
    viewMode: '2D',
    resizeEnable: true,
    mapStyle: 'amap://styles/whitesmoke',
  })
  const points = valleys.map((v) => ({ ...v, lnglat: [v.lng, v.lat] }))
  const cluster = new AMap.MarkerCluster(map, points, {
    gridSize: 60,
    maxZoom: 14,
    renderMarker: (ctx) => {
      ctx.marker.setContent(markerHTML(ctx.data))
      ctx.marker.setOffset(new AMap.Pixel(-11, -11))
      ctx.marker.on('click', () => onPick?.(ctx.data))
    },
    renderClusterMarker: (ctx) => ctx.marker.setContent(bubbleHTML(ctx.count)),
  })
  if (valleys.length) fitBounds(map, AMap, valleys)
  return { AMap, map, cluster }
}

/** 行政区聚焦：按该市点集重新框视野，聚合泡随之更新 */
export function focusCity(handle, valleys, city) {
  const { AMap, map } = handle || {}
  if (!map) return
  fitBounds(map, AMap, city ? valleys.filter((v) => v.city === city) : valleys)
}

/** ★ 同样只认 immediately=true：本构建里带动画的调用是空操作（zoom 不动、center 不动） */
export function focusValley(handle, v, zoom = 14) {
  handle?.map.setZoomAndCenter(zoom, [v.lng, v.lat], true)
}

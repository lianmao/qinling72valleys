/**
 * 高德导航唤起。
 * 关键点（PRD 未覆盖，实测坑）：
 * - uri.amap.com 必须带 callnative=1 才会在移动端尝试唤起 App，coordinate=gaode 声明是 GCJ-02；
 * - amapuri:// scheme 在微信内置浏览器里会被拦截 → 微信内一律走 Web 版并给出「在浏览器打开」提示。
 */
export const isWechat = () => /MicroMessenger/i.test(navigator.userAgent)
export const isMobile = () => /Android|iPhone|iPad|iPod|HarmonyOS|Mobile/i.test(navigator.userAgent)

const q = encodeURIComponent

export const appUri = (v) =>
  `amapuri://route/plan/?dlat=${v.lat}&dlon=${v.lng}&dname=${q(v.name)}&dev=0&t=0`

export const webUri = (v) =>
  `https://uri.amap.com/navigation?to=${v.lng},${v.lat},${q(v.name)}` +
  `&mode=car&policy=1&src=qinling72valleys&coordinate=gaode&callnative=1`

/** 返回 { label, href, target, hint } —— 交给按钮渲染，避免组件里写 UA 分支 */
export function navPlan(v) {
  const name = `${v.name}峪口`
  if (isWechat()) {
    return {
      label: '高德导航（网页版）',
      href: webUri(v),
      target: '_blank',
      hint: '微信内无法直接唤起高德 App：可点右上角「···」→ 在浏览器中打开，或用此网页版路线。',
    }
  }
  if (isMobile()) {
    return { label: '开始导航', href: appUri(v), target: '_self', hint: '将唤起高德地图 App 规划自驾路线。' }
  }
  return { label: '高德网页导航', href: webUri(v), target: '_blank', hint: 'PC 端打开高德网页版路线规划，不消耗额外的接口配额。' }
}

export const searchInAmap = (name) =>
  `https://uri.amap.com/search?keyword=${q(name)}&src=qinling72valleys`

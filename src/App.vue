<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { loadValleys, loadTop10, filterValleys, cityCounts, statusMeta } from './lib/data'
import MapView from './components/MapView.vue'
import ValleyDetail from './components/ValleyDetail.vue'

const valleys = ref([])
const meta = ref(null)
const details = ref({})
const fatal = ref('')
const loading = ref(true)

const q = ref('')
const city = ref('')
const status = ref('')
const top10Only = ref(false)
const selectedId = ref('')

const shown = computed(() => filterValleys(valleys.value, { q: q.value, city: city.value, status: status.value, top10Only: top10Only.value }))
const counts = computed(() => cityCounts(valleys.value))
const selected = computed(() => valleys.value.find((v) => v.id === selectedId.value) || null)
const selectedDetail = computed(() => details.value[selected.value?.id] || null)

const CITIES = ['西安市', '渭南市', '宝鸡市']
const STATUSES = [
  ['', '全部状态'],
  ['open', '开放'],
  ['closed', '管制'],
  ['unknown', '未核实'],
]

function syncHash() {
  const m = /^#\/v\/(VALLEY_\d+)/.exec(location.hash)
  selectedId.value = m ? m[1] : ''
}
function pick(v) {
  location.hash = `#/v/${v.id}`
}
function close() {
  if (location.hash) history.replaceState(null, '', location.pathname + location.search)
  selectedId.value = ''
}

onMounted(async () => {
  window.addEventListener('hashchange', syncHash)
  syncHash()
  try {
    const [v, d] = await Promise.all([loadValleys(), loadTop10()])
    valleys.value = v.valleys
    meta.value = v
    details.value = d.valleys
  } catch (e) {
    fatal.value = e.message
  } finally {
    loading.value = false
  }
})
onBeforeUnmount(() => window.removeEventListener('hashchange', syncHash))
</script>

<template>
  <div class="min-h-dvh">
    <header class="sticky top-0 z-20 border-b border-stone-200 bg-ridge-50/95 backdrop-blur">
      <div class="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3">
        <div class="min-w-0">
          <h1 class="truncate text-base font-semibold leading-tight">秦岭七十二峪</h1>
          <p class="truncate text-[11px] text-stone-500">露营 · 徒步 · 农家乐 · 安全状态</p>
        </div>
        <p v-if="meta" class="shrink-0 text-right text-[10px] leading-tight text-stone-400">
          数据版本<br /><span class="tabular-nums">{{ meta.data_version }}</span>
        </p>
      </div>
    </header>

    <div v-if="loading" class="mx-auto max-w-6xl px-4 py-16 text-center text-sm text-stone-500">加载数据…</div>
    <div v-else-if="fatal" class="mx-auto max-w-6xl px-4 py-16 text-center text-sm text-red-700">
      数据载入失败：{{ fatal }}
    </div>

    <main v-else class="mx-auto max-w-6xl px-4 py-4">
      <p class="mb-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-[11px] leading-relaxed text-amber-900">
        名录与坐标为未核实初稿（{{ meta.counts.needs_review }} 条已标待核），
        配套与状态信息同样待核；<strong class="font-semibold">请勿将本站坐标作为导航依据</strong>。
      </p>

      <!-- 筛选 -->
      <div class="space-y-2.5">
        <div class="-mx-1 flex gap-1.5 overflow-x-auto px-1 pb-1">
          <button
            class="min-h-11 shrink-0 rounded-lg px-3 text-sm transition-colors"
            :class="city === '' ? 'bg-ridge-900 text-white' : 'bg-white text-stone-700 ring-1 ring-stone-200'"
            @click="city = ''"
          >
            全景 {{ valleys.length }}
          </button>
          <button
            v-for="c in CITIES"
            :key="c"
            class="min-h-11 shrink-0 rounded-lg px-3 text-sm transition-colors"
            :class="city === c ? 'bg-ridge-900 text-white' : 'bg-white text-stone-700 ring-1 ring-stone-200'"
            @click="city = c"
          >
            {{ c.replace('市', '') }} {{ counts[c] || 0 }}
          </button>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <input
            v-model="q"
            type="search"
            placeholder="搜索峪名 / 区县 / 特色"
            class="min-h-11 min-w-0 flex-1 rounded-lg border border-stone-200 bg-white px-3 text-sm outline-none focus:border-ridge-900"
          />
          <select
            v-model="status"
            class="min-h-11 rounded-lg border border-stone-200 bg-white px-2 text-sm"
            aria-label="按开放状态筛选"
          >
            <option v-for="[val, label] in STATUSES" :key="val || 'all'" :value="val">{{ label }}</option>
          </select>
          <label class="flex min-h-11 cursor-pointer items-center gap-1.5 rounded-lg border border-stone-200 bg-white px-3 text-sm">
            <input v-model="top10Only" type="checkbox" class="h-4 w-4 accent-emerald-700" />首批核心
          </label>
        </div>

        <p class="text-[11px] text-stone-500">
          命中 <span class="tabular-nums font-medium text-stone-700">{{ shown.length }}</span> 个峪口
          <span v-if="meta.counts.needs_review" class="ml-2">· 含 {{ meta.counts.needs_review }} 条待核条目</span>
        </p>
      </div>

      <div class="mt-3 grid gap-4 lg:grid-cols-[minmax(0,400px)_minmax(0,1fr)]">
        <!-- 列表 -->
        <ul class="space-y-1.5 lg:max-h-[calc(100dvh-15rem)] lg:overflow-y-auto lg:pr-1">
          <li v-for="v in shown" :key="v.id">
            <button
              class="w-full rounded-lg border bg-white px-3 py-2.5 text-left transition-colors hover:border-ridge-900"
              :class="selectedId === v.id ? 'border-ridge-900 ring-1 ring-ridge-900' : 'border-stone-200'"
              @click="pick(v)"
            >
              <p class="flex items-center gap-2 text-sm font-medium leading-tight">
                <i class="h-2 w-2 shrink-0 rounded-full" :class="statusMeta(v).dot"></i>
                <span>{{ v.name }}</span>
                <span v-if="v.is_top10" class="text-[10px] font-normal text-amber-700">★{{ v.top10_rank }}</span>
                <span v-if="v.needs_review" class="ml-auto shrink-0 text-[10px] font-normal text-stone-400">待核</span>
              </p>
              <p class="mt-1 line-clamp-2 text-[11px] leading-snug text-stone-500">{{ v.summary }}</p>
              <p class="mt-1 text-[10px] text-stone-400">{{ v.city }} · {{ v.district }}</p>
            </button>
          </li>
          <li v-if="!shown.length" class="rounded-lg border border-dashed border-stone-300 px-3 py-8 text-center text-xs text-stone-500">
            没有匹配的峪口，试试放宽筛选
          </li>
        </ul>

        <!-- 地图 -->
        <div class="lg:sticky lg:top-20 lg:h-[calc(100dvh-15rem)]">
          <MapView :valleys="valleys" :city="city" :selected="selected" @pick="pick" />
        </div>
      </div>

      <footer class="mt-8 space-y-2 border-t border-stone-200 pt-4 text-[11px] leading-relaxed text-stone-500">
        <p>倡导 LNT 无痕山林：带走全部垃圾，不砍伐、不投喂、不占用河道扎营。</p>
        <p>免责：秦岭山区气候多变，未开发野径存在滑坡、山洪、失联风险。本站信息仅作规划参考，进山前请以属地政府与应急管理部门最新通告为准，并遵守封山管制禁令。</p>
        <p v-if="meta">数据来源：{{ meta.source_note }}（坐标系 {{ meta.coordinate_system }}）</p>
      </footer>
    </main>

    <!-- 详情：桌面右侧抽屉 / 移动底部抽屉 -->
    <div v-if="selected" class="fixed inset-0 z-30 flex justify-end bg-stone-900/30" @click.self="close">
      <div class="h-full w-full max-w-md shadow-xl max-lg:mt-auto max-lg:h-[82dvh] max-lg:rounded-t-2xl max-lg:overflow-hidden">
        <ValleyDetail :valley="selected" :detail="selectedDetail" @close="close" />
      </div>
    </div>
  </div>
</template>

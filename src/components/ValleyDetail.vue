<script setup>
import { computed } from 'vue'
import { statusMeta, DASH_LEGEND, CAMPSITE_TYPE } from '../lib/data'
import { navPlan, searchInAmap } from '../lib/nav'

const props = defineProps({
  valley: { type: Object, required: true },
  detail: { type: Object, default: null },
})
const emit = defineEmits(['close'])

const plan = computed(() => navPlan(props.valley))
const status = computed(() => statusMeta(props.valley))
const DIMS = [
  ['overnight', '可否过夜', '🏕'],
  ['water', '水源', '💧'],
  ['vehicle', '车辆直达', '🚗'],
  ['toilet', '公共洗手间', '🚻'],
]

/** 三类周边清单：同一套渲染，省掉三份重复模板 */
const AROUND = computed(() => {
  const a = props.detail?.around || {}
  return [
    { key: 'campsites', label: '周边露营地', items: a.campsites, pill: (i) => CAMPSITE_TYPE[i.type] || '营地' },
    { key: 'family_spots', label: '周边亲子游玩景点', items: a.family_spots, pill: () => '亲子' },
    { key: 'photo_spots', label: '网红打卡点', items: a.photo_spots, pill: () => '机位' },
  ].filter((s) => s.items?.length)
})
</script>

<template>
  <aside class="flex h-full flex-col bg-white">
    <header class="sticky top-0 z-10 border-b border-stone-200 bg-white/95 px-4 py-3 backdrop-blur">
      <div class="flex items-start justify-between gap-3">
        <div>
          <h2 class="text-lg font-semibold leading-tight">
            {{ valley.name }}
            <span v-if="valley.is_top10" class="ml-1 align-middle text-[11px] font-medium text-amber-700">★ 首批核心</span>
          </h2>
          <p class="mt-0.5 text-xs text-stone-500">
            {{ valley.city }} · {{ valley.district }}
            <span class="ml-2 tabular-nums">{{ valley.lng }}, {{ valley.lat }}</span>
          </p>
        </div>
        <button
          class="min-h-11 min-w-11 shrink-0 rounded-lg px-3 text-sm text-stone-500 hover:bg-stone-100"
          aria-label="关闭详情"
          @click="emit('close')"
        >
          关闭
        </button>
      </div>
      <p class="mt-2 inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-1 text-[11px]">
        <i class="h-2 w-2 rounded-full" :class="status.dot"></i>{{ status.label }}
        <span v-if="valley.status_reason" class="text-stone-500">· {{ valley.status_reason }}</span>
      </p>
    </header>

    <div class="flex-1 space-y-4 overflow-y-auto px-4 py-4 pb-safe">
      <p v-if="valley.summary" class="text-sm leading-relaxed text-stone-700">{{ valley.summary }}</p>

      <div class="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2.5">
        <p class="text-xs font-medium text-amber-900">坐标与配套信息为初稿，未经核实</p>
        <p class="mt-1 text-[11px] leading-relaxed text-amber-800">
          来源：{{ valley.source }}（confidence={{ valley.confidence }}）。导航前请以实际路口标识为准，
          封山/开放状态以属地政府与应急管理部门通告为准。
        </p>
      </div>

      <p
        v-if="valley.needs_review && valley.review_notes?.length"
        class="rounded-lg border border-stone-200 bg-stone-50 px-3 py-2 text-[11px] text-stone-600"
      >
        待核项：{{ valley.review_notes.join('；') }}
      </p>

      <section v-if="detail">
        <h3 class="mb-2 text-sm font-semibold">露营配套看板</h3>
        <div class="grid grid-cols-2 gap-2">
          <div
            v-for="[key, label, icon] in DIMS"
            :key="key"
            class="rounded-lg border border-stone-200 p-2.5"
          >
            <p class="flex items-center justify-between text-[11px] text-stone-500">
              <span>{{ icon }} {{ label }}</span>
              <span
                class="rounded px-1.5 py-0.5 text-[10px] font-medium"
                :class="DASH_LEGEND[detail.dashboard[key].state]?.tone"
              >
                {{ DASH_LEGEND[detail.dashboard[key].state]?.label }}
              </span>
            </p>
            <p class="mt-1.5 text-xs leading-snug text-stone-700">{{ detail.dashboard[key].text }}</p>
          </div>
        </div>
      </section>

      <p
        v-if="detail?.flood_risk"
        class="rounded-lg border-l-4 border-red-500 bg-red-50 px-3 py-2.5 text-xs leading-relaxed text-red-900"
      >
        <strong class="font-semibold">⚠️ 防汛安全警示：</strong>{{ detail.flood_warning }}<br />
        禁止河滩夜宿。暴雨后 24 小时内请勿进入沟谷。
      </p>

      <p
        v-else-if="detail"
        class="rounded-lg border border-stone-200 bg-stone-50 px-3 py-2 text-[11px] leading-relaxed text-stone-600"
      >
        本峪未标注河滩山洪点，但不等于无风险：秦岭山区汛期天气突变，进山前请查当日气象预警。
      </p>

      <section v-if="detail?.foods?.length">
        <h3 class="mb-2 text-sm font-semibold">在地美食</h3>
        <p class="flex flex-wrap gap-1.5">
          <span v-for="f in detail.foods" :key="f" class="rounded-md bg-ridge-50 px-2 py-1 text-xs text-stone-700">{{ f }}</span>
        </p>
      </section>

      <section v-if="detail?.agritainment?.length">
        <h3 class="mb-2 text-sm font-semibold">周边农家乐</h3>
        <ul class="divide-y divide-stone-100 rounded-lg border border-stone-200">
          <li v-for="s in detail.agritainment" :key="s.name" class="px-3 py-2.5">
            <p class="text-sm text-stone-800">{{ s.name }}</p>
            <p class="mt-0.5 text-[11px] text-stone-500">{{ s.tag }}</p>
          </li>
        </ul>
        <p class="mt-2 text-[11px] leading-relaxed text-stone-500">
          本站不收录联系电话与微信。到店前请在高德地图搜索店名确认营业与位置，
          名单为初稿，未经核实，不构成推荐。
        </p>
      </section>

      <section v-else class="rounded-lg border border-dashed border-stone-300 px-3 py-3 text-[11px] leading-relaxed text-stone-500">
        该峪尚未收录深度攻略（首批 10 个核心峪以外）。名录与坐标同样待核实。
      </section>

      <section v-for="s in AROUND" :key="s.key">
        <h3 class="mb-2 text-sm font-semibold">{{ s.label }}</h3>
        <ul class="divide-y divide-stone-100 rounded-lg border border-stone-200">
          <li v-for="i in s.items" :key="i.name" class="px-3 py-2.5">
            <p class="flex flex-wrap items-center gap-2 text-sm text-stone-800">
              <span class="rounded bg-ridge-50 px-1.5 py-0.5 text-[10px] font-medium text-stone-600">{{ s.pill(i) }}</span>
              {{ i.name }}
            </p>
            <p v-if="i.note" class="mt-1 text-[11px] leading-relaxed text-stone-500">{{ i.note }}</p>
            <p v-if="i.warning" class="mt-1 text-[11px] leading-relaxed text-red-700">⚠ {{ i.warning }}</p>
          </li>
        </ul>
        <p v-if="s.key === 'campsites'" class="mt-2 text-[11px] leading-relaxed text-stone-500">
          野营地一律适用无痕山林：不留垃圾、不生明火、不占河道；收费营地的开放与收费以现场为准。
        </p>
        <p v-else-if="s.key === 'photo_spots'" class="mt-2 text-[11px] leading-relaxed text-stone-500">
          打卡点为机位说明，未核实、不承诺拍摄效果。请勿为取景进入未开放区域或临崖边缘，禁止跨越护栏、攀爬文保石刻与涉水站位。
        </p>
      </section>

      <section class="space-y-2">
        <h3 class="text-sm font-semibold">出行</h3>
        <a
          :href="plan.href"
          :target="plan.target"
          rel="noopener"
          class="flex min-h-11 items-center justify-center rounded-lg bg-ridge-900 px-4 text-sm font-medium text-white"
        >
          {{ plan.label }}
        </a>
        <p class="text-[11px] leading-relaxed text-stone-500">{{ plan.hint }}</p>
        <a
          v-for="s in detail?.agritainment || []"
          :key="s.name"
          :href="searchInAmap(s.name)"
          target="_blank"
          rel="noopener"
          class="block min-h-11 py-2 text-xs text-emerald-800 underline underline-offset-2"
        >
          在高德搜索「{{ s.name }}」
        </a>
      </section>
    </div>
  </aside>
</template>

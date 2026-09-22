<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { initMap, focusCity, focusValley, hasKey } from '../lib/amap'

const props = defineProps({
  valleys: { type: Array, required: true },
  city: { type: String, default: '' },
  selected: { type: Object, default: null },
})
const emit = defineEmits(['pick'])

const el = ref(null)
const handle = ref(null)
const error = ref('')
const loading = ref(true)
let cancelled = false

onMounted(async () => {
  if (!hasKey()) {
    loading.value = false
    error.value = 'NO_KEY'
    return
  }
  try {
    const h = await initMap(el.value, props.valleys, (v) => emit('pick', v))
    if (cancelled) return
    handle.value = h
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  cancelled = true
  handle.value?.map?.destroy?.()
})

watch(() => props.city, (c) => focusCity(handle.value, props.valleys, c))
watch(
  () => props.selected?.id,
  () => {
    if (props.selected && handle.value) focusValley(handle.value, props.selected)
  },
)
</script>

<template>
  <div class="relative h-full min-h-[320px] overflow-hidden rounded-xl border border-stone-200 bg-white">
    <div ref="el" class="h-full w-full"></div>

    <div v-if="loading" class="absolute inset-0 grid place-items-center bg-white/80 text-sm text-stone-500">
      地图加载中…
    </div>

    <div v-else-if="error" class="absolute inset-0 grid place-items-center bg-ridge-50 p-6">
      <div class="max-w-sm space-y-2 text-center">
        <p class="text-sm font-semibold text-stone-700">
          {{ error === 'NO_KEY' ? '地图未启用' : '地图加载失败' }}
        </p>
        <p v-if="error === 'NO_KEY'" class="text-xs leading-relaxed text-stone-500">
          未配置高德 Key（构建变量 <code>VITE_AMAP_KEY</code>）。列表、筛选与导航链接不受影响，可直接使用。
        </p>
        <p v-else class="text-xs leading-relaxed text-stone-500">{{ error }}</p>
      </div>
    </div>

    <div
      v-else
      class="pointer-events-none absolute bottom-2 left-2 rounded-lg bg-white/90 px-2.5 py-1.5 text-[11px] leading-tight text-stone-600 shadow-sm"
    >
      <span class="mr-2"><i class="inline-block h-2 w-2 rounded-full bg-emerald-600"></i> 开放</span>
      <span class="mr-2"><i class="inline-block h-2 w-2 rounded-full bg-red-600"></i> 管制封山</span>
      <span><i class="inline-block h-2 w-2 rounded-full bg-slate-400"></i> 未核实</span>
    </div>
  </div>
</template>

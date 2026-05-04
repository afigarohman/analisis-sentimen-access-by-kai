<script setup lang="ts">
import { computed } from 'vue'

import DashboardCardShell, {
  type DashboardSpotlight,
} from '@/components/dashboard/DashboardCardShell.vue'

function formatNumber(value: number | string) {
  if (typeof value === 'number') return value.toLocaleString()
  return value
}

export type { DashboardSpotlight }

const props = defineProps<{
  title: string
  value: number | string
  percent?: number | null
  trend?: 'up' | 'down' | 'neutral'
  subtitle: string
  /** Empat nilai mini “candle” mengikuti data (tinggi relatif). */
  candles: number[]
  icon?: 'total' | 'positive' | 'neutral' | 'negative' | 'rating'
  /** Posisi sorot lampu di kartu (variasi antar KPI). */
  spotlight?: DashboardSpotlight
}>()

const trendTone = computed(() => {
  if (props.trend === 'up') {
    return {
      pill: 'bg-emerald-500/15 text-emerald-200 ring-emerald-400/25',
      dot: 'bg-emerald-400',
    }
  }
  if (props.trend === 'down') {
    return {
      pill: 'bg-rose-500/15 text-rose-200 ring-rose-400/25',
      dot: 'bg-rose-400',
    }
  }
  return {
    pill: 'bg-white/10 text-slate-200 ring-white/10',
    dot: 'bg-slate-300/70',
  }
})

const percentLabel = computed(() => {
  const p = props.percent
  if (p === null || p === undefined) return null
  if (!Number.isFinite(p)) return null
  return `${Math.round(p * 10) / 10}%`
})

const trendArrow = computed(() => {
  if (props.trend === 'up') return 'up'
  if (props.trend === 'down') return 'down'
  return 'flat'
})

const four = computed(() => {
  const raw = (props.candles ?? []).map((n) => Number(n) || 0)
  const out = [...raw]
  while (out.length < 4) out.unshift(0)
  return out.slice(-4)
})

const candleHeights = computed(() => {
  const s = four.value
  const max = Math.max(...s, 1)
  // chart area ~56px tall for candles
  return s.map((x) => Math.max(6, Math.round((x / max) * 56)))
})
</script>

<template>
  <DashboardCardShell
    :variant="spotlight ?? 'tl'"
    class="flex h-[198px] w-full flex-col p-5"
  >
    <div class="flex min-h-0 flex-1 items-start justify-between gap-3">
      <div class="min-w-0">
        <div class="flex items-center gap-3">
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white/[0.06] ring-1 ring-white/[0.08]"
          >
            <svg
              v-if="icon === 'total'"
              viewBox="0 0 24 24"
              class="h-5 w-5 text-white/90"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 7h10M7 12h10M7 17h6" />
            </svg>
            <svg
              v-else-if="icon === 'positive'"
              viewBox="0 0 24 24"
              class="h-5 w-5 text-white/90"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-5" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 22c5 0 9-4 9-9 0-5-4-9-9-9S3 8 3 13c0 5 4 9 9 9z" />
            </svg>
            <svg
              v-else-if="icon === 'neutral'"
              viewBox="0 0 24 24"
              class="h-5 w-5 text-white/90"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 15h8" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 22c5 0 9-4 9-9 0-5-4-9-9-9S3 8 3 13c0 5 4 9 9 9z" />
            </svg>
            <svg
              v-else-if="icon === 'negative'"
              viewBox="0 0 24 24"
              class="h-5 w-5 text-white/90"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 9l6 6M15 9l-6 6" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 22c5 0 9-4 9-9 0-5-4-9-9-9S3 8 3 13c0 5 4 9 9 9z" />
            </svg>
            <svg
              v-else-if="icon === 'rating'"
              viewBox="0 0 24 24"
              class="h-5 w-5 text-white/90"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 17.27l-5.18 3.04 1.64-5.81L3 9.24l5.9-.5L12 3l3.1 5.74 5.9.5-5.46 5.26 1.64 5.81z" />
            </svg>
            <svg
              v-else
              viewBox="0 0 24 24"
              class="h-5 w-5 text-white/90"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 19V5m0 14h16" />
            </svg>
          </div>

          <p class="text-xs font-semibold tracking-wide text-slate-300/90">
            {{ title }}
          </p>
        </div>

        <p class="mt-2 text-2xl font-extrabold leading-none tracking-tight text-white">
          {{ formatNumber(value) }}
        </p>

        <div class="mt-2 flex items-center gap-2">
          <span
            v-if="percentLabel"
            class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold ring-1"
            :class="trendTone.pill"
          >
            <svg
              v-if="trendArrow === 'up'"
              viewBox="0 0 24 24"
              class="h-3.5 w-3.5"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 5l6 6M12 5L6 11" />
            </svg>
            <svg
              v-else-if="trendArrow === 'down'"
              viewBox="0 0 24 24"
              class="h-3.5 w-3.5"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l6-6M12 19l-6-6" />
            </svg>
            <span class="inline-block h-1.5 w-1.5 rounded-full" :class="trendTone.dot" />
            {{ percentLabel }}
          </span>
          <span
            v-else
            class="inline-flex items-center gap-1.5 rounded-full bg-white/[0.06] px-2.5 py-1 text-[11px] font-semibold text-slate-200 ring-1 ring-white/[0.08]"
          >
            <span class="inline-block h-1.5 w-1.5 rounded-full bg-slate-400/70" />
            –
          </span>
        </div>

        <p class="mt-2 line-clamp-2 text-xs leading-snug text-slate-400">
          {{ subtitle }}
        </p>
      </div>

      <!-- 4 candlesticks (pill bars), data-driven -->
      <div class="relative flex shrink-0 flex-col justify-end pb-0.5">
        <div class="flex h-14 items-end justify-end gap-2">
          <div
            v-for="(h, idx) in candleHeights"
            :key="idx"
            class="w-2.5 rounded-full bg-gradient-to-t from-purple-500/35 via-fuchsia-400/65 to-purple-200/80 ring-1 ring-white/[0.10]"
            :style="{ height: `${h}px` }"
            :title="`Periode ${idx + 1}: ${four[idx]}`"
          />
        </div>
      </div>
    </div>
  </DashboardCardShell>
</template>

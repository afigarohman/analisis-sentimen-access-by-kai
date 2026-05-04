<script setup lang="ts">
import { computed } from 'vue'
import { Radar } from 'vue-chartjs'
import type { ChartOptions } from 'chart.js'

import type { AspectDistributionItem } from '@/api/dashboard'
import DashboardCardShell, {
  type DashboardSpotlight,
} from '@/components/dashboard/DashboardCardShell.vue'

const props = defineProps<{
  items: AspectDistributionItem[]
  spotlight?: DashboardSpotlight
}>()

export type AspectSpotlight = DashboardSpotlight

const ordered = computed(() => {
  const out = [...props.items]
    .map((x) => ({ aspect: x.aspect, total: Number(x.total ?? 0) }))
    .filter((x) => x.total > 0)
    .sort((a, b) => b.total - a.total)
  return out
})

const total = computed(() => ordered.value.reduce((acc, x) => acc + x.total, 0))

function pct(v: number): number {
  const t = total.value
  if (!t) return 0
  return Math.round((v / t) * 100)
}

const top = computed(() => {
  const first = ordered.value[0]
  if (!first) return null
  return { aspect: first.aspect, percent: pct(first.total) }
})

const radarLabels = computed(() => ordered.value.slice(0, 6).map((x) => x.aspect))
const radarValues = computed(() => ordered.value.slice(0, 6).map((x) => pct(x.total)))

const radarData = computed(() => ({
  labels: radarLabels.value,
  datasets: [
    {
      label: 'Aspek (%)',
      data: radarValues.value,
      borderColor: 'rgba(217, 70, 239, 0.9)', // fuchsia-ish
      backgroundColor: 'rgba(168, 85, 247, 0.18)', // purple glow fill
      pointBackgroundColor: 'rgba(217, 70, 239, 0.95)',
      pointBorderColor: 'rgba(255,255,255,0.25)',
      pointRadius: 2,
      borderWidth: 2,
    },
  ],
}))

const radarOptions: ChartOptions<'radar'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { enabled: true },
  },
  scales: {
    r: {
      angleLines: { color: 'rgba(255,255,255,0.10)' },
      grid: { color: 'rgba(255,255,255,0.08)' },
      pointLabels: { color: 'rgba(226,232,240,0.70)', font: { size: 10 } },
      ticks: { display: false },
      suggestedMin: 0,
      suggestedMax: 100,
    },
  },
}

const listRows = computed(() =>
  ordered.value.slice(0, 6).map((x) => ({ ...x, percent: pct(x.total) })),
)
</script>

<template>
  <DashboardCardShell tag="section" :variant="spotlight ?? 'bl'" class="p-6">
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <!-- left content -->
      <div>
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0">
            <p class="text-sm font-semibold text-white">Distribusi Aspek</p>
            <p class="mt-1 text-xs text-slate-300/85">
              Kategori masalah dari ulasan pengguna
            </p>
          </div>

          <!-- overview-style icon bubble -->
          <div
            class="flex h-12 w-12 items-center justify-center rounded-full bg-white/[0.06] ring-1 ring-white/[0.08]"
          >
            <svg
              viewBox="0 0 24 24"
              class="h-5 w-5 text-white/90"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M4 19V5m0 14h16M8 16v-5m4 5V8m4 8v-3"
              />
            </svg>
          </div>
        </div>

        <div class="mt-5">
          <p class="text-[11px] font-semibold uppercase tracking-wider text-slate-400/90">
            Top aspect
          </p>
          <p v-if="top" class="mt-1 text-2xl font-extrabold tracking-tight text-white">
            {{ top.aspect }}
            <span class="text-slate-300/90">({{ top.percent }}%)</span>
          </p>
          <p v-else class="mt-1 text-2xl font-extrabold tracking-tight text-white">
            -
          </p>
        </div>

        <div class="mt-5 space-y-3">
          <div
            v-for="row in listRows"
            :key="row.aspect"
            class="grid grid-cols-[1fr_auto] items-center gap-3"
          >
            <div class="min-w-0">
              <div class="flex items-center justify-between gap-3">
                <p class="truncate text-sm font-semibold text-slate-100">
                  {{ row.aspect }}
                </p>
                <p class="text-xs font-semibold text-slate-300/90">
                  {{ row.percent }}%
                </p>
              </div>
              <div class="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-white/10 ring-1 ring-white/10">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-purple-300/70 via-fuchsia-300/55 to-purple-200/60 shadow-[0_0_18px_rgba(168,85,247,0.35)] transition-[width] duration-500"
                  :style="{ width: `${row.percent}%` }"
                />
              </div>
            </div>
            <p class="pb-0.5 text-xs font-semibold text-slate-300/85">
              {{ row.total }}
            </p>
          </div>

          <div
            v-if="listRows.length === 0"
            class="rounded-xl bg-black/20 p-4 text-center text-sm text-slate-300/80 ring-1 ring-white/10"
          >
            Belum ada data
          </div>
        </div>
      </div>

      <!-- right spider/radar (floating, centered) -->
      <div class="relative flex min-h-[320px] items-center justify-center">
        <div class="relative h-[280px] w-full max-w-[360px]">
          <Radar v-if="radarLabels.length" :data="radarData" :options="radarOptions" />
          <p
            v-else
            class="flex h-full items-center justify-center text-sm text-slate-300/80"
          >
            Belum ada data
          </p>
        </div>
      </div>
    </div>
  </DashboardCardShell>
</template>

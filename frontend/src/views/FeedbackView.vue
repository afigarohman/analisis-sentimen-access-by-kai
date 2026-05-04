<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import {
  fetchNegativeAspectInsights,
  type NegativeAspectInsightItem,
} from '@/api/dashboard'
import DashboardCardShell from '@/components/dashboard/DashboardCardShell.vue'

const loading = ref(true)
const error = ref<string | null>(null)
const items = ref<NegativeAspectInsightItem[]>([])

const totalNegative = computed(() =>
  items.value.reduce((acc, x) => acc + x.total, 0),
)

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    items.value = await fetchNegativeAspectInsights()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Gagal memuat insight'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="mx-auto w-full max-w-6xl space-y-4 sm:space-y-6">
    <DashboardCardShell tag="section" variant="offset" class="p-6">
      <div>
        <h1 class="text-lg font-semibold text-white">
          <span
            class="bg-gradient-to-r from-purple-200 via-fuchsia-200 to-purple-100 bg-clip-text text-transparent"
          >
            Insight Ulasan Negatif
          </span>
        </h1>
        <p class="mt-1 text-sm text-slate-300/85">
          Ringkasan kategori masalah untuk ulasan dengan skor 1–2.
        </p>
        <p class="mt-3 text-sm font-semibold text-white">
          Total ulasan negatif:
          <span class="tabular-nums">{{ totalNegative }}</span>
        </p>
      </div>
    </DashboardCardShell>

    <DashboardCardShell v-if="loading" variant="tl" class="p-6">
      <p class="text-sm text-slate-300/85">Memuat insight…</p>
    </DashboardCardShell>

    <div
      v-else-if="error"
      class="rounded-[1.75rem] border border-red-400/35 bg-red-950/45 p-6 text-red-100 shadow-[0_18px_55px_-24px_rgba(239,68,68,0.25)] backdrop-blur-xl transition duration-300 hover:-translate-y-0.5 hover:border-red-300/45 hover:shadow-[0_28px_60px_-22px_rgba(239,68,68,0.35),0_14px_40px_-14px_rgba(248,113,113,0.12)]"
    >
      {{ error }}
    </div>

    <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <DashboardCardShell
        v-for="item in items"
        :key="item.aspect"
        variant="tr"
        compact
        class="px-5 py-4"
      >
        <div class="flex items-center justify-between gap-4">
          <div class="text-sm font-semibold text-slate-100">{{ item.aspect }}</div>
          <div class="text-sm font-bold text-fuchsia-200/90">
            {{ item.total }} ulasan
          </div>
        </div>
      </DashboardCardShell>

      <div
        v-if="items.length === 0"
        class="rounded-[1.75rem] border border-white/[0.08] bg-white/[0.04] p-6 text-center text-sm text-slate-400 shadow-[0_20px_50px_-20px_rgba(0,0,0,0.65)] backdrop-blur-xl transition duration-300 hover:-translate-y-0.5 hover:border-white/[0.13] hover:shadow-[0_28px_65px_-24px_rgba(168,85,247,0.42),0_18px_50px_-18px_rgba(217,70,239,0.16)] md:col-span-2 dark:bg-[rgba(255,255,255,0.045)]"
      >
        Belum ada data ulasan negatif.
      </div>
    </div>
  </div>
</template>

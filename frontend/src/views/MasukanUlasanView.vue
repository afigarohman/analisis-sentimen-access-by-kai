<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { getFeedbackList, type FeedbackItem, type FeedbackListResponse } from '@/api/ai'
import DashboardCardShell from '@/components/dashboard/DashboardCardShell.vue'

/** Urutan tetap seperti Review Ulasan; yang lain dari data menyusul */
const KNOWN_ASPECTS = ['Login', 'Sistem', 'Pembayaran', 'UI/UX', 'Performa', 'Lainnya'] as const

const loading = ref(true)
const error = ref<string | null>(null)
const data = ref<FeedbackListResponse | null>(null)

const selectedAspect = ref<string | null>(null)

const total = computed(() => data.value?.total ?? 0)
const items = computed(() => data.value?.items ?? [])
const truncated = computed(() => data.value?.truncated === true)
const shown = computed(() => data.value?.shown ?? items.value.length)

function normalizeAspect(a: string | undefined): string {
  return (a && a.trim()) || 'Lainnya'
}

const aspectCounts = computed(() => {
  const map = new Map<string, number>()
  for (const it of items.value) {
    const key = normalizeAspect(it.aspect)
    map.set(key, (map.get(key) ?? 0) + 1)
  }
  return map
})

/** Chips: daftar dikenal + aspek lain dari API (mis. typo / label baru */
const aspectOptions = computed(() => {
  const counts = aspectCounts.value
  const merged = new Map<string, number>()
  for (const a of KNOWN_ASPECTS) merged.set(a, counts.get(a) ?? 0)
  for (const [a, n] of counts) {
    if (!merged.has(a)) merged.set(a, n)
  }
  const knownFlat = KNOWN_ASPECTS as unknown as readonly string[]
  const rest = [...merged.entries()].filter(([a]) => !knownFlat.includes(a))
  rest.sort((x, y) => y[1] - x[1])
  const knownRows = KNOWN_ASPECTS.map((aspect) => ({
    aspect,
    count: merged.get(aspect) ?? 0,
  }))
  const extraRows = rest.map(([aspect, count]) => ({ aspect, count }))
  return [...knownRows, ...extraRows]
})

const filteredItems = computed(() => {
  const sel = selectedAspect.value
  if (!sel) return items.value
  return items.value.filter((it) => normalizeAspect(it.aspect) === sel)
})

function escapeHtml(s: string) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function escapeRegExp(s: string) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function highlightFeedbackHtml(text: string, keywords: string[]): string {
  const kws = [...new Set(keywords)].filter(Boolean)
  if (!kws.length) return escapeHtml(text)
  const sorted = [...kws].sort((a, b) => b.length - a.length)
  let out = escapeHtml(text)
  for (const kw of sorted) {
    const re = new RegExp(escapeRegExp(kw), 'gi')
    out = out.replace(
      re,
      '<mark class="rounded-sm bg-fuchsia-500/35 px-0.5 text-fuchsia-100 ring-1 ring-fuchsia-400/40">$&</mark>',
    )
  }
  return out
}

function sentimentClass(s: string): string {
  const x = s.toLowerCase()
  if (x === 'positive')
    return 'border-emerald-400/30 bg-emerald-500/15 text-emerald-200'
  if (x === 'negative') return 'border-rose-400/30 bg-rose-500/15 text-rose-200'
  if (x === 'neutral') return 'border-slate-400/30 bg-slate-500/15 text-slate-200'
  return 'border-white/15 bg-white/10 text-slate-300'
}

function selectAspectFilter(aspect: string | null) {
  selectedAspect.value = aspect
}

function itemKey(row: FeedbackItem, i: number) {
  return `${normalizeAspect(row.aspect)}:${i}:${row.text.length}:${row.text.slice(0, 48)}`
}

async function load() {
  loading.value = true
  error.value = null
  try {
    data.value = await getFeedbackList()
    selectedAspect.value = null
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Gagal memuat masukan'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void load()
})
</script>

<template>
  <div class="mx-auto w-full max-w-6xl space-y-4 sm:space-y-6">
    <DashboardCardShell tag="section" variant="tr" class="p-6">
      <div>
        <h1 class="text-lg font-semibold text-white sm:text-xl">
          <span
            class="bg-gradient-to-r from-purple-200 via-fuchsia-200 to-purple-100 bg-clip-text text-transparent"
          >
            Masukan Ulasan
          </span>
        </h1>
        <p class="mt-1 text-sm text-slate-300/85">
          Menampilkan ulasan pengguna yang mengandung <strong class="text-slate-200">saran</strong> atau
          permintaan perbaikan (bukan khusus ulasan negatif).
        </p>

        <p class="mt-4 text-sm font-semibold text-white">
          Total ulasan masukan:
          <span class="tabular-nums">{{ total }}</span>
          <template v-if="selectedAspect">
            <span class="text-slate-400"> · ditampilkan </span>
            <span class="tabular-nums text-fuchsia-200/90">{{ filteredItems.length }}</span>
            <span class="text-slate-400"> ({{ selectedAspect }})</span>
          </template>
        </p>
        <p v-if="truncated" class="mt-2 text-xs text-amber-200/90">
          Menampilkan {{ shown }} dari {{ total }} entri (respons dibatasi untuk performa).
        </p>
      </div>
    </DashboardCardShell>

    <DashboardCardShell v-if="loading" variant="tm" class="p-6">
      <p class="text-sm text-slate-300/85">Memuat masukan…</p>
    </DashboardCardShell>

    <div
      v-else-if="error"
      class="rounded-[1.75rem] border border-red-400/35 bg-red-950/45 p-6 text-red-100 shadow-[0_18px_55px_-24px_rgba(239,68,68,0.25)] backdrop-blur-xl transition duration-300 hover:-translate-y-0.5 hover:border-red-300/45 hover:shadow-[0_28px_60px_-22px_rgba(239,68,68,0.35),0_14px_40px_-14px_rgba(248,113,113,0.12)]"
    >
      {{ error }}
    </div>

    <div v-else class="space-y-4 sm:space-y-6">
      <DashboardCardShell tag="section" variant="bl" class="p-6">
        <div>
          <h2 class="text-base font-semibold text-white">Filter aspek</h2>
          <p class="mt-1 text-xs text-slate-300/85">
            Klik kategori untuk menyaring daftar ulasan di bawah. Chip tanpa data tidak dapat dipilih.
          </p>
          <div class="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium transition duration-300"
              :class="
                selectedAspect === null
                  ? 'border-fuchsia-400/45 bg-fuchsia-500/15 text-white ring-1 ring-fuchsia-400/40'
                  : 'border-white/10 bg-black/25 text-slate-200 hover:border-purple-400/35 hover:bg-black/35'
              "
              @click="selectAspectFilter(null)"
            >
              Semua
              <span class="font-bold tabular-nums text-fuchsia-200/90">{{ items.length }}</span>
            </button>
            <button
              v-for="row in aspectOptions"
              :key="row.aspect"
              type="button"
              :disabled="row.count === 0"
              class="inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs transition duration-300"
              :class="[
                row.count === 0
                  ? 'cursor-not-allowed border-white/[0.06] bg-black/15 text-slate-500 opacity-60'
                  : selectedAspect === row.aspect
                    ? 'border-fuchsia-400/45 bg-fuchsia-500/15 font-medium text-white ring-1 ring-fuchsia-400/40'
                    : 'border-white/10 bg-black/25 text-slate-200 hover:border-purple-400/35 hover:bg-black/35',
              ]"
              @click="row.count && selectAspectFilter(row.aspect)"
            >
              {{ row.aspect }}
              <span class="font-bold tabular-nums text-fuchsia-200/90">{{ row.count }}</span>
            </button>
          </div>
        </div>
      </DashboardCardShell>

      <DashboardCardShell tag="section" variant="br" class="p-6">
        <div>
          <h2 class="text-base font-semibold text-white">Daftar masukan</h2>
          <p class="mt-1 text-xs text-slate-300/85">
            Kata kunci seperti &quot;saran&quot;, &quot;tolong&quot;, &quot;sebaiknya&quot;, dll. disorot.
            Gulir halaman untuk melihat lebih banyak ulasan.
          </p>

          <div class="mt-4 space-y-3">
            <div
              v-if="!items.length"
              class="rounded-xl border border-white/10 bg-black/25 p-4 text-center text-sm text-slate-400 transition duration-300 hover:border-white/[0.14] hover:shadow-[0_20px_44px_-20px_rgba(168,85,247,0.35)]"
            >
              Belum ada ulasan yang terdeteksi sebagai masukan. Coba tingkatkan data ulasan atau
              perkaya kata kunci di backend jika perlu.
            </div>

            <div
              v-else-if="!filteredItems.length"
              class="rounded-xl border border-amber-400/25 bg-amber-950/25 p-4 text-center text-sm text-amber-100/90"
            >
              Tidak ada masukan untuk aspek
              <span class="font-semibold text-white">{{ selectedAspect }}</span
              >. Pilih kategori lain atau &quot;Semua&quot;.
            </div>

            <DashboardCardShell
              v-for="(row, idx) in filteredItems"
              :key="itemKey(row, idx)"
              tag="article"
              variant="tm"
              compact
              class="p-4"
            >
              <div class="flex flex-wrap items-center gap-2 text-[11px]">
                <span
                  class="rounded-full border px-2 py-0.5 font-semibold capitalize"
                  :class="sentimentClass(row.sentiment)"
                >
                  {{ row.sentiment }}
                </span>
                <span
                  class="rounded-full border border-white/15 bg-white/5 px-2 py-0.5 font-semibold text-slate-200"
                >
                  {{ normalizeAspect(row.aspect) }}
                </span>
                <span
                  v-for="kw in row.matched_keywords"
                  :key="kw"
                  class="rounded-full border border-fuchsia-400/25 bg-fuchsia-500/10 px-2 py-0.5 font-medium text-fuchsia-100"
                >
                  {{ kw }}
                </span>
              </div>
              <div
                class="mt-3 text-sm leading-relaxed text-slate-100"
                v-html="highlightFeedbackHtml(row.text, row.matched_keywords)"
              />
            </DashboardCardShell>
          </div>
        </div>
      </DashboardCardShell>
    </div>
  </div>
</template>

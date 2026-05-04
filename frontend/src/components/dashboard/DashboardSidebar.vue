<script setup lang="ts">
import { RouterLink } from 'vue-router'

defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()
</script>

<template>
  <aside
    class="fixed inset-y-0 left-0 z-50 flex h-screen w-72 flex-col overflow-hidden border-r border-transparent bg-white/85 shadow-lg backdrop-blur-xl transition-transform duration-300 dark:border-white/10 dark:bg-gradient-to-b dark:from-[#0d0c12] dark:via-[#12101a] dark:to-[#0a090e] dark:shadow-[inset_-1px_0_0_rgba(168,85,247,0.12)] md:w-64 md:translate-x-0"
    :class="
      open
        ? 'translate-x-0'
        : '-translate-x-full md:translate-x-0'
    "
  >
    <div class="flex items-center gap-3 border-b border-slate-100 px-5 py-6 dark:border-white/10">
      <div class="flex items-center gap-3">
        <img
          src="@/assets/logo-kai.png"
          alt="Access by KAI"
          class="h-10 w-auto object-contain"
        />
      </div>
    </div>

    <nav class="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto overscroll-contain px-4 pb-6 pt-6">
      <p class="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
        UTAMA
      </p>

      <RouterLink
        to="/dashboard"
        class="group relative overflow-hidden rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-300 hover:scale-[1.01] dark:text-slate-200"
        active-class="!bg-purple-500/20 !text-purple-100 dark:!shadow-[0_0_28px_-6px_rgba(168,85,247,0.45)] dark:!ring-1 dark:!ring-fuchsia-400/30"
        @click="emit('close')"
      >
        <span
          class="absolute inset-0 -z-10 bg-slate-100 transition group-hover:bg-slate-200/60 dark:bg-slate-900/40 dark:group-hover:bg-slate-900/70"
        />
        <span
          class="pointer-events-none absolute -left-10 top-1/2 -z-10 h-28 w-28 -translate-y-1/2 rounded-full bg-purple-500/0 blur-2xl transition group-hover:bg-purple-500/20"
        />
        Dashboard
      </RouterLink>

      <RouterLink
        to="/reviews"
        class="group relative overflow-hidden rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-300 hover:scale-[1.01] text-slate-700 dark:text-slate-200"
        active-class="!bg-purple-500/20 !text-purple-100 dark:!shadow-[0_0_28px_-6px_rgba(168,85,247,0.45)] dark:!ring-1 dark:!ring-fuchsia-400/30"
        @click="emit('close')"
      >
        <span
          class="absolute inset-0 -z-10 bg-slate-100 transition group-hover:bg-slate-200/60 dark:bg-slate-900/40 dark:group-hover:bg-slate-900/70"
        />
        <span
          class="pointer-events-none absolute -left-10 top-1/2 -z-10 h-28 w-28 -translate-y-1/2 rounded-full bg-purple-500/0 blur-2xl transition group-hover:bg-purple-500/20"
        />
        Review Ulasan
      </RouterLink>

      <RouterLink
        to="/ai-pipeline"
        class="group relative overflow-hidden rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-300 hover:scale-[1.01] text-slate-700 dark:text-slate-200"
        active-class="!bg-purple-500/20 !text-purple-100 dark:!shadow-[0_0_28px_-6px_rgba(168,85,247,0.45)] dark:!ring-1 dark:!ring-fuchsia-400/30"
        @click="emit('close')"
      >
        <span
          class="absolute inset-0 -z-10 bg-slate-100 transition group-hover:bg-slate-200/60 dark:bg-slate-900/40 dark:group-hover:bg-slate-900/70"
        />
        <span
          class="pointer-events-none absolute -left-10 top-1/2 -z-10 h-28 w-28 -translate-y-1/2 rounded-full bg-purple-500/0 blur-2xl transition group-hover:bg-purple-500/20"
        />
        AI Pipeline
      </RouterLink>

      <RouterLink
        to="/masukan-ulasan"
        class="group relative overflow-hidden rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-300 hover:scale-[1.01] text-slate-700 dark:text-slate-200"
        active-class="!bg-purple-500/20 !text-purple-100 dark:!shadow-[0_0_28px_-6px_rgba(168,85,247,0.45)] dark:!ring-1 dark:!ring-fuchsia-400/30"
        @click="emit('close')"
      >
        <span
          class="absolute inset-0 -z-10 bg-slate-100 transition group-hover:bg-slate-200/60 dark:bg-slate-900/40 dark:group-hover:bg-slate-900/70"
        />
        <span
          class="pointer-events-none absolute -left-10 top-1/2 -z-10 h-28 w-28 -translate-y-1/2 rounded-full bg-purple-500/0 blur-2xl transition group-hover:bg-purple-500/20"
        />
        Masukan Ulasan
      </RouterLink>
    </nav>
  </aside>
</template>

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
    class="fixed inset-y-0 left-0 z-50 flex w-72 flex-col shadow-lg backdrop-blur-xl transition-transform duration-300 md:static md:translate-x-0 md:shadow-none md:backdrop-blur-none md:w-64"
    :class="
      open
        ? 'translate-x-0 bg-white/80 dark:bg-slate-950/55'
        : '-translate-x-full bg-white/80 dark:bg-slate-950/55'
    "
  >
    <div class="flex items-center gap-3 border-b border-slate-100 px-5 py-6 dark:border-slate-800">
      <div class="flex items-center gap-3">
        <img
          src="@/assets/logo-kai.png"
          alt="Access by KAI"
          class="h-10 w-auto object-contain"
        />
      </div>
    </div>

    <nav class="flex flex-1 flex-col gap-3 px-4 pb-6 pt-6">
      <p class="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
        UTAMA
      </p>

      <RouterLink
        to="/"
        class="group relative overflow-hidden rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-300 hover:scale-[1.01] dark:text-slate-200"
        active-class="bg-blue-500/15 text-blue-700 dark:text-purple-200"
        @click="emit('close')"
      >
        <span
          class="absolute inset-0 -z-10 bg-slate-100 transition group-hover:bg-slate-200/60 dark:bg-slate-900/60 dark:group-hover:bg-slate-900"
        />
        <span
          class="pointer-events-none absolute -left-10 top-1/2 -z-10 h-28 w-28 -translate-y-1/2 rounded-full bg-purple-500/0 blur-2xl transition group-hover:bg-purple-500/12"
        />
        Dashboard
      </RouterLink>

      <RouterLink
        to="/reviews"
        class="group relative overflow-hidden rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-300 hover:scale-[1.01] text-slate-700 dark:text-slate-200"
        active-class="bg-blue-500/15 text-blue-700 dark:text-purple-200"
        @click="emit('close')"
      >
        <span
          class="absolute inset-0 -z-10 bg-slate-100 transition group-hover:bg-slate-200/60 dark:bg-slate-900/60 dark:group-hover:bg-slate-900"
        />
        <span
          class="pointer-events-none absolute -left-10 top-1/2 -z-10 h-28 w-28 -translate-y-1/2 rounded-full bg-purple-500/0 blur-2xl transition group-hover:bg-purple-500/12"
        />
        Review Ulasan
      </RouterLink>

      <RouterLink
        to="/ai-pipeline"
        class="group relative overflow-hidden rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-300 hover:scale-[1.01] text-slate-700 dark:text-slate-200"
        active-class="bg-blue-500/15 text-blue-700 dark:text-purple-200"
        @click="emit('close')"
      >
        <span
          class="absolute inset-0 -z-10 bg-slate-100 transition group-hover:bg-slate-200/60 dark:bg-slate-900/60 dark:group-hover:bg-slate-900"
        />
        <span
          class="pointer-events-none absolute -left-10 top-1/2 -z-10 h-28 w-28 -translate-y-1/2 rounded-full bg-purple-500/0 blur-2xl transition group-hover:bg-purple-500/12"
        />
        AI Pipeline
      </RouterLink>

      <a
        href="#"
        class="group relative overflow-hidden rounded-xl px-4 py-3 text-sm font-semibold text-slate-700 transition-all duration-300 hover:scale-[1.01] dark:text-slate-200"
        @click.prevent
      >
        <span
          class="absolute inset-0 -z-10 bg-slate-100 transition group-hover:bg-slate-200/60 dark:bg-slate-900/60 dark:group-hover:bg-slate-900"
        />
        <span
          class="pointer-events-none absolute -left-10 top-1/2 -z-10 h-28 w-28 -translate-y-1/2 rounded-full bg-purple-500/0 blur-2xl transition group-hover:bg-purple-500/12"
        />
        Masukan Ulasan
      </a>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps<{
  open?: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const isOpen = computed(() => props.open ?? false)
</script>

<template>
  <!-- Mobile overlay -->
  <button
    v-if="isOpen"
    class="fixed inset-0 z-40 bg-slate-900/30 md:hidden"
    aria-label="Tutup sidebar"
    @click="emit('close')"
  />

  <aside
    class="fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-slate-200 bg-white shadow-lg transition-transform md:static md:z-auto md:w-64 md:translate-x-0 md:shadow-none"
    :class="isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
  >
    <div class="flex items-center justify-between gap-3 border-b border-slate-100 px-5 py-5">
      <div class="flex items-center gap-3">
        <img
          src="@/assets/logo-kai.png"
          alt="Access by KAI"
          class="h-10 w-auto object-contain"
        />
      </div>
      <button
        class="rounded-lg p-2 text-slate-500 hover:bg-slate-100 md:hidden"
        aria-label="Tutup sidebar"
        @click="emit('close')"
      >
        <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <nav class="flex flex-1 flex-col gap-3 px-4 pb-6 pt-6">
      <p class="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
        UTAMA
      </p>

      <RouterLink
        to="/"
        class="rounded-xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-200/60"
        active-class="bg-blue-100 text-blue-700"
        @click="emit('close')"
      >
        Dashboard
      </RouterLink>

      <a
        href="#"
        class="rounded-xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-200/60"
        @click.prevent
      >
        Review Ulasan
      </a>

      <a
        href="#"
        class="rounded-xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-200/60"
        @click.prevent
      >
        AI Pipeline
      </a>

      <a
        href="#"
        class="rounded-xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-200/60"
        @click.prevent
      >
        Masukan Ulasan
      </a>
    </nav>
  </aside>
</template>

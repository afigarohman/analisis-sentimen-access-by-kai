<script setup lang="ts">
import { ref } from 'vue'
import { RouterView } from 'vue-router'
import DashboardSidebar from '@/components/dashboard/DashboardSidebar.vue'

const sidebarOpen = ref(false)
</script>

<template>
  <div
    class="relative min-h-screen overflow-hidden bg-slate-50 text-slate-800 dark:bg-gradient-to-br dark:from-slate-950 dark:via-blue-950 dark:to-slate-900 dark:text-white"
  >
    <!-- Global spotlight glow (dark only) -->
    <div
      class="pointer-events-none absolute -top-28 left-1/2 h-[680px] w-[680px] -translate-x-1/2 rounded-full bg-gradient-to-tr from-blue-500/26 via-purple-500/18 to-red-500/12 blur-2xl opacity-0 dark:opacity-100"
    />
    <div
      class="pointer-events-none absolute -top-14 right-6 h-[560px] w-[560px] rounded-full bg-gradient-to-tr from-purple-500/22 via-blue-500/14 to-transparent blur-2xl opacity-0 dark:opacity-100"
    />
    <div
      class="pointer-events-none absolute -bottom-52 left-8 h-[620px] w-[620px] rounded-full bg-gradient-to-tr from-red-500/16 via-purple-500/14 to-transparent blur-2xl opacity-0 dark:opacity-100"
    />

    <!-- Mobile overlay -->
    <button
      v-if="sidebarOpen"
      class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm md:hidden"
      aria-label="Tutup sidebar"
      @click="sidebarOpen = false"
    />

    <!-- Hamburger / X button -->
    <button
      class="fixed left-4 top-4 z-50 rounded-xl bg-white/70 p-2 shadow-md backdrop-blur transition md:hidden dark:bg-slate-950/50 dark:shadow-blue-500/10"
      aria-label="Toggle sidebar"
      @click="sidebarOpen = !sidebarOpen"
    >
      <svg
        viewBox="0 0 24 24"
        class="h-5 w-5 text-slate-800 dark:text-white"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
      >
        <path
          d="M4 6h16"
          class="origin-center transition-transform duration-300"
          :class="sidebarOpen ? 'translate-y-[6px] rotate-45' : ''"
        />
        <path
          d="M4 12h16"
          class="transition-opacity duration-300"
          :class="sidebarOpen ? 'opacity-0' : 'opacity-100'"
        />
        <path
          d="M4 18h16"
          class="origin-center transition-transform duration-300"
          :class="sidebarOpen ? '-translate-y-[6px] -rotate-45' : ''"
        />
      </svg>
    </button>

    <!-- Desktop layout: sidebar left, content right -->
    <div class="relative flex min-h-screen">
      <DashboardSidebar
        :open="sidebarOpen"
        class="w-72 md:w-64"
        @close="sidebarOpen = false"
      />

      <main class="relative min-w-0 flex-1">
        <div class="p-4 sm:p-6">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>


<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import DashboardSidebar from '@/components/dashboard/DashboardSidebar.vue'
import MainContentSpotlight from '@/components/layout/MainContentSpotlight.vue'
import { useMainSpotlightMode } from '@/composables/useMainSpotlightMode'

const sidebarOpen = ref(false)
const spotlightMode = useMainSpotlightMode()
const route = useRoute()
const isAuthOnlyLayout = computed(() => route.name === 'login')
</script>

<template>
  <div v-if="isAuthOnlyLayout" class="min-h-screen bg-[#07070d] antialiased">
    <RouterView />
  </div>
  <div
    v-else
    class="relative min-h-screen overflow-x-hidden bg-slate-50 font-sans text-slate-800 dark:bg-[#0a0a0c] dark:text-white"
  >
    <!-- Mobile overlay -->
    <button
      v-if="sidebarOpen"
      class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm md:hidden"
      aria-label="Tutup sidebar"
      @click="sidebarOpen = false"
    />

    <!-- Hamburger / X button -->
    <button
      class="fixed left-4 top-4 z-50 rounded-xl border border-white/10 bg-white/70 p-2 shadow-md shadow-purple-500/10 backdrop-blur transition md:hidden dark:bg-slate-950/60 dark:shadow-[0_0_28px_-6px_rgba(168,85,247,0.45)]"
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

    <!-- Sidebar fixed; konten digeser dengan padding kiri di desktop -->
    <DashboardSidebar
      :open="sidebarOpen"
      class="w-72 md:w-64"
      @close="sidebarOpen = false"
    />

    <main
      class="relative z-[5] min-h-screen min-w-0 overflow-x-hidden md:pl-64"
    >
      <MainContentSpotlight :mode="spotlightMode" />
      <div class="relative z-10 min-h-[inherit] p-4 sm:p-6">
        <RouterView />
      </div>
    </main>
  </div>
</template>


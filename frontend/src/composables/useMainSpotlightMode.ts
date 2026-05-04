import { computed } from 'vue'
import { useRoute } from 'vue-router'

export type SpotlightMode = 'top-left' | 'top-center' | 'bottom-center'

/** Ambiens global: atas tengah (soft glow) untuk hampir semua route; AI pipeline dari bawah tengah */
export function useMainSpotlightMode() {
  const route = useRoute()

  return computed<SpotlightMode>(() => {
    const p = route.path
    if (p.startsWith('/reviews')) return 'top-center'
    if (p.startsWith('/ai-pipeline')) return 'bottom-center'
    return 'top-left'
  })
}

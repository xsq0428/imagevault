<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { loadSiteConfig, site } from '../store'

const route = useRoute()
const dismissed = ref(sessionStorage.getItem('iv_announcement_dismissed') === '1')

function close() {
  dismissed.value = true
  sessionStorage.setItem('iv_announcement_dismissed', '1')
}

const show = computed(
  () =>
    site.loaded &&
    !route.path.startsWith('/admin') &&
    !dismissed.value &&
    site.announcement_enabled &&
    site.announcement_mode === 'modal' &&
    !!site.announcement_text
)

watch(
  () => [site.announcement_enabled, site.announcement_mode, site.announcement_text],
  () => {
    dismissed.value = false
    sessionStorage.removeItem('iv_announcement_dismissed')
  }
)

loadSiteConfig()
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="announcement-modal-backdrop" @click="close">
      <div class="announcement-modal" @click.stop>
        <button class="announcement-close" title="关闭" @click="close">
          <svg viewBox="0 0 24 24" width="18" height="18">
            <path d="M18 6L6 18M6 6l12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
        </button>
        <div class="announcement-modal-body">
          <span class="announcement-modal-icon">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path d="M4 10v4h3l5 3V7l-5 3H4Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" />
              <path d="M16 9.5a3.5 3.5 0 0 1 0 5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
            </svg>
          </span>
          <p>{{ site.announcement_text }}</p>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.announcement-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.4);
  display: grid;
  place-items: center;
  padding: 24px;
}

.announcement-modal {
  position: relative;
  width: 100%;
  max-width: 440px;
  background: var(--white);
  border-radius: 16px;
  box-shadow: var(--shadow-soft);
  overflow: hidden;
  animation: modal-in 0.2s ease;
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: scale(0.96) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.announcement-close {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: var(--ink-300);
  transition: background 0.15s ease, color 0.15s ease;
}

.announcement-close:hover {
  background: var(--mint-100);
  color: var(--mint-600);
}

.announcement-modal-body {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 24px 24px 20px;
}

.announcement-modal-icon {
  flex: 0 0 auto;
  color: var(--mint-500);
  margin-top: 2px;
}

.announcement-modal-body p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--ink-700);
}
</style>

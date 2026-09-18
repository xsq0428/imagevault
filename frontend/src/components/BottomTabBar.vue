<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { loadSiteConfig, site, notif, setNotifOpen } from '../store'
import AnnouncementPanel from './AnnouncementPanel.vue'

const route = useRoute()

const navTabs = computed(() => [
  { to: '/', label: '首页', icon: 'home' },
  { to: '/categories', label: '分类', icon: 'grid' }
])

const hasAnnouncement = computed(
  () =>
    site.loaded &&
    site.announcement_enabled &&
    site.announcement_mode === 'inbox' &&
    !!site.announcement_text
)

onMounted(() => loadSiteConfig())
</script>

<template>
  <nav class="bottom-tab" :class="{ 'has-notif': hasAnnouncement }">
    <template v-for="tab in navTabs" :key="tab.to">
      <router-link
        :to="tab.to"
        class="tab-item"
        :class="{ active: route.path === tab.to }"
      >
        <svg v-if="tab.icon === 'home'" viewBox="0 0 24 24" width="22" height="22">
          <path d="M4 10.5 12 4l8 6.5V19a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 19v-8.5Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
          <path d="M9.5 20.5V14h5v6.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
        </svg>
        <svg v-else viewBox="0 0 24 24" width="22" height="22">
          <rect x="3.5" y="3.5" width="7" height="7" rx="2" fill="none" stroke="currentColor" stroke-width="1.8" />
          <rect x="13.5" y="3.5" width="7" height="7" rx="2" fill="none" stroke="currentColor" stroke-width="1.8" />
          <rect x="3.5" y="13.5" width="7" height="7" rx="2" fill="none" stroke="currentColor" stroke-width="1.8" />
          <rect x="13.5" y="13.5" width="7" height="7" rx="2" fill="none" stroke="currentColor" stroke-width="1.8" />
        </svg>
        <span>{{ tab.label }}</span>
      </router-link>
    </template>

    <button
      v-if="hasAnnouncement"
      class="tab-item notif-tab"
      :class="{ active: notif.open }"
      @click="setNotifOpen(!notif.open)"
    >
      <svg viewBox="0 0 24 24" width="22" height="22">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" />
        <path d="M13.73 21a2 2 0 0 1-3.46 0" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
      </svg>
      <span>公告</span>
      <span class="tab-dot"></span>
    </button>

    <AnnouncementPanel v-if="hasAnnouncement" />
  </nav>
</template>

<style scoped>
.bottom-tab {
  position: fixed;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: 100%;
  max-width: 760px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  background: var(--white);
  border-top: 1px solid var(--line);
  box-shadow: 0 -2px 14px rgba(31, 61, 49, 0.06);
  z-index: 30;
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.bottom-tab.has-notif {
  grid-template-columns: repeat(3, 1fr);
}

.tab-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  height: 58px;
  color: var(--ink-300);
  text-decoration: none;
  font-size: 11px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color 0.15s ease;
}

.tab-item.active {
  color: var(--mint-600);
}

.tab-item.active svg {
  transform: translateY(-1px);
}

.tab-dot {
  position: absolute;
  top: 8px;
  right: calc(50% - 16px);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--mint-500);
}

@media (min-width: 1024px) {
  .bottom-tab {
    display: none;
  }
}
</style>

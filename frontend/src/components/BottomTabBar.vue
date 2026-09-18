<script setup>
const tabs = [
  { to: '/', label: '首页', icon: 'home' },
  { to: '/categories', label: '分类', icon: 'grid' }
]
</script>

<template>
  <nav class="bottom-tab">
    <router-link
      v-for="tab in tabs"
      :key="tab.to"
      :to="tab.to"
      class="tab-item"
      :class="{ active: $route.path === tab.to }"
    >
      <svg v-if="tab.icon === 'home'" viewBox="0 0 24 24" width="22" height="22">
        <path
          d="M4 10.5 12 4l8 6.5V19a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 19v-8.5Z"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linejoin="round"
        />
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

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  height: 58px;
  color: var(--ink-300);
  text-decoration: none;
  font-size: 11px;
  transition: color 0.15s ease;
}

.tab-item.active {
  color: var(--mint-600);
}

.tab-item.active svg {
  transform: translateY(-1px);
}

@media (min-width: 1024px) {
  .bottom-tab {
    display: none;
  }
}
</style>

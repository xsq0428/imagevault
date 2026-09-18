<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const items = computed(() => [
  { to: '/', label: '首页', icon: 'home', active: route.path === '/' },
  { to: '/categories', label: '分类', icon: 'grid', active: route.path === '/categories' }
])
</script>

<template>
  <aside class="app-sidebar">
    <router-link to="/" class="brand">
      <span class="brand-mark">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <rect x="3" y="3" width="8" height="8" rx="2" fill="currentColor" />
          <rect x="13" y="3" width="8" height="8" rx="2" fill="currentColor" />
          <rect x="3" y="13" width="8" height="8" rx="2" fill="currentColor" />
          <rect x="13" y="13" width="8" height="8" rx="2" fill="currentColor" />
        </svg>
      </span>
      <span class="brand-text">图库</span>
    </router-link>

    <nav class="nav">
      <router-link
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        :class="{ active: item.active }"
      >
        <svg v-if="item.icon === 'home'" viewBox="0 0 24 24" width="18" height="18">
          <path d="M4 10.5 12 4l8 6.5V19a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 19v-8.5Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
          <path d="M9.5 20.5V14h5v6.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
        </svg>
        <svg v-else viewBox="0 0 24 24" width="18" height="18">
          <rect x="3.5" y="3.5" width="7" height="7" rx="2" fill="none" stroke="currentColor" stroke-width="1.8" />
          <rect x="13.5" y="3.5" width="7" height="7" rx="2" fill="none" stroke="currentColor" stroke-width="1.8" />
          <rect x="3.5" y="13.5" width="7" height="7" rx="2" fill="none" stroke="currentColor" stroke-width="1.8" />
          <rect x="13.5" y="13.5" width="7" height="7" rx="2" fill="none" stroke="currentColor" stroke-width="1.8" />
        </svg>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar-foot">
      <router-link to="/admin/dashboard" class="nav-item subtle">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" />
        </svg>
        <span>素材上传后台</span>
      </router-link>
    </div>
  </aside>
</template>

<style scoped>
.app-sidebar {
  flex: 0 0 auto;
  width: 208px;
  height: 100dvh;
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 18px 14px;
  background: var(--white);
  border-right: 1px solid var(--line);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 46px;
  padding: 0 8px;
  margin-bottom: 10px;
  text-decoration: none;
}

.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: var(--mint-500);
  color: #fff;
}

.brand-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--ink-900);
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 44px;
  padding: 0 12px;
  border-radius: 10px;
  color: var(--ink-500);
  font-size: 14px;
  text-decoration: none;
  transition: background 0.15s ease, color 0.15s ease;
}

.nav-item:hover {
  background: var(--mint-100);
  color: var(--mint-600);
}

.nav-item.active {
  background: var(--mint-100);
  color: var(--mint-600);
  font-weight: 600;
}

.nav-item.subtle {
  color: var(--ink-300);
}

.sidebar-foot {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--line);
}
</style>

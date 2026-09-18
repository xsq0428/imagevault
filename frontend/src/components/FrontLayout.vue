<script setup>
import { onMounted } from 'vue'

import AppSidebar from './AppSidebar.vue'
import BottomTabBar from './BottomTabBar.vue'
import { loadSiteConfig, site } from '../store'

onMounted(() => loadSiteConfig())
</script>

<template>
  <div class="front-shell">
    <AppSidebar class="desktop-nav" />
    <main class="front-main">
      <slot />
      <footer v-if="site.footer_text || site.icp_number" class="front-footer">
        <span v-if="site.footer_text">{{ site.footer_text }}</span>
        <a
          v-if="site.icp_number"
          class="front-icp"
          href="https://beian.miit.gov.cn/"
          target="_blank"
          rel="noopener"
        >{{ site.icp_number }}</a>
      </footer>
    </main>
    <BottomTabBar />
  </div>
</template>

<style scoped>
.front-shell {
  display: flex;
  min-height: 100dvh;
  background: var(--white);
}

.front-shell .desktop-nav {
  display: none;
}

.front-main {
  flex: 1;
  min-width: 0;
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 70px;
}

@media (min-width: 1024px) {
  .front-shell .desktop-nav {
    display: flex;
  }
  .front-main {
    padding-bottom: 0;
  }
}

.front-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 28px 16px 24px;
  margin-top: 24px;
  font-size: 12px;
  color: var(--ink-300);
  border-top: 1px solid var(--line);
}

.front-icp {
  color: var(--ink-300);
  text-decoration: none;
}

.front-icp:hover {
  color: var(--mint-600);
}
</style>

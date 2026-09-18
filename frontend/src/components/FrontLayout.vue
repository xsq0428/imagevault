<script setup>
import AppSidebar from './AppSidebar.vue'
import BottomTabBar from './BottomTabBar.vue'
</script>

<template>
  <div class="front-shell">
    <AppSidebar class="desktop-nav" />
    <main class="front-main">
      <slot />
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
</style>

<script setup>
import { loadSiteConfig, notif, setNotifOpen, site } from '../store'

loadSiteConfig()
</script>

<template>
  <Teleport to="body">
    <div
      v-if="notif.open"
      class="notif-backdrop"
      @click="setNotifOpen(false)"
    />

    <div class="notif-panel" :class="{ active: notif.open }">
      <div class="notif-header">
        <span class="notif-title">站内公告</span>
        <button class="notif-close" title="关闭" @click="setNotifOpen(false)">
          <svg viewBox="0 0 24 24" width="16" height="16">
            <path d="M18 6L6 18M6 6l12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
        </button>
      </div>
      <div class="notif-body">
        <span class="notif-icon">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path d="M4 10v4h3l5 3V7l-5 3H4Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" />
            <path d="M16 9.5a3.5 3.5 0 0 1 0 5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
          </svg>
        </span>
        <p>{{ site.announcement_text }}</p>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.notif-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 90;
}

.notif-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 100%;
  max-width: 380px;
  height: 100dvh;
  background: var(--white);
  z-index: 91;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.12);
  transform: translateX(100%);
  transition: transform 0.25s ease;
  display: flex;
  flex-direction: column;
}

.notif-panel.active {
  transform: translateX(0);
}

.notif-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px 16px;
  border-bottom: 1px solid var(--line);
}

.notif-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--ink-900);
}

.notif-close {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: var(--ink-300);
  transition: background 0.15s ease, color 0.15s ease;
}

.notif-close:hover {
  background: var(--mint-100);
  color: var(--mint-600);
}

.notif-body {
  flex: 1;
  padding: 20px;
  display: flex;
  gap: 12px;
}

.notif-icon {
  flex: 0 0 auto;
  color: var(--mint-500);
  margin-top: 2px;
}

.notif-body p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--ink-700);
}
</style>

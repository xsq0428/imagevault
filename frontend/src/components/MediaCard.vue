<script setup>
import { ref } from 'vue'
import SmartImage from './SmartImage.vue'
import { thumbUrl } from '../api'

const props = defineProps({
  item: { type: Object, required: true },
  selectable: { type: Boolean, default: false },
  selected: { type: Boolean, default: false }
})

const emit = defineEmits(['open', 'open-set', 'toggle-select'])

const showInfo = ref(false)
let pressTimer = null
let suppressClick = false

function humanSize(bytes) {
  const kb = bytes / 1024
  return kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${Math.round(kb)} KB`
}

function startPress(event) {
  if (event.pointerType === 'mouse') return
  suppressClick = false
  pressTimer = setTimeout(() => {
    showInfo.value = true
    suppressClick = true
  }, 420)
}

function cancelPress() {
  if (pressTimer) {
    clearTimeout(pressTimer)
    pressTimer = null
  }
}

function onLeave() {
  cancelPress()
  showInfo.value = false
}

function activate() {
  if (suppressClick) {
    suppressClick = false
    showInfo.value = false
    return
  }
  if (props.item.item_type === 'set') emit('open-set', props.item)
  else emit('open', props.item.image || props.item)
}
</script>

<template>
  <article class="card" :class="{ 'is-set': item.item_type === 'set', 'show-info': showInfo }">
    <div
      class="cover"
      role="button"
      tabindex="0"
      :aria-label="item.title"
      @pointerdown="startPress"
      @pointerup="cancelPress"
      @pointercancel="cancelPress"
      @pointerleave="onLeave"
      @click="activate"
      @keydown.enter="activate"
      @keydown.space.prevent="activate"
    >
      <SmartImage
        :src="thumbUrl(item.cover_image_id || item.id)"
        :placeholder="item.placeholder"
        :alt="item.title"
      />

      <span v-if="item.item_type === 'set'" class="type-badge">
        <svg viewBox="0 0 24 24" width="12" height="12">
          <rect x="3" y="3" width="12" height="12" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.8" />
          <path d="M8 21h10a3 3 0 0 0 3-3V8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
        </svg>
        套图
      </span>
      <span v-if="item.item_type === 'set'" class="count-badge">{{ item.image_count }} 张</span>

      <span class="info-overlay">
        <span class="info-name">{{ item.title }}</span>
        <span class="info-meta">
          <template v-if="item.item_type === 'set'">
            {{ item.category_name || '未分类' }} · {{ item.image_count }} 张
          </template>
          <template v-else>
            {{ item.width }} × {{ item.height }}
            <template v-if="item.image && item.image.size"> · {{ humanSize(item.image.size) }}</template>
          </template>
        </span>
        <span v-if="item.tags.length" class="info-tags">
          <span v-for="tag in item.tags.slice(0, 3)" :key="tag" class="info-tag">{{ tag }}</span>
        </span>
      </span>
    </div>

    <button
      v-if="selectable"
      class="select-dot"
      :class="{ on: selected }"
      :title="selected ? '取消选择' : '选择'"
      @click.stop="emit('toggle-select', item.id)"
    >
      <svg v-if="selected" viewBox="0 0 24 24" width="14" height="14">
        <path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>

    <div class="card-body">
      <p class="name" :title="item.title">{{ item.title }}</p>
      <p v-if="item.item_type === 'set'" class="meta">
        {{ item.category_name || '未分类' }} · {{ item.image_count }} 张
      </p>
      <p v-else class="meta">{{ item.width }} × {{ item.height }}</p>
    </div>
  </article>
</template>

<style scoped>
.card {
  position: relative;
  background: var(--white);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--line);
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(24, 24, 27, 0.1);
}

.card.is-set {
  border-color: var(--mint-200);
}

.card:active {
  transform: translateY(-1px) scale(0.99);
}

.cover {
  position: relative;
  display: block;
  width: 100%;
  aspect-ratio: 3 / 4;
  background: var(--mint-100);
  overflow: hidden;
  cursor: pointer;
  user-select: none;
  -webkit-touch-callout: none;
  touch-action: manipulation;
}

.type-badge,
.count-badge {
  position: absolute;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 10px;
  color: #fff;
  background: rgba(24, 24, 27, 0.6);
  backdrop-filter: blur(4px);
}

.type-badge {
  left: 8px;
  top: 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(38, 121, 75, 0.9);
}

.count-badge {
  right: 8px;
  top: 8px;
}

.info-overlay {
  position: absolute;
  inset: auto 0 0 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 22px 10px 9px;
  text-align: left;
  color: #fff;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.72), rgba(0, 0, 0, 0));
  opacity: 0;
  transform: translateY(6px);
  transition: opacity 0.2s ease, transform 0.2s ease;
  pointer-events: none;
}

.card:hover .info-overlay,
.card.show-info .info-overlay {
  opacity: 1;
  transform: translateY(0);
}

.info-name {
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-meta {
  font-size: 10px;
  opacity: 0.85;
}

.info-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 2px;
}

.info-tag {
  padding: 1px 7px;
  border-radius: 999px;
  font-size: 9px;
  background: rgba(255, 255, 255, 0.22);
}

.select-dot {
  position: absolute;
  left: 8px;
  top: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.85);
  color: #fff;
  border: 2px solid rgba(24, 24, 27, 0.25);
}

.select-dot.on {
  background: var(--mint-500);
  border-color: var(--mint-500);
}

.card-body {
  padding: 9px 10px 11px;
}

.name {
  margin: 0 0 3px;
  font-size: 13px;
  font-weight: 500;
  color: var(--ink-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta {
  margin: 0;
  font-size: 11px;
  color: var(--ink-300);
}
</style>

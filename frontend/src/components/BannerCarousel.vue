<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import SmartImage from './SmartImage.vue'
import { bannerUrl } from '../api'

const props = defineProps({
  banners: { type: Array, default: () => [] }
})

const emit = defineEmits(['open'])

const current = ref(0)
const dragging = ref(false)
const offset = ref(0)
const suppressClick = ref(false)

let timer = null
let startX = 0

const count = computed(() => props.banners.length)

const trackStyle = computed(() => ({
  transform: `translateX(calc(-${current.value * 100}% + ${offset.value}px))`,
  transition: dragging.value ? 'none' : 'transform 0.4s ease'
}))

function go(index) {
  if (!count.value) return
  current.value = (index + count.value) % count.value
}

function next() {
  go(current.value + 1)
}

function prev() {
  go(current.value - 1)
}

function start() {
  stop()
  if (count.value <= 1) return
  timer = setInterval(next, 4000)
}

function stop() {
  if (timer) clearInterval(timer)
  timer = null
}

function select(index) {
  go(index)
  start()
}

function onPointerDown(event) {
  if (count.value <= 1) return
  dragging.value = true
  startX = event.clientX
  offset.value = 0
  suppressClick.value = false
  stop()
  event.currentTarget.setPointerCapture(event.pointerId)
}

function onPointerMove(event) {
  if (!dragging.value) return
  let delta = event.clientX - startX
  if (current.value === 0 && delta > 0) delta = 0
  if (current.value === count.value - 1 && delta < 0) delta = 0
  offset.value = delta
  if (Math.abs(delta) > 6) suppressClick.value = true
}

function onPointerUp() {
  if (!dragging.value) return
  dragging.value = false
  const threshold = 50
  if (offset.value <= -threshold) next()
  else if (offset.value >= threshold) prev()
  offset.value = 0
  start()
}

function activate(banner) {
  if (suppressClick.value) {
    suppressClick.value = false
    return
  }
  if (banner.link) emit('open', banner)
}

onMounted(start)
onBeforeUnmount(stop)
</script>

<template>
  <div v-if="count" class="banner">
    <div
      class="banner-track"
      :style="trackStyle"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
      @pointerleave="onPointerUp"
    >
      <div
        v-for="banner in banners"
        :key="banner.id"
        class="banner-slide"
      >
        <SmartImage
          :src="bannerUrl(banner.id)"
          :placeholder="banner.placeholder"
          :alt="banner.title || '广告图'"
        />
        <button
          class="slide-hit"
          :aria-label="banner.title || '广告图'"
          @click="activate(banner)"
        ></button>
        <span v-if="banner.title" class="banner-title">{{ banner.title }}</span>
      </div>
    </div>

    <button v-if="count > 1" class="arrow prev" aria-label="上一张" @click="select(current - 1)">
      <svg viewBox="0 0 24 24" width="20" height="20">
        <path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>
    <button v-if="count > 1" class="arrow next" aria-label="下一张" @click="select(current + 1)">
      <svg viewBox="0 0 24 24" width="20" height="20">
        <path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>

    <div v-if="count > 1" class="dots">
      <button
        v-for="(banner, index) in banners"
        :key="banner.id"
        class="dot"
        :class="{ active: index === current }"
        :aria-label="`第 ${index + 1} 张`"
        @click="select(index)"
      ></button>
    </div>
  </div>
</template>

<style scoped>
.banner {
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 1;
  overflow: hidden;
  background: var(--mint-100);
  touch-action: pan-y;
  cursor: grab;
}

@media (min-width: 1024px) {
  .banner {
    margin: 24px 32px 0;
    width: auto;
    max-height: 420px;
    border-radius: 16px;
  }
}

.banner:active {
  cursor: grabbing;
}

.banner-track {
  display: flex;
  height: 100%;
}

.banner-slide {
  position: relative;
  flex: 0 0 100%;
  width: 100%;
  height: 100%;
}

.slide-hit {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  padding: 0;
  background: transparent;
}

.banner-title {
  position: absolute;
  left: 14px;
  bottom: 12px;
  padding: 3px 12px;
  border-radius: 999px;
  font-size: 12px;
  color: #fff;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  pointer-events: none;
}

.arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(4px);
  opacity: 0;
  transition: opacity 0.18s ease, background 0.18s ease;
}

.banner:hover .arrow {
  opacity: 1;
}

.arrow:hover {
  background: rgba(0, 0, 0, 0.5);
}

.arrow.prev {
  left: 12px;
}

.arrow.next {
  right: 12px;
}

.dots {
  position: absolute;
  left: 50%;
  bottom: 10px;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
}

.dot {
  width: 6px;
  height: 6px;
  padding: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.25);
  transition: width 0.2s ease, background 0.2s ease;
}

.dot.active {
  width: 18px;
  border-radius: 999px;
  background: #fff;
}
</style>

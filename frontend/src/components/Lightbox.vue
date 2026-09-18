<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { originalUrl, thumbUrl } from '../api'

const props = defineProps({
  images: { type: Array, default: () => [] },
  index: { type: Number, default: -1 }
})

const emit = defineEmits(['close', 'change'])

const scale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)
const dragging = ref(false)
const showInfo = ref(false)
const filmstripRef = ref(null)

const image = computed(() =>
  props.index >= 0 ? props.images[props.index] || null : null
)
const open = computed(() => props.images.length > 0 && props.index >= 0 && !!image.value)

const transform = computed(
  () => `translate(${offsetX.value}px, ${offsetY.value}px) scale(${scale.value})`
)

const pointers = new Map()
let pinching = false
let pinchStartDist = 0
let pinchStartScale = 1
let panStartX = 0
let panStartY = 0
let swipeStartX = 0
let swipeStartY = 0
let swiped = false

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function reset() {
  scale.value = 1
  offsetX.value = 0
  offsetY.value = 0
}

function go(target) {
  if (target < 0 || target >= props.images.length || target === props.index) return
  emit('change', target)
}

function scrollFilmstrip() {
  requestAnimationFrame(() => {
    const active = filmstripRef.value?.querySelector('.film.active')
    active?.scrollIntoView({ inline: 'center', block: 'nearest', behavior: 'smooth' })
  })
}

watch(() => props.index, () => {
  reset()
  showInfo.value = false
  scrollFilmstrip()
})

watch(open, (value) => {
  if (value) scrollFilmstrip()
})

function onWheel(event) {
  event.preventDefault()
  const next = scale.value + (event.deltaY < 0 ? 0.25 : -0.25)
  scale.value = clamp(Number(next.toFixed(2)), 1, 5)
  if (scale.value === 1) reset()
}

function onDoubleClick(event) {
  if (scale.value > 1.05) {
    reset()
    return
  }
  const rect = event.currentTarget.getBoundingClientRect()
  const cx = event.clientX - rect.left - rect.width / 2
  const cy = event.clientY - rect.top - rect.height / 2
  scale.value = 2.5
  offsetX.value = -cx * 1.5
  offsetY.value = -cy * 1.5
}

function pointerDistance() {
  const points = [...pointers.values()]
  if (points.length < 2) return 0
  return Math.hypot(points[0].x - points[1].x, points[0].y - points[1].y)
}

function onPointerDown(event) {
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY })
  event.currentTarget.setPointerCapture?.(event.pointerId)
  if (pointers.size === 2) {
    pinching = true
    dragging.value = false
    pinchStartDist = pointerDistance()
    pinchStartScale = scale.value
  } else if (pointers.size === 1) {
    panStartX = event.clientX - offsetX.value
    panStartY = event.clientY - offsetY.value
    swipeStartX = event.clientX
    swipeStartY = event.clientY
    swiped = false
    dragging.value = scale.value > 1
  }
}

function onPointerMove(event) {
  if (!pointers.has(event.pointerId)) return
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY })

  if (pinching && pointers.size >= 2) {
    const ratio = pointerDistance() / (pinchStartDist || 1)
    scale.value = clamp(Number((pinchStartScale * ratio).toFixed(2)), 1, 5)
    if (scale.value === 1) reset()
  } else if (dragging.value) {
    offsetX.value = event.clientX - panStartX
    offsetY.value = event.clientY - panStartY
  } else if (scale.value === 1) {
    if (Math.abs(event.clientX - swipeStartX) > 8) swiped = true
  }
}

function onPointerUp(event) {
  const wasSingle = pointers.size === 1
  pointers.delete(event.pointerId)
  if (pointers.size < 2) pinching = false

  if (pointers.size > 0) return

  if (dragging.value) {
    dragging.value = false
    return
  }
  if (scale.value === 1 && swiped && wasSingle) {
    const dx = event.clientX - swipeStartX
    const dy = event.clientY - swipeStartY
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) {
      go(props.index + (dx < 0 ? 1 : -1))
    }
  }
}

function onKeydown(event) {
  if (event.key === 'Escape') emit('close')
  else if (event.key === 'ArrowLeft') go(props.index - 1)
  else if (event.key === 'ArrowRight') go(props.index + 1)
  else if (event.key === '+' || event.key === '=') scale.value = clamp(scale.value + 0.25, 1, 5)
  else if (event.key === '-') {
    scale.value = clamp(scale.value - 0.25, 1, 5)
    if (scale.value === 1) reset()
  } else if (event.key === '0') reset()
}

function humanSize(bytes) {
  if (!bytes) return '—'
  const kb = bytes / 1024
  return kb > 1024 ? `${(kb / 1024).toFixed(2)} MB` : `${Math.round(kb)} KB`
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('zh-CN')
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <transition name="fade">
    <div v-if="open" class="lightbox">
      <header class="lb-bar">
        <button class="tool" title="关闭（Esc）" @click="emit('close')">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>

        <div class="lb-title">
          <strong>{{ image.filename }}</strong>
          <span>{{ index + 1 }} / {{ images.length }}</span>
        </div>

        <div class="lb-actions">
          <button
            class="tool"
            :class="{ on: showInfo }"
            title="图片信息"
            @click="showInfo = !showInfo"
          >
            <svg viewBox="0 0 24 24" width="19" height="19">
              <circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.7" />
              <path d="M12 11v5" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" />
              <circle cx="12" cy="7.8" r="1.1" fill="currentColor" />
            </svg>
          </button>
          <a
            class="tool"
            :href="originalUrl(image.id)"
            :download="image.filename"
            title="下载原图"
          >
            <svg viewBox="0 0 24 24" width="19" height="19">
              <path d="M12 4v11m0 0l-4-4m4 4l4-4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M5 19h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </a>
        </div>
      </header>

      <div
        class="lb-stage"
        @wheel="onWheel"
        @dblclick="onDoubleClick"
        @pointerdown="onPointerDown"
        @pointermove="onPointerMove"
        @pointerup="onPointerUp"
        @pointercancel="onPointerUp"
      >
        <button
          v-if="index > 0"
          class="lb-nav prev"
          title="上一张"
          @pointerdown.stop
          @click.stop="go(index - 1)"
        >
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>

        <img
          :src="originalUrl(image.id)"
          :alt="image.filename"
          :style="{ transform }"
          :class="{ dragging }"
          draggable="false"
          @dblclick.stop="onDoubleClick"
        />

        <button
          v-if="index < images.length - 1"
          class="lb-nav next"
          title="下一张"
          @pointerdown.stop
          @click.stop="go(index + 1)"
        >
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>

        <div class="zoom-controls">
          <button title="缩小（-）" @click="scale = clamp(scale - 0.25, 1, 5)">−</button>
          <button title="重置（0）" @click="reset">{{ Math.round(scale * 100) }}%</button>
          <button title="放大（+）" @click="scale = clamp(scale + 0.25, 1, 5)">＋</button>
        </div>
      </div>

      <transition name="sheet">
        <aside v-if="showInfo" class="info-panel">
          <div class="info-row">
            <span>文件名</span><strong>{{ image.filename }}</strong>
          </div>
          <div class="info-row">
            <span>尺寸</span><strong>{{ image.width }} × {{ image.height }}</strong>
          </div>
          <div class="info-row">
            <span>大小</span><strong>{{ humanSize(image.size) }}</strong>
          </div>
          <div class="info-row">
            <span>分类</span><strong>{{ image.category_name || '未分类' }}</strong>
          </div>
          <div class="info-row">
            <span>上传时间</span><strong>{{ formatDate(image.created_at) }}</strong>
          </div>
          <div v-if="image.tags && image.tags.length" class="info-tags">
            <span v-for="tag in image.tags" :key="tag">{{ tag }}</span>
          </div>
        </aside>
      </transition>

      <footer v-if="images.length > 1" ref="filmstripRef" class="filmstrip">
        <button
          v-for="(item, i) in images"
          :key="item.id"
          class="film"
          :class="{ active: i === index }"
          :title="item.filename"
          @click="go(i)"
        >
          <img :src="thumbUrl(item.id)" :alt="item.filename" loading="lazy" />
        </button>
      </footer>
    </div>
  </transition>
</template>

<style scoped>
.lightbox {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  flex-direction: column;
  background: rgba(9, 9, 11, 0.95);
  color: #fff;
}

.lb-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  flex: 0 0 auto;
}

.lb-title {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.lb-title strong {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lb-title span {
  font-size: 11px;
  opacity: 0.6;
}

.lb-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff;
  background: rgba(255, 255, 255, 0.12);
  text-decoration: none;
  transition: background 0.15s ease;
}

.tool:hover {
  background: rgba(255, 255, 255, 0.24);
}

.tool.on {
  background: var(--mint-500);
}

.lb-stage {
  position: relative;
  flex: 1;
  min-height: 0;
  display: grid;
  place-items: center;
  overflow: hidden;
  touch-action: none;
}

.lb-stage img {
  max-width: 94%;
  max-height: 94%;
  user-select: none;
  transition: transform 0.12s ease-out;
  cursor: grab;
}

.lb-stage img.dragging {
  cursor: grabbing;
  transition: none;
}

.lb-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff;
  background: rgba(255, 255, 255, 0.12);
  z-index: 2;
  transition: background 0.15s ease;
}

.lb-nav:hover {
  background: rgba(255, 255, 255, 0.26);
}

.lb-nav.prev {
  left: 12px;
}

.lb-nav.next {
  right: 12px;
}

.zoom-controls {
  position: absolute;
  right: 14px;
  bottom: 14px;
  display: flex;
  align-items: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  overflow: hidden;
}

.zoom-controls button {
  min-width: 38px;
  height: 34px;
  padding: 0 10px;
  color: #fff;
  font-size: 13px;
}

.zoom-controls button:hover {
  background: rgba(255, 255, 255, 0.16);
}

.info-panel {
  flex: 0 0 auto;
  max-height: 40vh;
  overflow-y: auto;
  margin: 0 14px 10px;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(8px);
}

.info-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  padding: 5px 0;
  font-size: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.info-row:last-of-type {
  border-bottom: none;
}

.info-row span {
  opacity: 0.55;
  flex: 0 0 auto;
}

.info-row strong {
  font-weight: 500;
  text-align: right;
  word-break: break-all;
}

.info-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.info-tags span {
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 11px;
  background: rgba(255, 255, 255, 0.14);
}

.filmstrip {
  flex: 0 0 auto;
  display: flex;
  gap: 8px;
  padding: 10px 14px calc(14px + env(safe-area-inset-bottom, 0px));
  overflow-x: auto;
  scrollbar-width: none;
}

.filmstrip::-webkit-scrollbar {
  display: none;
}

.film {
  flex: 0 0 auto;
  width: 48px;
  height: 48px;
  padding: 0;
  border-radius: 8px;
  overflow: hidden;
  opacity: 0.48;
  border: 2px solid transparent;
  transition: opacity 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
}

.film:hover {
  opacity: 0.85;
}

.film.active {
  opacity: 1;
  border-color: var(--mint-500);
  transform: translateY(-2px);
}

.film img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.sheet-enter-active,
.sheet-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.sheet-enter-from,
.sheet-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>

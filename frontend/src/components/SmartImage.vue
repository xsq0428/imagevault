<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
  placeholder: { type: String, default: '' },
  alt: { type: String, default: '' },
  fit: { type: String, default: 'cover' }
})

const loaded = ref(false)
const failed = ref(false)

watch(
  () => props.src,
  () => {
    loaded.value = false
    failed.value = false
  }
)
</script>

<template>
  <span class="smart-image">
    <img
      v-if="placeholder && !loaded"
      class="layer ph"
      :src="placeholder"
      :style="{ objectFit: fit }"
      aria-hidden="true"
      alt=""
      draggable="false"
    />
    <span v-else-if="!loaded && !failed" class="layer skeleton" aria-hidden="true"></span>

    <img
      class="layer real"
      :class="{ loaded }"
      :src="src"
      :alt="alt"
      :style="{ objectFit: fit }"
      loading="lazy"
      decoding="async"
      draggable="false"
      @load="loaded = true"
      @error="failed = true"
    />

    <slot />
  </span>
</template>

<style scoped>
.smart-image {
  position: relative;
  display: block;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: var(--mint-100);
}

.layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
  pointer-events: none;
}

.ph {
  filter: blur(14px);
  transform: scale(1.08);
}

.real {
  opacity: 0;
  transition: opacity 0.45s ease;
}

.real.loaded {
  opacity: 1;
}

.skeleton {
  background: linear-gradient(100deg, #ececec 30%, #f7f7f7 50%, #ececec 70%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}

@keyframes shimmer {
  from {
    background-position: 200% 0;
  }
  to {
    background-position: -200% 0;
  }
}
</style>

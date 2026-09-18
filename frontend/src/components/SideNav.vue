<script setup>
defineProps({
  categories: { type: Array, required: true },
  active: { type: [String, Number], default: '' }
})

const emit = defineEmits(['select'])
</script>

<template>
  <aside class="rail">
    <button
      class="rail-item"
      :class="{ active: active === '' || active === null }"
      @click="emit('select', null)"
    >
      全部
    </button>
    <button
      v-for="category in categories"
      :key="category.id"
      class="rail-item"
      :class="{ active: category.id === active }"
      @click="emit('select', category.id)"
    >
      {{ category.name }}
    </button>
  </aside>
</template>

<style scoped>
.rail {
  flex: 0 0 auto;
  width: 96px;
  align-self: flex-start;
  position: sticky;
  top: var(--search-h, 62px);
  max-height: calc(100dvh - var(--search-h, 62px));
  overflow-y: auto;
  background: #f5f6f5;
  padding-bottom: 80px;
  scrollbar-width: none;
}

.rail::-webkit-scrollbar {
  display: none;
}

.rail-item {
  position: relative;
  display: block;
  width: 100%;
  padding: 15px 10px;
  font-size: 13px;
  line-height: 1.3;
  text-align: center;
  color: var(--ink-500);
  background: transparent;
  border: none;
  transition: background 0.15s ease, color 0.15s ease;
}

.rail-item:hover {
  color: var(--mint-600);
}

.rail-item.active {
  background: var(--white);
  color: var(--mint-600);
  font-weight: 600;
}

.rail-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 22px;
  border-radius: 0 4px 4px 0;
  background: var(--mint-500);
}

@media (min-width: 768px) {
  .rail {
    width: 120px;
  }
  .rail-item {
    padding: 17px 12px;
    font-size: 14px;
  }
}

@media (min-width: 1024px) {
  .rail {
    width: 150px;
    top: 0;
    max-height: 100dvh;
    padding-bottom: 24px;
  }
  .rail-item {
    padding: 18px 14px;
    font-size: 14px;
  }
}
</style>

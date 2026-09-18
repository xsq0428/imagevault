<script setup>
import { computed } from 'vue'
import MediaCard from './MediaCard.vue'

const props = defineProps({
  items: { type: Array, required: true },
  selectedIds: { type: Array, default: () => [] },
  selectable: { type: Boolean, default: false }
})

const emit = defineEmits(['open', 'open-set', 'toggle-select'])

const selectedSet = computed(() => new Set(props.selectedIds))
</script>

<template>
  <div class="grid">
    <MediaCard
      v-for="item in items"
      :key="`${item.item_type}-${item.id}`"
      :item="item"
      :selectable="selectable"
      :selected="selectedSet.has(item.id)"
      @open="emit('open', $event)"
      @open-set="emit('open-set', $event)"
      @toggle-select="emit('toggle-select', $event)"
    />
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

@media (min-width: 768px) {
  .grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
  }
}

@media (min-width: 1024px) {
  .grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px;
  }
}

@media (min-width: 1360px) {
  .grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}
</style>

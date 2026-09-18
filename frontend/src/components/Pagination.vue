<script setup>
import { computed } from 'vue'

const props = defineProps({
  page: { type: Number, required: true },
  total: { type: Number, required: true },
  limit: { type: Number, required: true }
})

const emit = defineEmits(['change'])

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.limit)))

const pages = computed(() => {
  const last = totalPages.value
  const current = props.page
  const start = Math.max(1, Math.min(current - 1, last - 2))
  const end = Math.min(last, start + 2)
  const result = []
  for (let i = start; i <= end; i += 1) result.push(i)
  return result
})

function go(target) {
  if (target < 1 || target > totalPages.value || target === props.page) return
  emit('change', target)
}
</script>

<template>
  <nav v-if="totalPages > 1" class="pagination">
    <button class="page-arrow" :disabled="page <= 1" @click="go(page - 1)">上一页</button>

    <button
      v-for="item in pages"
      :key="item"
      class="page-item"
      :class="{ active: item === page }"
      @click="go(item)"
    >
      {{ item }}
    </button>

    <button class="page-arrow" :disabled="page >= totalPages" @click="go(page + 1)">下一页</button>
  </nav>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 22px 0 6px;
  flex-wrap: wrap;
}

.page-item,
.page-arrow {
  min-width: 38px;
  height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: var(--white);
  color: var(--ink-500);
  font-size: 13px;
  box-shadow: var(--shadow-card);
  transition: background 0.15s ease, color 0.15s ease;
}

.page-item:hover,
.page-arrow:hover:not(:disabled) {
  color: var(--mint-600);
}

.page-item.active {
  background: var(--mint-500);
  color: var(--white);
}

.page-arrow:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>

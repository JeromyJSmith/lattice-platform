<template>
  <div class="row-actions">
    <button @click="onCorrect(true)" class="action-btn">👍</button>
    <button @click="onCorrect(false)" class="action-btn">👎</button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  params: {
    data: RowData;
  };
}>();

import { handleCorrect } from "../../stores/autocompleteStore";

function onCorrect(isCorrect: boolean) {
  handleCorrect(props.params.data.model, isCorrect);
}
</script>

<style scoped>
.row-actions {
  display: flex;
  gap: 8px;
  justify-content: space-between;
  padding: 0 20px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  font-size: 1.2em;
  transition: transform 0.1s;
}

.action-btn:hover {
  transform: scale(1.2);
}
</style>

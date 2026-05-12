<template>
  <div class="tool-randomizer">
    <select
      v-model="selectedCount"
      @change="handleSelection"
      class="styled-select"
    >
      <option value="">Randomize tool count...</option>
      <option value="reset">Clear list</option>
      <option v-for="count in toolCounts" :key="count" :value="count">
        Randomize {{ count }} tools
      </option>
    </select>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import { store } from "../../stores/toolCallStore";
import { allTools } from "../../utils";

const selectedCount = ref("");
const toolCounts = [3, 5, 7, 9, 11, 13, 15];

function handleSelection() {
  if (selectedCount.value === "reset") {
    store.expectedToolCalls = [];
  } else if (selectedCount.value) {
    const count = parseInt(selectedCount.value);
    const randomTools: string[] = [];

    // Create a copy of allTools to avoid modifying the original
    const availableTools = [...allTools];

    // Generate random selections
    while (randomTools.length < count && availableTools.length > 0) {
      const randomIndex = Math.floor(Math.random() * availableTools.length);
      randomTools.push(availableTools[randomIndex]);
    }

    store.expectedToolCalls = randomTools;
  }

  // Reset selection to placeholder
  selectedCount.value = "";
}
</script>

<style scoped>
.styled-select {
  appearance: none;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 32px 8px 12px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  min-width: 200px;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
}

.styled-select:hover {
  border-color: #bbb;
}

.styled-select:focus {
  outline: none;
  border-color: rgb(14, 68, 145);
  box-shadow: 0 0 0 2px rgba(14, 68, 145, 0.1);
}

.styled-select option {
  padding: 8px;
}
</style>

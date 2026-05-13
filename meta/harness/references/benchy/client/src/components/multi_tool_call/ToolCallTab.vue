<template>
  <div class="toolcalltab-w">
    <div style="display: flex; gap: 1rem; align-items: flex-start">
      <ToolCallExpectationList />
    </div>

    <div class="prompt-section">
      <h2 class="prompt-header">Tool Call Prompt</h2>
      <div class="prompt-content">
        <ToolCallInputField />
        <button
          @click="runToolCall"
          class="run-button"
          :disabled="store.isLoading"
        >
          {{ store.isLoading ? "Running..." : "Run Tool Call Prompt" }}
        </button>
      </div>
    </div>

    <ToolCallTable />
  </div>
</template>

<script lang="ts" setup>
import ToolCallInputField from "./ToolCallInputField.vue";
import ToolCallExpectationList from "./ToolCallExpectationList.vue";
import ToolCallTable from "../multi_tool_call/ToolCallTable.vue";
import { store } from "../../stores/toolCallStore";
import { runToolCall } from "../../apis/toolCallApi";
</script>

<style scoped>
.prompt-section {
  background-color: #f5f5f5;
  padding: 1rem 0 1rem 1rem;
  border-radius: 4px;
  width: auto;
}

.prompt-header {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin: 5px 0 4px 0;
}

.prompt-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.toolcalltab-w {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.run-button {
  background: linear-gradient(
    90deg,
    rgba(14, 68, 145, 1) 0%,
    rgba(0, 212, 255, 1) 100%
  );
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  align-self: flex-start;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.7);
  transition: box-shadow 0.3s ease-in-out;
}

.run-button:hover {
  box-shadow: 0 0 20px rgba(0, 212, 255, 1);
}

.run-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>

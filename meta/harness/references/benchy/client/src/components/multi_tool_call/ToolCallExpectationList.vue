<template>
  <div class="expectation-section">
    <h2 class="expectation-header" style="margin: 5px 0 4px 0">
      Expected Tools
    </h2>
    <div class="toolcallexpectationlist-w">
      <div class="tool-selector">
        <select
          v-model="selectedTool"
          @change="addToolCall"
          class="styled-select"
        >
          <option value="">Select a tool</option>
          <option v-for="tool in allTools" :key="tool" :value="tool">
            {{ getToolEmoji(tool) }} {{ tool }}
          </option>
        </select>
        <ToolCallExpectationRandomizer />
      </div>
      <div class="tool-tags">
        <div
          v-for="(tool, index) in store.expectedToolCalls"
          :key="index"
          class="tool-tag"
          :style="{ 
            backgroundColor: stringToColor(tool),
            color: getContrastTextColor(stringToColor(tool))
          }"
        >
          {{ getToolEmoji(tool) }} {{ tool }}
          <button @click="removeToolCall(index)" class="remove-tag">×</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import { store } from "../../stores/toolCallStore";
import { allTools, stringToColor, getContrastTextColor } from "../../utils";
import ToolCallExpectationRandomizer from "./ToolCallExpectationRandomizer.vue";

function getToolEmoji(toolName: string): string {
  const emojiMap: Record<string, string> = {
    run_coder_agent: "🤖",
    run_git_agent: "📦",
    run_docs_agent: "📝",
    // Add more mappings as needed
  };
  return emojiMap[toolName] || "🔧"; // Default emoji if no mapping exists
}
// Using imported stringToColor from utils

const selectedTool = ref("");

function addToolCall() {
  if (selectedTool.value) {
    store.expectedToolCalls.push(selectedTool.value);
    selectedTool.value = ""; // Reset selection
  }
}

function removeToolCall(index: number) {
  store.expectedToolCalls.splice(index, 1);
}
</script>

<style scoped>
.expectation-section {
  background-color: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  width: 100%;
}

.expectation-header {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
}

.toolcallexpectationlist-w {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.tool-selector {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}
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

.tool-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tool-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  color: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: transform 0.1s ease, box-shadow 0.1s ease;
  font-size: 1.2rem;
}

.tool-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
}

.remove-tag {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0;
  font-size: 1.2rem;
  line-height: 1;
}

.remove-tag:hover {
  opacity: 0.8;
}
</style>

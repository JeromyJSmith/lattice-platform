<script setup lang="ts">
import AutocompleteTab from "../components/multi_autocomplete/AutocompleteTab.vue";
import PromptTab from "../components/multi_autocomplete/PromptTab.vue";
import DevNotes from "../components/multi_autocomplete/DevNotes.vue";
import { store, resetState } from "../stores/autocompleteStore";

function saveState() {
  localStorage.setItem("appState", JSON.stringify(store));
}

document.title = "Multi Autocomplete LLM Benchmark";
</script>

<template>
  <div class="container">
    <h1>Multi Autocomplete LLM Benchmark</h1>
    <div class="tabs-container">
      <div class="tabs">
        <button
          :class="{ active: store.activeTab === 'benchmark' }"
          @click="store.activeTab = 'benchmark'"
        >
          Benchmark
        </button>
        <button
          :class="{ active: store.activeTab === 'prompt' }"
          @click="store.activeTab = 'prompt'"
        >
          Prompt
        </button>
        <button
          :class="{ active: store.activeTab === 'notes' }"
          @click="store.activeTab = 'notes'"
        >
          Notes
        </button>
      </div>
      <div class="state-controls">
        <button class="state-button save" @click="saveState">Save</button>
        <button class="state-button reset" @click="resetState">Reset</button>
      </div>
    </div>

    <div class="tab-content !w-1200px">
      <AutocompleteTab v-if="store.activeTab === 'benchmark'" />
      <PromptTab
        v-else-if="store.activeTab === 'prompt'"
        :prompt="store.basePrompt"
      />
      <DevNotes v-else />
    </div>
  </div>
</template>

<style scoped>
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

h1 {
  margin-bottom: 20px;
  color: rgb(14, 68, 145);
}

.tabs-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.tabs {
  display: flex;
}

.tabs button {
  padding: 10px 20px;
  margin-right: 10px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  color: #666;
}

.tabs button.active {
  color: rgb(14, 68, 145);
  border-bottom: 2px solid rgb(14, 68, 145);
}

.state-controls {
  display: flex;
  gap: 10px;
}

.state-button {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  color: white;
}

.state-button.save {
  background-color: rgb(14, 68, 145);
}

.state-button.save:hover {
  background-color: rgb(11, 54, 116);
}

.state-button.reset {
  background-color: rgb(145, 14, 14);
}

.state-button.reset:hover {
  background-color: rgb(116, 11, 11);
}

.tab-content {
  flex: 1;
  min-height: 0;
}
</style>

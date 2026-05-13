<template>
  <div class="container">
    <h1 v-if="store.settings.modelStatDetail !== 'hide'">Thought Bench</h1>

    <div
      class="benchmark-info"
      v-if="store.settings.modelStatDetail !== 'hide'"
    >
      <p>
        Analyze models reasoning processes and response quality through thought
        visualization.
      </p>
    </div>

    <div class="controls">
      <button
        @click="runBenchmark"
        :disabled="store.apiCallInProgress || isAnyColumnLoading"
      >
        {{ runButtonText }}
      </button>
      <button @click="clickResetState">Reset</button>
      <button @click="showSettings = !showSettings">
        {{ showSettings ? "Hide" : "Show" }} Settings
      </button>

      <div v-if="showSettings" class="settings-row">
        <div class="setting">
          <label>Model Stats:</label>
          <select v-model="store.settings.modelStatDetail">
            <option value="verbose">Verbose</option>
            <option value="hide">Hide</option>
          </select>
        </div>
        <div class="setting">
          <label>Column Height:</label>
          <input
            type="range"
            v-model.number="store.settings.columnHeight"
            min="100"
            max="1500"
            class="slider"
          />
          <span>{{ store.settings.columnHeight }}px</span>
        </div>
        <div class="setting">
          <label>Column Width:</label>
          <input
            type="range"
            v-model.number="store.settings.columnWidth"
            min="200"
            max="1500"
            class="slider"
          />
          <span>{{ store.settings.columnWidth }}px</span>
        </div>
        <div class="setting">
          <label>Display:</label>
          <select v-model="store.settings.columnDisplay">
            <option value="both">Both Sections</option>
            <option value="thoughts">Only Thoughts</option>
            <option value="response">Only Response</option>
          </select>
        </div>
      </div>
    </div>

    <div class="prompt-area">
      <textarea
        v-model="store.prompt"
        @keydown.ctrl.enter.prevent="runBenchmark"
        @keydown.meta.enter.prevent="runBenchmark"
        placeholder="Enter your reasoning prompt..."
        class="prompt-input"
      ></textarea>

      <div class="model-input-container">
        <div class="model-pills">
          <div
            v-for="model in store.dataColumns"
            :key="model.model"
            class="model-pill"
            :style="{
              backgroundColor: stringToColor(model.model),
              color: getContrastTextColor(stringToColor(model.model)),
              borderColor: isSoloed(model.model) ? '#0e4491' : 'transparent',
            }"
          >
            <span class="model-name">{{ model.model }}</span>
            <div class="pill-controls">
              <span
                class="solo-icon"
                @click="toggleSolo(model.model)"
                :title="
                  isSoloed(model.model) ? 'Show all models' : 'Solo this model'
                "
              >
                {{ isSoloed(model.model) ? "👀" : "👁️" }}
              </span>
              <span
                class="delete-icon"
                @click="removeModel(model.model)"
                title="Remove model"
              >
                ❌
              </span>
            </div>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem">
          <input
            v-model="store.newModel"
            @keyup.enter="addModel"
            placeholder="Add model (provider:model-name)"
            class="model-input"
          />
          <button @click="addModel" class="add-model-button">Add</button>
        </div>
      </div>
    </div>

    <div class="response-grid">
      <ThoughtColumn
        v-for="(column, index) in filteredColumns"
        :key="index"
        :columnData="column"
        :columnHeight="store.settings.columnHeight"
        @retry="runSingleBenchmark(column.model)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { stringToColor, getContrastTextColor } from "../utils";
import { store, resetState } from "../stores/thoughtBenchStore";

// Add reset handler
function clickResetState() {
  resetState();
  soloedModels.value = [];
}
import ThoughtColumn from "../components/thought_bench/ThoughtColumn.vue";
import { runThoughtPrompt } from "../apis/thoughtBenchApi";

const showSettings = ref(false);
const soloedModels = ref<string[]>([]);
function toggleSolo(model: string) {
  const index = soloedModels.value.indexOf(model);
  if (index === -1) {
    soloedModels.value.push(model);
  } else {
    soloedModels.value = [];
  }
}

function isSoloed(model: string) {
  return soloedModels.value.includes(model);
}

const filteredColumns = computed(() => {
  if (soloedModels.value.length === 0) return store.dataColumns;
  return store.dataColumns.filter((c) => soloedModels.value.includes(c.model));
});

function removeModel(model: string) {
  const index = store.dataColumns.findIndex((c) => c.model === model);
  if (index !== -1) {
    store.dataColumns.splice(index, 1);
  }
  const soloIndex = soloedModels.value.indexOf(model);
  if (soloIndex !== -1) {
    soloedModels.value.splice(soloIndex, 1);
  }
}

const isAnyColumnLoading = computed(() =>
  store.dataColumns.some((c) => c.state === "loading")
);

const runButtonText = computed(() => {
  if (store.apiCallInProgress) {
    const runningCount = store.dataColumns.filter(
      (c) => c.state === "loading"
    ).length;
    return `Running (${runningCount}/${store.dataColumns.length})`;
  }
  return "Thought Prompt";
});

function addModel() {
  if (!store.newModel.trim()) return;

  // Validate model format
  if (!store.newModel.includes(":")) {
    alert('Model must be in format "provider:model-name"');
    return;
  }

  // Check for duplicates
  if (store.dataColumns.some((c) => c.model === store.newModel)) {
    alert("Model already exists in benchmark");
    return;
  }

  store.dataColumns.push({
    model: store.newModel.trim(),
    totalCorrect: 0,
    responses: [],
    state: "idle",
  });

  store.newModel = "";
}

async function runBenchmark() {
  if (store.apiCallInProgress || isAnyColumnLoading.value) return;

  store.apiCallInProgress = true;
  try {
    const promises = store.dataColumns.map((column) =>
      runSingleBenchmark(column.model)
    );
    await Promise.allSettled(promises);
  } finally {
    store.apiCallInProgress = false;
  }
}

async function runSingleBenchmark(model: string) {
  const column = store.dataColumns.find((c) => c.model === model);
  if (!column || column.state === "loading") return;

  try {
    column.state = "loading";
    store.totalExecutions++;
    const response = await runThoughtPrompt({
      prompt: store.prompt,
      model: model,
    });

    column.responses.unshift(response);
    if (!response.error) column.totalCorrect++;
    column.state = "success";
  } catch (error) {
    console.error(`Error running benchmark for ${model}:`, error);
    column.responses.unshift({
      thoughts: "",
      response: `Error: ${(error as Error).message}`,
      error: (error as Error).message,
    });
    column.state = "error";
  } finally {
    column.state = "idle";
  }
}
</script>

<style scoped>
.container {
  background: #0a0f1b;
  min-height: 100vh;
  padding: 1.5rem;
  color: #e0e6eb;
}

h1 {
  font-size: 1.25rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  background: linear-gradient(90deg, #00d4ff 0%, #00ff88 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.benchmark-info {
  margin-bottom: 1rem;
  font-size: 0.75rem;
  color: #8b92a8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.prompt-area {
  margin: 1rem 0;
  position: relative;
}

.prompt-input {
  width: 100%;
  height: 100px;
  padding: 0.75rem;
  background: rgba(20, 28, 40, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 0.375rem;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
  font-size: 0.875rem;
  color: #e0e6eb;
  resize: vertical;
  transition: all 0.2s ease;
}

.prompt-input::placeholder {
  color: #4a5568;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}

.prompt-input:focus {
  outline: none;
  border-color: #00d4ff;
  background: rgba(20, 28, 40, 0.8);
  box-shadow: 0 0 0 1px rgba(0, 212, 255, 0.1);
}

.response-grid {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 1rem;
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 212, 255, 0.3) transparent;
}

.response-grid::-webkit-scrollbar {
  height: 8px;
}

.response-grid::-webkit-scrollbar-track {
  background: rgba(0, 212, 255, 0.05);
  border-radius: 4px;
}

.response-grid::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.3);
  border-radius: 4px;
}

.response-grid::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.5);
}

.controls {
  margin-bottom: 1rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
  position: relative;
}

.settings-row {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  display: flex;
  gap: 1.5rem;
  padding: 1rem;
  background: rgba(20, 28, 40, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 0.5rem;
  margin-top: 0.5rem;
  z-index: 10;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
}

.setting {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.setting label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #8b92a8;
}

.setting select,
.setting input[type="range"] {
  background: rgba(10, 15, 27, 0.8);
  border: 1px solid rgba(0, 212, 255, 0.2);
  color: #e0e6eb;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.slider {
  width: 80px;
}

.setting span {
  font-size: 0.75rem;
  color: #00d4ff;
  font-weight: 600;
}

button {
  padding: 0.5rem 1rem;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 0.25rem;
  color: #00d4ff;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(0, 212, 255, 0.2);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.3s, height 0.3s;
}

button:hover::before {
  width: 100%;
  height: 100%;
}

button:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(0, 212, 255, 0.05);
}

button:disabled:hover {
  transform: none;
  box-shadow: none;
}

.model-pills {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.model-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.25rem;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
  background: rgba(20, 28, 40, 0.8);
}

.model-pill::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 0.25rem;
  padding: 1px;
  background: linear-gradient(45deg, transparent, rgba(0, 212, 255, 0.3), transparent);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.2s;
}

.model-pill:hover::before {
  opacity: 1;
}

.model-pill:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.model-name {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #e0e6eb;
}

.pill-controls {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}

.solo-icon,
.delete-icon {
  cursor: pointer;
  opacity: 0.6;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.solo-icon:hover,
.delete-icon:hover {
  opacity: 1;
  transform: scale(1.1);
}

.delete-icon {
  filter: hue-rotate(320deg);
}

.model-input-container {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.model-input {
  padding: 0.5rem 0.75rem;
  background: rgba(20, 28, 40, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 0.25rem;
  color: #e0e6eb;
  font-size: 0.75rem;
  width: 280px;
  transition: all 0.2s ease;
}

.model-input::placeholder {
  color: #4a5568;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.model-input:focus {
  outline: none;
  border-color: #00d4ff;
  background: rgba(20, 28, 40, 0.8);
}

.add-model-button {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #00d4ff 0%, #00ff88 100%);
  color: #0a0f1b;
  border: none;
  border-radius: 0.25rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-model-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.4);
}
</style>

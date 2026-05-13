<template>
  <div class="container" :class="{ 'bench-mode': store.settings.benchMode }">
    <h1 v-if="!store.settings.benchMode">ISO Speed Bench</h1>

    <!-- UPLOAD FILE UI -->
    <div v-if="!store.benchmarkReport">
      <div
        class="file-drop"
        @dragover.prevent
        @drop="handleFileDrop"
        @dragenter.prevent
        :class="{ loading: store.isLoading }"
        :aria-busy="store.isLoading"
      >
        <div v-if="store.isLoading" class="loading-content">
          <div class="loading-spinner"></div>
          <p>Running benchmarks... Please wait</p>
        </div>
        <div v-else>
          <p>Drag & Drop YAML or JSON file here</p>
          <p>or</p>
          <button @click="fileInputRef?.click()" class="upload-button">
            Choose File
          </button>
        </div>
      </div>

      <!-- Hidden file input -->
      <input
        type="file"
        ref="fileInputRef"
        @change="handleFileSelect"
        accept=".yaml,.yml,.json"
        style="display: none"
      />

      <!-- UPLOADED SHOW DATA -->
      <!-- wip -->
      <template v-if="false">
        <div class="base-prompt-collapsible">
          <button @click="togglePrompt" class="collapse-button">
            {{
              showUploadedTempPrompt ? "Hide Base Prompt" : "Show Base Prompt"
            }}
          </button>
          <div v-if="showUploadedTempPrompt" class="benchmark-prompt">
            <pre>{{ tempUploadedBenchmark?.base_prompt }}</pre>
          </div>
        </div>
        <div class="prompt-iterations" v-if="tempUploadedBenchmark?.prompts">
          <h3>Prompt Iterations</h3>
          <ul>
            <li
              v-for="(iteration, idx) in tempUploadedBenchmark.prompts"
              :key="idx"
            >
              <pre>{{ iteration }}</pre>
            </li>
          </ul>
        </div>
      </template>

      <!-- DEFAULT -->
      <template v-else>
        <button @click="useSampleData" class="sample-data-button">
          Or use sample data
        </button>

        <!-- how to use -->
        <div class="how-to-use">
          <h2>How to use</h2>
          <p>Drag & Drop a YAML or JSON file into the file drop area.</p>
          <p>
            You can find YAML benchmark configuration files in
            'server/benchmark_data/*.yaml' to run against your own machine.
            Study this file to see how to structure your own.
          </p>
          <p>
            Or you can find JSON benchmark result files in
            'server/reports/*.json' to see how existing/your models performed.
          </p>
          <p>
            Or click the "Or use sample data" button to use a pre-defined
            dataset.
          </p>
          <p></p>
        </div>
      </template>
    </div>

    <!-- FULL BENCHMARK UI -->
    <div v-else class="benchmark-container">
      <div class="benchmark-info">
        <h2>{{ store.benchmarkReport.benchmark_name }}</h2>
        <p>{{ store.benchmarkReport.purpose }}</p>
        <div style="display: flex; gap: 10px; margin-top: 10px">
          <button @click="togglePrompt" class="collapse-button">
            {{ showPrompt ? "Hide Prompt" : "Show Prompt" }}
          </button>
          <button @click="toggleTestData" class="collapse-button">
            {{ showTestData ? "Hide Test Data" : "Show Test Data" }}
          </button>
        </div>
        <div v-if="showPrompt" class="benchmark-prompt">
          <h3>Prompt</h3>
          <pre>{{ store.benchmarkReport.base_prompt }}</pre>
        </div>
        <div
          v-if="showTestData && store.benchmarkReport?.prompt_iterations"
          class="test-data"
        >
          <h3>Test Data</h3>
          <pre>{{
            JSON.stringify(store.benchmarkReport.prompt_iterations, null, 2)
          }}</pre>
        </div>
      </div>

      <div class="controls">
        <button @click="startBenchmark()">Play Benchmark</button>
        <button @click="flashBenchmark()">Flash Benchmark</button>
        <button @click="fullReset">Reset</button>
        <button @click="showSettings = !showSettings">
          {{ showSettings ? "Hide" : "Show" }} Settings
        </button>

        <div v-if="showSettings" class="settings-row">
          <div class="setting">
            <label>Bench Mode:</label>
            <input type="checkbox" v-model="settings.benchMode" />
          </div>
          <div class="setting">
            <label>Speed (ms):</label>
            <input
              type="range"
              v-model="settings.speed"
              min="10"
              max="1000"
              class="slider"
            />
            <span>{{ settings.speed }}ms</span>
          </div>

          <div class="setting">
            <label>Block Scale:</label>
            <input
              type="range"
              v-model="settings.scale"
              min="20"
              max="150"
              class="slider"
            />
            <span>{{ settings.scale }}px</span>
          </div>

          <div class="setting">
            <label>Model Stats:</label>
            <select v-model="settings.modelStatDetail">
              <option value="verbose">Verbose</option>
              <option value="simple">Simple</option>
              <option value="hide">Hide</option>
            </select>
          </div>
          <div class="setting">
            <label>Show Provider:</label>
            <input type="checkbox" v-model="settings.showProviderPrefix" />
          </div>
        </div>
      </div>

      <IsoSpeedBenchRow
        v-for="(modelReport, index) in store.benchmarkReport.models"
        :key="index"
        :modelReport="modelReport"
        :scale="Number(settings.scale)"
        :modelStatDetail="settings.modelStatDetail"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import {
  store,
  resetBenchmark,
  startBenchmark,
  flashBenchmark,
  inMemoryBenchmarkReport,
} from "../stores/isoSpeedBenchStore";
import YAML from "yamljs";
import { ExecEvalBenchmarkFile } from "../types";
const tempUploadedBenchmark = ref<ExecEvalBenchmarkFile | null>(null);

const fileInputRef = ref<HTMLInputElement | null>(null);

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file) {
    processFile(file);
  }
  // Reset the input so the same file can be selected again
  input.value = "";
}

function processFile(file: File) {
  const reader = new FileReader();
  reader.onload = async (e) => {
    const content = e.target?.result;
    if (typeof content !== "string") return;

    if (file.name.endsWith(".json")) {
      try {
        const jsonData = JSON.parse(content);
        if (
          jsonData.benchmark_name &&
          jsonData.models &&
          Array.isArray(jsonData.models)
        ) {
          store.benchmarkReport = jsonData;
          return;
        }
      } catch (error) {
        console.error("Error parsing JSON:", error);
        alert("Invalid JSON file format");
        return;
      }
    }

    if (file.name.endsWith(".yaml") || file.name.endsWith(".yml")) {
      tempUploadedBenchmark.value = YAML.parse(content);
      console.log(`tempUploadedBenchmark.value`, tempUploadedBenchmark.value);
      try {
        store.isLoading = true;
        const response = await fetch("/iso-speed-bench", {
          method: "POST",
          headers: {
            "Content-Type": "application/yaml",
          },
          body: content,
        });
        const responseText = await response.text();

        store.benchmarkReport = JSON.parse(responseText);
      } catch (error) {
        console.error("Error running benchmark:", error);
        alert("Error processing YAML file");
      } finally {
        store.isLoading = false;
      }
    }
  };
  reader.readAsText(file);
}
import IsoSpeedBenchRow from "../components/iso_speed_bench/IsoSpeedBenchRow.vue";

const showSettings = ref(false);
const { settings } = store;
const showPrompt = ref(false);
const showTestData = ref(false);
const showUploadedTempPrompt = ref(false);

function togglePrompt() {
  showPrompt.value = !showPrompt.value;
}

function toggleTestData() {
  showTestData.value = !showTestData.value;
}

function useSampleData() {
  store.benchmarkReport = inMemoryBenchmarkReport;
}

function fullReset() {
  resetBenchmark();
  store.benchmarkReport = null;
}

function handleFileDrop(event: DragEvent) {
  event.preventDefault();
  const file = event.dataTransfer?.files[0];
  if (file) {
    processFile(file);
  }
}
</script>

<style scoped>
.container {
  padding: 20px;
  max-width: 95vw;
  min-width: 70vw;
  margin: 0 auto;
}

.file-drop {
  border: 2px dashed #ccc;
  padding: 20px;
  text-align: center;
  margin: 20px 0;
  cursor: pointer;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  .upload-button {
    margin-top: 10px;
    padding: 8px 16px;
    background-color: #e0e0e0;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
      background-color: #d0d0d0;
    }
  }
}

.file-drop.loading {
  border-color: #666;
  background-color: #f5f5f5;
  cursor: wait;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.speed-control {
  margin: 20px 0;
}

button {
  padding: 8px 16px;
  background-color: #e0e0e0; /* Light gray */
  color: #333; /* Darker text for better contrast */
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #d0d0d0; /* Slightly darker on hover */
}

.sample-data-button {
  margin-bottom: 20px;
  background-color: #e0e0e0; /* Light gray */
}

.sample-data-button:hover {
  background-color: #d0d0d0; /* Slightly darker on hover */
}

.controls button {
  background-color: #e0e0e0; /* Light gray */
}

.controls button:hover {
  background-color: #d0d0d0; /* Slightly darker on hover */
}

.benchmark-info {
  display: v-bind('benchMode ? "none" : "block"');
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.benchmark-info h2 {
  margin: 0 0 10px 0;
  font-size: 1.8em;
}

.benchmark-info p {
  margin: 0;
  color: #666;
  font-size: 1.1em;
  line-height: 1.5;
}

.loading-spinner {
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top: 3px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

.controls {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: flex-start;
  min-width: 200px;
  overflow: visible; /* Ensure settings are visible */
}

.settings-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  max-width: 600px; /* Add max-width constraint */
  overflow: hidden; /* Prevent overflow */
  margin-left: auto; /* Keep aligned to right */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.setting {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1 1 200px;
}

.slider {
  width: 100px;
}

select {
  padding: 4px;
  border-radius: 4px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
.bench-mode {
  padding: 10px;

  h1 {
    display: none;
  }

  .benchmark-info {
    display: none;
  }

  .controls {
    margin-bottom: 10px;
  }

  .row {
    margin-bottom: 20px;
  }
}
</style>

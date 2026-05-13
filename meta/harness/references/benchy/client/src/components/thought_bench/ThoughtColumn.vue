<template>
  <div
    class="thought-column"
    :class="columnData.state"
    :style="{ width: `${store.settings.columnWidth}px` }"
  >
    <div class="column-header">
      <div
        class="provider-logo-wrapper"
        style="display: flex; align-items: center; width: 100%"
      >
        <div class="provider-logo" v-if="getProviderFromModel">
          <img
            class="provider-logo-img"
            :src="getProviderLogo"
            :alt="getProviderFromModel"
          />
        </div>
        <h3
          :style="{
            margin: 0,
            width: '100%',
            lineHeight: 2,
            backgroundColor: modelBackgroundColor,
            color: modelTextColor,
          }"
        >
          {{ columnData.model }}
        </h3>
      </div>
      <div class="stats">
        <span>
          <!-- optional spot for stats -->
        </span>
      </div>
    </div>

    <div class="responses-container">
      <div v-if="columnData.state === 'loading'" class="loading-indicator">
        <div class="spinner"></div>
        <span>Processing...</span>
      </div>

      <div v-else-if="columnData.state === 'error'" class="error-message">
        <span>{{ columnData.responses[0]?.error }}</span>
        <button @click="$emit('retry', columnData.model)">Retry</button>
      </div>

      <template v-else>
        <div
          v-for="(response, index) in columnData.responses"
          :key="index"
          class="response-card"
        >
          <div class="response-header">
            <span>Prompt #{{ columnData.responses.length - index }}</span>
          </div>

          <div class="thought-section" v-if="store.settings.columnDisplay !== 'response'">
            <div class="section-header">
              <h4>Thoughts</h4>
              <button
                @click="copyToClipboard(response.thoughts)"
                class="copy-button"
              >
                Copy
              </button>
            </div>
            <div class="content" :style="{ maxHeight: columnHeight + 'px' }">
              <VueMarkdown
                v-if="response.thoughts"
                :source="response.thoughts"
                class="markdown-content"
              />
              <span v-else>No thoughts provided</span>
            </div>
          </div>

          <div class="response-section" v-if="store.settings.columnDisplay !== 'thoughts'">
            <div class="section-header">
              <h4>Response</h4>
              <button
                @click="copyToClipboard(response.response)"
                class="copy-button"
              >
                Copy
              </button>
            </div>
            <div class="content" :style="{ maxHeight: columnHeight + 'px' }">
              <VueMarkdown
                :source="response.response"
                class="markdown-content"
              />
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { store } from "../../stores/thoughtBenchStore";
import type { ThoughtBenchColumnData } from "../../types";
import { copyToClipboard } from "../../utils";
import VueMarkdown from "vue-markdown-render";
import { computed } from "vue";
import { stringToColor, getContrastTextColor } from "../../utils";
import anthropicLogo from "../../assets/anthropic.svg";
import ollamaLogo from "../../assets/ollama.svg";
import openaiLogo from "../../assets/openai.svg";
import googleLogo from "../../assets/google.svg";
import groqLogo from "../../assets/groq.svg";
import deepseekLogo from "../../assets/deepseek.svg";

const props = defineProps<{
  columnData: ThoughtBenchColumnData;
  columnHeight: number;
}>();

const emit = defineEmits<{
  (e: "retry", model: string): void;
}>();

const getProviderFromModel = computed(() => {
  const provider = props.columnData.model.split(":")[0];
  return provider ? provider.toLowerCase() : null;
});

const getProviderLogo = computed(() => {
  const provider = getProviderFromModel.value;
  switch (provider) {
    case "anthropic":
      return anthropicLogo;
    case "openai":
      return openaiLogo;
    case "google":
      return googleLogo;
    case "groq":
      return groqLogo;
    case "ollama":
      return ollamaLogo;
    case "deepseek":
      return deepseekLogo;
    case "gemini":
      return googleLogo;
    default:
      return null;
  }
});

const modelBackgroundColor = computed(() => {
  return stringToColor(props.columnData.model);
});

const modelTextColor = computed(() => {
  return getContrastTextColor(modelBackgroundColor.value);
});
</script>

<style scoped>
.thought-column {
  background: rgba(20, 28, 40, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 0.5rem;
  padding: 0.75rem;
  transition: all 0.3s ease;
  flex: 0 0 auto;
  position: relative;
  min-width: 0;
}

.thought-column::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 0.5rem;
  padding: 1px;
  background: linear-gradient(180deg, rgba(0, 212, 255, 0.2), transparent);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.3s;
}

.thought-column:hover::before {
  opacity: 1;
}

.thought-column.loading {
  background: rgba(20, 28, 40, 0.4);
}

.thought-column.loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.thought-column.error {
  border-color: rgba(255, 68, 68, 0.5);
  background: rgba(255, 68, 68, 0.05);
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  margin-bottom: 0.75rem;
}

.provider-logo {
  width: 24px;
  height: 24px;
  margin-right: 0.5rem;
  display: inline-block;
  vertical-align: middle;
  opacity: 0.8;
}

.provider-logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: brightness(0) saturate(100%) invert(91%) sepia(13%) saturate(528%) hue-rotate(177deg) brightness(95%) contrast(90%);
}

.column-header h3 {
  display: inline-block;
  vertical-align: middle;
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.stats {
  font-size: 0.75rem;
  color: #8b92a8;
}

.responses-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 100%;
}

.response-card {
  background: rgba(10, 15, 27, 0.4);
  border: 1px solid rgba(0, 212, 255, 0.05);
  border-radius: 0.375rem;
  overflow: hidden;
  transition: all 0.2s ease;
}

.response-card:hover {
  background: rgba(10, 15, 27, 0.6);
  border-color: rgba(0, 212, 255, 0.1);
}

.thought-section {
  background: rgba(0, 212, 255, 0.05);
  border-left: 2px solid #00d4ff;
  margin: 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.thought-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.1), transparent);
  transition: left 0.5s;
}

.thought-section:hover::before {
  left: 100%;
}

.thought-section:hover {
  background: rgba(0, 212, 255, 0.08);
  transform: translateX(2px);
}

.thought-section .section-header {
  padding: 0.5rem 0.75rem;
  background: rgba(0, 212, 255, 0.08);
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
}

.thought-section h4 {
  color: #00d4ff;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.thought-section h4::before {
  content: "▸";
  font-size: 1.2em;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.response-section {
  background: rgba(255, 20, 147, 0.05);
  border-left: 2px solid #ff1493;
  margin: 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.response-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 20, 147, 0.1), transparent);
  transition: left 0.5s;
}

.response-section:hover::before {
  left: 100%;
}

.response-section:hover {
  background: rgba(255, 20, 147, 0.08);
  transform: translateX(2px);
}

.response-section .section-header {
  padding: 0.5rem 0.75rem;
  background: rgba(255, 20, 147, 0.08);
  border-bottom: 1px solid rgba(255, 20, 147, 0.1);
}

.response-section h4 {
  color: #ff1493;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.response-section h4::before {
  content: "◆";
  font-size: 1em;
  animation: pulse 2s infinite;
}

.response-section .copy-button {
  background: rgba(255, 20, 147, 0.1);
  color: #ff1493;
  border: 1px solid rgba(255, 20, 147, 0.2);
}

.response-section .copy-button:hover {
  background: rgba(255, 20, 147, 0.2);
  border-color: #ff1493;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h4 {
  margin: 0;
}

.content {
  overflow-y: auto;
  white-space: pre-wrap;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
  font-size: 0.75rem;
  line-height: 1.5;
  padding: 0.75rem;
  color: #e0e6eb;
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 212, 255, 0.3) transparent;
}

.content::-webkit-scrollbar {
  width: 6px;
}

.content::-webkit-scrollbar-track {
  background: transparent;
}

.content::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.3);
  border-radius: 3px;
}

.content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.5);
}

.copy-button {
  padding: 0.25rem 0.5rem;
  font-size: 0.65rem;
  background: rgba(0, 212, 255, 0.1);
  color: #00d4ff;
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.copy-button:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  transform: translateY(-1px);
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: rgba(0, 212, 255, 0.03);
  border-bottom: 1px solid rgba(0, 212, 255, 0.05);
  font-size: 0.65rem;
  color: #8b92a8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.prompt-preview {
  font-style: normal;
  color: #4a5568;
  max-width: 40%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem;
  color: #8b92a8;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(0, 212, 255, 0.1);
  border-top: 2px solid #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-indicator span {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  animation: fadeInOut 1.5s infinite;
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.error-message {
  color: #ff4444;
  text-align: center;
  padding: 1rem;
  font-size: 0.75rem;
}

.error-message button {
  margin-top: 0.5rem;
  padding: 0.375rem 0.75rem;
  background: rgba(255, 68, 68, 0.1);
  color: #ff4444;
  border: 1px solid rgba(255, 68, 68, 0.3);
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  transition: all 0.2s;
}

.error-message button:hover {
  background: rgba(255, 68, 68, 0.2);
  border-color: #ff4444;
  transform: translateY(-1px);
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.markdown-content ul,
.markdown-content ol {
  margin: 0.5rem 0;
  padding-left: 1rem;
}

.markdown-content li {
  margin: 0.25rem 0;
  font-size: 0.75rem;
  line-height: 1.5;
}
</style>

<style>
/* Add markdown styling */
.markdown-content {
  color: #e0e6eb;
  line-height: 1.5;
  font-size: 0.75rem;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3 {
  color: #00d4ff;
  margin: 1rem 0 0.5rem;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.markdown-content p {
  margin: 0.75rem 0;
}

.markdown-content code {
  background: rgba(0, 212, 255, 0.1);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  color: #00ff88;
  font-size: 0.7rem;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
}

.markdown-content pre {
  background: rgba(10, 15, 27, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.1);
  padding: 0.75rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  margin: 0.75rem 0;
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 212, 255, 0.3) transparent;
}

.markdown-content pre::-webkit-scrollbar {
  height: 6px;
}

.markdown-content pre::-webkit-scrollbar-track {
  background: transparent;
}

.markdown-content pre::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.3);
  border-radius: 3px;
}

.markdown-content pre code {
  background: transparent;
  padding: 0;
  color: #e0e6eb;
  font-size: 0.7rem;
}

.markdown-content blockquote {
  border-left: 2px solid #00d4ff;
  padding-left: 0.75rem;
  margin: 0.75rem 0;
  color: #8b92a8;
  font-style: italic;
  background: rgba(0, 212, 255, 0.05);
  padding: 0.5rem 0.75rem;
  border-radius: 0.25rem;
}

.markdown-content a {
  color: #00d4ff;
  text-decoration: none;
  transition: all 0.2s;
}

.markdown-content a:hover {
  color: #00ff88;
  text-decoration: underline;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.75rem 0;
  font-size: 0.7rem;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid rgba(0, 212, 255, 0.1);
  padding: 0.5rem;
  text-align: left;
}

.markdown-content th {
  background: rgba(0, 212, 255, 0.1);
  color: #00d4ff;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.markdown-content tr:hover {
  background: rgba(0, 212, 255, 0.05);
}
</style>

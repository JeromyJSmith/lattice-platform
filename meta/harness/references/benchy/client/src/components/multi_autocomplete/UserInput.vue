<template>
  <div class="user-input-container">
    <code-mirror
      v-model="store.userInput"
      :basic="true"
      class="editor !h-100px !w-full"
      placeholder="Enter your code here..."
    />
  </div>
</template>

<script lang="ts" setup>
import CodeMirror from "vue-codemirror6";
import { store } from "../../stores/autocompleteStore";
import { useDebounceFn } from "@vueuse/core";
import { runAutocomplete } from "../../apis/autocompleteApi";
import { watch } from "vue";

const debouncedAutocomplete = useDebounceFn(() => {
  if (store.userInput.trim()) {
    runAutocomplete();
  }
}, 2000);

// Watch for changes in userInput
watch(
  () => store.userInput,
  () => {
    debouncedAutocomplete();
  }
);
</script>

<style scoped>
.user-input-container {
  margin-bottom: 20px;
  width: 100%;
}

.editor {
  width: 100%;
  font-family: "Monaco", "Menlo", "Ubuntu Mono", "Consolas", monospace;
  background-color: #f5f5f5;
}

:deep(.cm-editor) {
  height: 100%;
}

:deep(.cm-scroller) {
  overflow: auto;
}
</style>

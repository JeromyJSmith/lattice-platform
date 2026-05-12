<template>
  <div class="wrap">
    <code-mirror
      v-model="store.basePrompt"
      :basic="true"
      class="editor !h-700px"
    />
    <!-- {{ store.prompt }} -->
  </div>
</template>

<script lang="ts" setup>
import CodeMirror from "vue-codemirror6";
import { store } from "../../stores/autocompleteStore";
</script>

<style scoped>
.editor {
  width: 100%;
  height: 100%;
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

<template>
  <div class="wrap">
    <code-mirror
      v-model="store.jsonPrompt"
      :basic="true"
      class="editor !h-700px"
    />
  </div>
</template>

<script lang="ts" setup>
import { onMounted } from "vue";
import CodeMirror from "vue-codemirror6";
import { store } from "../../stores/toolCallStore";
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

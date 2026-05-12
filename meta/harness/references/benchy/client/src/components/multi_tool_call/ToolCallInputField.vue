<template>
  <div class="toolcallinputfield-w">
    <code-mirror
      v-model="store.userInput"
      :basic="true"
      class="editor !h-150px !w-full"
      placeholder="Enter your prompt for tool calls..."
      ref="editorRef"
      @focus="isFocused = true"
      @blur="isFocused = false"
    />
  </div>
</template>

<script lang="ts" setup>
import CodeMirror from "vue-codemirror6";
import { store } from "../../stores/toolCallStore";
import { useMagicKeys } from "@vueuse/core";
import { ref, watch } from "vue";
import { runToolCall } from "../../apis/toolCallApi";

const editorRef = ref();
const isFocused = ref(false);

const { cmd_enter } = useMagicKeys();

// Watch for cmd+enter when input is focused
watch(cmd_enter, (pressed) => {
  if (pressed && isFocused.value && !store.isLoading) {
    runToolCall();
    store.userInput = store.userInput.trim();
  }
});
</script>

<style scoped>
.toolcallinputfield-w {
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

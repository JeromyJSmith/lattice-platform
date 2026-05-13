<template>
  <div class="ag-theme-quartz" style="height: 635px; width: 100%">
    <ag-grid-vue
      :columnDefs="columnDefs"
      :rowData="rowData"
      :pagination="false"
      :rowClassRules="rowClassRules"
      :components="components"
      :autoSizeStrategy="fitStrategy"
      style="width: 100%; height: 100%"
    />
  </div>
</template>

<script setup lang="ts">
import { AgGridVue } from "ag-grid-vue3";
import { computed, ref } from "vue";
import { store } from "../../stores/toolCallStore";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";

const rowData = computed(() => [...store.rowData]);

const components = {
  // Define any custom cell renderers if needed
};

const columnDefs = ref([
  { field: "model", headerName: "Model", minWidth: 240 },
  {
    field: "toolCalls",
    headerName: "Tool Calls",
    cellRenderer: (params) => {
      if (!params.value) return "";
      return params.value.map((tc) => tc.tool_name).join(", ");
    },
    minWidth: 140,
  },
  {
    field: "execution_time",
    headerName: "Exe. Time",
    valueFormatter: formatMs,
  },
  {
    field: "total_execution_time",
    headerName: "Total Time",
    valueFormatter: formatMs,
  },
  {
    field: "execution_cost",
    headerName: "Exe. Cost",
    valueFormatter: formatMoney,
  },
  {
    field: "total_cost",
    headerName: "Total Cost",
    valueFormatter: formatMoney,
  },
  {
    field: "relativePricePercent",
    headerName: "Relative Cost (%)",
    valueFormatter: formatPercent,
  },
  { field: "number_correct", headerName: "# Correct", maxWidth: 75 },
  {
    field: "percent_correct",
    headerName: "% Correct",
    valueFormatter: formatPercent,
  },
]);

function formatPercent(params: any) {
  if (!params.value) return "0%";
  return `${params.value}%`;
}

function formatMs(params: any) {
  if (!params.value) return "0ms";
  return `${Math.round(params.value)}ms`;
}

function formatMoney(params: any) {
  if (!params.value) return "$0.000000";
  return `$${params.value.toFixed(6)}`;
}

const fitStrategy = ref({
  type: "fitGridWidth",
});

const rowClassRules = {
  "status-idle": (params: any) => params.data.status === "idle",
  "status-loading": (params: any) => params.data.status === "loading",
  "status-success": (params: any) => params.data.status === "success",
  "status-error": (params: any) => params.data.status === "error",
};
</script>

<style scoped>
.ag-theme-quartz {
  --ag-foreground-color: rgb(14, 68, 145);
  --ag-background-color: rgb(241, 247, 255);
  --ag-header-background-color: rgb(228, 237, 250);
  --ag-row-hover-color: rgb(216, 226, 255);
}

:deep(.status-idle) {
  background-color: #cccccc44;
}

:deep(.status-loading) {
  background-color: #ffeb3b44;
}

:deep(.status-success) {
  background-color: #4caf5044;
}

:deep(.status-error) {
  background-color: #f4433644;
}
</style>

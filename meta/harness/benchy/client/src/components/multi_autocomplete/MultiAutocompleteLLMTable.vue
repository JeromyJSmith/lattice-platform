<template>
  <div class="header-controls">
    <UserInput />
  </div>
  <div class="ag-theme-quartz" style="height: 600px; width: 100%">
    <ag-grid-vue
      :columnDefs="columnDefs"
      :rowData="rowData"
      :pagination="false"
      :paginationPageSize="20"
      :rowClassRules="rowClassRules"
      style="width: 100%; height: 100%"
      :components="components"
      :autoSizeStrategy="fitStrategy"
    >
    </ag-grid-vue>
  </div>
</template>

<script setup lang="ts">
import UserInput from "./UserInput.vue";
import RowActions from "./RowActions.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import { AgGridVue } from "ag-grid-vue3";
import { computed, ref } from "vue";
import { store } from "../../stores/autocompleteStore";

const rowData = computed(() => [...store.rowData]);

const components = {
  rowActions: RowActions,
};
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

const columnDefs = ref([
  {
    field: "completion",
    headerName: "Completion",
    editable: true,
    minWidth: 150,
  },
  { field: "model", headerName: "Model", minWidth: 240 },

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
    valueFormatter: (params) => (params.value ? `${params.value}%` : "0%"),
  },
  {
    headerName: "Actions",
    cellRenderer: "rowActions",
    sortable: false,
    filter: false,
    minWidth: 120,
  },
  { field: "number_correct", headerName: "# Correct", maxWidth: 75 },
  {
    field: "percent_correct",
    headerName: "% Correct",
    valueFormatter: formatPercent,
  },
]);

const rowClassRules = {
  "status-idle": (params: any) => params.data.status === "idle",
  "status-loading": (params: any) => params.data.status === "loading",
  "status-success": (params: any) => params.data.status === "success",
  "status-error": (params: any) => params.data.status === "error",
};

const fitStrategy = ref({
  type: "fitGridWidth",
});
</script>

<style scoped>
.header-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

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

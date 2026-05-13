Vue Data Grid
Cell Components

vue logoVue
Custom HTML / DOM inside Cells is achieved using Cell Components. Create Custom Cell Components to have any HTML markup in a cell. The grid comes with some Provided Cell Components for common grid tasks.

The example below shows adding images, hyperlinks, and buttons to a cell using Custom Cell Components.


 Code
New Tab
CodeSandbox
Plunker
Provided Components 
The grid comes with some built in Cell Components that cover some common cell rendering requirements.

Group Cell Component: For showing group details with expand & collapse functionality when using any of Row Grouping, Master Detail or Tree Data.

Animate Change Cell Renderers: For animating changes when data is updated.

Checkbox Cell Renderer: For displaying boolean values with a checkbox when cellDataType of Boolean is used.

Custom Components 
You can access the params object via this.params in the usual methods (lifecycle hooks, methods etc), and via props.params when using setup.

  // ...
  beforeMount() {
    this.cellValue = this.params.value;
  }
  // ...
The params (interface ICellRendererParams) passed to the Cell Component are as follows:

value
TValue | null | undefined
Value to be rendered.
valueFormatted
string | null | undefined
Formatted value to be rendered.
fullWidth
boolean
True if this is a full width row.
pinned
'left' | 'right' | null
Pinned state of the cell.
data
TData | undefined
The row's data. Data property can be undefined when row grouping or loading infinite row models.
node
IRowNode
The row node.
colDef
ColDef
The cell's column definition.
column
Column
The cell's column.
eGridCell
HTMLElement
The grid's cell, a DOM div element.
eParentOfValue
HTMLElement
The parent DOM item for the cell renderer, same as eGridCell unless using checkbox selection.
getValue

Function
Convenience function to get most recent up to data value.
setValue

Function
Convenience function to set the value.
formatValue

Function
Convenience function to format a value using the column's formatter.
refreshCell

Function
Convenience function to refresh the cell.
registerRowDragger

Function
registerRowDragger:
rowDraggerElement The HTMLElement to be used as Row Dragger
dragStartPixels The amount of pixels required to start the drag (Default: 4)
value The value to be displayed while dragging. Note: Only relevant with Full Width Rows.
suppressVisibilityChange Set to true to prevent the Grid from hiding the Row Dragger when it is disabled.
setTooltip

Function
Sets a tooltip to the main element of this component.
value The value to be displayed by the tooltip
shouldDisplayTooltip A function returning a boolean that allows the tooltip to be displayed conditionally. This option does not work when enableBrowserTooltips={true}.
api
GridApi
The grid api.
context
TContext
Application context as set on gridOptions.context.
Vue 3 - Class Based Components & Typed Components 
If you're using a Class Based Component (i.e. you're using vue-property-decorator/vue-class-component), or if you're using a vanilla Vue 3 component with lang='ts' then you'll need to specify the params object as a prop.

For example:

<script lang="ts">
   import {defineComponent} from "vue";

   export default defineComponent({
       name: "MyComponent",
       props: ['params'],  // required for TypeScript ...
Note that if Row Selection is enabled, it is recommended to set suppressKeyboardEvent on the column definition to prevent the ␣ Space key from triggering both row selection and toggling the checkbox.

Cell Component Function 
Instead of using a Vue component, it's possible to use a function for a Cell Component.

This is useful if you have a String value to render and want to avoid the overhead of a Vue component.

In the example below we're outputting a string value that depends on the cell value:

<template>
    <ag-grid-vue :columnDefs="columnDefs" ...other properties>
    </ag-grid-vue>
</template>

<script>
//...other imports
import {AgGridVue} from "ag-grid-vue3";

export default {
 components: {
     AgGridVue
 },
 data() {
     return {
         columnDefs: [
             {
                 headerName: "Value",
                 field: "value",
                 cellRenderer: params => params.value > 1000 ? "LARGE VALUE" : "SMALL VALUE"
             }
         ]
     }
 }
 //...
}
</script>
It is also possible to write a JavaScript-based Cell Component - refer to the docs here for more information

Selecting Components 
The Cell Component for a Column is set via colDef.cellRenderer and can be any of the following types:

String: The name of a registered Cell Component, see Registering Custom Components
Function: A function that returns either an HTML string or DOM element for display.
The code snippet below demonstrates each of these method types.

<ag-grid-vue
    :columnDefs="columnDefs"
    /* other grid options ... */>
</ag-grid-vue>

this.columnDefs = [
    // 1 - String - The name of a Cell Component registered with the grid.
    {
        field: 'age',
        cellRenderer: 'agGroupCellRenderer',
    },
    // 2 - Function - A function that returns an HTML string or DOM element for display
    {
        field: 'year',
        cellRenderer: params => {
            // put the value in bold
            return 'Value is <b>' + params.value + '</b>';
        }
    }
];
Dynamic Component Selection 
The colDef.cellRendererSelector function allows setting different Cell Components for different Rows within a Column.

The params passed to cellRendererSelector are the same as those passed to the Cell Renderer Component. Typically the selector will use this to check the row's contents and choose a renderer accordingly.

The result is an object with component and params to use instead of cellRenderer and cellRendererParams.

This following shows the Selector always returning back a Mood Cell Renderer:

cellRendererSelector: params => {
   return {
       component: 'GenderCellRenderer',
       params: {values: ['Male', 'Female']}
   };
}
However a selector only makes sense when a selection is made. The following demonstrates selecting between Mood and Gender Cell Renderers:

cellRendererSelector: params => {

   const type = params.data.type;

   if (type === 'gender') {
       return {
           component: 'GenderCellRenderer',
           params: {values: ['Male', 'Female']}
       };
   }

   if (type === 'mood') {
       return {
           component: 'MoodCellRenderer'
       };
   }

   return undefined;
}
Here is a full example.

The column 'Value' holds data of different types as shown in the column 'Type' (numbers/genders/moods).
colDef.cellRendererSelector is a function that selects the renderer based on the row data.
The column 'Rendered Value' show the data rendered applying the component and params sp


## Full example (use script setup syntax instead though)

import { createApp, onBeforeMount, ref, shallowRef } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import "./styles.css";
import CompanyLogoRenderer from "./companyLogoRendererVue.js";
import CompanyRenderer from "./companyRendererVue.js";
import CustomButtonComponent from "./customButtonComponentVue.js";
import MissionResultRenderer from "./missionResultRendererVue.js";
import PriceRenderer from "./priceRendererVue.js";

const VueExample = {
  template: `
        <div style="height: 100%">
                <ag-grid-vue
      style="width: 100%; height: 100%;"
      :class="themeClass"
      :columnDefs="columnDefs"
      @grid-ready="onGridReady"
      :defaultColDef="defaultColDef"
      :rowData="rowData"></ag-grid-vue>
        </div>
    `,
  components: {
    "ag-grid-vue": AgGridVue,
    CompanyRenderer,
    CompanyLogoRenderer,
    PriceRenderer,
    MissionResultRenderer,
    CustomButtonComponent,
  },
  setup(props) {
    const columnDefs = ref([
      { field: "company", flex: 6 },
      { field: "website", cellRenderer: "CompanyRenderer" },
      {
        headerName: "Logo",
        field: "company",
        cellRenderer: "CompanyLogoRenderer",
        cellClass: "logoCell",
        minWidth: 100,
      },
      { field: "revenue", cellRenderer: "PriceRenderer" },
      {
        field: "hardware",
        headerName: "Hardware",
        cellRenderer: "MissionResultRenderer",
      },
      {
        field: "actions",
        headerName: "Actions",
        cellRenderer: "CustomButtonComponent",
      },
    ]);
    const gridApi = shallowRef();
    const defaultColDef = ref({
      flex: 10,
    });
    const rowData = ref(null);

    onBeforeMount(() => {
      rowData.value = [];
    });

    const onGridReady = (params) => {
      gridApi.value = params.api;

      const updateData = (data) => {
        rowData.value = data;
      };

      fetch("https://www.ag-grid.com/example-assets/small-company-data.json")
        .then((resp) => resp.json())
        .then((data) => updateData(data));
    };

    return {
      columnDefs,
      gridApi,
      defaultColDef,
      rowData,
      onGridReady,
      themeClass:
        "ag-theme-quartz-dark",
    };
  },
};

createApp(VueExample).mount("#app");
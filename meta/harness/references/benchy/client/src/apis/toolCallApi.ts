import { store as toolCallStore } from "../stores/toolCallStore";

async function sendToolPrompt(prompt: string, model: ModelAlias): Promise<ToolCallResponse> {
    let finalPrompt = prompt;

    if (model.includes('-json')) {
        finalPrompt = toolCallStore.jsonPrompt.replace('{{tool_call_prompt}}', toolCallStore.userInput);
    }

    const response = await fetch('/tool-prompt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prompt: finalPrompt,
            model,
        }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

export async function runToolCall() {
    if (toolCallStore.isLoading) return;

    console.log("Running tool call");

    toolCallStore.isLoading = true;
    toolCallStore.promptResponses = [];
    toolCallStore.total_executions += 1;

    toolCallStore.rowData.forEach(async (row: ToolCallRowData) => {
        const rowIndex = toolCallStore.rowData.findIndex((r: ToolCallRowData) => r.model === row.model);
        if (rowIndex === -1) return;

        // Set status to loading
        toolCallStore.rowData[rowIndex].status = 'loading';
        toolCallStore.rowData[rowIndex].toolCalls = null;
        toolCallStore.rowData[rowIndex].execution_time = null;

        try {
            console.log(`Running tool call for '${row.model}' with prompt '${toolCallStore.userInput}', and expected tool calls '${toolCallStore.expectedToolCalls}'`);
            const response = await sendToolPrompt(toolCallStore.userInput, row.model);

            console.log(`'${row.model}' response`, response)

            // Update row with results
            const updatedRow: ToolCallRowData = { ...toolCallStore.rowData[rowIndex] };
            updatedRow.toolCalls = response.tool_calls;
            updatedRow.execution_time = response.runTimeMs;
            updatedRow.execution_cost = response.inputAndOutputCost;
            updatedRow.total_cost = Number(((updatedRow.total_cost || 0) + response.inputAndOutputCost).toFixed(6));
            updatedRow.total_execution_time = (updatedRow.total_execution_time || 0) + response.runTimeMs;

            // Check if tool calls match expected calls
            const isCorrect = toolCallStore.expectedToolCalls.length > 0 &&
                response.tool_calls.length === toolCallStore.expectedToolCalls.length &&
                response.tool_calls.every((tc, idx) => tc.tool_name === toolCallStore.expectedToolCalls[idx]);

            if (toolCallStore.expectedToolCalls.length > 0) {
                if (isCorrect) {
                    updatedRow.number_correct = Math.min(updatedRow.number_correct + 1, toolCallStore.total_executions);
                    updatedRow.status = 'success';
                } else {
                    updatedRow.number_correct = Math.max(0, updatedRow.number_correct - 1);
                    updatedRow.status = 'error';
                }
                updatedRow.percent_correct = calculatePercentCorrect(updatedRow.number_correct);
            }

            toolCallStore.promptResponses.push(response);

            toolCallStore.rowData.splice(rowIndex, 1, updatedRow);

            // After all rows complete, calculate relative percentages
            const allComplete = toolCallStore.rowData.every((row: ToolCallRowData) =>
                row.status === 'success' || row.status === 'error'
            );

            if (allComplete) {
                const lowestCost = Math.min(...toolCallStore.rowData
                    .filter((row: ToolCallRowData) => row.total_cost > 0)
                    .map((row: ToolCallRowData) => row.total_cost));

                toolCallStore.rowData.forEach((row: ToolCallRowData, idx: number) => {
                    const updatedRow = { ...row };
                    updatedRow.relativePricePercent = row.total_cost > 0
                        ? Math.round((row.total_cost / lowestCost) * 100)
                        : 0;
                    toolCallStore.rowData.splice(idx, 1, updatedRow);
                });
            }
        } catch (error) {
            console.error(`Error processing model '${row.model}':`, error);
            const updatedRow = { ...toolCallStore.rowData[rowIndex] };
            updatedRow.toolCalls = null;
            updatedRow.execution_time = 0;
            if (toolCallStore.expectedToolCalls.length > 0) {
                updatedRow.number_correct = Math.max(0, updatedRow.number_correct - 1);
                updatedRow.percent_correct = calculatePercentCorrect(updatedRow.number_correct);
            }
            updatedRow.status = 'error';
            toolCallStore.rowData.splice(rowIndex, 1, updatedRow);
        }
    });

    toolCallStore.isLoading = false;
}


export function calculatePercentCorrect(numberCorrect: number): number {
    if (toolCallStore.total_executions === 0 || numberCorrect === 0) return 0;
    const percent = Math.round((numberCorrect / toolCallStore.total_executions) * 100);
    return Math.max(0, Math.min(100, percent));
}

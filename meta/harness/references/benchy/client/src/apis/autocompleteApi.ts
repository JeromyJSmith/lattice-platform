import { calculatePercentCorrect, store as autocompleteStore } from "../stores/autocompleteStore";

async function sendPrompt(prompt: string, model: ModelAlias): Promise<PromptResponse> {
    const response = await fetch('/prompt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prompt,
            model,
        }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

export async function runAutocomplete() {
    if (autocompleteStore.isLoading) return;

    console.log("Running autocomplete");

    autocompleteStore.isLoading = true;
    autocompleteStore.promptResponses = [];
    autocompleteStore.total_executions += 1;

    // Process each model independently
    autocompleteStore.rowData.forEach(async (row: RowData) => {
        const rowIndex = autocompleteStore.rowData.findIndex((r: RowData) => r.model === row.model);
        if (rowIndex === -1) return;

        // Set status to loading
        autocompleteStore.rowData[rowIndex].status = 'loading';
        autocompleteStore.rowData[rowIndex].completion = '';
        autocompleteStore.rowData[rowIndex].execution_time = 0;

        try {
            console.log(`Running autocomplete for '${row.model}'`);
            const completedPrompt = autocompleteStore.basePrompt.replace(
                "{input_text}",
                autocompleteStore.userInput
            );

            const response = await sendPrompt(completedPrompt, row.model);

            // Update row with results
            const updatedRow = { ...autocompleteStore.rowData[rowIndex] };
            updatedRow.completion = response.response;
            updatedRow.execution_time = response.runTimeMs;
            updatedRow.execution_cost = response.inputAndOutputCost;
            updatedRow.total_cost = Number(((updatedRow.total_cost || 0) + response.inputAndOutputCost).toFixed(6));
            updatedRow.total_execution_time = (updatedRow.total_execution_time || 0) + response.runTimeMs;
            updatedRow.number_correct = Math.min(updatedRow.number_correct + 1, autocompleteStore.total_executions);
            updatedRow.percent_correct = calculatePercentCorrect(updatedRow.number_correct);
            updatedRow.status = 'success';
            autocompleteStore.promptResponses.push(response);

            console.log(`Success: '${row.model}': '${response.response}'`);
            autocompleteStore.rowData.splice(rowIndex, 1, updatedRow);

            // After all rows complete, calculate relative percentages
            const allComplete = autocompleteStore.rowData.every(row =>
                row.status === 'success' || row.status === 'error'
            );

            if (allComplete) {
                const lowestCost = Math.min(...autocompleteStore.rowData
                    .filter(row => row.total_cost > 0)
                    .map(row => row.total_cost));

                autocompleteStore.rowData.forEach((row, idx) => {
                    const updatedRow = { ...row };
                    updatedRow.relativePricePercent = row.total_cost > 0
                        ? Math.round((row.total_cost / lowestCost) * 100)
                        : 0;
                    autocompleteStore.rowData.splice(idx, 1, updatedRow);
                });
            }
        } catch (error) {
            console.error(`Error processing model '${row.model}':`, error);
            const updatedRow = { ...autocompleteStore.rowData[rowIndex] };
            updatedRow.completion = "Error occurred";
            updatedRow.execution_time = 0;
            updatedRow.number_correct = Math.max(0, updatedRow.number_correct - 1);
            updatedRow.percent_correct = calculatePercentCorrect(updatedRow.number_correct);
            updatedRow.status = 'error';
            autocompleteStore.rowData.splice(rowIndex, 1, updatedRow);
        }
    });

    autocompleteStore.isLoading = false;
}

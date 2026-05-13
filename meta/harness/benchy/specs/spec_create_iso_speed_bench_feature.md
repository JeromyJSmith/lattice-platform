# Create a new front-end app called: Iso Speed Bench
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- Here we're building a new front-end micro app called: iso speed bench.

## Mid-Level Objective

- Once we click on this new micro app, we'll be asked to drag and drop a yaml file into the app.
  - The yaml file will contain the benchmark prompt data in the form `ExecEvalBenchmarkFile`
- This will take the yaml file and upload it to a new endpoint: `server/server.py: /iso-speed-bench`
- The endpoint will take it, attempt to validate the pydantic structure `ExecEvalBenchmarkFile`
- If the structure is valid, it will run the benchmark () and return the results which will be the type `ExecEvalBenchmarkReport`.
- This will be returned to the front-end to be displayed 'live' by replaying the results. The app will be infinitely replayable. they can hit 'Replay Bench' or 'New Bench'. Replay will reset and bring them back to the start of the benchmark.
- As for the 'live' functionality. This is where we take the `ExecEvalBenchmarkReport` structure and for each model. show a left to right, square based grid of results. one for each prompt. The square will be red of wrong, and green if correct. It will be gray before the square has 'run'. To mirror 'running'. We'll keep a timer that runs at a 50ms interval (adjustable) and we'll update the squares based on their index, the time, a sum time, and their correct/incorrect status. When we hover over each square we want to see the tps (tokens per second). If we click into it we want to see a modal with the prompt, the response, the expected response, the input prompt, the model, and the correct/incorrect status, tokens per second, total duration, load duration. We'll also have a cancel button there to close the modal.
- So to recap the UI will be a single column where each component represents one model running every prompt (ExecEvalBenchmarkReport). now flowing left to right will be the model name, the provider, the correct count, the incorrect count, the accuracy, the average tokens per second, the average total duration, and the average load duration then to the right we'll have a grid of flex box squares where each square represents one prompt.
- We'll want to create the `ExecEvalBenchmarkReport` type on the front-end in src/types.d.ts.
- Just like src/stores/autocompleteStore.ts and src/stores/toolCallStore.ts we'll want to create a new store for this new micro app called `src/stores/isoSpeedBenchStore.ts`.
- Just like our other pages in src/pages/* we'll want to create a new page called `src/pages/isoSpeedBench.vue`.
- Break each row into a new component called `src/components/isoSpeedBenchRow.vue`.
- Keep the style isolated to this page and consistent with the styles from the other pages.
- For the server functionality reuse the existing exbench_module.py and exbench.py. Deduplicate any code from exbench.py that you need to. exbench.py is exclusively for the command line interface, move anything you need to reuse into new functions in exbench_module.py.


## Implementation Notes
- First create types
- Then create the store
- Then create the page
- Then create the row component
- Then create the modal component
- Then create the live functionality
- Then create the replay/reset functionality
- Then create the server endpoint
- Then update/refactor the existing exbench.py to use the new functions in exbench_module.py if you need better reuse.
<template>
  <div class="notes-container">
    <ul>
      <li>
        This is a micro-application for benchmarking different LLM models on
        long chains of tool/function calls (15+ calls)
      </li>
      <li>
        Supports multiple models:
        <ul>
          <li>
            Claude Models:
            <ul>
              <li>Claude 3.5 Haiku (claude-3-haiku-20240307)</li>
              <li>Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)</li>
              <li>Claude 3.5 Haiku JSON (claude-3-5-haiku-latest-json)</li>
              <li>Claude 3.5 Sonnet JSON (claude-3-5-sonnet-20241022-json)</li>
            </ul>
          </li>
          <li>
            Gemini Models:
            <ul>
              <li>Gemini 1.5 Pro (gemini-1.5-pro-002)</li>
              <li>Gemini 1.5 Flash (gemini-1.5-flash-002)</li>
              <li>Gemini 1.5 Pro JSON (gemini-1.5-pro-002-json)</li>
              <li>Gemini 1.5 Flash JSON (gemini-1.5-flash-002-json)</li>
              <li>Gemini Experimental JSON (gemini-exp-1114-json)</li>
            </ul>
          </li>
          <li>
            GPT Models:
            <ul>
              <li>GPT-4o (gpt-4o)</li>
              <li>GPT-4o Mini (gpt-4o-mini)</li>
              <li>GPT-4o JSON (gpt-4o-json)</li>
              <li>GPT-4o Mini JSON (gpt-4o-mini-json)</li>
              <li>O1 Mini JSON (o1-mini-json)</li>
            </ul>
          </li>
        </ul>
      </li>
      <li>
        Features:
        <ul>
          <li>Live tool call execution and benchmarking</li>
          <li>Response time measurements</li>
          <li>Execution cost tracking</li>
          <li>Relative cost comparisons</li>
          <li>Success rate tracking</li>
          <li>Support for function calling and JSON structured outputs</li>
          <li>State persistence with save/reset functionality</li>
        </ul>
      </li>
      <li>
        Key Findings:
        <ul>
          <li>
            There are several models that perform 100% accuracy with tool
            calling both natively and with JSON prompting / structured outputs.
            Try these for the best results (ordered by recommendation):
            <ul>
              <li>gemini-1.5-flash-002</li>
              <li>gpt-4o-mini-json</li>
              <li>gemini-1.5-flash-002-json</li>
              <li>gpt-4o-json</li>
              <li>gemini-1.5-pro-002-json</li>
              <li>gemini-1.5-pro-002</li>
              <li>gemini-exp-1114-json</li>
            </ul>
          </li>
          <li>
            Gemini 1.5 Flash is the fastest and most cost-effective for long
            tool call chains
          </li>
          <li>
            Manual JSON prompting often outperforms native function calling
          </li>
          <li>
            Larger reasoning models (o1-mini) don't necessarily perform better
            at tool calling
          </li>
          <li>
            Claude 3.5 Sonnet, and GPT-4o don't perform like you think they
            would. The tool calling variants have quite low accuracy.
          </li>
        </ul>
      </li>
      <li>Uses Vue 3 with TypeScript</li>
      <li>Grid implementation using AG Grid</li>
      <li>Code editor using CodeMirror 6</li>
      <li>Styling with UnoCSS</li>
      <li>
        Known Limitations:
        <ul>
          <li>
            Network latency to LLM provider servers is not factored into
            performance measurements
          </li>
          <li>
            Cost calculations for Gemini models do not account for price
            increases after 128k tokens
          </li>
          <li>Cost calculations do not include caching costs</li>
          <li>
            Uses default settings in
            <a
              target="_blank"
              href="https://github.com/simonw/llm?tab=readme-ov-file"
              >LLM</a
            >
            and
            <a target="_blank" href="https://github.com/openai/openai-python"
              >OpenAI</a
            >
            libraries with streaming disabled - not utilizing response token
            limits or other performance optimization techniques
          </li>
          <li>
            Models are not dynamically loaded - must manually update and setup
            every API key (see `.env.sample`)
          </li>
          <li>
            Currently only includes cloud provider models - no local or Llama
            models
          </li>
          <li>Not taking into account temperature optimizations</li>
          <li>JSON prompt can be hyper optimized for better results</li>
          <li>LLMs are non-deterministic - results will vary</li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.notes-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

ul {
  list-style-type: disc;
  margin-left: 20px;
  line-height: 1.6;
}

ul ul {
  margin-top: 10px;
  margin-bottom: 10px;
}

li {
  margin-bottom: 12px;
  color: #333;
}
</style>

<template>
  <div class="notes-container">
    <ul>
      <li>
        This is a micro-application for benchmarking different LLM models on
        autocomplete tasks
      </li>
      <li>
        Supports multiple models:
        <ul>
          <li>
            Claude Models:
            <ul>
              <li>Claude 3.5 Haiku (claude-3-5-haiku-20241022)</li>
              <li>Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)</li>
            </ul>
          </li>
          <li>
            Gemini Models:
            <ul>
              <li>Gemini 1.5 Pro (gemini-1.5-pro-002)</li>
              <li>Gemini 1.5 Flash (gemini-1.5-flash-002)</li>
              <li>Gemini 1.5 Flash 8B (gemini-1.5-flash-8b-latest)</li>
            </ul>
          </li>
          <li>
            GPT Models:
            <ul>
              <li>GPT-4o (gpt-4o)</li>
              <li>GPT-4o Mini (gpt-4o-mini)</li>
              <li>GPT-4o Predictive (gpt-4o with predictive output)</li>
              <li>
                GPT-4o Mini Predictive (gpt-4o-mini with predictive output)
              </li>
            </ul>
          </li>
        </ul>
      </li>
      <li>
        Features:
        <ul>
          <li>Customizable prompt template</li>
          <li>Response time measurements</li>
          <li>Execution cost tracking</li>
          <li>State persistence with save/reset functionality</li>
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

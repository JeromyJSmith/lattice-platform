# BENCHY
> Benchmarks you can **feel**
>
> We all love benchmarks, but there's nothing like a hands on vibe check. What if we could meet somewhere in the middle?
> 
> Enter BENCHY. A chill, live benchmark tool that lets you see the performance, price, and speed of LLMs in a side by side comparison for SPECIFIC use cases.
>
> Watch the latest development [video here](https://youtu.be/f8RnRuaxee8)

## Project Structure

This project is organized as a full-stack application with clear separation between frontend and backend:

```
benchy/
├── client/                 # Frontend Vue.js application
│   ├── src/               # Vue source code
│   │   ├── apis/          # API layer for all requests
│   │   ├── components/    # Vue components
│   │   ├── pages/         # Frontend per app pages
│   │   ├── stores/        # Frontend state and prompts
│   │   └── ...           # Other source files
│   ├── public/            # Static assets
│   ├── package.json       # Frontend dependencies
│   ├── vite.config.ts     # Vite configuration
│   ├── uno.config.ts      # UnoCSS configuration
│   └── ...               # Other frontend config files
├── server/                # Backend Python server
│   ├── modules/           # Python modules
│   ├── benchmark_data/    # Benchmark configurations
│   ├── reports/          # Benchmark results
│   ├── tests/            # Python tests
│   ├── pyproject.toml    # Python dependencies
│   ├── server.py         # Main server file
│   ├── .env              # Server environment variables
│   └── ...               # Other server files
├── ai_docs/              # AI documentation
├── images/               # Project images
├── specs/                # Project specifications
├── trees/                # Git worktrees directory
├── .env                  # Root environment variables
├── start.sh              # Convenience script to start both services
└── ...                   # Other project files
```

### Quick Start
```bash
# Start both frontend and backend together
./start.sh
```

This will start:
- Frontend dev server at `http://localhost:5173` (or next available port)
- Backend API server at `http://localhost:8000`

<img src="./images/o3-mini.png" alt="deepseek-r1" style="max-width: 800px;">

<img src="./images/deepseek-r1.png" alt="deepseek-r1" style="max-width: 800px;">

<img src="./images/o1-ai-coding-limit-testing.png" alt="o1-ai-coding-limit-testing" style="max-width: 800px;">

<img src="./images/m4-max-mac-book-pro-benchmarked.png" alt="m4-mac-book-pro" style="max-width: 800px;">

<img src="./images/parallel-function-calling.png" alt="parallel-function-calling" style="max-width: 800px;">

<img src="./images/perf-price-speed-pick-two.png" alt="pick-two" style="max-width: 800px;">

## Benchy Micro Apps
- [Thought Bench](https://youtu.be/UgSGtBZnwEo)
  - Goal: Compare multiple reasoning models side by side in parallel to analyze their thinking processes and responses
  - Default models: Anthropic Claude 4.0 Sonnet/Opus, OpenAI o4-mini/o3, Anthropic Claude 3.7 Sonnet, Gemini 2.5 Flash/Pro, Ollama Qwen3/Gemma3/Devstral
  - Watch the walk through [video here](https://youtu.be/UgSGtBZnwEo)
  - Front end: [client/src/pages/ThoughtBench.vue](client/src/pages/ThoughtBench.vue)
- [BIG AI Coding Updates to Benchy](https://youtu.be/y_ywOVQyafE)
  - Watch the walk through [video here](https://youtu.be/y_ywOVQyafE)
- [Iso Speed Bench](https://youtu.be/OwUm-4I22QI)
  - Goal: Create a unified, config file based, multi-llm provider, yes/no evaluation based benchmark for high quality insights and iteration.
  - Watch o3-mini vibe check, comparison, and benchmark [video here](https://youtu.be/K5xs669ANQo)
  - Watch the M4 Unboxing and benchmark [video here](https://youtu.be/OwUm-4I22QI)
  - Front end: [client/src/pages/IsoSpeedBench.vue](client/src/pages/IsoSpeedBench.vue)
- [Long Tool Calling](https://youtu.be/ZlljCLhq814)
  - Goal: Understand the best LLMs and techniques for LONG chains of tool calls / function calls (15+).
  - Watch the walk through [video here](https://youtu.be/ZlljCLhq814)
  - Front end: [client/src/pages/AppMultiToolCall.vue](client/src/pages/AppMultiToolCall.vue)
- [Multi Autocomplete](https://youtu.be/1ObiaSiA8BQ)
  - Goal: Understand [claude 3.5 haiku](https://www.anthropic.com/claude/haiku) & GPT-4o [predictive outputs](https://platform.openai.com/docs/guides/predicted-outputs) compared to existing models. 
  - Watch the walk through [video here](https://youtu.be/1ObiaSiA8BQ)
  - Front end: [client/src/pages/AppMultiAutocomplete.vue](client/src/pages/AppMultiAutocomplete.vue)

## Important Files

### Frontend (client/)
- `client/package.json` - Frontend dependencies and scripts
- `client/src/stores/*` - Stores all frontend state and prompts
- `client/src/apis/*` - API layer for all requests
- `client/src/pages/*` - Frontend per app pages
- `client/src/components/*` - Vue components
- `client/vite.config.ts` - Vite build configuration
- `client/uno.config.ts` - UnoCSS configuration

### Backend (server/)
- `server/server.py` - Main server routes and API endpoints
- `server/pyproject.toml` - Python dependencies
- `server/modules/llm_models.py` - All LLM model definitions
- `server/modules/openai_llm.py` - OpenAI integration
- `server/modules/anthropic_llm.py` - Anthropic integration
- `server/modules/gemini_llm.py` - Google Gemini integration
- `server/modules/ollama_llm.py` - Ollama integration
- `server/modules/deepseek_llm.py` - Deepseek integration
- `server/benchmark_data/*` - Benchmark configuration files
- `server/reports/*` - Generated benchmark results

### Configuration
- `.env` - Root environment variables for API keys
- `server/.env` - Server-specific environment variables
- `start.sh` - Convenience script to start both services
- `.claude/` - Claude Code configuration and commands
  - `.claude/settings.local.json` - Claude Code permissions and settings
  - `.claude/commands/prime.md` - Custom Claude commands for project context

## Setup

### Get API Keys & Models
- [Anthropic](https://docs.anthropic.com/en/api/getting-started)
- [Google Cloud](https://ai.google.dev/gemini-api/docs/api-key)
- [OpenAI](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key)
- [Deepseek](https://platform.deepseek.com/)
- [Ollama](https://ollama.ai/download)
  - After installing Ollama, pull the required models:
  ```bash
  # Pull Llama 3.2 1B model
  ollama pull llama3.2:1b
  
  # Pull Llama 3.2 latest (3B) model
  ollama pull llama3.2:latest
  
  # Pull Qwen2.5 Coder 14B model
  ollama pull qwen2.5-coder:14b

  # Pull Deepseek R1 1.5B, 7b, 8b, 14b, 32b, 70b models
  ollama pull deepseek-r1:1.5b
  ollama pull deepseek-r1:latest
  ollama pull deepseek-r1:8b
  ollama pull deepseek-r1:14b
  ollama pull deepseek-r1:32b
  ollama pull deepseek-r1:70b

  # Pull mistral-small 3
  ollama pull mistral-small:latest

  # Pull Phi-4 model
  ollama pull phi4:latest

  # Pull Falcon 3 10B model
  ollama pull falcon3:10b

  # Pull Qwen 3 14B model
  ollama pull qwen3:14b

  # Pull Gemma 3 4B model
  ollama pull gemma3:4b

  # Pull Devstral model
  ollama pull devstral
  ```

### Frontend Setup (client/)
```bash
# Navigate to client directory
cd client

# Install dependencies using bun (recommended)
bun install

# Or using npm
npm install

# Or using yarn
yarn install

# Start development server
bun dev  # or npm run dev / yarn dev
```

### Backend Setup (server/)
```bash
# Navigate to server directory
cd server

# Create and activate virtual environment using uv
uv sync

# Set up environment variables
cp ../.env.sample ../.env  # Root .env file
cp .env.sample .env        # Server .env file

# Set EVERY .env key with your API keys and settings in both files
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=
DEEPSEEK_API_KEY=
FIREWORKS_API_KEY=

# Start server
uv run python server.py

# Run tests
uv run pytest (**beware will hit APIs and cost money**)
```

### Development Workflow
```bash
# Start both services at once (recommended)
./start.sh

# Or start them separately in different terminals:
# Terminal 1: Frontend
cd client && bun dev

# Terminal 2: Backend  
cd server && uv run python server.py
```

### Claude Code Integration

This project includes Claude Code configuration for enhanced development experience:

- **Custom Commands**: Use the `/prime` command in Claude Code to quickly load project context
- **Permissions**: Pre-configured permissions for common development tasks (mkdir, mv, ls)
- **Project Context**: The `.claude/commands/prime.md` file automatically reads key project files and shows the directory structure

To use with Claude Code:
1. Open the project in Claude Code
2. Type `/prime` to load the project context
3. Claude will have immediate understanding of the codebase structure and key files

## Resources
- https://github.com/simonw/llm?tab=readme-ov-file
- https://github.com/openai/openai-python
- https://platform.openai.com/docs/guides/predicted-outputs
- https://community.openai.com/t/introducing-predicted-outputs/1004502
- https://unocss.dev/integrations/vite
- https://www.npmjs.com/package/vue-codemirror6
- https://vuejs.org/guide/scaling-up/state-management
- https://www.ag-grid.com/vue-data-grid/getting-started/
- https://www.ag-grid.com/vue-data-grid/value-formatters/
- https://llm.datasette.io/en/stable/index.html
- https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/get-token-count
- https://ai.google.dev/gemini-api/docs/tokens?lang=python
- https://ai.google.dev/pricing#1_5flash
- https://ai.google.dev/gemini-api/docs/structured-output?lang=python
- https://platform.openai.com/docs/guides/structured-outputs
- https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- https://ai.google.dev/gemini-api/docs/models/experimental-models
- https://sqlparse.readthedocs.io/en/latest/intro.html
- mlx: https://huggingface.co/mlx-community
- ollama docs: https://github.com/ollama/ollama/blob/main/docs/api.md#examples
- deepseek docs: https://platform.deepseek.com/usage

## Multi-Agent Git Worktree

### Why Run in Parallel

LLMs are non-deterministic probabilistic machines - every run produces different results. 

This is a feature, not a bug. We can leverage it to see **multiple versions of the future** and **choose the best outcome**.

By running multiple AI agents in parallel on separate git worktrees, you can:

#### #1
Hedge against model failures on complex tasks with multiple outcomes (startups/big tech tech does this all the time)

#### #2
Get different perspectives on the same problem - choose the best implementation

#### #3
Isolate and delegate your engineering work to 2-N agents


### How It Works

Git worktrees allow you to duplicate your entire codebase into a new branch and directory:

```bash
# Create a directory for worktrees
mkdir trees

# Create three parallel worktrees for UI improvements
git worktree add -b ui_revamp-1 trees/ui_revamp-1
git worktree add -b ui_revamp-2 trees/ui_revamp-2
git worktree add -b ui_revamp-3 trees/ui_revamp-3

# Copy environment variables to each worktree
cp .env trees/ui_revamp-1/
cp .env trees/ui_revamp-2/
cp .env trees/ui_revamp-3/
```

Then run separate AI agents (like Claude Code) on each worktree with the same plan/prompt. Each agent works in isolation, producing different variations.

### When to Use This Technique

1. **Multiple Satisfactory Outcomes**: Perfect for UI work where many versions could be acceptable
2. **Complex Tasks with Failure Risk**: If one agent might fail, run three and pick the winner
3. **When You Have a Clear Plan**: The plan is the prompt - detailed planning enables parallel execution

### Big Ideas

- **Non-determinism is a feature**: Different versions give you options
- **The plan is the prompt**: Great planning = great prompting
- **Scale compute = scale impact**: Use more tokens to see more possibilities
- **Pick and merge**: Choose the best version or combine elements from multiple

This advanced technique requires burning significant tokens (dollars per run) but enables you to:
- Work on multiple timelines simultaneously
- Get different perspectives on the same problem
- Dramatically increase development velocity
- See multiple versions of the future, literally

As AI models improve, this parallel approach will become increasingly powerful for leveraging their capabilities at scale.

## Master AI Coding 
Learn to code with AI with foundational [Principles of AI Coding](https://agenticengineer.com/principled-ai-coding?y=benchy)

Follow the [IndyDevDan youtube channel](https://www.youtube.com/@indydevdan) for more AI coding tips and tricks.
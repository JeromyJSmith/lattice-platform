# Capability Harvest - n8n-mcp

| Field | Value |
|---|---|
| Source repo | `https://github.com/czlonkowski/n8n-mcp` |
| Reviewed version | `n8n-mcp 2.53.0` |
| Harvest date | `2026-05-17` |
| LATTICE owner | Capability research |

## Live Wiring Seen In This Repo

| Path | Role |
|---|---|
| `.mcp.json` | Repo-local MCP entry `n8n` via `npx -y n8n-mcp` |
| `.env.example` | Declares `N8N_API_URL` + `N8N_API_KEY` required for management tools |

## Harvest Inputs

- `npm view n8n-mcp bin` -> `{ 'n8n-mcp': 'dist/mcp/stdio-wrapper.js' }`
- `npm view n8n-mcp homepage` -> `https://github.com/czlonkowski/n8n-mcp#readme`
- Upstream README capability sections (`Available MCP Tools`, `n8n Management Tools`)

## Harvested MCP Tool Surface

### Core tools (no n8n API credentials required)

| Capability | Current repo stance |
|---|---|
| `tools_documentation` | active |
| `search_nodes` | active |
| `get_node` | active |
| `validate_node` | active |
| `validate_workflow` | active |
| `search_templates` | active |
| `get_template` | active |

### n8n management tools (require API configuration)

| Capability | Current repo stance |
|---|---|
| `n8n_create_workflow` | blocked |
| `n8n_get_workflow` | blocked |
| `n8n_update_full_workflow` | blocked |
| `n8n_update_partial_workflow` | blocked |
| `n8n_delete_workflow` | blocked |
| `n8n_list_workflows` | blocked |
| `n8n_validate_workflow` | blocked |
| `n8n_autofix_workflow` | blocked |
| `n8n_workflow_versions` | blocked |
| `n8n_deploy_template` | blocked |
| `n8n_test_workflow` | blocked |
| `n8n_executions` | blocked |
| `n8n_manage_credentials` | blocked |
| `n8n_audit_instance` | blocked |
| `n8n_health_check` | blocked |

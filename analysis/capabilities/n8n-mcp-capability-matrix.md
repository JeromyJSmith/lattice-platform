# Capability Matrix - n8n-mcp

| Capability ID | Harness | Value | Risk | Decision | Evidence | Registry state | Verification target | Tracking |
|---|---|---|---|---|---|---|---|---|
| `mcp-core-docs-and-search` | `agent-runtime` | `high` | `low` | `promote` | `.mcp.json`, `analysis/capabilities/n8n-mcp-capability-harvest.md` | `ACTIVE` | MCP entry resolves and core documentation/search tool surface is available | `analysis/capabilities/n8n-mcp-capability-registry.yaml` |
| `mcp-template-validation` | `workflow-design` | `high` | `low` | `promote` | `analysis/capabilities/n8n-mcp-capability-harvest.md` | `ACTIVE` | Template search/get and node/workflow validation tools are documented and wired | `analysis/capabilities/n8n-mcp-capability-registry.yaml` |
| `mcp-workflow-management` | `workflow-actuation` | `high` | `medium` | `block` | `.env.example` missing live credentials and n8n API instance | `BLOCKED` | Add `N8N_API_URL` + `N8N_API_KEY`, then validate with `n8n_health_check` | `analysis/capabilities/n8n-mcp-capability-registry.yaml` |
| `mcp-credential-and-audit` | `security-ops` | `high` | `high` | `block` | Management tools require authenticated instance access | `BLOCKED` | Run `n8n_manage_credentials` and `n8n_audit_instance` against live n8n | `analysis/capabilities/n8n-mcp-capability-registry.yaml` |

## First Active Slice

```text
Use n8n-mcp now for node discovery, template discovery, and workflow validation
planning. Keep create/update/delete/deploy/execution/audit operations blocked
until credentials and a target n8n instance are provisioned.
```

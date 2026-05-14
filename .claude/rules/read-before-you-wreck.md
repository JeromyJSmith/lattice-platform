# Read Before You Wreck

An agent wrote code before reading the repo. The Desktop agent hit three dead walls inside sixty seconds. The user lost context, money, and time. This file exists so you don't repeat that.

---

## MANDATORY PRE-FLIGHT — read these four files before writing a single line

| File | What it contains that will burn you if you skip it |
|---|---|
| `meta/SCHEMA.md` | Every Pixeltable table, its exact path, its columns. If you write a table path without reading this, it will be wrong. |
| `meta/ARCHITECTURE.md` | Sidecar URL, port, health endpoint, MCP topology, data flow. If you write a health check or service URL without reading this, it will be wrong. |
| `meta/AGENT_ONBOARDING.md` | Boot sequence, exact commands, exact URLs. Ground truth overrides anything else you think you know. |
| `.mcp.json` | What MCP servers are actually registered. If a tool isn't in this file, it is not available via MCP. |

If you skip any of these, you will write confident-sounding wrong things and waste everyone's time.

---

## Confirmed mistakes — never repeat these

### Sidecar URL
- **WRONG:** `http://localhost:8001/health`
- **WRONG:** `http://localhost:8001/healthz`
- **RIGHT:** `curl 127.0.0.1:7770/healthz`
- **Why:** `AGENT_ONBOARDING.md` and `ARCHITECTURE.md` both say `127.0.0.1:7770`. `AGENTS.md` has a stale `localhost:8001` reference. Canonical docs beat stale docs every time.

### vwx-mcp
- **WRONG:** `curl http://localhost:9878/health` — it is not an HTTP service
- **RIGHT:** vwx-mcp is a TCP socket that lives **inside the Vectorworks application process**. It is not in `.mcp.json`. You cannot health-check it with curl. Check whether VW is running and whether vicquick/vwx-mcp is installed before assuming anything.

### Pixeltable table paths
- **WRONG:** `lattice/bridge/ifc_elements`
- **WRONG:** `lattice/bridge/dwg_entities` (this table does not exist)
- **RIGHT:** `lattice/bridge/ifc/ifc_elements` (nested under `ifc/` subfolder)
- **Why:** Read `meta/SCHEMA.md`. All 40 tables are listed there with exact paths. If the table isn't in that file, it doesn't exist. Do not invent table names.

### Port assumptions
- This project uses **portless** — OrbStack proxy on `:1355` with HTTPS subdomains (e.g. `sidecar.localhost`). Do not assume raw port numbers are how services are reached. Read `meta/ARCHITECTURE.md` for the actual network topology.

---

## The protocol violation that caused all of this

The agent was asked to write a plan and two new files. It wrote them from assumptions — URLs it vaguely remembered, table names that sounded right — without opening a single canonical document.

The information was sitting in four files. Four files. None of them were read first.

The result: a plan with three wrong facts that sent another agent into three dead walls in under a minute.

---

## The rule

**Read before you write. Verify before you assert. If a URL, table path, file path, or service name appears in your output, you must have read it from a canonical source in this session.**

Assumption is not research. Sounding confident is not the same as being correct.

If you don't know the answer, say you don't know and read the file that has it. That takes thirty seconds. Getting it wrong takes an entire context window to undo.

---

## Quick reference — canonical sources

| Question | Where to look |
|---|---|
| What Pixeltable tables exist? | `meta/SCHEMA.md` |
| What is the sidecar URL/port? | `meta/ARCHITECTURE.md`, `meta/AGENT_ONBOARDING.md` |
| What MCP servers are registered? | `.mcp.json` |
| What migrations have been applied? | `meta/SCHEMA.md` migration trail, `pixeltable/migrations/` |
| What endpoints does the FastAPI sidecar expose? | `meta/API.md` |
| What is the project architecture? | `meta/ARCHITECTURE.md` |
| What VWX projects are registered? | `projects/registry.yaml` |
| What DDC tools are available? | `meta/DDC_MAPPING.md` |
| What is the boot sequence? | `meta/AGENT_ONBOARDING.md` |
| What rules must never be broken? | `AGENTS.md`, `CLAUDE.md` |

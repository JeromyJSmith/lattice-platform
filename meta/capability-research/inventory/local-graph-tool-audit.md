# Local Graph Tool Audit

Date: 2026-05-13
Scope: `/Volumes/PixelTable`, user-local tool paths, and current LATTICE repo

This audit checks whether Graphify, GitNexus, and InfraNodus have already been
used on this workstation or PixelTable volume. The answer is yes: there is prior
local history, but the current LATTICE repo is its own unindexed situation.

## Tool Availability

| Tool | Local evidence | Current implication |
|---|---|---|
| Graphify | `graphify` exists at `/Users/ojeromyo/.local/bin/graphify` | Available locally; do not assume repo config exists |
| GitNexus | `gitnexus` exists at `/opt/homebrew/bin/gitnexus`, version `1.6.3`; npm global has `gitnexus@1.6.3` | Available locally; current LATTICE repo is not indexed |
| InfraNodus | `claude mcp list` reports `infranodus: npx -y infranodus-mcp-server - connected` | Ready for curated-doc MCP analysis if API key env resolves |

Current LATTICE `.mcp.json` contains only InfraNodus:

```text
infranodus -> npx -y infranodus-mcp-server
```

The current LATTICE repo is not registered in GitNexus:

```text
gitnexus status
Repository not indexed.
Run: gitnexus analyze
```

## PixelTable Volume Findings

### MARPA Platform

Found:

```text
/Volumes/PixelTable/MARPA_PLATFORM/.gitnexus
/Volumes/PixelTable/MARPA_PLATFORM/.claude/skills/gitnexus
/Volumes/PixelTable/MARPA_PLATFORM/vw-bridge/docs_corpus/queryable_docs/gitnexus
/Volumes/PixelTable/MARPA_PLATFORM/vw-bridge/docs_corpus/queryable_docs/graphify
```

GitNexus metadata:

```text
repoPath: /Volumes/PixelTable/MARPA_PLATFORM
indexedAt: 2026-05-02T01:10:10.525Z
files: 16975
nodes: 119101
edges: 136561
communities: 362
processes: 250
```

MARPA Platform `.mcp.json` includes GitNexus:

```text
gitnexus -> npx -y gitnexus@latest mcp
```

Lesson for LATTICE: GitNexus can index a large repo, but the output is large and
should not be run before LATTICE has explicit include/exclude boundaries.

### MARPA 918 Juniper

Found:

```text
/Volumes/PixelTable/MARPA_918_JUNIPER/graphify-out
/Volumes/PixelTable/MARPA_918_JUNIPER/.graphifyignore
/Volumes/PixelTable/MARPA_918_JUNIPER/.claude/hooks/graphify-precommit.sh
/Volumes/PixelTable/MARPA_918_JUNIPER/.claude/skills/graphify
/Volumes/PixelTable/MARPA_918_JUNIPER/docs/reorg/GRAPHIFY_MAP_REPORT.md
```

Graphify summary:

```text
386 files
~986,951 words
1746 nodes
3489 edges
70 communities
elapsed: 75.3 seconds
```

The graph report warned that the corpus was large and semantic extraction would
be expensive. The `.graphifyignore` excluded `node_modules`, `.git`, `.venv`,
`dist`, Pixeltable internals, large raw data, binary geospatial data, model
files, and Graphify's own output.

Lesson for LATTICE: start with a docs-only or small scoped run. Do not run
Graphify on the full repo without a `.graphifyignore` and corpus manifest.

### GROVE Harness

Found:

```text
/Volumes/PixelTable/GROVE_HARNESS/juniper2026/_attic/docs/.claude-code-docs/graphify-out
```

Lesson for LATTICE: graph outputs can survive in attic/reference folders; do not
blindly treat every graphify-out on the volume as current project state.

### User-Local Scripts And Logs

Found:

```text
/Users/ojeromyo/.config/graphify-launch.sh
/Users/ojeromyo/.config/graphify-queue.sh
/Users/ojeromyo/.config/graphify-runs
/Users/ojeromyo/.config/graphify-queue
/Users/ojeromyo/.config/gitnexus-marpa.log
/Users/ojeromyo/.config/gitnexus-juniper2026.log
```

The queue scripts show a prior pattern:

- Run smaller scopes first.
- Use explicit excludes.
- Write outputs to a known vault/output location.
- Use hard cost caps when invoking Claude-backed semantic extraction.
- Prefer one worker for expensive semantic passes.

GitNexus logs show successful indexing, but also benign Python package edge
cases on empty `__init__.py` files and a non-git `HEAD` warning for one mirror.

## Existing Indexed GitNexus Repositories

`gitnexus list` currently reports:

| Alias | Path | Indexed | Scale |
|---|---|---:|---|
| `juniper2026-guide` | `/Users/ojeromyo/dev/juniper2026-guide` | 2026-04-30 | 123 files, 3159 symbols, 4130 edges |
| `juniper2026` | `/Users/ojeromyo/imac-sync/dev/juniper2026` | 2026-04-29 | 185 files, 2024 symbols, 2310 edges |
| `marpa-918-juniper` | `/Users/ojeromyo/imac-sync/dev/marpa-918-juniper` | 2026-04-29 | 5236 files, 9017 symbols, 9629 edges |
| `MARPA_PLATFORM` | `/Volumes/PixelTable/MARPA_PLATFORM` | 2026-05-01 | 16975 files, 119101 symbols, 136561 edges |

LATTICE is not currently in that list.

## Current LATTICE Conclusion

This application is not the first project on this machine to use Graphify or
GitNexus. The tools exist and prior patterns are available.

However, LATTICE should still be treated as its own graph-tool setup because:

1. Its current repo is not indexed in GitNexus.
2. Its `.mcp.json` currently wires InfraNodus only.
3. Its capability research docs were just reorganized.
4. Its graph-tool registries contain harvested intent that predates the current
   folder layout.
5. Its first useful analysis should be constrained to curated capability docs,
   not the whole repo.

## Reuse From Prior Work

Reuse these patterns:

| Prior pattern | LATTICE adoption |
|---|---|
| `.graphifyignore` with strong excludes | Add LATTICE-specific ignore before any Graphify run |
| Smaller scopes first | First run should be `meta/capability-research/` plus selected top-level docs |
| Known output directory | Use `meta/capability-research/inventory/graphify/` or session evidence path |
| GitNexus local index only after scope is clear | Do not run `gitnexus analyze` until include/exclude boundary is written |
| MCP entries are repo-specific | Do not copy MARPA Platform `.mcp.json` blindly into LATTICE |

Do not reuse:

- MARPA Platform `.gitnexus` index.
- MARPA 918 `graphify-out` as if it describes LATTICE.
- Old generated skills without checking whether they match current LATTICE paths.
- Any queue script that writes outside the approved LATTICE output paths.

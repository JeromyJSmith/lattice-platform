# GitNexus Bounded Proof — 2026-05-13

## Scope

Bounded first-pass index for the current LATTICE repo using a repo-local
development dependency and a repo-local `.gitnexusignore`.

Included proof subset:

- `pixeltable/service/main.py`
- `pixeltable/service/routes/harness.py`
- `scripts/audit-dead-dna.sh`
- `scripts/check-python-docstrings.py`

## Commands

```bash
bun add -d gitnexus@1.6.3
gitnexus analyze --skip-agents-md --name lattice-platform-scoped
gitnexus status
gitnexus list
gitnexus cypher "MATCH (f:File) RETURN f LIMIT 3" -r lattice-platform-scoped
```

## Verified outcomes

- `gitnexus` is now present in `package.json` `devDependencies`.
- The repo-local binary at `node_modules/.bin/gitnexus` reports version `1.6.3`.
- The Bun-installed package required one repair step to become executable:

```bash
node node_modules/@ladybugdb/core/install.js
```

This copied the prebuilt `lbugjs.node` binary into `node_modules/@ladybugdb/core/`.
- `gitnexus analyze --skip-agents-md --name lattice-platform-scoped` completed
  successfully.
- Indexed summary:
  - 4 files
  - 158 symbols/nodes
  - 247 edges
  - 5 clusters
  - 15 flows
- `gitnexus status` reports the repo is indexed and up to date at commit
  `60af3b0`.
- `gitnexus cypher` can return file nodes from the scoped index, proving the
  structural graph exists.
- `gitnexus detect-changes --scope unstaged -r lattice-platform-scoped` returns
  a valid result (`No changes detected.`) and is safe for the repo hook.

## Partial failures

- `gitnexus query harness -r lattice-platform-scoped` emitted read-only FTS
  index warnings before returning an empty result.
- `gitnexus impact pixeltable/service/routes/harness.py -r lattice-platform-scoped`
  did not resolve the file path as a target.

These two results mean:

- Structural indexing is real.
- Text-search/FTS health still needs follow-up.
- Path-target impact queries should be validated against symbol names rather than
  assumed file-path inputs.

## Wiring changes made in this session

- Added repo-local `gitnexus` MCP entry to `.mcp.json`
- Added repo-local `.gitnexusignore`
- Corrected `.claude/settings.json` to use a valid pre-hook command:
  `detect-changes --scope unstaged -r lattice-platform-scoped`
- Removed the invalid `index --incremental` post-hook command

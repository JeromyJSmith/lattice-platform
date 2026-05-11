# LATTICE Security Rules

Project-local security rules for the LATTICE platform.
These live in `.claude/rules/` (version-controlled) and override
the minimal global baseline in `~/.claude/rules/security.md`.

## Approved install patterns for this project

- `curl` to `/tmp/` for inspection THEN exec after review — OK for graphify-parisgroup
- `uv tool install graphify` — OK (isolated uv tool environment)
- `npx -y infranodus-mcp-server` — OK (ephemeral, no global install)
- `npm install gitnexus --save-dev` — OK (project-local devDep, never `-g`)

## Approved cross-project read/write paths

- `~/.lattice-docs/`          read/write (doc mirrors)
- `~/.claude-code-docs/`      read/write (Claude Code doc mirror)
- `~/.vectorworks-docs/`      read-only  (VW SDK docs)
- `~/.gitnexus/`              read/write (GitNexus registry, managed by CLI)
- `/tmp/`                     write then clean (temporary downloads)

## Banned Patterns

- `npm install -g <anything>` — global installs are banned for this project
- `pip` / `conda` / `poetry` / `pipenv` — `uv` only
- Reading `~/.ssh/`, `~/.aws/`, `~/.config/` without explicit per-session user confirmation
- Any write outside the repo root or the approved paths above without explicit user confirmation

## Pipe-to-shell rule (project-specific override)

For this project, `curl | bash` and `wget | sh` are BLOCKED unless:
  1. The source URL is a verified GitHub release asset (`github.com/*/releases/*`)
  2. The content is first downloaded to `/tmp/`, inspected by the agent, then executed
  3. The user has explicitly approved the dependency in `dependency-allowlist.md`

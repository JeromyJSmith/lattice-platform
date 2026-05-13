<!-- spec-verified: vercel-labs/portless 0.9.4 2026-05-13 -->
# Capability Harvest — portless

| Field | Value |
|---|---|
| Source repo | `https://github.com/vercel-labs/portless` |
| Reviewed version | `0.9.4` |
| Canonical docs | `https://github.com/vercel-labs/portless/blob/main/README.md` |
| Harvest date | `2026-05-13` |
| LATTICE owner | Meta-Harness (dev infrastructure) |
| Harvested by | claude-haiku-4-5 |

## Capability Surfaces

| Capability ID | Surface | Name | Source command/doc | Raw capability | Notes |
|---|---|---|---|---|---|
| `portless-cli-run` | `cli_command` | `portless <name> <cmd>` | `portless --help` | Prepend to dev command; auto-assigns ephemeral PORT and routes `https://<name>.localhost` → port | core invocation; framework auto-detects PORT env |
| `portless-cli-auto-infer` | `cli_command` | `portless run <cmd>` | `portless --help` | Auto-infer service name from Git worktree or package.json; wrapper convenience | reduces config friction for single-service projects |
| `portless-cli-alias` | `cli_command` | `portless alias <name> <port>` | `portless --help` | Register static port→subdomain mapping for external services (Docker, etc.) | enables routing to non-Portless services |
| `portless-cli-list` | `cli_command` | `portless list` | `portless --help` | Display active routes (subdomains, ports, process info) | observability surface for operator |
| `portless-cli-proxy-control` | `cli_command` | `portless proxy {start\|stop\|restart}` | `portless --help` | Explicit daemon lifecycle management; flags: `--lan`, `--no-tls`, `--port` | daemon control; lifecycle gates |
| `portless-cli-service-install` | `cli_command` | `portless service {install\|uninstall}` | `portless --help` | Register proxy daemon for OS-level startup (systemd/launchd/etc.) | persistence across system reboot |
| `portless-config-json` | `pattern` | `.portless.json` config file | repo README | Per-service config: `{"name": "...", "appPort": ..., "script": ...}` | optional; defaults inferred if absent |
| `portless-config-pkg-json` | `pattern` | `package.json` "portless" key | repo README | Inline config: `{"portless": {"name": "...", "script": ...}}` | alternative to .portless.json; monorepo-friendly |
| `portless-config-monorepo` | `pattern` | Monorepo workspace mapping | repo README + npm/yarn/pnpm workspaces | Config maps workspace paths to custom subdomain names; single proxy serves all apps | enables multi-app dev without port collision |
| `portless-hostname-routing` | `pattern` | Subdomain-to-port routing | repo README | Routes by HOSTNAME (subdomain of `.localhost` or custom TLD), not path; strict or wildcard modes | key architectural property; isolates by subdomain |
| `portless-https-auto-cert` | `pattern` | Auto-generated trusted HTTPS certs | repo README | Adds root CA to OS trust store on first run; creates per-subdomain leaf certs | unlocks WebGPU, SharedArrayBuffer, and secure-context APIs |
| `portless-port-env-injection` | `pattern` | `$PORT` environment variable | repo README | Portless assigns ephemeral PORT; framework reads it (most Node frameworks respect $PORT) | no CLI flag injection needed; clean env var interface |
| `portless-custom-tld` | `pattern` | Configurable TLD override | repo README | Default `.localhost`; can override to `.dev` or custom domain | team naming convention support |
| `portless-git-worktree-prefix` | `pattern` | Git worktree branch-name prefix | repo README | Auto-prefixes subdomains with Git branch name (e.g., `fix-ui.myapp.localhost`) | collision avoidance without config |
| `portless-mdn-discovery` | `pattern` | LAN mode (mDNS) | repo README | Optional: resolve via mDNS for device-to-device (iPhone, tablet, etc.); default: localhost-only | team dev + mobile testing without setup |
| `portless-tailscale-integration` | `pattern` | Tailscale sharing | repo README | Optional: expose via Tailscale Funnel for team/public access (requires Tailscale CLI) | team sharing without ngrok/tunnel install |
| `portless-framework-auto-flags` | `pattern` | Framework-specific flag injection | repo README | Auto-detects framework (Vite, Astro, Next, React Router, etc.) and injects build flags | reduces config duplication per framework |
| `portless-env-vars-portless-prefix` | `pattern` | `PORTLESS_*` env var config | repo README | Runtime config via env (e.g., `PORTLESS_NAME`, `PORTLESS_PROXY_PORT`); overrides file config | CI/container-friendly configuration |

## Evidence

### Help/list commands

- `portless --help` (verified available at bun pm ls -g | grep portless@0.9.4)
- `portless list` (lists active routes)
- `portless proxy start --help` (daemon control)

### Docs path

- Canonical: `https://github.com/vercel-labs/portless/blob/main/README.md`
- Local install: `bun pm ls -g | grep portless@0.9.4` shows installed at global scope
- No local config path; uses home-dir daemon socket and OS trust store for HTTPS certs

### Local install verified

- Command: `bun pm ls -g | grep portless@0.9.4`
- Result: Portless 0.9.4 installed globally via Bun package manager

### Gaps or unknowns

1. **Exact daemon socket location**: README implies `/tmp` or home-dir location; not explicitly documented. Assumption: standard XDG config or macOS ~/Library/Application Support/.
2. **PORTLESS_* env var names**: README mentions env config but full list of supported `PORTLESS_*` vars not enumerated; common pattern assumed (NAME, PROXY_PORT, TLD, etc.).
3. **Framework auto-detect scope**: README lists Vite, Astro, Next, React Router as examples; full list not provided. Likely heuristic-based on `package.json` dependencies.
4. **Tailscale Funnel lifecycle**: Requires Tailscale CLI; integration model (auto-enable vs manual) not explicit.
5. **Windows/Linux daemon registration**: README mentions systemd/launchd; exact service unit names and paths not detailed.

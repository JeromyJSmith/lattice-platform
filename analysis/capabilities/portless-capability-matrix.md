<!-- spec-verified: vercel-labs/portless 0.9.4 2026-05-13 -->
# Capability Matrix — portless

| Capability ID | Harness | Value | Risk | Decision | Proof run | Registry state after proof | Verification target | Tracking |
|---|---|---|---|---|---|---|---|---|
| `portless-cli-run` | `meta-harness` | `high` | `low` | `candidate` | `none` | `none` | `portless myapp bun run dev --help; bun pm ls -g \| grep portless@0.9` | Meta-Harness — Dev Infrastructure (#TBD-portless-cli-run) |
| `portless-cli-auto-infer` | `meta-harness` | `medium` | `low` | `candidate` | `none` | `none` | `portless run bun run dev` (in a Git repo); verify HOSTNAME auto-detection | Meta-Harness — Dev Infrastructure (#TBD-portless-cli-auto-infer) |
| `portless-cli-alias` | `meta-harness` | `medium` | `low` | `candidate` | `none` | `none` | `portless alias docker-api localhost:9999; portless list \| grep docker-api` | Meta-Harness — Dev Infrastructure (#TBD-portless-cli-alias) |
| `portless-cli-list` | `meta-harness` | `medium` | `low` | `candidate` | `none` | `none` | `portless list` (displays running routes and port assignments) | Meta-Harness — Dev Infrastructure (#TBD-portless-cli-list) |
| `portless-cli-proxy-control` | `meta-harness` | `high` | `low` | `candidate` | `none` | `none` | `portless proxy start; portless proxy stop; portless proxy restart` (daemon lifecycle) | Meta-Harness — Dev Infrastructure (#TBD-portless-cli-proxy-control) |
| `portless-cli-service-install` | `meta-harness` | `low` | `low` | `defer` | `none` | `DEFERRED` | System-level registration requires sandbox exception on macOS or systemd privilege on Linux; deferred to team ops setup phase | Meta-Harness / Operations (#TBD-portless-cli-service-install) |
| `portless-config-json` | `meta-harness` | `medium` | `low` | `candidate` | `none` | `none` | Create `.portless.json` in project root; run `portless run dev; curl https://myapp.localhost/` | Meta-Harness — Dev Infrastructure (#TBD-portless-config-json) |
| `portless-config-pkg-json` | `meta-harness` | `medium` | `low` | `defer` | `none` | `DEFERRED` | out-of-scope-for-current-phase (Wave 1 uses explicit .portless.json; package.json config is convenience variant); future proof targets monorepo setups | Meta-Harness / Phase 2 — Monorepo (#TBD-portless-config-pkg-json) |
| `portless-config-monorepo` | `meta-harness` | `medium` | `low` | `defer` | `none` | `DEFERRED` | out-of-scope-for-current-phase (Wave 1 focuses on single-service proxy; monorepo multi-app routing is Phase 2 concern); future proof: Bun workspace + portless.json paths mapping | Meta-Harness / Phase 2 — Monorepo (#TBD-portless-config-monorepo) |
| `portless-hostname-routing` | `meta-harness` | `high` | `low` | `candidate` | `none` | `none` | DNS resolution and HTTP Host header routing; verify `curl -H "Host: myapp.localhost" http://localhost:4000` matches `curl https://myapp.localhost` | Meta-Harness — Dev Infrastructure (#TBD-portless-hostname-routing) |
| `portless-https-auto-cert` | `meta-harness` | `high` | `low` | `candidate` | `none` | `none` | First run: `portless proxy start`; verify OS trust store updated; `openssl s_client -connect myapp.localhost:443` shows valid cert with zero warnings | Meta-Harness — Dev Infrastructure (#TBD-portless-https-auto-cert) |
| `portless-port-env-injection` | `meta-harness` | `high` | `low` | `candidate` | `none` | `none` | Run dev server with `portless myapp bun run dev`; verify child process reads `$PORT` env and binds to it; `portless list` confirms port assignment | Meta-Harness — Dev Infrastructure (#TBD-portless-port-env-injection) |
| `portless-custom-tld` | `meta-harness` | `low` | `low` | `defer` | `none` | `DEFERRED` | out-of-scope-for-current-phase (team TLD conventions not yet defined); target phase for post-Wave 1 multi-team setup | Meta-Harness / Phase 3 — Team Config (#TBD-portless-custom-tld) |
| `portless-git-worktree-prefix` | `meta-harness` | `high` | `low` | `candidate` | `none` | `none` | Create Git worktree with branch name; `portless myapp bun run dev`; verify HOSTNAME includes branch prefix (e.g., `fix-ui.myapp.localhost`) | Meta-Harness — Dev Infrastructure (#TBD-portless-git-worktree-prefix) |
| `portless-mdn-discovery` | `meta-harness` | `low` | `low` | `defer` | `none` | `DEFERRED` | out-of-scope-for-current-phase (LAN mode requires mDNS + network isolation setup); target phase: team mobile testing (Phase 3) | Meta-Harness / Phase 3 — Mobile Testing (#TBD-portless-mdn-discovery) |
| `portless-tailscale-integration` | `meta-harness` | `low` | `medium` | `defer` | `none` | `DEFERRED` | awaiting-upstream-dep (Tailscale CLI provisioning not yet configured in LATTICE); target phase: team sharing (Phase 3) | Meta-Harness / Phase 3 — Team Sharing (#TBD-portless-tailscale-integration) |
| `portless-framework-auto-flags` | `meta-harness` | `high` | `low` | `candidate` | `none` | `none` | Run against multiple frameworks (Next, Vite, Astro); verify auto-detected flags applied without explicit --flag args; check child process received correct PORT and flags | Meta-Harness — Dev Infrastructure (#TBD-portless-framework-auto-flags) |
| `portless-env-vars-portless-prefix` | `meta-harness` | `medium` | `low` | `candidate` | `none` | `none` | Set `PORTLESS_NAME=my-override PORTLESS_PROXY_PORT=5000` and run portless; verify config overrides file-based defaults | Meta-Harness — Dev Infrastructure (#TBD-portless-env-vars-portless-prefix) |

## Notes on decision policy

**Why all CLI commands and most patterns are `candidate`:** Portless is a dev-only proxy tool with zero production impact. All core surfaces (CLI, config, HTTPS cert generation, PORT injection, hostname routing, Git worktree integration) are low-risk utilities. They have zero access to production data, no financial impact, and no permission model. Candidates are promoted to ACTIVE when wired into a concrete use case (e.g., `https://llm.localhost:443` serving the LATTICE language-model endpoint).

**Why some patterns are deferred:**

1. **`portless-cli-service-install`** (low value, deferred to ops phase): System-level daemon registration is valuable for persistent dev environments but requires privileged operations (launchd on macOS, systemd on Linux). Deferred pending team infrastructure setup.

2. **`portless-config-pkg-json`** (medium value, deferred to monorepo phase): The feature is real and useful for single-purpose monorepos, but Wave 1 uses explicit `.portless.json`. This is convenience duplication, not a critical blocker.

3. **`portless-config-monorepo`** (medium value, deferred to monorepo phase): LATTICE Wave 1 focuses on single-service proxy routing. Multi-app monorepo setups are Phase 2 scope once Bun workspace and LATTICE polyrepo layout is finalized.

4. **`portless-custom-tld`** (low value, deferred to team config phase): Team naming conventions (`.dev`, `.local`, custom domain) are not yet determined. Deferred to Phase 3 post-Wave 1.

5. **`portless-mdn-discovery`** (low value, deferred to mobile testing phase): LAN mode via mDNS is useful for device-to-device mobile testing but adds network complexity. Phase 3 scope once team testing workflows are defined.

6. **`portless-tailscale-integration`** (medium risk, deferred pending provisioning): Tailscale Funnel is powerful for team sharing but depends on Tailscale CLI provisioning not yet configured in LATTICE. Deferred pending infrastructure setup.

**Proof gate:** All rows transition from candidate/deferred to ACTIVE once at least one working end-to-end route is operational. The target proof is `https://llm.localhost:443` serving the LATTICE LLM endpoint (already in flight in `feature/portless-browser-bonsai` branch). Once that route is live and verified via curl/browser, ALL candidate rows become ACTIVE in the same commit, with wiring evidence from the route definition.


<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Dependency Allowlist

Machine-readable form of the user-approved dependency allowlist. Any new external dependency requires a PR that appends a row here, with rationale.

User directive (verbatim): *"All Dependencies can be added to an allowlist: {dependency}"*.

```yaml
# spec-verified: code.claude.com/docs 2026-05-11
allowlist:
  - id: graphify-parisgroup
    name: graphify
    upstream: github.com/parisgroup-ai/graphify
    language: rust
    install_method: curl_install_to_tmp_then_review_then_exec
    install_target: /tmp/graphify-install.sh
    install_review_required: true
    scope: project-local (graphify install-integrations --project-local)
    justification: Structural AST + dependency graph; project-local MCP integration
    phase_added: 1
    capability_registry: analysis/capabilities/graphify-parisgroup-capability-registry.yaml

  - id: gitnexus
    name: gitnexus
    upstream: github.com/abhigyanpatwari/GitNexus
    language: nodejs
    install_method: npm_install_local
    install_target: package.json (devDependency)
    install_globally: false  # USER PREFERENCE — NOT -g
    scope: project-local
    justification: Execution-graph + PreToolUse/PostToolUse hooks; local devDep keeps tooling scoped to repo
    phase_added: 1
    capability_registry: analysis/capabilities/gitnexus-capability-registry.yaml

  - id: infranodus-mcp-server
    name: infranodus-mcp-server
    upstream: github.com/infranodus/mcp-server-infranodus
    language: nodejs
    install_method: npx
    install_target: .mcp.json (no global install)
    api_key_env: INFRANODUS_API_KEY
    api_key_in_env_example: true   # empty value placeholder only — never a real key
    scope: per-session via npx -y
    justification: Semantic graph + content-gap analysis; API-key gated; runs ephemerally per session
    phase_added: 1
    capability_registry: analysis/capabilities/infranodus-capability-registry.yaml

  - id: graphifyy-safishamsi
    name: graphifyy
    upstream: github.com/safishamsi/graphify
    language: python
    install_method: uv_tool_install
    install_target: graphifyy   # note the double-y — PyPI name disambiguator
    scope: user-local via uv tool
    justification: Multi-format + YouTube URL ingestion; complements the Rust graphify; powers Amendment 07 substrate
    phase_added: 0.7
    capability_registry: analysis/capabilities/graphify-safishamsi-capability-registry.yaml

  - id: infranodus-skills
    name: infranodus-skills
    upstream: github.com/infranodus/skills
    language: markdown_bundle
    install_method: unzip_to_skills_dir
    install_target: ~/.claude/skills/
    scope: user-global
    justification: InfraNodus's bundled Claude skills (Cognitive Variability, Ontology Creator, etc.)
    phase_added: 1
    capability_registry: analysis/capabilities/infranodus-capability-registry.yaml  # listed under "skills" surface
```

## Adding a new dependency

1. Open a PR that appends a row to the YAML above
2. Same PR creates `analysis/capabilities/<id>-capability-registry.yaml` (stub OK, but every capability surface enumerated per Capability Harvest Protocol)
3. PR description includes: what alternative was considered, why this one was chosen, install footprint, runtime cost, security surface
4. Merge gated on reviewer approval (Zero Dead DNA enforced from first commit)

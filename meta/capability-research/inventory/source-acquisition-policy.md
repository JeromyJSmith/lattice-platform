# Source Acquisition Policy

Governs how external source repositories, tool binaries, and third-party
artifacts enter the LATTICE repository. Prevents nested `.git/` contamination
and ensures every vendored dependency is auditable and reproducible.

## The Rule

**Vendored = plain copy. No nested `.git/` directories.**

When incorporating external source (Disler SFAs, parisgroup tools, any GitHub
repo), the nested `.git/` directory MUST be stripped before `git add`.

```bash
# Wrong — adds entire repo including .git/
cp -r external-repo/ vendor/

# Correct — strip .git/ before staging
cp -r external-repo/ vendor/
rm -rf vendor/.git
git add vendor/
```

Failure to strip `.git/` causes:
- Submodule detection failures in CI (git treats it as a submodule)
- `git status` confusion (changes inside nested repo invisible to outer git)
- `git diff` not showing vendored file changes

## Source Families

### Disler / IndyDevDan (github.com/disler)

SFA (Single-File Agentic) scripts vendored into `meta/harness/tools/sfa-eval/`.

Policy:
- Copy individual `.py` files, not the entire repo directory
- Strip any data fixtures, .env files, or `.git/` from copy
- Add a `# vendored from: github.com/disler/<repo>@<sha>` comment at top of file
- Create corresponding ACTIVE registry row in the appropriate capability registry

### parisgroup / graphify (github.com/parisgroup/graphify)

Binary installed globally via npm/homebrew — do NOT vendor the binary.

Policy:
- Record the installed version in capability registry (install-evidence type)
- `graphify.toml` is the in-repo config surface; hand-author it
- Skills in `.claude/skills/generated/` are hand-crafted until graphify gains auto-generate

### InfraNodus (github.com/noduslabs/infranodus)

Cloud service + MCP server — nothing to vendor.

Policy:
- Auth via `INFRANODUS_API_KEY` env var (set in shell rc, never committed)
- Output artifacts (`analysis/infranodus/*.json`) ARE committed as proof
- `build-gap-analysis.py` is the CLI driver for CI/cron use

### IfcOpenShell (github.com/ifcopenshell/ifcopenshell-python)

Installed via `uv` into the pixeltable sidecar environment.

Policy:
- Version pinned in `pixeltable/pyproject.toml`
- Never vendor IfcOpenShell source; use published wheel
- IFC test fixtures (`.ifc` files) go in `pixeltable/tests/fixtures/`

## Checking for Nested .git/ Contamination

Before any commit that adds external source:

```bash
# Find nested .git/ directories (should return empty)
find . -name ".git" -not -path "./.git" -type d

# Check git submodule status
git submodule status
```

CI enforces this via `audit-dead-dna.sh` which will flag unexpected submodule refs.

## Proof Requirements for Vendored Sources

Every vendored file needs an ACTIVE registry row with:
- `surface: vendored_script` or `surface: cli_command`
- `wired_at:` pointing to the vendored path
- `proof.evidence:` pointing to a session JSON in `meta/harness/docs/sessions/`

Without proof, the row is DEFERRED. Without a row, it has no formal status in
the capability lifecycle.

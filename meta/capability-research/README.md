# Capability Research

This folder is the home for LATTICE capability research and source
organization. It sits outside `meta/harness/` because research organization is
not the same thing as harness execution.

## Read Order

1. `ARCHITECTURE.md`
2. `INVENTORY.md`
3. `tools/READINESS.md`
4. `inventory/local-graph-tool-audit.md`
5. `tools/infranodus-skills-master-audit.md`
6. `tools/infranodus-gap-analysis-2026-05-13.md`
7. `census/repo-census-001.md`
8. `census/repo-census-002-ui-transfer.md`
9. `census/repo-census-003-vectorworks.md`
10. `census/repo-census-004-odbc.md`

## Folder Contract

| Path | Purpose |
|---|---|
| `ARCHITECTURE.md` | System architecture for capability research, proof gates, and runtime adoption |
| `INVENTORY.md` | Current audit of what exists, what is misplaced, what is missing, and where things should move |
| `census/` | Human-readable research sweeps for source families |
| `tools/` | Readiness notes for InfraNodus, Graphify, GitNexus, and related graph/research tools |
| `inventory/` | Corpus manifests, local tool audits, machine-generated inventory snapshots, and allowed graph outputs |

## Related Runtime And Proof Locations

| Location | Purpose |
|---|---|
| `analysis/capabilities/` | Machine-readable capability registries consumed by the harness matrix |
| `meta/harness/` | Golden Path proof execution, verifier rules, evidence policy, and operator handoff |
| `pixeltable/service/routes/harness.py` | Current FastAPI harness API surface |
| `src/routes/harness.*` | Current operator UI surfaces for harness/capability proof |
| Future `lattice/knowledge/*` | Source repo, artifact, vocabulary, and capability tables |
| Future `lattice/harness/*` | Run contract, verifier result, evidence, and promotion tables |

## Rule

Do not run Graphify or GitNexus over the whole repo until `INVENTORY.md`,
`inventory/corpus-manifest.yaml`, `tools/output-manifest.md`, and
`tools/READINESS.md` say the corpus boundaries are ready. InfraNodus can run
first against the curated doc list because its job is gap analysis, not repo
indexing.

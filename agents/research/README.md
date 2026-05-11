# Research agent

Knowledge graph + literature retrieval for design decisions. Wraps the local knowledge index at `~/.config/knowledge-index.sqlite` (see [`CLAUDE.md`](../../CLAUDE.md)), the DDC skill patterns ([`skills/ddc/`](../../skills/ddc/)), and ad-hoc web research.

Output rows go to `lattice/bridge/semantic/landscape_entities`; cited sources to `lattice/execution/evidence`.

See [`AGENTS.md`](../../AGENTS.md).

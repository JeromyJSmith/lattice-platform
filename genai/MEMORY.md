# GenAI Pipeline Harness — Session Memory

## Open Decisions

1. **Quality scoring model**: should quality_score be automated (heuristic: texture resolution + geometry vertex count + botanical feature detection) or human-curated? Current: placeholder, needs definition. May implement hybrid (80% heuristic + 20% human override).
2. **Plant species taxonomy**: are we using USDA PLANTS Database names, scientific binomial, or VW Plant Style Manager naming? Currently inconsistent. Need unified taxonomy mapping before scaling.
3. **Asset versioning**: should we track asset iterations (species + v1, v2, v3) or always replace? Current: no versioning. May add git-like commit hashes for traceability.

## Failed Experiments

- (placeholder — no failed experiments logged yet for this section)

## Session Handoff Notes

**Current state (2026-05-13)**: Asset registry table scaffolded in migration 0013. `assets/plants/lod-100/` and `assets/plants/lod-300/` directories created. ComfyUI job tracking table created. Training run table created. Plant-2d-to-3d pipeline sketched (feature extraction + registry lookup, not yet wired to VW bridge).

**Known issues**:
- No training data yet (would come from annotated VW symbol library)
- ComfyUI integration pending (assumes ComfyUI server at localhost:8188, not yet installed)
- Quality scoring logic undefined — currently hardcoded placeholder values
- Asset promotion UX undefined (who clicks the promote button?)

**Ready for next agent**: Asset registry ready for population. ComfyUI integration ready for wiring. Quality evaluation model ready for design + implementation. Plant-2d-to-3d pipeline ready for VW bridge connection. Next: define quality scoring, add sample training data, wire ComfyUI dispatcher.

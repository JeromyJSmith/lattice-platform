# DDC Skill Corpus Mirror

This directory mirrors the upstream DDC skill corpus from:

- `projects/DDC_Skills_for_AI_Agents_in_Construction-main`

The mirror is refreshed with:

```bash
uv run scripts/harvest_ddc_assets.py --skills-only
```

Current structure keeps upstream top-level groups:

- `1_DDC_Toolkit/`
- `2_DDC_Book/`
- `3_DDC_Insights/`
- `4_DDC_Curated/`
- `5_DDC_Innovative/`

Each skill package contributes an upstream `SKILL.md` that can be indexed and searched by LATTICE semantic services.

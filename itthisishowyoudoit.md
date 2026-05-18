# itthisishowyoudoit

This is the exact workflow to get GitNexus + Graphify running and queryable in this repo.

## 1) GitNexus UI (Docker) pointed at this repo

```bash
docker rm -f gitnexus-web gitnexus-server || true

docker run -d --name gitnexus-server \
  -p 4747:4747 \
  -e GITNEXUS_HOME=/data/gitnexus \
  -v "/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge:/workspace" \
  -v vw_itwin_gitnexus_data:/data/gitnexus \
  ghcr.io/abhigyanpatwari/gitnexus:latest

docker run -d --name gitnexus-web \
  -p 4173:4173 \
  ghcr.io/abhigyanpatwari/gitnexus-web:latest
```

## 2) Programmatically register/analyze this mounted workspace

```bash
curl -sS -X POST http://127.0.0.1:4747/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"path":"/workspace"}'
```

Check repo registration:

```bash
curl -sS http://127.0.0.1:4747/api/repos
```

Open UI:

```text
http://127.0.0.1:4173
```

Select `lattice-platform-scoped`.

## 3) Refresh Graphify AST graph

```bash
graphify update /Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge
```

## 4) Run full LLM semantic extraction with Claude Code CLI (not API backend)

Important: strip the paid-API env vars listed in `.claude/hooks/api-key-policy.json#denylist` so Graphify uses subscription session auth. The `.claude/bin/env-strip` helper reads the policy data and does this automatically.

```bash
rm -f /Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/graphify-out/manifest.json
.claude/bin/env-strip graphify extract \
  /Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge --backend claude-cli
```

Authority: `~/.claude-code-docs/docs/authentication.md` (Authentication precedence).

## 5) Quick verification

```bash
python3 - <<'PY'
import json
g=json.load(open('graphify-out/graph.json'))
print('nodes', len(g.get('nodes', [])))
print('links', len(g.get('links', [])))
print('built_at_commit', g.get('built_at_commit'))
PY
```

If `nodes` and `links` are non-zero and UI is reachable on `:4173`, setup is good.

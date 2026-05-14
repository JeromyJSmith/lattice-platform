# Graph restart + query runbook (full geometry)
This is the full process to recover after a machine restart and get:
- full GitNexus graph in browser
- terminal/agent query access for answers

## 0) Preconditions
- Docker is running.
- You are in repo root:

```bash
pwd
# /Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge
```

## 1) Ensure GitNexus is not scoped to a tiny subset
Use this `.gitnexusignore` (minimal exclusions only):

```bash
cat > .gitnexusignore <<'EOF'
.git/
node_modules/
dist/
build/
coverage/
graphify-out/
.gitnexus/
EOF
```

## 2) Start/restart GitNexus Docker services

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

## 3) Build full-repo index (force reindex)

```bash
docker exec -w /workspace gitnexus-server \
  node /app/gitnexus/dist/cli/index.js analyze . --force --name lattice-platform-scoped
```

## 4) Verify index size from terminal

```bash
curl -sS http://127.0.0.1:4747/api/repos
```

Expected shape (counts will vary):
- files: hundreds
- nodes: thousands
- edges: thousands

## 5) Open full graph UI
Open:

```text
http://127.0.0.1:4173/?project=lattice-platform-scoped&server=http%3A%2F%2Flocalhost%3A4747
```

If browser still shows old tiny counts, force reload services once:

```bash
docker restart gitnexus-server gitnexus-web
```

Then hard refresh the page.

## 6) Query graph from terminal (agent-ready)
Use `/api/query` with Cypher.

### 6.1 God nodes (highest-degree hotspots)

```bash
curl -sS -X POST 'http://127.0.0.1:4747/api/query?repo=lattice-platform-scoped' \
  -H 'Content-Type: application/json' \
  -d '{"cypher":"MATCH (n)-[r]-() RETURN n.name AS node, labels(n) AS type, count(r) AS degree ORDER BY degree DESC LIMIT 20"}'
```

### 6.2 Macro geometry by node type

```bash
curl -sS -X POST 'http://127.0.0.1:4747/api/query?repo=lattice-platform-scoped' \
  -H 'Content-Type: application/json' \
  -d '{"cypher":"MATCH (n) RETURN labels(n) AS label, count(*) AS c ORDER BY c DESC LIMIT 20"}'
```

### 6.3 Top process flows

```bash
curl -sS -X POST 'http://127.0.0.1:4747/api/query?repo=lattice-platform-scoped' \
  -H 'Content-Type: application/json' \
  -d '{"cypher":"MATCH (n) WHERE labels(n)=\"Process\" RETURN n.id AS process_id, n.label AS process, n.processType AS type, n.stepCount AS steps ORDER BY steps DESC LIMIT 20"}'
```

### 6.4 Pull full graph payload for custom scripts

```bash
curl -sS 'http://127.0.0.1:4747/api/graph?repo=lattice-platform-scoped' > /tmp/gitnexus-graph.json
```

## 7) Fast UI tuning for useful geometry (not noise)
In GitNexus UI:
1. Select a hotspot file (from god-node list).
2. Open `Filters`.
3. Hide noisy node types (`Variable`, `Import`) for structure-first view.
4. Set `Focus Depth` to `2 hops`.
5. Click `Focus on Selected Node`.
6. Use `Fit to Screen`.

This gives a readable architecture lens instead of dense symbol fog.

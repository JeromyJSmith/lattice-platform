# CWICR Install — OrbStack Ubuntu VM + Qdrant

Goal: have Qdrant running locally at `localhost:6333` with 55,719 CWICR cost items loaded as embedded points.

Time budget: ~15 min on Apple Silicon.

## 1. Install OrbStack (if not already)

```bash
brew install orbstack
```

OrbStack is the lightweight Mac-native Linux/Docker runtime. We use it to run Qdrant (Docker) and any DDC Linux-only converters (Ubuntu VM, fallback only — see `../converters/`).

## 2. Start Qdrant via OrbStack's Docker

```bash
docker run -d \
  --name lattice-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $HOME/.lattice/qdrant:/qdrant/storage \
  qdrant/qdrant:latest

# Verify
curl -s http://localhost:6333/collections
```

OrbStack proxies Docker port 6333 to the Mac host with zero config.

## 3. Seed the 55,719 items

```bash
./seed-qdrant.sh
```

The script:

1. Downloads the latest CWICR release tarball from the OpenConstructionEstimate-DDC-CWICR releases page.
2. Creates a Qdrant collection `cwicr` with `vector_size=768` and cosine distance (matches `sentence-transformers/all-mpnet-base-v2`, the embedding model the LATTICE sidecar already pins).
3. Encodes each cost item's description + region + unit and POSTs in batches of 256.

Expect ~3 minutes on Apple Silicon. The script is idempotent — re-running picks up where it stopped via the `upsert` endpoint.

## 4. Verify

```bash
python3 cost-search.py "concrete slab 10cm reinforced" --region US --top 3
```

Should return three ranked items with `unit_cost`, `unit_currency`, and `unit_cost_region` fields.

## 5. Wire into the LATTICE sidecar

Add to `pixeltable/service/routes/erp.py` (create this file as part of the BOQ adapter feature):

```python
@router.post("/cost-search")
def post_cost_search(body: dict, ...):
    import subprocess, json
    proc = subprocess.run(
        ["python3", "/abs/path/to/ddc/cwicr/cost-search.py",
         body["description"], "--region", body.get("region", "US"),
         "--top", str(body.get("top", 5))],
        capture_output=True, text=True, check=True,
    )
    return {"results": json.loads(proc.stdout)}
```

Better: import `cost-search.py` directly as a module so we avoid subprocess overhead. The above pattern is the fastest path to "it works".

## 6. Re-seed on CWICR updates

When DDC publishes a new CWICR release, just re-run `./seed-qdrant.sh`. The collection is idempotent on the item's stable ID.

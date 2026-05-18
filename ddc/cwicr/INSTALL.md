# CWICR Install — OrbStack Ubuntu VM + Qdrant

Goal: have Qdrant running locally at `localhost:6333` with the smallest published CWICR snapshot loaded into `cwicr` as 3072-dimensional vectors. The bounded default is `HI_MUMBAI_workitems_costs_resources_EMBEDDINGS_3072_DDC_CWICR.snapshot` at 49,600 points; the broader 55,719-point corpus target remains a follow-on restore.

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

## 3. Seed the bounded local snapshot

```bash
./seed-qdrant.sh
```

The bounded seed contract:

1. Verifies the latest CWICR GitHub release exposes snapshot assets for the live corpus.
2. Verifies the target Qdrant collection `cwicr` is reachable on `localhost:6333`.
3. Restores the published `HI_MUMBAI_workitems_costs_resources_EMBEDDINGS_3072_DDC_CWICR.snapshot` asset when needed.
4. Fails closed unless the local collection reports 49,600 points at vector size 3072.

This repository now proves the smallest real restore path against the published release by recovering the bounded HI_MUMBAI snapshot into `cwicr`. It does **not** yet prove a full 55,719-point / multi-locale reseed in-session.

## 4. Verify

```bash
./seed-qdrant.sh
```

The command exits `0` only when `cwicr` matches the bounded local release contract (`49,600 x 3072`). Otherwise it exits non-zero and prints machine-readable blockers describing the observed point-count/vector-size mismatch.

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

When DDC publishes a new CWICR release, rerun `./seed-qdrant.sh`. It will only go green once the local collection has been restored or reseeded to match the new release contract.

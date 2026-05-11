# Orchestrator agent

Routes incoming runtime tasks to the right specialized agent. Owns the dispatch loop that picks up `agent_runs` rows in `status: pending` and decides which adapter to call.

Currently a stub. The active dispatcher is `pixeltable/service/worker.py` which always routes to `claude-cli`. When tasks accumulate distinct shapes (IFC ingest, geometry, research) the orchestrator picks the right downstream agent here.

See [`AGENTS.md`](../../AGENTS.md) § Runtime purpose.

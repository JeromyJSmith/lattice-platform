.DEFAULT_GOAL := help

PXT_HOME ?= /Volumes/PixelTable/.pixeltable
SOCK     ?= /tmp/vwbridge-pxt.sock
PORT     ?= 7770

export PIXELTABLE_HOME := $(PXT_HOME)
export PYTHONPATH      := $(PWD)

.PHONY: help bootstrap migrate-dryrun migrate fixture-load verify sidecar-up sidecar-up-tcp doctor test test-no-pxt test-pxt check snapshot

help:
	@grep -E '^[a-zA-Z][a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?##"}{printf "%-22s %s\n", $$1, $$2}'

bootstrap: ## Install Python deps via uv into a local .venv
	uv sync --extra dev

migrate-dryrun: ## Plan-only: prints would-create / exists per namespace and table
	uv run python scripts/bootstrap.py --dry-run

migrate: ## Idempotent: create namespaces, tables, embedding indices
	uv run python scripts/bootstrap.py

fixture-load: ## Load deterministic mini fixtures into the live PXT instance
	uv run python scripts/load_fixtures.py

verify: ## Full self-check; writes bridge_gap_matrix; exits non-zero on drift
	uv run python scripts/verify.py

snapshot: ## Write live schema descriptor to .schema-snapshot.yaml (for PR review)
	uv run python scripts/verify.py --write

sidecar-up: ## Foreground sidecar over UNIX socket ($(SOCK))
	uv run uvicorn service.main:app --uds $(SOCK) --reload

sidecar-up-tcp: ## Foreground sidecar over TCP (loopback) for WSL/dev-container
	uv run uvicorn service.main:app --host 127.0.0.1 --port $(PORT) --reload

doctor: ## Diagnose env (PIXELTABLE_HOME, sidecar socket, deps)
	uv run python scripts/doctor.py

test: ## Run full test suite (requires writeable PIXELTABLE_HOME; uses ephemeral if not set)
	uv run pytest -q

test-no-pxt: ## Run only the tests that don't touch Pixeltable
	uv run pytest -q -m "not pxt" tests/no_pxt

test-pxt: ## Run only the integration tests that spin up an ephemeral PXT_HOME
	uv run pytest -q tests/pxt

check: bootstrap migrate-dryrun migrate fixture-load verify ## CI-equivalent local chain

"""Sidecar settings.

Environment variables (see ../../.env.example):

  PIXELTABLE_HOME           Required. Path to the shared Pixeltable instance.
  RUNTIME_RUNS_DIR          Default ./runtime-runs (relative to harness repo).
  BENTLEY_CLIENT_ID         iTwin OAuth 2.0 client_credentials.
  BENTLEY_CLIENT_SECRET     iTwin OAuth 2.0 client_credentials.
  BENTLEY_TOKEN_ENDPOINT    Default https://ims.bentley.com/connect/token
  BENTLEY_API_BASE          Default https://api.bentley.com
  BENTLEY_SCOPES            Space-separated; defaults match spec §5.4.
  EMBED_MODEL_ID            Default sentence-transformers/all-mpnet-base-v2.
  QDRANT_URL                Optional. If set, sidecar mirrors embeddings.
  QDRANT_API_KEY            Optional.
  IFC_MAX_BYTES             Default 50_000_000 (50 MB) per spec §12.
  PXT_LOG_LEVEL             Default INFO.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

DEFAULT_BENTLEY_SCOPES = (
    "itwin-platform itwins:read imodels:read "
    "synchronization:read synchronization:modify changedelements:read"
)


@dataclass(frozen=True)
class Settings:
    pixeltable_home: str
    runtime_runs_dir: str = "./runtime-runs"
    bentley_client_id: str | None = None
    bentley_client_secret: str | None = None
    bentley_token_endpoint: str = "https://ims.bentley.com/connect/token"
    bentley_api_base: str = "https://api.bentley.com"
    bentley_scopes: str = DEFAULT_BENTLEY_SCOPES
    embed_model_id: str = "sentence-transformers/all-mpnet-base-v2"
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    ifc_max_bytes: int = 50_000_000
    log_level: str = "INFO"
    contract_version: str = "v1"
    idempotency_lru_size: int = 4096
    grammars_version_file: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "grammars", "VERSION",
    ))


def load() -> Settings:
    home = os.environ.get("PIXELTABLE_HOME")
    if not home:
        raise RuntimeError(
            "PIXELTABLE_HOME is not set. Export PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable"
        )
    return Settings(
        pixeltable_home=home,
        runtime_runs_dir=os.environ.get("RUNTIME_RUNS_DIR", "./runtime-runs"),
        bentley_client_id=os.environ.get("BENTLEY_CLIENT_ID") or None,
        bentley_client_secret=os.environ.get("BENTLEY_CLIENT_SECRET") or None,
        bentley_token_endpoint=os.environ.get(
            "BENTLEY_TOKEN_ENDPOINT", "https://ims.bentley.com/connect/token"
        ),
        bentley_api_base=os.environ.get("BENTLEY_API_BASE", "https://api.bentley.com"),
        bentley_scopes=os.environ.get("BENTLEY_SCOPES", DEFAULT_BENTLEY_SCOPES),
        embed_model_id=os.environ.get(
            "EMBED_MODEL_ID", "sentence-transformers/all-mpnet-base-v2"
        ),
        qdrant_url=os.environ.get("QDRANT_URL") or None,
        qdrant_api_key=os.environ.get("QDRANT_API_KEY") or None,
        ifc_max_bytes=int(os.environ.get("IFC_MAX_BYTES", "50000000")),
        log_level=os.environ.get("PXT_LOG_LEVEL", "INFO"),
    )

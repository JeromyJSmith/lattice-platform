#!/usr/bin/env bash
set -euo pipefail

ROOT="/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge"
REPO_DIR="$ROOT/.cache/vectorworks-mcp-github"
SERVER_DIR="$REPO_DIR/mcp-server"
BIN="$SERVER_DIR/target/release/vectorworks-mcp-server"

if [[ ! -d "$REPO_DIR" ]]; then
  git clone --depth 1 https://github.com/mako-357/vectorworks-mcp.git "$REPO_DIR" >&2
fi

if [[ ! -x "$BIN" ]]; then
  cargo build --release --manifest-path "$SERVER_DIR/Cargo.toml" >&2
fi

exec "$BIN"

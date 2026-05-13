#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Minimal localhost static server for the WebGPU Bonsai host page.

WebGPU requires a "secure context" (HTTPS or localhost). We bind to
127.0.0.1 so the browser treats this as a secure context without
needing TLS. Default port 8765; override with --port.

Usage:
  uv run meta/harness/in-tab-llm/serve.py
  uv run meta/harness/in-tab-llm/serve.py --port 8765 --bind 127.0.0.1

The SFA at sfa_in_tab_bonsai_v1.py auto-launches this in a subprocess.
You can also run it standalone for manual testing in a real browser.
"""
from __future__ import annotations

import argparse
import http.server
import socketserver
import sys
from pathlib import Path


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler that logs to stderr in a terse format."""

    def log_message(self, format: str, *args) -> None:
        """Emit a single-line access log to stderr."""
        sys.stderr.write(f"[serve.py] {self.address_string()} - {format % args}\n")
        sys.stderr.flush()

    def end_headers(self) -> None:
        """Add cross-origin isolation headers so SharedArrayBuffer + WebGPU compute work."""
        # transformers.js benefits from cross-origin isolation for some
        # backends; harmless when not used.
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()


def main() -> int:
    """Entry point: parse args, serve until killed."""
    parser = argparse.ArgumentParser(description="Localhost static server for in-tab-llm.")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind (default 8765).")
    parser.add_argument("--bind", default="127.0.0.1", help="Address to bind (default 127.0.0.1).")
    parser.add_argument("--root", default=str(Path(__file__).parent), help="Document root (default: this dir).")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        sys.stderr.write(f"[serve.py] ERROR: root {root} is not a directory\n")
        return 1

    # Change CWD so SimpleHTTPRequestHandler serves from root.
    import os
    os.chdir(root)

    handler = QuietHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((args.bind, args.port), handler) as httpd:
        url = f"http://{args.bind}:{args.port}/bonsai-host.html"
        sys.stderr.write(f"[serve.py] serving {root} at http://{args.bind}:{args.port}/\n")
        sys.stderr.write(f"[serve.py] bonsai host:  {url}\n")
        sys.stderr.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            sys.stderr.write("[serve.py] shutdown\n")
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

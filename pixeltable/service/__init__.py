"""FastAPI sidecar for the VW-iTwin-MARPA Pixeltable bridge.

Exposes the only process that holds an open `pixeltable` session for this
body. All writes from the TanStack/Bun harness flow through here over a
loopback UNIX socket.
"""

__version__ = "0.1.0"
__contract_version__ = "v1"

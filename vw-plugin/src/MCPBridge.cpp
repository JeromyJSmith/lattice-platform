// MCPBridge.cpp — Unix socket client to the LATTICE FastAPI sidecar.

#include "MCPBridge.h"

// On Windows, swap to a named pipe (`\\.\pipe\vwbridge-pxt`). The bridge
// presents the same API either way.

namespace lattice {

namespace {
std::string g_socket_path;
bool        g_active = false;
}  // namespace

bool MCPBridgeStart(const std::string& socket_path) {
  g_socket_path = socket_path;
  g_active = true;  // TODO: actually connect, retain socket, manage reconnects
  return true;
}

void MCPBridgeStop() {
  g_active = false;
  // TODO: close socket
}

bool MCPBridgeEmit(const std::string& /*kind*/, const std::string& /*payload_json*/) {
  if (!g_active) return false;
  // TODO: write JSON line to the Unix socket. Format must match
  // pixeltable/service/routes/runtime.py expectations.
  return true;
}

}  // namespace lattice

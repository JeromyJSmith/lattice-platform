// MCPBridge.h — Unix-socket IPC to the LATTICE MCP server.
//
// Allows agent runtimes (Claude CLI, etc.) to read/write VW document state
// through the LATTICE sidecar without driving the GUI.

#pragma once

#include <string>

namespace lattice {

bool MCPBridgeStart(const std::string& socket_path);
void MCPBridgeStop();

// Fire-and-forget event to the sidecar. Returns false on socket error.
bool MCPBridgeEmit(const std::string& kind, const std::string& payload_json);

}  // namespace lattice

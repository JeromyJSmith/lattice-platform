// plugin-entry.cpp — VWSDK module entry point.
//
// VW calls into this file when the .vwlibrary is loaded. We register the
// menu commands and start the MCP bridge. Wire this up properly once VWSDK
// headers are downloaded — see vw-plugin/sdk/README.md.

#include "PlaceholderCmd.h"
#include "MCPBridge.h"

// VWSDK macros (e.g. ADD_MODULE_REQUIREMENT) live in VWSDK headers; this
// file is intentionally minimal until the SDK is present.

namespace lattice {

void PluginInit() {
  RegisterPlaceholderCmd();
  MCPBridgeStart("/tmp/vwbridge-pxt.sock");
}

void PluginShutdown() {
  MCPBridgeStop();
}

}  // namespace lattice

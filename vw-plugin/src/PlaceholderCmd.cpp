// PlaceholderCmd.cpp — implementation of the "Generate LATTICE Placeholders" menu command.
//
// Tracked in meta/FEATURE_BACKLOG.md § C++ VECTORWORKS PLUGIN → PlaceholderCmd.cpp.
//
// Algorithm:
//   1. Load vw-plugin/config/placeholder_rules.json
//   2. Walk the active VW document; for each landscape record matching a category in the rules,
//      create the configured primitive at the record's position
//   3. Assign the result to the appropriate Plant Style (never per-instance geometry)
//   4. Emit a "placeholders_created" event to the MCP bridge with run statistics

#include "PlaceholderCmd.h"
#include "MCPBridge.h"
#include "GeometryUtils.h"

namespace lattice {

void RegisterPlaceholderCmd() {
  // TODO: VWSDK menu registration.
}

void RunPlaceholderCmd() {
  // TODO: full implementation — see file header.
  MCPBridgeEmit("placeholders_created", R"({"status":"stub","created":0})");
}

}  // namespace lattice

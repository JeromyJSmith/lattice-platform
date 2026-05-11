// PlaceholderCmd.h — menu command "Generate LATTICE Placeholders".
//
// Reads all landscape elements from the active VW document and creates
// LOD 100 placeholder geometry per category (cone/sphere/disc/box) using
// rules from vw-plugin/config/placeholder_rules.json.
//
// Tracked in meta/FEATURE_BACKLOG.md § C++ VECTORWORKS PLUGIN.

#pragma once

namespace lattice {

void RegisterPlaceholderCmd();
void RunPlaceholderCmd();

}  // namespace lattice

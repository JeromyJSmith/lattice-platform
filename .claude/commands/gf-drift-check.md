---
description: "Check for code graph drift since last Graphify snapshot"
command: "uv tool run graphify diff --baseline .graphify/snapshot.json --current . --format diff"
---
Compares the current code graph against the last saved snapshot. Use after large commits to surface unexpected coupling or dead code introductions.

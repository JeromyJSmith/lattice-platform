---
description: "Generate a Graphify-based refactor plan for a specific module"
command: "uv tool run graphify refactor-plan --module ${MODULE:-pixeltable/} --output /tmp/refactor-plan.md && cat /tmp/refactor-plan.md"
---
Set `MODULE` env var to target a specific path. Defaults to `pixeltable/`. Prints the plan to stdout.

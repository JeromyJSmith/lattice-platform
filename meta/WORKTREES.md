# LATTICE Worktree Map

Long-lived feature branches each have a dedicated worktree under
`../lattice-worktrees/` so you can switch areas without losing in-flight
state in `main`. All branches track `origin/<branch>` and are pushed.

| Branch                    | Worktree path                                          | Owner area     |
|---------------------------|--------------------------------------------------------|----------------|
| `main`                    | `VW_iTwin_Bridge/`                                     | release line   |
| `develop`                 | `../lattice-worktrees/develop`                         | integration    |
| `feature/vw-bridge`       | `../lattice-worktrees/feature-vw-bridge`               | VW / IFC       |
| `feature/3d-viewer`       | `../lattice-worktrees/feature-3d-viewer`               | ThatOpen / R3F |
| `feature/analytics-layer` | `../lattice-worktrees/feature-analytics-layer`         | deck.gl / DuckDB WASM |
| `feature/plant-geometry`  | `../lattice-worktrees/feature-plant-geometry`          | LOD 100→300    |
| `feature/point-cloud`     | `../lattice-worktrees/feature-point-cloud`             | Potree / PDAL  |

## Common operations

```bash
# Open another feature in your editor without leaving main
code ../lattice-worktrees/feature-3d-viewer

# List active worktrees
git worktree list

# Bring a worktree up to date with main
cd ../lattice-worktrees/feature-3d-viewer && git pull origin main --rebase

# Tear down a worktree (won't delete the branch)
git worktree remove ../lattice-worktrees/feature-3d-viewer
```

## Why worktrees instead of multiple clones

- Single `.git` directory, one fetch, one set of remotes.
- Bun and uv caches are shared (the `node_modules/` and `.venv/` live per
  worktree, but the package store is shared across them).
- Hooks, config, and ignore rules stay consistent.

If you're running a sidecar in one worktree and a frontend in another,
make sure both point at the same Pixeltable instance via
`PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable` (the live shared store).

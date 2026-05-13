# Simple Init Parallel

Initialize three parallel git worktree directories for concurrent development.

## Variables

FEATURE_NAME: $ARGUMENTS

## Execute these tasks

CREATE new directory `trees/`

> Execute these steps in parallel for concurrency
>
> Use absolute paths for all commands

CREATE first worktree:
- RUN `git worktree add -b FEATURE_NAME-1 ./trees/FEATURE_NAME-1`
- COPY `./server/.env` to `./trees/FEATURE_NAME-1/server/.env`
- RUN `cd ./trees/FEATURE_NAME-1/server` then `uv sync`
- RUN `cd ../client` then `bun i`
- UPDATE `./trees/FEATURE_NAME-1/client/vite.config.ts` port to `5174`

CREATE second worktree:
- RUN `git worktree add -b FEATURE_NAME-2 ./trees/FEATURE_NAME-2`
- COPY `./server/.env` to `./trees/FEATURE_NAME-2/server/.env`
- RUN `cd ./trees/FEATURE_NAME-2/server` then `uv sync`
- RUN `cd ../client` then `bun i`
- UPDATE `./trees/FEATURE_NAME-2/client/vite.config.ts` port to `5175`

CREATE third worktree:
- RUN `git worktree add -b FEATURE_NAME-3 ./trees/FEATURE_NAME-3`
- COPY `./server/.env` to `./trees/FEATURE_NAME-3/server/.env`
- RUN `cd ./trees/FEATURE_NAME-3/server` then `uv sync`
- RUN `cd ../client` then `bun i`
- UPDATE `./trees/FEATURE_NAME-3/client/vite.config.ts` port to `5176`

VERIFY setup by running `git worktree list`
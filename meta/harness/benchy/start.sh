#!/bin/bash

# Start the dev server in the background
(cd client && bun run dev) &

# Start Python server
(cd server && uv run --env-file .env python server.py) &

# Wait for both processes
wait

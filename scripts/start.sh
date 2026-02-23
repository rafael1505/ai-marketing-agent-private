#!/bin/bash
# Docker container entrypoint for the backend service.
#
# Port note: uvicorn binds to 0.0.0.0:8000 INSIDE the container.
# docker-compose.yml maps this to host port 8088 ("8088:8000").
# The canonical host-facing port is always 8088 per the project constitution.
# Do NOT change this port to 8088 here — it would break the container binding.
# For local non-Docker runs, use: uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload
exec uvicorn app.main:api_app --host 0.0.0.0 --port 8000

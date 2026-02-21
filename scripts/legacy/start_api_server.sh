#!/bin/bash
cd "/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent"
uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload

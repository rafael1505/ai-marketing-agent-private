#!/usr/bin/env python3
import os
import sys
import logging
import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from starlette.middleware.cors import CORSMiddleware
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="API Config Debugger")

# Enable CORS for all origins in debug mode
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Simple root endpoint to test connection"""
    logging.info("Root endpoint called")
    return {
        "status": "API server is running",
        "endpoints": ["/", "/debug", "/api/v1/companies/active"]
    }

@app.get("/debug")
async def debug_info(request: Request):
    """Returns detailed debug info about the request and server"""
    client_host = request.client.host if request.client else "Unknown"
    logging.info(f"Debug endpoint called from {client_host}")
    
    # Get environment variables (filtering out sensitive ones)
    env_vars = {k: v for k, v in os.environ.items() 
                if not any(x in k.lower() for x in ['secret', 'password', 'key'])}
    
    return {
        "request": {
            "client": client_host,
            "headers": dict(request.headers),
            "url": str(request.url)
        },
        "server": {
            "host": "127.0.0.1",
            "port": 8088,
            "python_version": sys.version,
        },
        "environment": env_vars
    }

@app.get("/api/v1/companies/active")
async def test_company():
    """Return a test company for debugging"""
    logging.info("Companies/active endpoint called")
    return {
        "id": "test_company",
        "name": "Test Company",
        "description": "This is a test company for debugging",
        "logo_url": "https://via.placeholder.com/150x50?text=TestCompany",
        "brand_colors": ["#3B82F6", "#A855F7", "#EC4899"],
        "active": True,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8088
    logging.info(f"Starting debug API server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

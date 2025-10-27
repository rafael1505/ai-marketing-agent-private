#!/usr/bin/env python3
"""
Standard Port Configuration for AI Marketing Agent

This module provides standardized port configuration for the AI Marketing Agent application.
All components should import from this file to ensure consistency.
"""

# Standard ports that must be used across all application components
API_PORT = 8088  # API server must always use this port
FRONTEND_PORT = 3001  # Frontend NextJS must always use this port

# Additional port configuration
ALT_FRONTEND_PORT = 3002  # Alternative port for frontend (only for testing)

def get_api_url(protocol="http", host="127.0.0.1"):
    """Return the standard API URL"""
    return f"{protocol}://{host}:{API_PORT}"

def get_frontend_url(protocol="http", host="127.0.0.1"):
    """Return the standard frontend URL"""
    return f"{protocol}://{host}:{FRONTEND_PORT}"

def print_port_config():
    """Print the standard port configuration"""
    print(f"API Server: {get_api_url()}")
    print(f"Frontend: {get_frontend_url()}")

if __name__ == "__main__":
    print("AI Marketing Agent - Standard Port Configuration")
    print("=============================================")
    print_port_config()
    print("\nNOTE: These ports must be used consistently across all application components.")
    print("      If these ports are in use, they should be freed rather than changing the configuration.")

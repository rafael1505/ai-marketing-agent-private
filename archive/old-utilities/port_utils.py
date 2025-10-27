#!/usr/bin/env python3
"""
Port Utility for AI Marketing Agent

This script provides utilities to check, free, and manage the required ports
for the AI Marketing Agent application.
"""

import os
import sys
import time
import socket
import signal
import subprocess
import platform
import requests
from pathlib import Path

# Import standard port configuration
try:
    from port_config import API_PORT, FRONTEND_PORT
except ImportError:
    # Fallback if config not available
    API_PORT = 8088  
    FRONTEND_PORT = 3001

# ANSI colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_colored(text, color=None, bold=False):
    """Print text with ANSI color and optionally bold."""
    prefix = ''
    if color:
        prefix += color
    if bold:
        prefix += BOLD
    
    if prefix:
        print(f"{prefix}{text}{RESET}")
    else:
        print(text)

def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def check_api_health(port):
    """Check if API is running on the specified port."""
    try:
        import requests
        response = requests.get(f"http://127.0.0.1:{port}/api/v1/diagnostic/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def find_process_using_port(port):
    """Find the process ID using a specific port."""
    os_name = platform.system().lower()
    
    try:
        if os_name == 'windows':
            # Windows
            cmd = f'netstat -ano | findstr :{port}'
            output = subprocess.check_output(cmd, shell=True).decode()
            if output:
                for line in output.strip().split('\n'):
                    if f':{port}' in line:
                        parts = line.strip().split()
                        if len(parts) > 4:
                            return int(parts[4])
        elif os_name in ['linux', 'darwin']:
            # Linux/Mac
            if os.path.exists('/usr/bin/lsof') or os.path.exists('/usr/sbin/lsof'):
                cmd = f'lsof -i :{port} -t'
                output = subprocess.check_output(cmd, shell=True).decode()
                if output.strip():
                    return int(output.strip().split('\n')[0])
            else:
                # Alternative method if lsof is not available
                cmd = f"netstat -tunlp 2>/dev/null | grep :{port}"
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode()
                if output:
                    for line in output.strip().split('\n'):
                        if f':{port}' in line:
                            pid_part = line.split()[-1]
                            if '/' in pid_part:
                                return int(pid_part.split('/')[0])
    except:
        pass
    
    return None

def kill_process(pid):
    """Attempt to kill a process by PID."""
    try:
        # Try gentle termination first
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        
        # Check if process is still alive
        try:
            os.kill(pid, 0)  # Signal 0 is used to check if process exists
            # Process still alive, try harder
            os.kill(pid, signal.SIGKILL)
            time.sleep(1)
        except OSError:
            # Process already terminated
            pass
            
        return True
    except:
        return False

def free_port(port, prompt=True):
    """Free a port by finding and killing the process using it."""
    if not is_port_in_use(port):
        print_colored(f"Port {port} is not in use.", GREEN)
        return True
        
    pid = find_process_using_port(port)
    if not pid:
        print_colored(f"Could not identify process using port {port}.", YELLOW)
        return False
        
    print_colored(f"Process {pid} is using port {port}.", BLUE)
    
    if prompt:
        response = input(f"Do you want to terminate process {pid} to free port {port}? (y/n): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return False
    
    success = kill_process(pid)
    if success:
        print_colored(f"Successfully terminated process {pid} and freed port {port}.", GREEN)
        return True
    else:
        print_colored(f"Failed to terminate process {pid}.", RED)
        return False

def verify_ports():
    """Verify that the required ports are available or used by the correct services."""
    print_colored("Verifying required ports for AI Marketing Agent...", BLUE, bold=True)
    print()
    
    # Check API port
    print_colored(f"Checking API port {API_PORT}...", BLUE)
    if is_port_in_use(API_PORT):
        if check_api_health(API_PORT):
            print_colored(f"✓ API is running correctly on port {API_PORT}", GREEN)
        else:
            print_colored(f"✗ Port {API_PORT} is in use but not by our API server", RED)
            print(f"  Process: {find_process_using_port(API_PORT)}")
            print(f"  To free this port, run: python port_utils.py free-api")
    else:
        print_colored(f"✓ API port {API_PORT} is available", GREEN)
    
    # Check frontend port
    print_colored(f"\nChecking frontend port {FRONTEND_PORT}...", BLUE)
    if is_port_in_use(FRONTEND_PORT):
        print_colored(f"✗ Port {FRONTEND_PORT} is in use", YELLOW)
        print(f"  Process: {find_process_using_port(FRONTEND_PORT)}")
        print(f"  To free this port, run: python port_utils.py free-frontend")
    else:
        print_colored(f"✓ Frontend port {FRONTEND_PORT} is available", GREEN)
    
    print("\nFor further details, see PORT_CONFIGURATION.md")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print_colored("AI Marketing Agent - Port Utilities", BLUE, bold=True)
        print("Usage:")
        print("  python port_utils.py verify       - Verify port availability")
        print("  python port_utils.py free-api     - Free the API port")
        print("  python port_utils.py free-frontend - Free the frontend port")
        print("  python port_utils.py free-all     - Free all required ports")
        return
        
    command = sys.argv[1].lower()
    
    if command == 'verify':
        verify_ports()
    elif command == 'free-api':
        free_port(API_PORT)
    elif command == 'free-frontend':
        free_port(FRONTEND_PORT)
    elif command == 'free-all':
        print_colored("Freeing all required ports...", BLUE, bold=True)
        free_port(API_PORT)
        free_port(FRONTEND_PORT)
    else:
        print(f"Unknown command: {command}")
        
if __name__ == "__main__":
    main()

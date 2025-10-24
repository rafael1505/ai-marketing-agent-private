#!/usr/bin/env python3
"""
API Port Configuration Fix Tool

This script automatically detects and fixes API port configuration issues
in the AI Marketing Agent application.
"""

import os
import sys
import time
import signal
import socket
import subprocess
import platform
import requests
from pathlib import Path

# ANSI colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

CORRECT_PORT = 8088
INCORRECT_PORT = 8089
WORKSPACE_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))

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
        response = requests.get(f"http://127.0.0.1:{port}/api/v1/diagnostic/health", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def find_process_using_port(port):
    """Find the process ID using the specified port."""
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
            if output:
                lines = output.strip().split('\n')
                for line in lines:
                    if f":{port}" in line and "LISTENING" in line:
                        parts = line.split()
                        return parts[-1]  # Last column is PID
        except subprocess.CalledProcessError:
            pass
    else:  # Linux/Mac
        try:
            output = subprocess.check_output(f"lsof -t -i:{port}", shell=True).decode()
            if output:
                return output.strip()
        except subprocess.CalledProcessError:
            pass
    return None

def kill_process(pid):
    """Kill a process by its PID."""
    try:
        if platform.system() == "Windows":
            subprocess.run(f"taskkill /F /PID {pid}", shell=True, check=True)
        else:
            os.kill(int(pid), signal.SIGTERM)
        time.sleep(1)
        return True
    except (subprocess.SubprocessError, OSError):
        return False

def start_api_server(port=CORRECT_PORT):
    """Start the API server on the specified port."""
    os.chdir(WORKSPACE_ROOT)
    
    # Check if the main.py file exists
    if not (WORKSPACE_ROOT / "app" / "main.py").exists():
        print_colored("Error: Could not find app/main.py. Make sure you're in the project root.", RED, bold=True)
        return False
    
    # Start the API server as a background process
    log_file = WORKSPACE_ROOT / f"api_server_{port}.log"
    
    try:
        if platform.system() == "Windows":
            subprocess.Popen(
                f"start cmd /k \"cd {WORKSPACE_ROOT} && uvicorn app.main:app --host 127.0.0.1 --port {port} --reload\"", 
                shell=True
            )
        else:
            with open(log_file, "w") as log:
                subprocess.Popen(
                    ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port), "--reload"],
                    stdout=log, stderr=log,
                    start_new_session=True
                )
        
        # Wait for the server to start
        print("Waiting for API server to start...", end="", flush=True)
        for _ in range(10):
            time.sleep(1)
            print(".", end="", flush=True)
            if check_api_health(port):
                print("\n" + GREEN + "✓ API server started successfully on port " + str(port) + RESET)
                return True
        
        print("\n" + RED + "✗ Failed to start API server" + RESET)
        return False
    except Exception as e:
        print_colored(f"\nError starting API server: {e}", RED)
        return False

def check_config_files():
    """Check frontend config files for port references."""
    issues_found = False
    
    # Check Next.js config
    next_config = WORKSPACE_ROOT / "frontend" / "next.config.js"
    if next_config.exists():
        content = next_config.read_text()
        if f":{INCORRECT_PORT}" in content:
            print_colored(f"⚠️ Found incorrect port {INCORRECT_PORT} in next.config.js", YELLOW)
            issues_found = True
    
    # Check API service
    api_service = WORKSPACE_ROOT / "frontend" / "src" / "services" / "api.ts"
    if api_service.exists():
        content = api_service.read_text()
        if f":{INCORRECT_PORT}" in content:
            print_colored(f"⚠️ Found incorrect port {INCORRECT_PORT} in api.ts", YELLOW)
            issues_found = True
    
    return issues_found

def main():
    """Main function."""
    print_colored("===== API Port Configuration Fix Tool =====", BLUE, bold=True)
    print("Checking API server ports...\n")
    
    # Check if incorrect port is in use
    incorrect_port_used = False
    if is_port_in_use(INCORRECT_PORT):
        print_colored(f"⚠️ Detected service running on incorrect port {INCORRECT_PORT}!", YELLOW, bold=True)
        
        # Check if it's our API
        if check_api_health(INCORRECT_PORT):
            print_colored(f"API server is running on the wrong port ({INCORRECT_PORT})!", RED)
            incorrect_port_used = True
            
            # Attempt to fix
            print("Attempting to fix by restarting on correct port...")
            
            # Find and kill the process on wrong port
            pid = find_process_using_port(INCORRECT_PORT)
            if pid:
                print(f"Found process using port {INCORRECT_PORT}: PID {pid}")
                if kill_process(pid):
                    print_colored("Successfully stopped process on incorrect port", GREEN)
                else:
                    print_colored("Failed to stop process. Please close it manually.", RED)
                    return 1
    
    # Check if correct port is in use
    correct_port_in_use = is_port_in_use(CORRECT_PORT)
    api_running_correctly = False
    
    if correct_port_in_use:
        if check_api_health(CORRECT_PORT):
            print_colored(f"✓ API server is running correctly on port {CORRECT_PORT}", GREEN)
            api_running_correctly = True
        else:
            print_colored(f"⚠️ Port {CORRECT_PORT} is in use but not by our API server", YELLOW)
            
            # Ask to free up the port
            response = input("Would you like to try to free up this port? (y/n): ").lower()
            if response == 'y':
                pid = find_process_using_port(CORRECT_PORT)
                if pid:
                    print(f"Found process using port {CORRECT_PORT}: PID {pid}")
                    if kill_process(pid):
                        print_colored("Successfully freed up port", GREEN)
                        correct_port_in_use = False
                    else:
                        print_colored("Failed to free up port. Please close it manually.", RED)
                        return 1
    
    # Start API server if not running correctly
    if not api_running_correctly and not correct_port_in_use:
        response = input("Would you like to start the API server on the correct port? (y/n): ").lower()
        if response == 'y':
            if start_api_server(CORRECT_PORT):
                api_running_correctly = True
    
    # Check configuration files
    print("\nChecking configuration files...")
    if check_config_files():
        print_colored("\nWarning: Found incorrect port references in configuration files.", YELLOW)
        print("Please review and update the following files:")
        print("  - frontend/next.config.js")
        print("  - frontend/src/services/api.ts")
    else:
        print_colored("✓ No incorrect port references found in configuration files", GREEN)
    
    # Summary
    print_colored("\n===== Summary =====", BLUE, bold=True)
    if api_running_correctly:
        print_colored("✓ API server is running correctly on port " + str(CORRECT_PORT), GREEN)
        print_colored("✓ You can now use the application normally", GREEN)
    else:
        print_colored("✗ API server is not running on the correct port", RED)
        print_colored("Please run the API server manually with:", YELLOW)
        print(f"  cd {WORKSPACE_ROOT}")
        print(f"  uvicorn app.main:app --host 127.0.0.1 --port {CORRECT_PORT} --reload")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Clean startup script for API server.
This script bypasses any potential issues in the app/main.py file.
"""

import os
import subprocess
import time
import sys

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(78, "*"))
    print("=" * 80 + "\n")

def main():
    print_header("API SERVER STARTUP SCRIPT")
    
    # 1. Check if port 8088 is already in use
    print("Checking if port 8088 is in use...")
    port_check = subprocess.run(
        ["ss", "-tulnp", "| grep 8088"],
        shell=True,
        capture_output=True,
        text=True
    )
    
    if port_check.stdout.strip():
        print("Port 8088 is already in use. Stopping existing process...")
        subprocess.run(["pkill", "-f", "uvicorn app.main:app"], capture_output=True)
        time.sleep(2)
    else:
        print("Port 8088 is free.")
    
    # 2. Create a minimal app/main.py.new file that we can use
    print("Creating simplified API server file...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if the bug in app/main.py has been fixed
    with open(os.path.join(current_dir, "app/main.py"), "r") as f:
        content = f.read()
        
    # Check if there are too many startup event handlers
    startup_count = content.count("@app.on_event(\"startup\")")
    if startup_count > 1:
        print(f"Found {startup_count} startup event handlers, should only have 1")
        print("Creating backup and fixing app/main.py...")
        
        # Create backup
        backup_path = os.path.join(current_dir, "app/main.py.bak2")
        with open(backup_path, "w") as f:
            f.write(content)
        print(f"Created backup at {backup_path}")
        
        # Remove the second startup handler
        lines = content.split("\n")
        found_first = False
        fixed_lines = []
        
        for line in lines:
            if "@app.on_event(\"startup\")" in line:
                if not found_first:
                    found_first = True
                    fixed_lines.append(line)
                else:
                    # Skip this line and create a normal function instead
                    fixed_lines.append("async def init_test_data():")
            else:
                fixed_lines.append(line)
        
        # Write the fixed file
        with open(os.path.join(current_dir, "app/main.py"), "w") as f:
            f.write("\n".join(fixed_lines))
        print("Fixed app/main.py")
    else:
        print("No duplicate startup handlers found")
    
    # 3. Start the API server
    print_header("STARTING API SERVER")
    print("Running: python -m uvicorn app.main:app --host 127.0.0.1 --port 8088")
    
    # Start the server
    server_process = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8088"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit to see if it starts successfully
    time.sleep(3)
    
    # Check if the process is still running
    if server_process.poll() is None:
        print("API server started successfully!")
        print("API is now available at http://127.0.0.1:8088")
        
        # Continue running and show output
        try:
            while True:
                line = server_process.stdout.readline()
                if not line:
                    break
                print(line.strip())
        except KeyboardInterrupt:
            print("Stopping API server...")
            server_process.terminate()
    else:
        print("Failed to start API server!")
        stdout, stderr = server_process.communicate()
        print("STDOUT:")
        print(stdout)
        print("STDERR:")
        print(stderr)
        
        # Try with --reload flag which has better error reporting
        print("\nTrying with --reload flag for better error reporting...")
        subprocess.run(
            ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8088", "--reload"],
            text=True
        )

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import requests
import time
import sys
import os
from datetime import datetime

# Generate a unique log file name in /tmp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = f"/tmp/test_direct_login_output_{timestamp}.txt"

def log_and_print(message):
    """Prints to stdout and writes to the log file."""
    print(message, file=sys.stdout, flush=True)
    try:
        with open(log_file_path, "a") as f:
            f.write(message + "\\n")
    except Exception as e:
        print(f"Error writing to log file {log_file_path}: {e}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    log_and_print("Script started.")
    
    url = "http://127.0.0.1:8088/api/v1/auth/login"
    data = {
        "username": "test@example.com",
        "password": "password"
    }
    
    log_and_print(f"Sending POST request to {url} with data: {data}")
    
    try:
        response = requests.post(url, data=data, timeout=20)
        log_and_print(f"Response status code: {response.status_code}")
        log_and_print(f"Response headers: {response.headers}")
        log_and_print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as e:
        log_and_print(f"Request failed: {e}")
    except Exception as e:
        log_and_print(f"An unexpected error occurred: {e}")
    finally:
        log_and_print("Script finished.")
        # Attempt to read the log file and print its content to stderr for verification
        try:
            with open(log_file_path, "r") as f:
                log_content = f.read()
                print(f"--- Content of {log_file_path} ---", file=sys.stderr, flush=True)
                print(log_content, file=sys.stderr, flush=True)
                print(f"--- End of {log_file_path} ---", file=sys.stderr, flush=True)
        except Exception as e_read:
            print(f"Error reading back log file {log_file_path}: {e_read}", file=sys.stderr, flush=True)

    sys.exit(0)

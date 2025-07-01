#!/bin/bash

# Company persistence fix verification script
# This script will:
# 1. Check if API is running
# 2. Run the persistence test
# 3. Provide a summary of findings

echo -e "\n\033[1;36m===== COMPANY PERSISTENCE FIX VERIFICATION =====\033[0m"

# Check if API is running
echo -e "\n\033[1;34m[1] Checking API status...\033[0m"
if nc -z localhost 8088; then
  echo -e "\033[1;32m✓ API is running on port 8088\033[0m"
else 
  echo -e "\033[1;31m✗ API is NOT running on port 8088\033[0m"
  echo -e "\033[1;33m[*] Would you like to start the API? (y/n)\033[0m"
  read -r answer
  if [[ "$answer" == "y" ]]; then
    echo "Starting API in a separate terminal..."
    gnome-terminal -- bash -c "cd \"$(pwd)\" && uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload; bash" || \
    xterm -e "cd \"$(pwd)\" && uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload; bash" || \
    echo "Could not open a new terminal. Please start the API manually."
    
    # Wait for API to start
    echo "Waiting for API to start..."
    for i in {1..10}; do
      if nc -z localhost 8088; then
        echo -e "\033[1;32m✓ API started successfully\033[0m"
        break
      fi
      echo -n "."
      sleep 1
      if [ $i -eq 10 ]; then
        echo -e "\n\033[1;31m✗ API did not start in time. Please check for errors.\033[0m"
        exit 1
      fi
    done
  else
    echo "Please start the API manually before continuing."
    exit 1
  fi
fi

# Run the persistence test
echo -e "\n\033[1;34m[2] Running persistence test...\033[0m"
python company_persistence_test.py

# Check test result
TEST_RESULT=$?
if [ $TEST_RESULT -eq 0 ]; then
  echo -e "\n\033[1;32m===== COMPANY PERSISTENCE FIX VERIFICATION SUMMARY =====\033[0m"
  echo -e "\033[1;32m✓ The fix has been successfully applied!\033[0m"
  echo -e "\033[1;32m✓ Company data including brand colors is now persisting correctly.\033[0m"
else
  echo -e "\n\033[1;31m===== COMPANY PERSISTENCE FIX VERIFICATION SUMMARY =====\033[0m"
  echo -e "\033[1;31m✗ The fix was not successful.\033[0m"
  echo -e "\033[1;31m✗ Company data is still not persisting correctly.\033[0m"
  echo -e "\033[1;33m[*] Please check the logs for more details.\033[0m"
fi

echo -e "\n\033[1;36m==================================================\033[0m\n"

exit $TEST_RESULT

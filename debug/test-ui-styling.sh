#!/bin/bash

# UI Testing Script
# This script automates the UI testing process for the AI Marketing Agent application

# Color codes for terminal output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI Marketing Agent UI Testing Script ===${NC}"
echo -e "Testing Date: $(date)"
echo -e "---------------------------------------------"

# Check if frontend is running
check_frontend() {
  echo -e "\n${YELLOW}Checking if frontend server is running...${NC}"
  if curl -s http://localhost:3001 >/dev/null; then
    echo -e "${GREEN}✓ Frontend server is running on port 3001${NC}"
    FRONTEND_PORT=3001
    return 0
  elif curl -s http://localhost:3002 >/dev/null; then
    echo -e "${GREEN}✓ Frontend server is running on port 3002${NC}"
    FRONTEND_PORT=3002
    return 0
  else
    echo -e "${RED}✗ Frontend server is not running${NC}"
    echo -e "${YELLOW}Starting frontend server...${NC}"
    
    # Kill any processes on port 3001
    lsof -i :3001 >/dev/null && kill -9 $(lsof -t -i:3001) >/dev/null 2>&1
    
    # Start frontend in background
    cd frontend && npm run dev -- --port 3001 > /dev/null 2>&1 &
    
    # Wait for server to start
    sleep 5
    
    if curl -s http://localhost:3001 >/dev/null; then
      echo -e "${GREEN}✓ Frontend server started successfully${NC}"
      FRONTEND_PORT=3001
      return 0
    else
      echo -e "${RED}✗ Failed to start frontend server${NC}"
      return 1
    fi
  fi
}

# Test specific page styles
test_page_styles() {
  local page=$1
  echo -e "\n${YELLOW}Testing page: $page${NC}"
  
  # Use curl to fetch the page HTML
  local html=$(curl -s http://localhost:$FRONTEND_PORT$page)
  
  # Check for key style markers
  if [[ $html == *"directGradientText"* ]]; then
    echo -e "${GREEN}✓ directGradientText class found${NC}"
  else
    echo -e "${RED}✗ directGradientText class not found${NC}"
  fi
  
  if [[ $html == *"directHoverCard"* ]]; then
    echo -e "${GREEN}✓ directHoverCard class found${NC}"
  else
    echo -e "${RED}✗ directHoverCard class not found${NC}"
  fi
  
  if [[ $html == *"directBtnScale"* ]]; then
    echo -e "${GREEN}✓ directBtnScale class found${NC}"
  else
    echo -e "${RED}✗ directBtnScale class not found${NC}"
  fi
  
  if [[ $html == *"directFadeIn"* ]]; then
    echo -e "${GREEN}✓ directFadeIn class found${NC}"
  else
    echo -e "${RED}✗ directFadeIn class not found${NC}"
  fi
  
  echo -e "${YELLOW}Open in browser for visual confirmation:${NC}"
  echo -e "http://localhost:$FRONTEND_PORT$page"
}

# Test CSS file existence and content
check_css_files() {
  echo -e "\n${YELLOW}Checking CSS files...${NC}"
  
  if [ -f "frontend/src/app/direct-styles.css" ]; then
    echo -e "${GREEN}✓ direct-styles.css exists${NC}"
  else
    echo -e "${RED}✗ direct-styles.css not found${NC}"
  fi
  
  if [ -f "frontend/src/app/custom-styles.css" ]; then
    echo -e "${GREEN}✓ custom-styles.css exists${NC}"
  else
    echo -e "${RED}✗ custom-styles.css not found${NC}"
  fi
  
  if [ -f "frontend/src/app/globals.css" ]; then
    echo -e "${GREEN}✓ globals.css exists${NC}"
  else
    echo -e "${RED}✗ globals.css not found${NC}"
  fi
}

# Main execution
main() {
  # Check if frontend is running
  check_frontend
  if [ $? -ne 0 ]; then
    echo -e "${RED}Exiting due to frontend server issues${NC}"
    exit 1
  fi
  
  # Test pages
  echo -e "\n${YELLOW}Testing pages...${NC}"
  test_page_styles "/fixed-style"
  test_page_styles "/en/login"
  
  # Check CSS files
  check_css_files
  
  echo -e "\n${GREEN}=== Testing Complete ===${NC}"
  echo -e "For complete testing, follow the steps in ui-test-results.md"
}

# Run main function
main

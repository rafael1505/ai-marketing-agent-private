#!/bin/bash
# This script checks the status of MongoDB in the current environment

echo "Checking MongoDB status..."

# Try connecting to MongoDB
echo "Attempting to connect to MongoDB..."
if ! command -v mongosh &> /dev/null; then
  echo "mongosh not found. Checking for older mongo client..."
  
  if ! command -v mongo &> /dev/null; then
    echo "MongoDB client not installed."
    echo "MongoDB status: NOT INSTALLED"
    exit 1
  fi
  
  MONGO_CMD="mongo"
else
  MONGO_CMD="mongosh"
fi

# Try to connect to MongoDB
if $MONGO_CMD --eval "db.adminCommand('ping')" --quiet; then
  echo "MongoDB is running!"
  echo "MongoDB status: RUNNING"
  exit 0
else
  echo "MongoDB is not running or not accessible."
  echo "MongoDB status: NOT RUNNING"
  exit 1
fi

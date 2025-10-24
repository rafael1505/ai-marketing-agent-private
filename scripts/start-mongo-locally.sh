#!/bin/bash

# Update /etc/hosts to add mongo entry
echo "127.0.0.1 mongo" | sudo tee -a /etc/hosts

# Check if mongo is running locally
if ! nc -z localhost 27017 &>/dev/null; then
  # If MongoDB is not running, start a MongoDB container
  docker run -d --name mongodb -p 27017:27017 mongo:4.4
  echo "Started MongoDB container"
else
  echo "MongoDB is already running on port 27017"
fi

# Start the API
cd "$(dirname "$0")"
echo "Starting API with mock database..."
uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload

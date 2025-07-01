#!/bin/bash

# This script helps set up a local MongoDB for development without Docker
# It checks for MongoDB installation and guides you through setup steps

echo "=== AI Marketing Agent Database Setup ==="
echo

# Function to check if MongoDB is installed
check_mongodb() {
  if command -v mongod &> /dev/null; then
    echo "MongoDB is installed."
    return 0
  else
    echo "MongoDB is not installed."
    return 1
  fi
}

# Function to check if MongoDB is running
check_mongodb_running() {
  if pgrep mongod &> /dev/null; then
    echo "MongoDB is running."
    return 0
  else
    echo "MongoDB is not running."
    return 1
  fi
}

# Check MongoDB installation
if check_mongodb; then
  echo "✅ MongoDB found on system."
else
  echo "❌ MongoDB not found. You need to install MongoDB to continue."
  echo
  echo "To install MongoDB on Ubuntu:"
  echo "1. Add MongoDB repository:"
  echo "   sudo apt update"
  echo "   sudo apt install -y gnupg curl"
  echo "   curl -fsSL https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -"
  echo "   echo \"deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/4.4 multiverse\" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list"
  echo "2. Install MongoDB:"
  echo "   sudo apt update"
  echo "   sudo apt install -y mongodb-org"
  echo "3. Start MongoDB:"
  echo "   sudo systemctl start mongod"
  echo "4. Enable MongoDB at startup:"
  echo "   sudo systemctl enable mongod"
  echo
  echo "After installation, run this script again."
  exit 1
fi

# Check if MongoDB is running
if check_mongodb_running; then
  echo "✅ MongoDB is running."
else
  echo "❌ MongoDB is not running."
  echo "Starting MongoDB..."
  sudo systemctl start mongod
  
  # Check if we managed to start MongoDB
  if check_mongodb_running; then
    echo "✅ Successfully started MongoDB."
  else
    echo "❌ Failed to start MongoDB. Please start it manually with:"
    echo "   sudo systemctl start mongod"
    exit 1
  fi
fi

# Create the database and collections
echo "Setting up AI Marketing Agent database..."
mongosh --eval '
  db = db.getSiblingDB("ai_marketing_agent");
  
  // Create collections if they don't exist
  db.createCollection("users");
  db.createCollection("companies");
  db.createCollection("materials");
  
  // Create a test user if none exists
  if (db.users.countDocuments() === 0) {
    db.users.insertOne({
      name: "Test User",
      email: "test@example.com",
      password: "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", // "password"
      is_active: true,
      is_superuser: true,
      created_at: new Date(),
      updated_at: new Date()
    });
    print("Created test user: test@example.com / password");
  }
  
  print("Database setup complete!");
'

# Update the application configuration
echo
echo "Updating application configuration..."
CONFIG_FILE="app/core/config.py"

# Make a backup of the config file
cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"

# Update the MONGODB_URL in the config file
sed -i 's/MONGODB_URL: str = "mongodb:\/\/localhost:27017"/MONGODB_URL: str = "mongodb:\/\/localhost:27017"  # Updated by setup script/' "$CONFIG_FILE"

echo "✅ Setup complete!"
echo
echo "Your AI Marketing Agent is now configured to use a local MongoDB database."
echo "To start the application, run:"
echo "   ./start-dev.sh"
echo
echo "Test user credentials:"
echo "   Email: test@example.com"
echo "   Password: password"

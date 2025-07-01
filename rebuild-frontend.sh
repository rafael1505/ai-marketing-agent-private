#!/bin/bash

# Script to properly rebuild the frontend with all styles
echo "🔄 Rebuilding frontend with updated styles..."

cd "$(dirname "$0")/frontend"

# Remove any .next cache
echo "🗑️ Clearing build cache..."
rm -rf .next

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
fi

# Build the application
echo "🏗️ Building application..."
npm run build

# Start the development server
echo "🚀 Starting development server on port 3001..."
npm run dev -- --port 3001 --host 127.0.0.1

echo "✅ Done!"

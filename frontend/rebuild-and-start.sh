#!/bin/bash

# Clear all caches and modules
echo "Clearing caches and node_modules..."
rm -rf .next node_modules package-lock.json

# Reinstall dependencies
echo "Installing dependencies..."
npm cache clean --force
npm install

echo "Starting development server..."
npm run dev

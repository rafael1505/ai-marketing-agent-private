#!/bin/bash

# AI Marketing Agent - Stop Script
# This script stops both the API server and frontend development server

echo "🛑 Stopping AI Marketing Agent services..."
echo "=========================================="

# Function to stop a service by process pattern
stop_service() {
    local service_name="$1"
    local process_pattern="$2"
    local port="$3"
    
    echo "🔄 Stopping $service_name..."
    
    # Find and kill processes matching the pattern
    local pids=$(pgrep -f "$process_pattern")
    
    if [ -n "$pids" ]; then
        echo "   Found PIDs: $pids"
        kill $pids 2>/dev/null
        
        # Wait a moment and check if they're really stopped
        sleep 2
        
        # Force kill if still running
        local remaining=$(pgrep -f "$process_pattern")
        if [ -n "$remaining" ]; then
            echo "   Force killing remaining processes: $remaining"
            kill -9 $remaining 2>/dev/null
        fi
        
        echo "   ✅ $service_name stopped"
    else
        echo "   ℹ️  $service_name was not running"
    fi
    
    # Check port status if provided
    if [ -n "$port" ]; then
        if ss -tulpn | grep -q ":$port "; then
            echo "   ⚠️  Port $port may still be in use by another process"
        else
            echo "   ✅ Port $port is now free"
        fi
    fi
}

# Stop API server
stop_service "API Server" "uvicorn.*8088" "8088"

echo ""

# Stop Frontend server
stop_service "Frontend Server" "next-server" "3000"

echo ""

# Additional cleanup for any Next.js processes
echo "🧹 Additional cleanup..."
pkill -f "next" 2>/dev/null && echo "   ✅ Cleaned up additional Next.js processes" || echo "   ℹ️  No additional Next.js processes found"

# Check final status
echo ""
echo "📊 Final Status Check:"
echo "====================="

# Check API port
if ss -tulpn | grep -q ":8088 "; then
    echo "⚠️  Port 8088 still in use"
else
    echo "✅ Port 8088 is free"
fi

# Check frontend ports
if ss -tulpn | grep -q ":3000 "; then
    echo "⚠️  Port 3000 still in use"
else
    echo "✅ Port 3000 is free"
fi

if ss -tulpn | grep -q ":3001 "; then
    echo "⚠️  Port 3001 still in use"
else
    echo "✅ Port 3001 is free"
fi

echo ""
echo "✨ Service shutdown complete!"
echo ""
echo "💡 To start services again, run: ./start_app.sh"

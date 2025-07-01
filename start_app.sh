#!/bin/bash

# AI Marketing Agent - Startup Script
# This script starts both the API server and frontend development server

echo "🚀 Starting AI Marketing Agent..."
echo "================================="

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Expected to find: app/main.py"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if ss -tulpn | grep -q ":$1 "; then
        echo "⚠️  Port $1 is already in use"
        return 0
    else
        return 1
    fi
}

# Function to start API server
start_api() {
    echo "📡 Starting API Server (Port 8088)..."
    
    if check_port 8088; then
        echo "   API may already be running. Checking health..."
        if curl -s http://127.0.0.1:8088/api/v1/diagnostic/health > /dev/null 2>&1; then
            echo "   ✅ API server is already running and healthy"
            return 0
        else
            echo "   🔄 Port occupied but API not responding. You may need to kill existing process."
            echo "   Run: pkill -f 'uvicorn.*8088' to stop existing server"
            return 1
        fi
    fi
    
    # Start API server in background
    uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload > api_server.log 2>&1 &
    API_PID=$!
    
    # Wait for API to start
    echo "   Waiting for API server to start..."
    for i in {1..30}; do
        if curl -s http://127.0.0.1:8088/api/v1/diagnostic/health > /dev/null 2>&1; then
            echo "   ✅ API server started successfully (PID: $API_PID)"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    echo ""
    echo "   ❌ API server failed to start within 30 seconds"
    echo "   Check api_server.log for details"
    return 1
}

# Function to start frontend
start_frontend() {
    echo "🌐 Starting Frontend Development Server..."
    
    if [ ! -d "frontend" ]; then
        echo "   ❌ Frontend directory not found"
        return 1
    fi
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "   📦 Installing frontend dependencies..."
        npm install
    fi
    
    # Check available ports
    if check_port 3000; then
        echo "   Port 3000 in use, trying 3001..."
        if check_port 3001; then
            echo "   ⚠️  Both ports 3000 and 3001 are in use"
            echo "   Frontend may already be running or ports are occupied"
        fi
    fi
    
    # Start frontend in background
    echo "   Starting Next.js development server..."
    npm run dev > ../frontend_server.log 2>&1 &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    echo "   Waiting for frontend to start..."
    for i in {1..60}; do
        if curl -s -I http://localhost:3000 > /dev/null 2>&1; then
            echo "   ✅ Frontend started on http://localhost:3000 (PID: $FRONTEND_PID)"
            cd ..
            return 0
        elif curl -s -I http://localhost:3001 > /dev/null 2>&1; then
            echo "   ✅ Frontend started on http://localhost:3001 (PID: $FRONTEND_PID)"
            cd ..
            return 0
        fi
        sleep 1
        if [ $((i % 10)) -eq 0 ]; then
            echo -n " ${i}s"
        else
            echo -n "."
        fi
    done
    
    echo ""
    echo "   ❌ Frontend failed to start within 60 seconds"
    echo "   Check frontend_server.log for details"
    cd ..
    return 1
}

# Function to test the system
test_system() {
    echo "🧪 Testing System Integration..."
    
    # Test API
    if curl -s http://127.0.0.1:8088/api/v1/ai-providers -H "Authorization: Bearer mock_test_token" > /dev/null; then
        echo "   ✅ API endpoints responding"
    else
        echo "   ❌ API endpoints not responding"
        return 1
    fi
    
    # Test frontend
    if curl -s -I http://localhost:3000 > /dev/null 2>&1; then
        echo "   ✅ Frontend accessible at http://localhost:3000"
        FRONTEND_URL="http://localhost:3000"
    elif curl -s -I http://localhost:3001 > /dev/null 2>&1; then
        echo "   ✅ Frontend accessible at http://localhost:3001"
        FRONTEND_URL="http://localhost:3001"
    else
        echo "   ❌ Frontend not accessible"
        return 1
    fi
    
    return 0
}

# Function to show running services
show_status() {
    echo ""
    echo "📊 Service Status:"
    echo "=================="
    
    # Check API
    if curl -s http://127.0.0.1:8088/api/v1/diagnostic/health > /dev/null 2>&1; then
        echo "🟢 API Server: Running on http://127.0.0.1:8088"
        echo "   - Health endpoint: http://127.0.0.1:8088/api/v1/diagnostic/health"
        echo "   - AI Providers: http://127.0.0.1:8088/api/v1/ai-providers"
    else
        echo "🔴 API Server: Not running"
    fi
    
    # Check frontend
    if curl -s -I http://localhost:3000 > /dev/null 2>&1; then
        echo "🟢 Frontend: Running on http://localhost:3000"
        echo "   - Settings page: http://localhost:3000/en/settings"
    elif curl -s -I http://localhost:3001 > /dev/null 2>&1; then
        echo "🟢 Frontend: Running on http://localhost:3001"
        echo "   - Settings page: http://localhost:3001/en/settings"
    else
        echo "🔴 Frontend: Not running"
    fi
    
    echo ""
    echo "📝 Log files:"
    echo "   - API: api_server.log"
    echo "   - Frontend: frontend_server.log"
}

# Main execution
main() {
    # Start API server
    if ! start_api; then
        echo "❌ Failed to start API server"
        exit 1
    fi
    
    echo ""
    
    # Start frontend
    if ! start_frontend; then
        echo "❌ Failed to start frontend"
        exit 1
    fi
    
    echo ""
    
    # Test system
    if test_system; then
        echo "   ✅ System integration test passed"
    else
        echo "   ⚠️  System integration test failed"
    fi
    
    # Show status
    show_status
    
    echo ""
    echo "🎉 AI Marketing Agent is now running!"
    echo ""
    echo "🔗 Quick Links:"
    echo "   - Settings (AI Providers): ${FRONTEND_URL:-http://localhost:3000}/en/settings"
    echo "   - API Documentation: http://127.0.0.1:8088/docs"
    echo ""
    echo "💡 To stop the services:"
    echo "   - API: pkill -f 'uvicorn.*8088'"
    echo "   - Frontend: pkill -f 'next-server'"
    echo "   - Both: ./stop_servers.sh (if you create this script)"
    echo ""
    echo "📊 Monitor logs with:"
    echo "   - API: tail -f api_server.log"
    echo "   - Frontend: tail -f frontend_server.log"
}

# Handle Ctrl+C
trap 'echo -e "\n⚠️  Startup interrupted by user"; exit 1' INT

# Run main function
main

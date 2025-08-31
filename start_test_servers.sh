#!/bin/bash

echo "🚀 Starting Amazon Sales Agent Test Environment"
echo "=============================================="

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
pkill -f "next.*dev" 2>/dev/null || true

sleep 2

# Start Backend Server
echo "🔧 Starting Backend Server (FastAPI)..."
cd backend
if check_port 8000; then
    uv run python -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0 &
    BACKEND_PID=$!
    echo "✅ Backend server starting on http://localhost:8000"
    echo "   PID: $BACKEND_PID"
else
    echo "❌ Cannot start backend - port 8000 is busy"
    exit 1
fi

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend
echo "🧪 Testing backend API..."
if curl -s -X GET "http://localhost:8000/api/v1/test/status" > /dev/null; then
    echo "✅ Backend API is responding"
else
    echo "❌ Backend API is not responding"
fi

# Start Frontend Server
echo "🎨 Starting Frontend Server (Next.js)..."
cd ../frontend
if check_port 3000; then
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ Frontend server starting on http://localhost:3000"
    echo "   PID: $FRONTEND_PID"
else
    echo "❌ Cannot start frontend - port 3000 is busy"
fi

echo ""
echo "🎉 Test Environment Ready!"
echo "=========================="
echo "📱 Frontend Test Page: http://localhost:3000/test"
echo "🔧 Backend API Docs: http://localhost:8000/docs"
echo "🧪 Test Status: http://localhost:8000/api/v1/test/status"
echo ""
echo "📋 Instructions:"
echo "1. Open http://localhost:3000/test in your browser"
echo "2. Upload the CSV file: backend/US_AMAZON_cerebro_B00O64QJOC_2025-08-21.csv"
echo "3. Click 'Test Keyword Agent' to run the analysis"
echo "4. Review results and download CSV"
echo ""
echo "🛑 To stop servers: Ctrl+C or run 'pkill -f uvicorn && pkill -f next'"
echo ""

# Keep script running
wait 
#!/bin/bash

echo "🚀 Starting Amazon Sales Agent Full Stack"
echo "========================================"

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: This script must be run from the project root directory"
    echo "   Make sure you have both 'backend' and 'frontend' directories"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    jobs -p | xargs -r kill
    exit 0
}

# Trap Ctrl+C to cleanup
trap cleanup SIGINT

echo "📦 Installing dependencies..."

# Install backend dependencies
echo "🔧 Backend setup..."
cd backend
if command -v uv &> /dev/null; then
    echo "✅ Using uv for backend dependencies"
    uv sync
else
    echo "❌ uv not found. Please install uv: https://docs.astral.sh/uv/"
    exit 1
fi
cd ..

# Install frontend dependencies
echo "🎨 Frontend setup..."
cd frontend
if command -v npm &> /dev/null; then
    echo "✅ Installing frontend dependencies with npm"
    npm install
elif command -v yarn &> /dev/null; then
    echo "✅ Installing frontend dependencies with yarn"
    yarn install
else
    echo "❌ Neither npm nor yarn found. Please install Node.js"
    exit 1
fi
cd ..

echo ""
echo "🌟 Starting services..."
echo "📍 Backend will be available at: http://localhost:8000"
echo "📍 Frontend will be available at: http://localhost:3000"
echo "📍 Test page will be at: http://localhost:3000/test-pipeline"
echo ""

# Start backend
echo "🔧 Starting backend server..."
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
if command -v npm &> /dev/null; then
    npm run dev &
else
    yarn dev &
fi
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both services started!"
echo ""
echo "🔗 Quick Links:"
echo "   • Backend API: http://localhost:8000/docs"
echo "   • Frontend Dashboard: http://localhost:3000/dashboard"
echo "   • Pipeline Test Page: http://localhost:3000/test-pipeline"
echo ""
echo "💡 Tips:"
echo "   • Use the test page to verify your AI pipeline"
echo "   • Check backend logs for debugging"
echo "   • Press Ctrl+C to stop both services"
echo ""

# Wait for both processes
wait 
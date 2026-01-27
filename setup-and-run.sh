#!/bin/bash

echo "========================================"
echo "LLM Security MVP - Setup & Run"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY not set${NC}"
    echo "   Running in DEMO MODE with mock data"
    echo "   To use real AI testing, set: export OPENAI_API_KEY='your-key'"
    echo ""
else
    echo -e "${GREEN}✓ OPENAI_API_KEY found${NC}"
    echo "   Running in FULL MODE with real AI testing"
    echo ""
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install backend dependencies${NC}"
    exit 1
fi
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    else
        echo -e "${RED}✗ Failed to install frontend dependencies${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi
cd ..

echo ""
echo "========================================"
echo "🚀 Starting Application"
echo "========================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Start backend in background
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend in background
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait

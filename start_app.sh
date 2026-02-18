#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID
    exit
}

trap cleanup SIGINT

echo "Starting Backend..."
uvicorn src.backend.app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "Servers are running."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173" # Assuming Vite default
echo "Press Ctrl+C to stop."

wait

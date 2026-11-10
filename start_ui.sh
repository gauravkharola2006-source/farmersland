#!/bin/bash

echo "Starting Smart Farming System UI..."
echo ""
echo "Make sure the C backend is compiled first!"
echo ""

# Check if executable exists
if [ ! -f "./smart_farming_system" ]; then
    echo "Error: smart_farming_system not found!"
    echo "Please compile the project first using: make"
    exit 1
fi

# Start the Python server
echo "Starting API server on port 8000..."
echo "Open ui/index.html in your browser after the server starts"
echo "Press Ctrl+C to stop the server"
echo ""
python3 server.py



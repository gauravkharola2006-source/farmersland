@echo off
echo Starting Smart Farming System UI...
echo.
echo Make sure the C backend is compiled first!
echo.

REM Check if executable exists
if not exist "smart_farming_system.exe" (
    echo Error: smart_farming_system.exe not found!
    echo Please compile the project first using: make
    pause
    exit /b 1
)

REM Start the Python server
echo Starting API server on port 8000...
echo Open ui/index.html in your browser after the server starts
echo Press Ctrl+C to stop the server
echo.
python server.py







#!/bin/bash
echo "===================================================="
echo "NGO Attendance Portal - Starting Server"
echo "===================================================="

if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment 'venv' not found."
    echo "Please run ./setup_unix.sh first to install dependencies."
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "===================================================="
echo "  Server is starting!"
echo ""
echo "  - To access on this laptop: http://localhost:8000"
echo ""
echo "  - To access on a phone (same WiFi):"
echo "    Find your IP address by running: ipconfig getifaddr en0"
echo "    or check local network IPs. Then open http://[your-ip]:8000"
echo ""
echo "  - Press Ctrl+C in this window to stop the server."
echo "===================================================="
echo ""

python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

#!/bin/bash
echo "===================================================="
echo "NGO Attendance Portal - macOS/Linux Setup"
echo "===================================================="

# Check python3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    echo "Please install Python 3.8+ using Homebrew or from python.org"
    exit 1
fi

echo "Creating virtual environment (venv)..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment."
    exit 1
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r backend/requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Dependency installation failed."
    exit 1
fi

chmod +x start_unix.sh

echo ""
echo "===================================================="
echo "Setup completed successfully!"
echo "To start the application, run: ./start_unix.sh"
echo "===================================================="

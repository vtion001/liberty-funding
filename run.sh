#!/bin/bash
echo "Liberty Funding - Bounce Rate Update"
echo "======================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found. Please install Python 3.9+"
    exit 1
fi

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -q -r requirements.txt

# Run
python3 scripts/run.py

#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install or upgrade dependencies
pip install -r requirements.txt

echo "Virtual environment activated and dependencies installed."
echo "Run 'deactivate' to exit the virtual environment." 
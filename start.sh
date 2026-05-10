#!/bin/bash

# AluuGPT Startup Script

# 1. Ensure we are in the project directory
cd "$(dirname "$0")"

# 2. Check for virtual environment
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment 'venv' not found."
    echo "Please create it using: python -m venv venv"
    exit 1
fi

# 3. Ensure required directories exist
echo "Initializing directories..."
mkdir -p data
mkdir -p static/animations

# 4. Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating one from .env.example..."
    cp .env.example .env
    echo "Please edit the .env file with your API keys before proceeding."
fi

# 5. Run the server
echo "Starting AluuGPT Platform on http://localhost:8000..."
./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload

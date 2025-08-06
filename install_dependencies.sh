#!/bin/bash

# Agent Zero Dependency Installation Script
# This script installs all required Python dependencies

echo "Installing Agent Zero dependencies..."

# Upgrade pip first
python3 -m pip install --upgrade pip setuptools wheel

# Install all dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt --break-system-packages

# Install additional dependencies discovered during troubleshooting
echo "Installing additional dependencies..."
pip install \
    cryptography \
    nest-asyncio \
    python-crontab \
    --break-system-packages

echo "✅ All dependencies installed successfully!"
echo "You can now run: python3 run_ui.py"
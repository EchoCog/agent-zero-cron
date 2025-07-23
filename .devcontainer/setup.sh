#!/bin/bash

# Agent Zero Development Environment Setup Script
# This script helps set up the development environment after container creation

echo "🚀 Setting up Agent Zero development environment..."

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp example.env .env
    echo "✅ Created .env file. Please edit it with your API keys."
fi

# Install playwright browsers if not already installed
echo "🎭 Installing Playwright browsers..."
playwright install chromium --with-deps || echo "⚠️  Playwright install failed, but continuing..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "🐳 Docker is available in the devcontainer"
else
    echo "⚠️  Docker not found - some features may not work"
fi

# Create logs and memory directories if they don't exist
mkdir -p logs memory tmp

echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run 'python run_ui.py' to start the web interface"
echo "3. Run 'python run_cli.py' to start the CLI interface"
echo ""
echo "Web UI will be available at: http://localhost:50001"
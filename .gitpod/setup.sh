#!/bin/bash

#
# Gitpod Setup Script for Agent Zero
# Automates the complete Guix build & deploy process
#

set -e

echo "🚀 Starting Agent Zero Gitpod setup..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Guix if not present
install_guix() {
    if ! command_exists guix; then
        echo "📦 Installing GNU Guix package manager..."
        
        # Download and run Guix installer
        cd /tmp
        wget -q https://git.savannah.gnu.org/cgit/guix.git/plain/etc/guix-install.sh
        chmod +x guix-install.sh
        
        # Install Guix (may need to run as root)
        if sudo ./guix-install.sh; then
            echo "✅ Guix installed successfully"
        else
            echo "⚠️ Guix installation had issues, continuing..."
        fi
        
        # Source Guix profile
        if [ -f "$HOME/.config/guix/current/etc/profile" ]; then
            source "$HOME/.config/guix/current/etc/profile"
        fi
    else
        echo "✅ Guix already installed"
    fi
}

# Function to setup Guix environment
setup_guix_environment() {
    echo "🔧 Setting up Guix environment..."
    
    # Pull latest Guix
    if command_exists guix; then
        echo "📥 Pulling latest Guix packages..."
        guix pull || echo "⚠️ Guix pull failed, continuing with existing packages"
        
        # Install packages from manifest
        if [ -f "guix/manifest.scm" ]; then
            echo "📦 Installing packages from Guix manifest..."
            guix install -m guix/manifest.scm || echo "⚠️ Some Guix packages failed to install"
        fi
    fi
}

# Function to setup Python environment
setup_python_environment() {
    echo "🐍 Setting up Python environment..."
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        echo "📦 Installing Python dependencies..."
        python -m pip install -r requirements.txt
    fi
}

# Function to setup Agent Zero
setup_agent_zero() {
    echo "⚡ Setting up Agent Zero..."
    
    # Create necessary directories
    mkdir -p logs memory tmp
    
    # Run preload if script exists
    if [ -f "preload.py" ]; then
        echo "🔄 Running Agent Zero preload..."
        python preload.py --dockerized=true || echo "⚠️ Preload completed with warnings"
    fi
    
    # Setup environment file if example exists
    if [ -f "example.env" ] && [ ! -f ".env" ]; then
        echo "📄 Creating environment file from example..."
        cp example.env .env
    fi
}

# Function to start Agent Zero services
start_agent_zero() {
    echo "🌟 Starting Agent Zero services..."
    
    # Check if we should start the web UI
    if [ "${1:-web}" = "web" ] && [ -f "run_ui.py" ]; then
        echo "🌐 Starting Agent Zero Web UI..."
        python run_ui.py &
        WEB_PID=$!
        echo "Web UI started with PID: $WEB_PID"
    elif [ "$1" = "cli" ] && [ -f "run_cli.py" ]; then
        echo "💻 Starting Agent Zero CLI..."
        python run_cli.py
    fi
}

# Function to show status
show_status() {
    echo ""
    echo "📊 Agent Zero Status:"
    echo "===================="
    echo "🐍 Python: $(python --version)"
    if command_exists guix; then
        echo "📦 Guix: $(guix --version | head -1)"
    else
        echo "📦 Guix: Not installed"
    fi
    echo "📁 Working directory: $(pwd)"
    echo "🌐 Web UI will be available on port 50001"
    echo "🔧 Alternative port 50080 also configured"
    echo ""
    echo "🎯 Available commands:"
    echo "  python run_ui.py     # Start web interface"
    echo "  python run_cli.py    # Start CLI interface"
    echo "  guix shell           # Enter Guix shell"
    echo ""
}

# Main execution
main() {
    cd /workspace/agent-zero-cron
    
    echo "🎯 Starting Agent Zero Gitpod deployment..."
    
    # Run setup steps
    install_guix
    setup_guix_environment
    setup_python_environment
    setup_agent_zero
    
    # Show status
    show_status
    
    # Start services if requested
    if [ "${AUTO_START:-true}" = "true" ]; then
        start_agent_zero "${1:-web}"
    fi
}

# Execute main function with all arguments
main "$@"
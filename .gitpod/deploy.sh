#!/bin/bash

#
# Agent Zero Gitpod Deployment Script
# Integrates existing Guix build system with Gitpod environment
#

set -e

# Configuration
AGENT_ZERO_PORT="${AGENT_ZERO_PORT:-50001}"
GITPOD_WORKSPACE="${GITPOD_WORKSPACE_URL:-localhost}"
LOG_FILE="/tmp/agent-zero-deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Python
    if command -v python >/dev/null 2>&1; then
        PYTHON_VERSION=$(python --version)
        log_success "Python found: $PYTHON_VERSION"
    else
        log_error "Python not found"
        return 1
    fi
    
    # Check pip
    if command -v pip >/dev/null 2>&1; then
        log_success "pip found"
    else
        log_error "pip not found"
        return 1
    fi
    
    # Check if we're in Gitpod
    if [ -n "$GITPOD_WORKSPACE_ID" ]; then
        log_success "Running in Gitpod environment"
        export IN_GITPOD=true
    else
        log_warning "Not running in Gitpod"
        export IN_GITPOD=false
    fi
}

# Function to setup Python dependencies
setup_python_deps() {
    log "Setting up Python dependencies..."
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        log "Installing from requirements.txt..."
        python -m pip install -r requirements.txt
        log_success "Python dependencies installed"
    else
        log_error "requirements.txt not found"
        return 1
    fi
}

# Function to integrate with existing Guix setup
setup_guix_integration() {
    log "Setting up Guix integration..."
    
    # Check if Guix scripts exist
    if [ -d "guix/scripts" ]; then
        log "Found existing Guix scripts"
        
        # Make scripts executable
        chmod +x guix/scripts/*.sh
        
        # Source Guix environment if available
        if [ -f "$HOME/.config/guix/current/etc/profile" ]; then
            log "Sourcing Guix profile..."
            source "$HOME/.config/guix/current/etc/profile"
        fi
        
        log_success "Guix integration setup complete"
    else
        log_warning "Guix scripts not found, continuing without Guix"
    fi
}

# Function to setup Agent Zero environment
setup_agent_zero() {
    log "Setting up Agent Zero environment..."
    
    # Create necessary directories
    mkdir -p logs memory tmp
    
    # Copy example env if needed
    if [ -f "example.env" ] && [ ! -f ".env" ]; then
        log "Creating .env from example.env..."
        cp example.env .env
        
        # Update for Gitpod if in Gitpod environment
        if [ "$IN_GITPOD" = "true" ]; then
            log "Configuring for Gitpod environment..."
            # Add Gitpod-specific configurations
            echo "" >> .env
            echo "# Gitpod specific configurations" >> .env
            echo "GITPOD_WORKSPACE=true" >> .env
            echo "WEB_PORT=$AGENT_ZERO_PORT" >> .env
        fi
    fi
    
    # Run preload
    if [ -f "preload.py" ]; then
        log "Running Agent Zero preload..."
        python preload.py --dockerized=true || log_warning "Preload completed with warnings"
    fi
    
    log_success "Agent Zero environment setup complete"
}

# Function to build with Guix if available
build_with_guix() {
    if command -v guix >/dev/null 2>&1; then
        log "Building with Guix..."
        
        # Choose manifest file - prefer Gitpod-specific if available
        MANIFEST_FILE=""
        if [ "$IN_GITPOD" = "true" ] && [ -f ".gitpod/manifest.scm" ]; then
            MANIFEST_FILE=".gitpod/manifest.scm"
            log "Using Gitpod-optimized manifest"
        elif [ -f "guix/manifest.scm" ]; then
            MANIFEST_FILE="guix/manifest.scm"
            log "Using standard Guix manifest"
        fi
        
        # Try to use existing Guix build script
        if [ -f "guix/scripts/build.sh" ]; then
            log "Using existing Guix build script..."
            bash guix/scripts/build.sh || log_warning "Guix build completed with warnings"
        elif [ -n "$MANIFEST_FILE" ]; then
            # Fallback to manual Guix setup with chosen manifest
            log "Setting up Guix packages from $MANIFEST_FILE..."
            guix install -m "$MANIFEST_FILE" || log_warning "Some Guix packages failed to install"
        fi
        
        log_success "Guix build completed"
    else
        log_warning "Guix not available, skipping Guix build"
    fi
}

# Function to start Agent Zero
start_agent_zero() {
    log "Starting Agent Zero..."
    
    # Start web UI
    if [ -f "run_ui.py" ]; then
        log "Starting Agent Zero Web UI on port $AGENT_ZERO_PORT..."
        
        if [ "$IN_GITPOD" = "true" ]; then
            # In Gitpod, start in background and show URL
            python run_ui.py &
            AGENT_PID=$!
            
            # Wait a moment for startup
            sleep 3
            
            # Generate Gitpod URL
            GITPOD_URL="https://$AGENT_ZERO_PORT-$GITPOD_WORKSPACE_ID.$GITPOD_WORKSPACE_CLUSTER_HOST"
            
            log_success "Agent Zero started successfully!"
            log_success "Web UI available at: $GITPOD_URL"
            log "Process ID: $AGENT_PID"
            
            # Keep the script running
            wait $AGENT_PID
        else
            # Local/other environment
            log_success "Starting Agent Zero Web UI..."
            python run_ui.py
        fi
    else
        log_error "run_ui.py not found"
        return 1
    fi
}

# Function to show deployment status
show_status() {
    log "Deployment Status:"
    echo "=================="
    echo "🐍 Python: $(python --version)"
    echo "📦 Pip: $(pip --version)"
    if command -v guix >/dev/null 2>&1; then
        echo "🔧 Guix: $(guix --version | head -1)"
    else
        echo "🔧 Guix: Not available"
    fi
    echo "📁 Working directory: $(pwd)"
    echo "🌐 Web UI port: $AGENT_ZERO_PORT"
    
    if [ "$IN_GITPOD" = "true" ]; then
        echo "☁️ Gitpod Workspace: $GITPOD_WORKSPACE_ID"
        echo "🔗 Access URL: https://$AGENT_ZERO_PORT-$GITPOD_WORKSPACE_ID.$GITPOD_WORKSPACE_CLUSTER_HOST"
    fi
    
    echo ""
    echo "📋 Available commands:"
    echo "  python run_ui.py     # Start web interface"
    echo "  python run_cli.py    # Start CLI interface"
    if command -v guix >/dev/null 2>&1; then
        echo "  guix shell           # Enter Guix shell"
    fi
    echo ""
}

# Main deployment function
main() {
    log "🚀 Starting Agent Zero Gitpod deployment..."
    log "Log file: $LOG_FILE"
    
    # Change to correct directory
    if [ -d "/workspace/agent-zero-cron" ]; then
        cd /workspace/agent-zero-cron
    fi
    
    # Run deployment steps
    check_prerequisites || exit 1
    setup_python_deps || exit 1
    setup_guix_integration
    setup_agent_zero || exit 1
    build_with_guix
    
    show_status
    
    # Start Agent Zero
    if [ "${AUTO_START:-true}" = "true" ]; then
        start_agent_zero
    else
        log "Auto-start disabled. Run 'python run_ui.py' to start Agent Zero."
    fi
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "start")
        start_agent_zero
        ;;
    "status")
        show_status
        ;;
    "help")
        echo "Agent Zero Gitpod Deployment Script"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  deploy   Complete deployment (default)"
        echo "  start    Start Agent Zero services"
        echo "  status   Show deployment status"
        echo "  help     Show this help"
        echo ""
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
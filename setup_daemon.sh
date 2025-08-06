#!/bin/bash
# Daemon Zero Setup Script
# This script helps set up Daemon Zero for production use

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/daemon_config.json"
SERVICE_NAME="daemon-zero"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "=================================="
    echo "$1"
    echo "=================================="
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# Check Python version
check_python() {
    print_info "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python3 found: $PYTHON_VERSION"
        return 0
    else
        print_error "Python3 not found. Please install Python 3.8 or higher."
        return 1
    fi
}

# Install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        print_info "Installing from requirements.txt..."
        pip3 install -r "$SCRIPT_DIR/requirements.txt" --user || {
            print_warning "Failed to install from requirements.txt, continuing..."
        }
    fi
    
    # Install minimal required packages
    print_info "Installing minimal required packages..."
    pip3 install --user asyncio || print_warning "asyncio installation failed"
    
    print_success "Dependencies installation completed"
}

# Set up configuration
setup_configuration() {
    print_info "Setting up configuration..."
    
    if [ -f "$CONFIG_FILE" ]; then
        print_info "Configuration file already exists: $CONFIG_FILE"
        read -p "Do you want to overwrite it? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing configuration"
            return 0
        fi
    fi
    
    print_info "Creating default configuration..."
    
    # Create configuration with user inputs
    read -p "Enter daemon tick interval in seconds [60]: " TICK_INTERVAL
    TICK_INTERVAL=${TICK_INTERVAL:-60}
    
    read -p "Enter maximum concurrent tasks [5]: " MAX_TASKS
    MAX_TASKS=${MAX_TASKS:-5}
    
    read -p "Enter maximum memory limit in MB [2048]: " MAX_MEMORY
    MAX_MEMORY=${MAX_MEMORY:-2048}
    
    read -p "Enter log level (DEBUG/INFO/WARNING/ERROR) [INFO]: " LOG_LEVEL
    LOG_LEVEL=${LOG_LEVEL:-INFO}
    
    cat > "$CONFIG_FILE" << EOF
{
  "scheduler": {
    "enabled": true,
    "tick_interval": $TICK_INTERVAL,
    "max_concurrent_tasks": $MAX_TASKS
  },
  "workflow": {
    "enabled": true,
    "inngest_enabled": false
  },
  "agent": {
    "model_provider": "openai",
    "model_name": "gpt-4",
    "max_context_length": 8000
  },
  "daemon": {
    "auto_restart": true,
    "health_check_interval": 300,
    "max_memory_mb": $MAX_MEMORY
  },
  "logging": {
    "level": "$LOG_LEVEL",
    "max_files": 10,
    "max_size_mb": 100
  }
}
EOF
    
    print_success "Configuration created: $CONFIG_FILE"
}

# Set up directories and permissions
setup_directories() {
    print_info "Setting up directories..."
    
    # Create logs directory
    mkdir -p "$SCRIPT_DIR/logs"
    print_success "Created logs directory"
    
    # Create work directory
    mkdir -p "$SCRIPT_DIR/work"
    print_success "Created work directory"
    
    # Make scripts executable
    chmod +x "$SCRIPT_DIR/daemon_zero.py" 2>/dev/null || true
    chmod +x "$SCRIPT_DIR/daemon_cli.py" 2>/dev/null || true
    chmod +x "$SCRIPT_DIR/daemon_control.sh" 2>/dev/null || true
    
    print_success "Set script permissions"
}

# Install as system service
install_system_service() {
    if ! check_root; then
        print_error "System service installation requires root privileges"
        return 1
    fi
    
    print_info "Installing system service..."
    
    # Create daemon user if it doesn't exist
    if ! id "daemon-zero" &>/dev/null; then
        print_info "Creating daemon-zero user..."
        useradd -r -s /bin/false -d "$SCRIPT_DIR" daemon-zero
        print_success "Created daemon-zero user"
    fi
    
    # Set ownership
    chown -R daemon-zero:daemon-zero "$SCRIPT_DIR"
    print_success "Set directory ownership"
    
    # Create systemd service file
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Daemon Zero - Background Agent Daemon for Agent Zero
After=network.target
Wants=network.target

[Service]
Type=simple
User=daemon-zero
Group=daemon-zero
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/daemon_zero.py run --config $CONFIG_FILE
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
Restart=always
RestartSec=10
TimeoutStopSec=30

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$SCRIPT_DIR
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable "${SERVICE_NAME}.service"
    
    print_success "System service installed: $SERVICE_NAME"
    print_info "Use 'systemctl start $SERVICE_NAME' to start the service"
    print_info "Use 'systemctl status $SERVICE_NAME' to check service status"
}

# Test installation
test_installation() {
    print_info "Testing installation..."
    
    # Test daemon help
    print_info "Testing daemon help..."
    if python3 "$SCRIPT_DIR/daemon_zero.py" --help > /dev/null 2>&1; then
        print_success "Daemon help test passed"
    else
        print_error "Daemon help test failed"
        return 1
    fi
    
    # Test CLI help
    print_info "Testing CLI help..."
    if python3 "$SCRIPT_DIR/daemon_cli.py" --help > /dev/null 2>&1; then
        print_success "CLI help test passed"
    else
        print_error "CLI help test failed"
        return 1
    fi
    
    # Test control script
    print_info "Testing control script..."
    if "$SCRIPT_DIR/daemon_control.sh" status > /dev/null 2>&1; then
        print_success "Control script test passed"
    else
        print_error "Control script test failed"
        return 1
    fi
    
    # Test configuration loading
    print_info "Testing configuration..."
    if python3 -c "
import json, sys, os
sys.path.append('$SCRIPT_DIR')
from daemon_zero import DaemonZero
daemon = DaemonZero(config_file='$CONFIG_FILE')
config = daemon.load_config()
print('Configuration test passed')
" > /dev/null 2>&1; then
        print_success "Configuration test passed"
    else
        print_error "Configuration test failed"
        return 1
    fi
    
    print_success "All installation tests passed!"
}

# Show usage information
show_usage() {
    print_header "Daemon Zero Setup Complete!"
    
    echo "Basic Usage:"
    echo "  Start daemon:    $SCRIPT_DIR/daemon_control.sh start"
    echo "  Stop daemon:     $SCRIPT_DIR/daemon_control.sh stop"
    echo "  Check status:    $SCRIPT_DIR/daemon_control.sh status"
    echo "  View logs:       $SCRIPT_DIR/daemon_control.sh logs"
    echo ""
    echo "Task Management:"
    echo "  List tasks:      $SCRIPT_DIR/daemon_control.sh cli tasks list"
    echo "  Add task:        $SCRIPT_DIR/daemon_control.sh cli tasks add 'Task Name'"
    echo "  Run scheduler:   $SCRIPT_DIR/daemon_control.sh cli scheduler tick"
    echo ""
    echo "Configuration:"
    echo "  Config file:     $CONFIG_FILE"
    echo "  View config:     $SCRIPT_DIR/daemon_control.sh cli config show"
    echo ""
    echo "Documentation:"
    echo "  README:          $SCRIPT_DIR/DAEMON_README.md"
    echo "  Examples:        $SCRIPT_DIR/example_*.py"
    echo "  Demo:            python3 $SCRIPT_DIR/demo_daemon.py"
    
    if systemctl is-enabled "${SERVICE_NAME}.service" &>/dev/null; then
        echo ""
        echo "System Service:"
        echo "  Start service:   sudo systemctl start $SERVICE_NAME"
        echo "  Stop service:    sudo systemctl stop $SERVICE_NAME"
        echo "  Service status:  sudo systemctl status $SERVICE_NAME"
        echo "  View logs:       sudo journalctl -u $SERVICE_NAME -f"
    fi
}

# Main setup function
main() {
    print_header "Daemon Zero Setup Script"
    
    echo "This script will set up Daemon Zero for production use."
    echo "It will:"
    echo "  1. Check system requirements"
    echo "  2. Install dependencies"
    echo "  3. Set up configuration"
    echo "  4. Create necessary directories"
    echo "  5. Optionally install as system service"
    echo "  6. Test the installation"
    echo ""
    
    read -p "Continue with setup? (Y/n): " -r
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Setup cancelled by user"
        exit 0
    fi
    
    # Check system requirements
    print_header "1. Checking System Requirements"
    check_python || exit 1
    
    # Install dependencies
    print_header "2. Installing Dependencies"
    install_dependencies
    
    # Set up configuration
    print_header "3. Setting Up Configuration"
    setup_configuration
    
    # Set up directories
    print_header "4. Setting Up Directories"
    setup_directories
    
    # Ask about system service
    print_header "5. System Service Installation"
    if check_root; then
        read -p "Install as system service? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_system_service
        else
            print_info "Skipping system service installation"
        fi
    else
        print_info "System service installation requires root privileges"
        print_info "Run 'sudo $0' to install as system service"
    fi
    
    # Test installation
    print_header "6. Testing Installation"
    test_installation || {
        print_error "Installation tests failed"
        exit 1
    }
    
    # Show usage
    show_usage
    
    print_success "Daemon Zero setup completed successfully!"
    print_info "You can now start using Daemon Zero"
}

# Handle command line arguments
case "${1:-setup}" in
    setup)
        main
        ;;
    service)
        if check_root; then
            install_system_service
        else
            print_error "Service installation requires root privileges"
            exit 1
        fi
        ;;
    test)
        test_installation
        ;;
    help|--help|-h)
        echo "Daemon Zero Setup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  setup     - Run full setup (default)"
        echo "  service   - Install system service only (requires root)"
        echo "  test      - Test existing installation"
        echo "  help      - Show this help"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
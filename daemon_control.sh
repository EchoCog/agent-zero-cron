#!/bin/bash
# Daemon Zero startup script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAEMON_SCRIPT="$SCRIPT_DIR/daemon_zero.py"
CLI_SCRIPT="$SCRIPT_DIR/daemon_cli.py"
PIDFILE="/tmp/daemon_zero.pid"
CONFIG_FILE="$SCRIPT_DIR/daemon_config.json"

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

# Check if daemon is running
is_running() {
    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        else
            print_warning "Stale PID file found, removing..."
            rm -f "$PIDFILE"
            return 1
        fi
    else
        return 1
    fi
}

# Start daemon
start_daemon() {
    if is_running; then
        PID=$(cat "$PIDFILE")
        print_warning "Daemon is already running (PID: $PID)"
        return 1
    fi
    
    print_info "Starting Daemon Zero..."
    
    # Check if Python script exists
    if [ ! -f "$DAEMON_SCRIPT" ]; then
        print_error "Daemon script not found: $DAEMON_SCRIPT"
        return 1
    fi
    
    # Start daemon in background
    cd "$SCRIPT_DIR"
    nohup python3 "$DAEMON_SCRIPT" run --config "$CONFIG_FILE" --pidfile "$PIDFILE" \
        > /tmp/daemon_zero.log 2>&1 &
    
    # Wait a moment and check if it started
    sleep 2
    
    if is_running; then
        PID=$(cat "$PIDFILE")
        print_success "Daemon Zero started successfully (PID: $PID)"
        print_info "Log file: /tmp/daemon_zero.log"
        print_info "Config file: $CONFIG_FILE"
        return 0
    else
        print_error "Failed to start daemon"
        print_info "Check log file: /tmp/daemon_zero.log"
        return 1
    fi
}

# Stop daemon
stop_daemon() {
    if ! is_running; then
        print_warning "Daemon is not running"
        return 1
    fi
    
    PID=$(cat "$PIDFILE")
    print_info "Stopping Daemon Zero (PID: $PID)..."
    
    # Send SIGTERM
    kill -TERM "$PID" 2>/dev/null
    
    # Wait for graceful shutdown
    for i in {1..30}; do
        if ! kill -0 "$PID" 2>/dev/null; then
            print_success "Daemon stopped gracefully"
            rm -f "$PIDFILE"
            return 0
        fi
        sleep 1
    done
    
    # Force kill if still running
    print_warning "Daemon did not stop gracefully, force killing..."
    kill -KILL "$PID" 2>/dev/null
    sleep 2
    
    if ! kill -0 "$PID" 2>/dev/null; then
        print_success "Daemon force killed"
        rm -f "$PIDFILE"
        return 0
    else
        print_error "Failed to stop daemon"
        return 1
    fi
}

# Show daemon status
show_status() {
    if is_running; then
        PID=$(cat "$PIDFILE")
        print_success "Daemon Zero is running (PID: $PID)"
        
        # Show additional info if available
        if [ -f "$CONFIG_FILE" ]; then
            print_info "Config file: $CONFIG_FILE"
        fi
        
        if [ -f "/tmp/daemon_zero.log" ]; then
            print_info "Log file: /tmp/daemon_zero.log"
            print_info "Last 3 log lines:"
            tail -n 3 /tmp/daemon_zero.log | sed 's/^/  /'
        fi
        
        return 0
    else
        print_warning "Daemon Zero is not running"
        return 1
    fi
}

# Show daemon logs
show_logs() {
    if [ -f "/tmp/daemon_zero.log" ]; then
        if [ "$1" = "follow" ] || [ "$1" = "-f" ]; then
            print_info "Following daemon logs (Ctrl+C to stop)..."
            tail -f /tmp/daemon_zero.log
        else
            lines=${1:-50}
            print_info "Showing last $lines lines of daemon logs:"
            tail -n "$lines" /tmp/daemon_zero.log
        fi
    else
        print_warning "Log file not found: /tmp/daemon_zero.log"
        return 1
    fi
}

# CLI wrapper
run_cli() {
    if [ ! -f "$CLI_SCRIPT" ]; then
        print_error "CLI script not found: $CLI_SCRIPT"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
    python3 "$CLI_SCRIPT" "$@"
}

# Install daemon as system service (systemd)
install_service() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root to install system service"
        return 1
    fi
    
    SERVICE_FILE="/etc/systemd/system/daemon-zero.service"
    
    print_info "Installing Daemon Zero as system service..."
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Daemon Zero - Background Agent Daemon for Agent Zero
After=network.target

[Service]
Type=forking
User=daemon-zero
Group=daemon-zero
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/daemon_zero.py start --config $CONFIG_FILE --pidfile $PIDFILE
ExecStop=$SCRIPT_DIR/daemon_zero.py stop --pidfile $PIDFILE
PIDFile=$PIDFILE
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Create user if it doesn't exist
    if ! id "daemon-zero" &>/dev/null; then
        print_info "Creating daemon-zero user..."
        useradd -r -s /bin/false daemon-zero
    fi
    
    # Set permissions
    chown -R daemon-zero:daemon-zero "$SCRIPT_DIR"
    chmod +x "$DAEMON_SCRIPT"
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable daemon-zero.service
    
    print_success "Daemon Zero service installed successfully"
    print_info "Use 'systemctl start daemon-zero' to start the service"
    print_info "Use 'systemctl status daemon-zero' to check service status"
}

# Show help
show_help() {
    echo "Daemon Zero Control Script"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|logs|cli|install-service|help}"
    echo ""
    echo "Commands:"
    echo "  start          - Start the daemon"
    echo "  stop           - Stop the daemon"
    echo "  restart        - Restart the daemon"
    echo "  status         - Show daemon status"
    echo "  logs [lines]   - Show daemon logs (default: 50 lines)"
    echo "  logs follow    - Follow daemon logs in real-time"
    echo "  cli [args]     - Run CLI interface"
    echo "  install-service- Install as system service (requires root)"
    echo "  help           - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start daemon"
    echo "  $0 status                   # Check status"
    echo "  $0 logs 100                 # Show last 100 log lines"
    echo "  $0 logs follow              # Follow logs"
    echo "  $0 cli tasks list           # List tasks via CLI"
    echo "  $0 cli daemon status        # Check daemon status via CLI"
}

# Main script logic
case "$1" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        stop_daemon
        sleep 2
        start_daemon
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    cli)
        shift
        run_cli "$@"
        ;;
    install-service)
        install_service
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

exit $?
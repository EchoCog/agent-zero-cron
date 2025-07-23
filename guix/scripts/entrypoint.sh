#!/bin/bash

#
# Agent Zero Guix Entrypoint Script
# Initializes the Guix environment and starts Agent Zero services
#

set -e

# Source Guix profile
if [ -f "$GUIX_PROFILE/etc/profile" ]; then
    source "$GUIX_PROFILE/etc/profile"
fi

# Function to run commands in Guix environment
run_guix() {
    /entry-point.sh "$@"
}

# Function to start Agent Zero services
start_agent_zero() {
    echo "Starting Agent Zero services..."
    
    # Change to Agent Zero directory
    cd /a0
    
    # Run preload if needed
    if [ ! -f /tmp/.preload_done ]; then
        echo "Running Agent Zero preload..."
        run_guix python preload.py --dockerized=true
        touch /tmp/.preload_done
    fi
    
    # Start the web UI
    echo "Starting Agent Zero Web UI..."
    run_guix python run_ui.py
}

# Function to start CLI mode
start_cli() {
    echo "Starting Agent Zero CLI..."
    cd /a0
    run_guix python run_cli.py
}

# Function to show help
show_help() {
    echo "Agent Zero Guix Deployment"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  run      Start Agent Zero Web UI (default)"
    echo "  cli      Start Agent Zero CLI"
    echo "  shell    Drop into Guix shell"
    echo "  help     Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  BRANCH   Git branch to use (default: main)"
    echo ""
}

# Main command handling
case "${1:-run}" in
    "run")
        start_agent_zero
        ;;
    "cli")
        start_cli
        ;;
    "shell")
        echo "Starting Guix shell..."
        run_guix bash
        ;;
    "help")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
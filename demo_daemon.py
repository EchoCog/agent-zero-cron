#!/usr/bin/env python3
"""
Daemon Zero Demonstration

This script demonstrates the key features of Daemon Zero including:
- Starting and stopping the daemon
- Managing tasks through the CLI
- Monitoring daemon health and status
- Viewing logs and configuration
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"🔧 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd or os.path.dirname(__file__),
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.stdout:
            print(f"📄 Output:\n{result.stdout}")
        
        if result.stderr and result.returncode != 0:
            print(f"❌ Error:\n{result.stderr}")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
        return False, "", "Command timed out"
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False, "", str(e)

def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"🚀 {title}")
    print(f"{'=' * 60}")

def print_step(step_num, description):
    """Print a step header."""
    print(f"\n{step_num}. {description}")
    print("-" * 40)

def wait_for_user():
    """Wait for user to press Enter."""
    input("\n⏸️  Press Enter to continue...")

def main():
    """Run the daemon demonstration."""
    print("🎯 Daemon Zero - Live Demonstration")
    print("This demo will show you how to use Daemon Zero for background agent processing")
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print_section("Pre-flight Check")
    
    # Check if files exist
    required_files = [
        "daemon_zero.py",
        "daemon_cli.py", 
        "daemon_control.sh"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - Found")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n💀 Missing required files: {', '.join(missing_files)}")
        return 1
    
    wait_for_user()
    
    print_section("Step 1: Check Initial Status")
    print_step(1, "Checking if daemon is already running")
    
    success, output, error = run_command(["./daemon_control.sh", "status"])
    
    wait_for_user()
    
    print_section("Step 2: Start Daemon Zero")
    print_step(2, "Starting the daemon in background mode")
    
    success, output, error = run_command(["./daemon_control.sh", "start"])
    
    if success:
        print("✅ Daemon started successfully!")
    else:
        print("❌ Failed to start daemon")
        print("Let's try the CLI approach...")
        success, output, error = run_command([sys.executable, "daemon_zero.py", "start", "--foreground"])
    
    # Wait a moment for daemon to start
    time.sleep(2)
    
    wait_for_user()
    
    print_section("Step 3: Verify Daemon Status")
    print_step(3, "Checking daemon status and health")
    
    # Check status via control script
    run_command(["./daemon_control.sh", "status"])
    
    # Check status via CLI
    run_command(["./daemon_control.sh", "cli", "daemon", "status"])
    
    # Run health check
    run_command(["./daemon_control.sh", "cli", "daemon", "health"])
    
    wait_for_user()
    
    print_section("Step 4: Configuration Management")
    print_step(4, "Viewing daemon configuration")
    
    # Show configuration
    run_command(["./daemon_control.sh", "cli", "config", "show"])
    
    wait_for_user()
    
    print_section("Step 5: Task Management")
    print_step(5, "Managing background tasks")
    
    # List initial tasks
    print("📋 Initial task list:")
    run_command(["./daemon_control.sh", "cli", "tasks", "list"])
    
    # Add some test tasks
    print("\n➕ Adding test tasks:")
    run_command(["./daemon_control.sh", "cli", "tasks", "add", "Daily Health Check"])
    run_command(["./daemon_control.sh", "cli", "tasks", "add", "Weekly Report Generation"])
    run_command(["./daemon_control.sh", "cli", "tasks", "add", "Background Data Processing"])
    
    # List tasks again
    print("\n📋 Updated task list:")
    run_command(["./daemon_control.sh", "cli", "tasks", "list"])
    
    wait_for_user()
    
    print_section("Step 6: Scheduler Operations")
    print_step(6, "Testing scheduler functionality")
    
    # Run scheduler tick manually
    print("⚙️ Running scheduler tick manually:")
    run_command(["./daemon_control.sh", "cli", "scheduler", "tick"])
    
    wait_for_user()
    
    print_section("Step 7: Log Monitoring")
    print_step(7, "Viewing daemon logs")
    
    # Show recent logs
    print("📜 Recent daemon logs:")
    run_command(["./daemon_control.sh", "logs", "10"])
    
    wait_for_user()
    
    print_section("Step 8: Testing Task Execution")
    print_step(8, "Executing a task manually")
    
    # Get a task UUID and run it
    success, output, error = run_command(["./daemon_control.sh", "cli", "tasks", "list"])
    
    if success and "mock-" in output:
        # Extract UUID from output (simple approach)
        lines = output.split('\n')
        for line in lines:
            if "mock-" in line:
                parts = line.split()
                if parts:
                    uuid = parts[0]
                    print(f"🎯 Found task UUID: {uuid}")
                    print(f"🚀 Executing task {uuid}:")
                    run_command(["./daemon_control.sh", "cli", "tasks", "run", uuid])
                    break
    else:
        print("ℹ️ No tasks available for execution")
    
    wait_for_user()
    
    print_section("Step 9: Final Status Check")
    print_step(9, "Final health and status verification")
    
    # Final status check
    run_command(["./daemon_control.sh", "status"])
    
    # Final health check
    run_command(["./daemon_control.sh", "cli", "daemon", "health"])
    
    wait_for_user()
    
    print_section("Step 10: Cleanup")
    print_step(10, "Stopping the daemon")
    
    # Stop the daemon
    run_command(["./daemon_control.sh", "stop"])
    
    # Verify it's stopped
    run_command(["./daemon_control.sh", "status"])
    
    print_section("Demonstration Complete!")
    
    print("🎉 Daemon Zero demonstration completed successfully!")
    print("\n📚 What we demonstrated:")
    print("   ✅ Daemon lifecycle management (start/stop)")
    print("   ✅ Status monitoring and health checks")
    print("   ✅ Task management (add/list/run)")
    print("   ✅ Scheduler operations")
    print("   ✅ Configuration management")
    print("   ✅ Log monitoring")
    print("   ✅ CLI interface usage")
    
    print("\n🔧 Available commands:")
    print("   ./daemon_control.sh start|stop|restart|status")
    print("   ./daemon_control.sh cli tasks list")
    print("   ./daemon_control.sh cli daemon health")
    print("   ./daemon_control.sh logs [follow]")
    
    print("\n📖 See DAEMON_README.md for complete documentation")
    print("\n🚀 Daemon Zero is ready for production use!")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Demonstration interrupted by user")
        print("🧹 Cleaning up...")
        
        # Try to stop daemon if it's running
        try:
            subprocess.run(["./daemon_control.sh", "stop"], 
                         cwd=os.path.dirname(__file__), 
                         timeout=10)
        except:
            pass
        
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Demonstration failed: {e}")
        sys.exit(1)
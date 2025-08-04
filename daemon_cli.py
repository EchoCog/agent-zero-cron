#!/usr/bin/env python3
"""
Daemon Zero CLI - Command line interface for managing Daemon Zero

This provides a convenient CLI for managing the Agent Zero daemon,
including task management, status monitoring, and configuration.
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daemon_zero import DaemonZero, daemon_status, stop_daemon
from minimal_stubs import get_minimal_task_scheduler, MockTask


class DaemonCLI:
    """CLI interface for Daemon Zero management."""
    
    def __init__(self):
        self.scheduler = None
    
    async def init_scheduler(self):
        """Initialize scheduler for task operations."""
        if not self.scheduler:
            self.scheduler = get_minimal_task_scheduler()
    
    async def list_tasks(self, args):
        """List all tasks in the scheduler."""
        await self.init_scheduler()
        
        tasks = self.scheduler.get_tasks()
        
        if not tasks:
            print("No tasks found")
            return
        
        print(f"\nFound {len(tasks)} task(s):")
        print("-" * 80)
        print(f"{'UUID':<20} {'Name':<25} {'State':<10} {'Last Run':<20}")
        print("-" * 80)
        
        for task in tasks:
            last_run = task.last_run.strftime("%Y-%m-%d %H:%M:%S") if task.last_run else "Never"
            print(f"{task.uuid:<20} {task.name:<25} {task.state:<10} {last_run:<20}")
    
    async def add_task(self, args):
        """Add a new task to the scheduler."""
        await self.init_scheduler()
        
        # Create a simple mock task for demonstration
        task = MockTask(
            name=args.name,
            uuid=args.uuid if hasattr(args, 'uuid') and args.uuid else None
        )
        
        self.scheduler.add_task(task)
        print(f"Added task: {task.name} (UUID: {task.uuid})")
    
    async def remove_task(self, args):
        """Remove a task from the scheduler."""
        await self.init_scheduler()
        
        task = self.scheduler.get_task_by_uuid(args.uuid)
        if not task:
            print(f"Task with UUID {args.uuid} not found")
            return 1
        
        # For mock implementation, just remove from list
        if hasattr(self.scheduler, 'tasks'):
            self.scheduler.tasks = [t for t in self.scheduler.tasks if t.uuid != args.uuid]
            print(f"Removed task: {task.name}")
        else:
            print("Remove task functionality not available in real scheduler via CLI")
            print("Use the web interface or API instead")
    
    async def run_task(self, args):
        """Run a specific task."""
        await self.init_scheduler()
        
        try:
            await self.scheduler.run_task_by_uuid(args.uuid)
            print(f"Task {args.uuid} executed successfully")
        except Exception as e:
            print(f"Failed to run task {args.uuid}: {e}")
            return 1
    
    async def scheduler_tick(self, args):
        """Manually trigger a scheduler tick."""
        await self.init_scheduler()
        
        print("Running scheduler tick...")
        await self.scheduler.tick()
        print("Scheduler tick completed")
    
    def daemon_status(self, args):
        """Show daemon status."""
        status = daemon_status(args.pidfile)
        
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"Daemon Status: {status['status']}")
            if 'pid' in status:
                print(f"PID: {status['pid']}")
            if 'reason' in status:
                print(f"Reason: {status['reason']}")
            if 'pidfile' in status:
                print(f"PID File: {status['pidfile']}")
    
    async def daemon_start(self, args):
        """Start the daemon."""
        # Check if already running
        status = daemon_status(args.pidfile)
        if status["status"] == "running":
            print(f"Daemon already running (PID: {status['pid']})")
            return 1
        
        daemon = DaemonZero(config_file=args.config, pidfile=args.pidfile)
        
        if args.foreground:
            print("Starting daemon in foreground...")
            await daemon.start()
        else:
            print("Starting daemon in background...")
            # For simplicity, we'll run in foreground for now
            # In production, this would fork and detach
            print("Note: Background mode not fully implemented, running in foreground")
            await daemon.start()
    
    def daemon_stop(self, args):
        """Stop the daemon."""
        if stop_daemon(args.pidfile):
            return 0
        else:
            return 1
    
    async def daemon_restart(self, args):
        """Restart the daemon."""
        print("Restarting daemon...")
        stop_daemon(args.pidfile)
        time.sleep(2)
        
        daemon = DaemonZero(config_file=args.config, pidfile=args.pidfile)
        await daemon.start()
    
    def show_config(self, args):
        """Show current configuration."""
        if os.path.exists(args.config):
            with open(args.config, 'r') as f:
                config = json.load(f)
            print(json.dumps(config, indent=2))
        else:
            print(f"Config file {args.config} not found")
    
    async def health_check(self, args):
        """Perform health check."""
        status = daemon_status(args.pidfile)
        
        if status["status"] != "running":
            print("Daemon is not running")
            return 1
        
        # If daemon is running, we can try to get more detailed health info
        # For now, just show basic status
        print("Daemon is running and healthy")
        print(f"PID: {status['pid']}")
        
        # Show scheduler status if available
        await self.init_scheduler()
        tasks = self.scheduler.get_tasks()
        print(f"Scheduler: {len(tasks)} tasks loaded")


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Daemon Zero CLI - Manage Agent Zero Background Daemon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s daemon start                 # Start the daemon
  %(prog)s daemon status                # Check daemon status
  %(prog)s daemon stop                  # Stop the daemon
  %(prog)s tasks list                   # List all tasks
  %(prog)s tasks add "Daily Backup"     # Add a new task
  %(prog)s scheduler tick               # Manually run scheduler
        """
    )
    
    # Global options
    parser.add_argument(
        "--config", "-c",
        default="daemon_config.json",
        help="Configuration file path"
    )
    
    parser.add_argument(
        "--pidfile", "-p",
        default="/tmp/daemon_zero.pid",
        help="PID file path"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Daemon management commands
    daemon_parser = subparsers.add_parser('daemon', help='Daemon management')
    daemon_subparsers = daemon_parser.add_subparsers(dest='daemon_command')
    
    # Daemon start
    start_parser = daemon_subparsers.add_parser('start', help='Start daemon')
    start_parser.add_argument('--foreground', '-f', action='store_true',
                             help='Run in foreground')
    
    # Daemon stop
    daemon_subparsers.add_parser('stop', help='Stop daemon')
    
    # Daemon restart
    restart_parser = daemon_subparsers.add_parser('restart', help='Restart daemon')
    restart_parser.add_argument('--foreground', '-f', action='store_true',
                               help='Run in foreground')
    
    # Daemon status
    daemon_subparsers.add_parser('status', help='Show daemon status')
    
    # Health check
    daemon_subparsers.add_parser('health', help='Perform health check')
    
    # Task management commands
    tasks_parser = subparsers.add_parser('tasks', help='Task management')
    tasks_subparsers = tasks_parser.add_subparsers(dest='tasks_command')
    
    # Tasks list
    tasks_subparsers.add_parser('list', help='List all tasks')
    
    # Tasks add
    add_parser = tasks_subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('name', help='Task name')
    add_parser.add_argument('--uuid', help='Task UUID (optional)')
    
    # Tasks remove
    remove_parser = tasks_subparsers.add_parser('remove', help='Remove a task')
    remove_parser.add_argument('uuid', help='Task UUID')
    
    # Tasks run
    run_parser = tasks_subparsers.add_parser('run', help='Run a specific task')
    run_parser.add_argument('uuid', help='Task UUID')
    
    # Scheduler commands
    scheduler_parser = subparsers.add_parser('scheduler', help='Scheduler management')
    scheduler_subparsers = scheduler_parser.add_subparsers(dest='scheduler_command')
    
    # Scheduler tick
    scheduler_subparsers.add_parser('tick', help='Run scheduler tick manually')
    
    # Config commands
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='config_command')
    
    # Config show
    config_subparsers.add_parser('show', help='Show current configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = DaemonCLI()
    
    try:
        # Handle daemon commands
        if args.command == 'daemon':
            if args.daemon_command == 'start':
                return await cli.daemon_start(args) or 0
            elif args.daemon_command == 'stop':
                return cli.daemon_stop(args)
            elif args.daemon_command == 'restart':
                return await cli.daemon_restart(args) or 0
            elif args.daemon_command == 'status':
                cli.daemon_status(args)
                return 0
            elif args.daemon_command == 'health':
                return await cli.health_check(args) or 0
            else:
                daemon_parser.print_help()
                return 1
        
        # Handle task commands
        elif args.command == 'tasks':
            if args.tasks_command == 'list':
                await cli.list_tasks(args)
                return 0
            elif args.tasks_command == 'add':
                await cli.add_task(args)
                return 0
            elif args.tasks_command == 'remove':
                return await cli.remove_task(args) or 0
            elif args.tasks_command == 'run':
                return await cli.run_task(args) or 0
            else:
                tasks_parser.print_help()
                return 1
        
        # Handle scheduler commands
        elif args.command == 'scheduler':
            if args.scheduler_command == 'tick':
                await cli.scheduler_tick(args)
                return 0
            else:
                scheduler_parser.print_help()
                return 1
        
        # Handle config commands
        elif args.command == 'config':
            if args.config_command == 'show':
                cli.show_config(args)
                return 0
            else:
                config_parser.print_help()
                return 1
        
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
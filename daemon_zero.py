#!/usr/bin/env python3
"""
Daemon Zero - Background Agent Daemon for Agent Zero

This module provides daemon functionality for running Agent Zero in the background,
enabling continuous operation of scheduled tasks, background agents, and workflow orchestration.
"""

import asyncio
import argparse
import atexit
import json
import logging
import os
import signal
import sys
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class DaemonZero:
    """
    Main daemon class for Agent Zero background processing.
    
    Provides:
    - Background task scheduling and execution
    - Agent Zero workflow orchestration  
    - Process management and monitoring
    - Graceful startup/shutdown
    - Status monitoring and health checks
    """
    
    def __init__(self, config_file: Optional[str] = None, pidfile: Optional[str] = None):
        self.config_file = config_file or "daemon_config.json"
        self.pidfile = pidfile or "/tmp/daemon_zero.pid"
        self.running = False
        self.config = {}
        self.scheduler = None
        self.workflow_manager = None
        self.logger = self._setup_logging()
        self._shutdown_event = asyncio.Event()
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Register cleanup on exit (only once per class)
        if not hasattr(DaemonZero, '_atexit_registered'):
            atexit.register(self.__class__._global_cleanup)
            DaemonZero._atexit_registered = True
            DaemonZero._instances = []
        
        # Track instances for global cleanup
        DaemonZero._instances.append(self)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for daemon."""
        logger = logging.getLogger('daemon_zero')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(log_dir / "daemon_zero.log")
        file_handler.setLevel(logging.INFO)
        
        # Console handler  
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        if self.running:
            self._shutdown_event.set()
    
    def load_config(self) -> Dict[str, Any]:
        """Load daemon configuration."""
        default_config = {
            "scheduler": {
                "enabled": True,
                "tick_interval": 60,  # seconds
                "max_concurrent_tasks": 5
            },
            "workflow": {
                "enabled": True,
                "inngest_enabled": False
            },
            "agent": {
                "model_provider": "openai",
                "model_name": "gpt-4",
                "max_context_length": 8000
            },
            "daemon": {
                "auto_restart": True,
                "health_check_interval": 300,  # seconds
                "max_memory_mb": 2048
            },
            "logging": {
                "level": "INFO",
                "max_files": 10,
                "max_size_mb": 100
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    default_config.update(user_config)
                    self.logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load config file {self.config_file}: {e}")
                self.logger.info("Using default configuration")
        else:
            self.logger.info("No config file found, using default configuration")
            # Create default config file
            try:
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                self.logger.info(f"Created default config file: {self.config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to create config file: {e}")
        
        self.config = default_config
        return default_config
    
    def create_pidfile(self) -> None:
        """Create PID file for daemon."""
        try:
            with open(self.pidfile, 'w') as f:
                f.write(str(os.getpid()))
            self.logger.info(f"Created PID file: {self.pidfile}")
        except Exception as e:
            self.logger.error(f"Failed to create PID file: {e}")
            raise
    
    def remove_pidfile(self) -> None:
        """Remove PID file."""
        try:
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
                self.logger.info(f"Removed PID file: {self.pidfile}")
        except Exception as e:
            self.logger.warning(f"Failed to remove PID file: {e}")
    
    async def initialize_components(self) -> None:
        """Initialize daemon components."""
        try:
            # Initialize task scheduler (real or lite or mock)
            try:
                from python.helpers.task_scheduler import TaskScheduler
                self.scheduler = TaskScheduler.get()
                self.logger.info("Real task scheduler initialized")
            except ImportError as e:
                self.logger.warning(f"Real task scheduler not available: {e}")
                try:
                    from python.helpers.task_scheduler_lite import TaskScheduler as LiteTaskScheduler
                    self.scheduler = LiteTaskScheduler.get()
                    self.logger.info("Lite task scheduler initialized")
                except ImportError as e2:
                    self.logger.warning(f"Lite task scheduler not available: {e2}")
                    from minimal_stubs import get_minimal_task_scheduler
                    self.scheduler = get_minimal_task_scheduler()
                    self.logger.info("Mock task scheduler initialized")
            
            # Initialize workflow manager (real or lite or mock)
            try:
                from python.helpers.task_workflow import TaskWorkflowManager
                self.workflow_manager = TaskWorkflowManager.get_instance()
                self.logger.info("Real workflow manager initialized")
            except ImportError as e:
                self.logger.warning(f"Real workflow manager not available: {e}")
                try:
                    from python.helpers.workflow_manager_lite import TaskWorkflowManager as LiteWorkflowManager
                    self.workflow_manager = LiteWorkflowManager.get_instance()
                    self.logger.info("Lite workflow manager initialized")
                except ImportError as e2:
                    self.logger.warning(f"Lite workflow manager not available: {e2}")
                    from minimal_stubs import get_minimal_workflow_manager
                    self.workflow_manager = get_minimal_workflow_manager()
                    self.logger.info("Mock workflow manager initialized")
            
            self.logger.info("Daemon components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": time.time() - self.start_time if hasattr(self, 'start_time') else 0,
            "pid": os.getpid(),
            "memory_mb": self._get_memory_usage(),
            "components": {
                "scheduler": self.scheduler is not None,
                "workflow_manager": self.workflow_manager is not None
            },
            "status": "healthy"
        }
        
        # Check memory usage
        memory_limit = self.config.get("daemon", {}).get("max_memory_mb", 2048)
        if status["memory_mb"] > memory_limit:
            status["status"] = "warning"
            status["warnings"] = [f"Memory usage ({status['memory_mb']}MB) exceeds limit ({memory_limit}MB)"]
        
        # Check component health
        if self.scheduler:
            try:
                # Basic scheduler health check
                tasks = self.scheduler.get_tasks()
                status["scheduler_tasks"] = len(tasks)
            except Exception as e:
                status["status"] = "error"
                status["errors"] = status.get("errors", []) + [f"Scheduler error: {e}"]
        
        return status
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback if psutil not available
            return 0.0
    
    async def run_scheduler_tick(self) -> None:
        """Run scheduler tick if scheduler is available."""
        if self.scheduler and self.config.get("scheduler", {}).get("enabled", True):
            try:
                await self.scheduler.tick()
                self.logger.debug("Scheduler tick completed")
            except Exception as e:
                self.logger.error(f"Scheduler tick failed: {e}")
    
    async def main_loop(self) -> None:
        """Main daemon loop."""
        self.logger.info("Starting main daemon loop")
        
        scheduler_interval = self.config.get("scheduler", {}).get("tick_interval", 60)
        health_check_interval = self.config.get("daemon", {}).get("health_check_interval", 300)
        
        last_health_check = 0
        last_scheduler_tick = 0
        
        while self.running and not self._shutdown_event.is_set():
            try:
                current_time = time.time()
                
                # Run scheduler tick
                if current_time - last_scheduler_tick >= scheduler_interval:
                    await self.run_scheduler_tick()
                    last_scheduler_tick = current_time
                
                # Run health check
                if current_time - last_health_check >= health_check_interval:
                    health_status = await self.health_check()
                    self.logger.info(f"Health check: {health_status['status']}")
                    if health_status["status"] != "healthy":
                        self.logger.warning(f"Health issues detected: {health_status}")
                    last_health_check = current_time
                
                # Sleep for a short interval
                try:
                    await asyncio.wait_for(self._shutdown_event.wait(), timeout=1.0)
                    break  # Shutdown event was set
                except asyncio.TimeoutError:
                    continue  # Continue with the loop
                    
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                if self.config.get("daemon", {}).get("auto_restart", True):
                    self.logger.info("Auto-restart enabled, continuing...")
                    await asyncio.sleep(5)  # Brief pause before retrying
                else:
                    break
        
        self.logger.info("Main daemon loop ended")
    
    async def start(self) -> None:
        """Start the daemon."""
        self.logger.info("Starting Daemon Zero...")
        self.start_time = time.time()
        
        # Load configuration
        self.load_config()
        
        # Create PID file
        self.create_pidfile()
        
        # Initialize components
        await self.initialize_components()
        
        # Set running flag
        self.running = True
        
        self.logger.info("Daemon Zero started successfully")
        
        # Run main loop
        await self.main_loop()
    
    def stop(self) -> None:
        """Stop the daemon."""
        self.logger.info("Stopping Daemon Zero...")
        self.running = False
        self._shutdown_event.set()
    
    def cleanup(self) -> None:
        """Cleanup daemon resources."""
        # Use a flag to prevent multiple cleanup calls
        if hasattr(self, '_cleaned_up') and self._cleaned_up:
            return
        
        self._cleaned_up = True
        self.logger.info("Cleaning up daemon resources...")
        self.remove_pidfile()
        self.logger.info("Daemon Zero cleanup completed")
    
    @classmethod
    def _global_cleanup(cls):
        """Global cleanup for all instances."""
        if hasattr(cls, '_instances'):
            for instance in cls._instances:
                if hasattr(instance, 'cleanup'):
                    instance.cleanup()
            cls._instances.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current daemon status."""
        if not self.running:
            return {
                "status": "stopped",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # This would normally be async, but for CLI we provide sync version
        return {
            "status": "running",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(),
            "config_file": self.config_file,
            "pidfile": self.pidfile,
            "uptime_seconds": time.time() - getattr(self, 'start_time', time.time())
        }


def read_pid_from_file(pidfile: str) -> Optional[int]:
    """Read PID from file."""
    try:
        with open(pidfile, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def is_process_running(pid: int) -> bool:
    """Check if process with given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def daemon_status(pidfile: str) -> Dict[str, Any]:
    """Get daemon status from PID file."""
    pid = read_pid_from_file(pidfile)
    if pid is None:
        return {"status": "stopped", "reason": "No PID file found"}
    
    if is_process_running(pid):
        return {
            "status": "running", 
            "pid": pid,
            "pidfile": pidfile
        }
    else:
        return {
            "status": "stopped", 
            "reason": f"Process {pid} not running",
            "stale_pidfile": pidfile
        }


def stop_daemon(pidfile: str) -> bool:
    """Stop daemon using PID file."""
    pid = read_pid_from_file(pidfile)
    if pid is None:
        print("No PID file found")
        return False
    
    if not is_process_running(pid):
        print(f"Process {pid} not running")
        # Clean up stale PID file
        try:
            os.remove(pidfile)
            print(f"Removed stale PID file: {pidfile}")
        except OSError:
            pass
        return False
    
    try:
        print(f"Stopping daemon process {pid}...")
        os.kill(pid, signal.SIGTERM)
        
        # Wait for process to stop
        for _ in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if not is_process_running(pid):
                print("Daemon stopped successfully")
                return True
        
        # Force kill if still running
        print("Force killing daemon...")
        os.kill(pid, signal.SIGKILL)
        time.sleep(2)
        
        if not is_process_running(pid):
            print("Daemon force killed")
            return True
        else:
            print("Failed to stop daemon")
            return False
            
    except OSError as e:
        print(f"Error stopping daemon: {e}")
        return False


async def main():
    """Main entry point for daemon."""
    parser = argparse.ArgumentParser(
        description="Daemon Zero - Background Agent Daemon for Agent Zero"
    )
    
    parser.add_argument(
        "command", 
        choices=["start", "stop", "restart", "status", "run"],
        help="Daemon command"
    )
    
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
        "--foreground", "-f",
        action="store_true",
        help="Run in foreground (don't daemonize)"
    )
    
    args = parser.parse_args()
    
    if args.command == "start":
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
            await daemon.start()
    
    elif args.command == "stop":
        if stop_daemon(args.pidfile):
            return 0
        else:
            return 1
    
    elif args.command == "restart":
        print("Restarting daemon...")
        stop_daemon(args.pidfile)
        time.sleep(2)
        
        daemon = DaemonZero(config_file=args.config, pidfile=args.pidfile)
        await daemon.start()
    
    elif args.command == "status":
        status = daemon_status(args.pidfile)
        print(json.dumps(status, indent=2))
        
        if status["status"] == "running":
            return 0
        else:
            return 1
    
    elif args.command == "run":
        # Run daemon in foreground for development/testing
        daemon = DaemonZero(config_file=args.config, pidfile=args.pidfile)
        await daemon.start()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
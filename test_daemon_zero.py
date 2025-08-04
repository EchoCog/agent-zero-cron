#!/usr/bin/env python3
"""
Tests for Daemon Zero functionality.

This module tests the daemon functionality including:
- Basic daemon operations (start/stop/status)
- Task scheduler integration
- CLI interface
- Configuration management
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daemon_zero import DaemonZero, daemon_status, stop_daemon
from minimal_stubs import MockTaskScheduler, MockTask, get_minimal_task_scheduler


class TestDaemonZero(unittest.TestCase):
    """Test cases for Daemon Zero functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "test_config.json")
        self.pidfile = os.path.join(self.test_dir, "test_daemon.pid")
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up PID file if it exists
        if os.path.exists(self.pidfile):
            try:
                stop_daemon(self.pidfile)
            except:
                pass
            try:
                os.remove(self.pidfile)
            except:
                pass
        
        # Clean up config file
        if os.path.exists(self.config_file):
            try:
                os.remove(self.config_file)
            except:
                pass
    
    def test_daemon_creation(self):
        """Test daemon instance creation."""
        daemon = DaemonZero(config_file=self.config_file, pidfile=self.pidfile)
        
        self.assertEqual(daemon.config_file, self.config_file)
        self.assertEqual(daemon.pidfile, self.pidfile)
        self.assertFalse(daemon.running)
        self.assertIsNotNone(daemon.logger)
    
    def test_config_loading(self):
        """Test configuration loading."""
        daemon = DaemonZero(config_file=self.config_file, pidfile=self.pidfile)
        
        # Test default config creation
        config = daemon.load_config()
        self.assertIsInstance(config, dict)
        self.assertIn("scheduler", config)
        self.assertIn("daemon", config)
        self.assertIn("agent", config)
        
        # Test config file was created
        self.assertTrue(os.path.exists(self.config_file))
        
        # Test loading existing config
        with open(self.config_file, 'w') as f:
            json.dump({"test": "value"}, f)
        
        config = daemon.load_config()
        self.assertIn("test", config)
        self.assertEqual(config["test"], "value")
    
    async def test_component_initialization(self):
        """Test daemon component initialization."""
        daemon = DaemonZero(config_file=self.config_file, pidfile=self.pidfile)
        
        await daemon.initialize_components()
        
        # Should have scheduler (mock)
        self.assertIsNotNone(daemon.scheduler)
        
        # Should have workflow manager (mock)
        self.assertIsNotNone(daemon.workflow_manager)
    
    async def test_health_check(self):
        """Test daemon health check."""
        daemon = DaemonZero(config_file=self.config_file, pidfile=self.pidfile)
        daemon.start_time = time.time()
        
        await daemon.initialize_components()
        
        health = await daemon.health_check()
        
        self.assertIsInstance(health, dict)
        self.assertIn("timestamp", health)
        self.assertIn("uptime_seconds", health)
        self.assertIn("pid", health)
        self.assertIn("status", health)
        self.assertIn("components", health)
        
        self.assertEqual(health["status"], "healthy")
        self.assertTrue(health["components"]["scheduler"])
        self.assertTrue(health["components"]["workflow_manager"])
    
    def test_daemon_status_not_running(self):
        """Test daemon status when not running."""
        status = daemon_status(self.pidfile)
        
        self.assertEqual(status["status"], "stopped")
        self.assertIn("reason", status)
    
    def test_pidfile_operations(self):
        """Test PID file creation and removal."""
        daemon = DaemonZero(config_file=self.config_file, pidfile=self.pidfile)
        
        # Test PID file creation
        daemon.create_pidfile()
        self.assertTrue(os.path.exists(self.pidfile))
        
        with open(self.pidfile, 'r') as f:
            pid = int(f.read().strip())
        self.assertEqual(pid, os.getpid())
        
        # Test PID file removal
        daemon.remove_pidfile()
        self.assertFalse(os.path.exists(self.pidfile))


class TestMockScheduler(unittest.TestCase):
    """Test cases for mock scheduler functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.scheduler = MockTaskScheduler()
    
    def test_scheduler_creation(self):
        """Test scheduler creation."""
        self.assertIsNotNone(self.scheduler)
        self.assertEqual(len(self.scheduler.get_tasks()), 0)
    
    def test_task_management(self):
        """Test task addition and retrieval."""
        task = MockTask("Test Task", "test-uuid-123")
        
        # Add task
        self.scheduler.add_task(task)
        
        # Check task list
        tasks = self.scheduler.get_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].name, "Test Task")
        self.assertEqual(tasks[0].uuid, "test-uuid-123")
        
        # Get task by UUID
        retrieved_task = self.scheduler.get_task_by_uuid("test-uuid-123")
        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task.name, "Test Task")
        
        # Get non-existent task
        non_existent = self.scheduler.get_task_by_uuid("non-existent")
        self.assertIsNone(non_existent)
    
    async def test_scheduler_tick(self):
        """Test scheduler tick functionality."""
        # Add some tasks
        task1 = MockTask("Task 1")
        task2 = MockTask("Task 2")
        
        self.scheduler.add_task(task1)
        self.scheduler.add_task(task2)
        
        # Run tick
        await self.scheduler.tick()
        
        # Should complete without error
        self.assertEqual(len(self.scheduler.get_tasks()), 2)
    
    async def test_task_execution(self):
        """Test task execution."""
        task = MockTask("Execution Test", "exec-test-123")
        self.scheduler.add_task(task)
        
        # Initially no last run
        self.assertIsNone(task.last_run)
        
        # Execute task
        await self.scheduler.run_task_by_uuid("exec-test-123")
        
        # Should have last run time
        self.assertIsNotNone(task.last_run)
        self.assertIsNotNone(task.last_result)
        self.assertEqual(task.last_result, "Mock execution completed")


class TestMinimalStubs(unittest.TestCase):
    """Test cases for minimal stub implementations."""
    
    def test_get_minimal_scheduler(self):
        """Test getting minimal scheduler."""
        scheduler = get_minimal_task_scheduler()
        self.assertIsNotNone(scheduler)
        
        # Should be mock implementation
        self.assertIsInstance(scheduler, MockTaskScheduler)
    
    def test_mock_task_creation(self):
        """Test mock task creation."""
        task = MockTask("Test Task")
        
        self.assertEqual(task.name, "Test Task")
        self.assertIsNotNone(task.uuid)
        self.assertEqual(task.state, "idle")
        self.assertIsNotNone(task.created_at)
        self.assertIsNone(task.last_run)
        self.assertIsNone(task.last_result)
    
    def test_task_schedule_check(self):
        """Test task schedule checking."""
        task = MockTask("Schedule Test")
        
        # Mock tasks don't run by default
        self.assertFalse(task.check_schedule())
        
        # Next run should be None
        self.assertIsNone(task.get_next_run())


class TestDaemonCLI(unittest.TestCase):
    """Test cases for daemon CLI functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "test_config.json")
        self.pidfile = os.path.join(self.test_dir, "test_daemon.pid")
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up files
        for file_path in [self.pidfile, self.config_file]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
    
    def test_cli_help(self):
        """Test CLI help functionality."""
        result = subprocess.run([
            sys.executable, "daemon_cli.py", "--help"
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Daemon Zero CLI", result.stdout)
        self.assertIn("daemon", result.stdout)
        self.assertIn("tasks", result.stdout)
        self.assertIn("scheduler", result.stdout)
    
    def test_cli_daemon_status(self):
        """Test CLI daemon status check."""
        result = subprocess.run([
            sys.executable, "daemon_cli.py", 
            "--pidfile", self.pidfile,
            "daemon", "status"
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("stopped", result.stdout)


def run_async_test(coro):
    """Helper to run async tests."""
    return asyncio.run(coro)


class AsyncTestCase(unittest.TestCase):
    """Base class for async tests."""
    
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        self.loop.close()
    
    def async_test(self, coro):
        return self.loop.run_until_complete(coro)


def main():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestDaemonZero))
    suite.addTests(loader.loadTestsFromTestCase(TestMockScheduler))
    suite.addTests(loader.loadTestsFromTestCase(TestMinimalStubs))
    suite.addTests(loader.loadTestsFromTestCase(TestDaemonCLI))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    # Handle async tests
    import types
    
    # Patch TestDaemonZero methods to run async tests
    test_methods = [
        "test_component_initialization",
        "test_health_check"
    ]
    
    for method_name in test_methods:
        if hasattr(TestDaemonZero, method_name):
            original_method = getattr(TestDaemonZero, method_name)
            if asyncio.iscoroutinefunction(original_method):
                def make_sync_wrapper(async_method):
                    def sync_wrapper(self):
                        return asyncio.run(async_method(self))
                    return sync_wrapper
                
                setattr(TestDaemonZero, method_name, make_sync_wrapper(original_method))
    
    # Same for TestMockScheduler
    test_methods = [
        "test_scheduler_tick",
        "test_task_execution"
    ]
    
    for method_name in test_methods:
        if hasattr(TestMockScheduler, method_name):
            original_method = getattr(TestMockScheduler, method_name)
            if asyncio.iscoroutinefunction(original_method):
                def make_sync_wrapper(async_method):
                    def sync_wrapper(self):
                        return asyncio.run(async_method(self))
                    return sync_wrapper
                
                setattr(TestMockScheduler, method_name, make_sync_wrapper(original_method))
    
    exit_code = main()
    sys.exit(exit_code)
"""
Minimal stub implementations to allow daemon functionality without full dependencies.
This allows the daemon to run with basic functionality even when some dependencies are missing.
"""

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union


class PrintStyle:
    """Minimal PrintStyle implementation."""
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    def print(self, message: str) -> None:
        """Print message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def stream(self, message: str) -> None:
        """Stream message."""
        print(message, end='', flush=True)


class MockTask:
    """Mock task for testing when real TaskScheduler is not available."""
    
    def __init__(self, name: str, uuid: str = None):
        self.name = name
        self.uuid = uuid or f"mock-{int(time.time())}"
        self.state = "idle"
        self.created_at = datetime.now(timezone.utc)
        self.last_run = None
        self.last_result = None
    
    def check_schedule(self) -> bool:
        """Mock schedule check."""
        return False
    
    def get_next_run(self) -> Optional[datetime]:
        """Mock next run time."""
        return None


class MockTaskScheduler:
    """Mock TaskScheduler for testing when real one is not available."""
    
    def __init__(self):
        self.tasks = []
        self._printer = PrintStyle()
    
    @classmethod
    def get(cls):
        """Get singleton instance."""
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
    
    def get_tasks(self) -> List[MockTask]:
        """Get all tasks."""
        return self.tasks
    
    def get_task_by_uuid(self, uuid: str) -> Optional[MockTask]:
        """Get task by UUID."""
        for task in self.tasks:
            if task.uuid == uuid:
                return task
        return None
    
    def add_task(self, task: MockTask) -> None:
        """Add a task."""
        self.tasks.append(task)
        self._printer.print(f"Added mock task: {task.name}")
    
    async def tick(self) -> None:
        """Run scheduler tick."""
        self._printer.print(f"Mock scheduler tick - {len(self.tasks)} tasks")
        
        # Mock task execution
        for task in self.tasks:
            if task.check_schedule():
                self._printer.print(f"Would execute task: {task.name}")
                task.last_run = datetime.now(timezone.utc)
                task.last_result = "Mock execution completed"
    
    async def run_task_by_uuid(self, uuid: str, context: str = None) -> None:
        """Mock task execution."""
        task = self.get_task_by_uuid(uuid)
        if task:
            self._printer.print(f"Mock executing task: {task.name}")
            task.last_run = datetime.now(timezone.utc)
            task.last_result = "Mock execution completed"
        else:
            raise ValueError(f"Task {uuid} not found")


class MockWorkflowManager:
    """Mock workflow manager for testing."""
    
    def __init__(self):
        self._printer = PrintStyle()
    
    @classmethod
    def get_instance(cls, config=None):
        """Get singleton instance."""
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
    
    def get_status(self) -> Dict[str, Any]:
        """Get workflow manager status."""
        return {
            "enabled": False,
            "type": "mock",
            "workflows": 0
        }
    
    async def create_workflow(self, workflow_id: str, definition: Dict[str, Any]) -> bool:
        """Mock workflow creation."""
        self._printer.print(f"Mock creating workflow: {workflow_id}")
        return True


def get_minimal_task_scheduler():
    """Get task scheduler - real if available, mock otherwise."""
    try:
        from python.helpers.task_scheduler import TaskScheduler
        return TaskScheduler.get()
    except ImportError:
        return MockTaskScheduler.get()


def get_minimal_workflow_manager():
    """Get workflow manager - real if available, mock otherwise."""
    try:
        from python.helpers.task_workflow import TaskWorkflowManager
        return TaskWorkflowManager.get_instance()
    except ImportError:
        return MockWorkflowManager.get_instance()


def get_minimal_print_style(*args, **kwargs):
    """Get PrintStyle - real if available, mock otherwise."""
    try:
        from python.helpers.print_style import PrintStyle
        return PrintStyle(*args, **kwargs)
    except ImportError:
        return PrintStyle(*args, **kwargs)
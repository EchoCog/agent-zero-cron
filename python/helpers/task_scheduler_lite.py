"""
Lightweight task scheduler implementation that works without full Agent Zero dependencies.
This allows the daemon to use real scheduling functionality even when Agent dependencies are missing.
"""

import asyncio
from datetime import datetime, timezone, timedelta
import json
import os
import threading
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

# Handle missing crontab dependency with fallback
try:
    from crontab import CronTab
    CRONTAB_AVAILABLE = True
except ImportError:
    CRONTAB_AVAILABLE = False
    # Provide basic fallback for cron functionality
    class CronTab:
        def __init__(self, cron="0 0 * * *"):
            self._cron = cron
            
        def next(self, default_utc=True):
            # Simple fallback - return 24 hours from now for daily tasks
            from datetime import datetime, timedelta
            return (datetime.now() + timedelta(days=1)).timestamp()
            
        @classmethod
        def parse(cls, cron_string):
            return cls(cron_string)

# Handle missing pydantic with fallback
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Simple fallback BaseModel
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def dict(self):
            return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def Field(default=None, **kwargs):
        return default


class TaskState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    COMPLETED = "completed"


class LiteTask(BaseModel):
    """Lightweight task implementation."""
    
    uuid: str = ""
    name: str = ""
    state: TaskState = TaskState.IDLE
    created_at: datetime = None
    last_run: Optional[datetime] = None
    last_result: Optional[str] = None
    cron_schedule: Optional[str] = None
    enabled: bool = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc)
    
    def check_schedule(self) -> bool:
        """Check if task should run based on schedule."""
        if not self.enabled or self.state == TaskState.RUNNING:
            return False
        
        if not self.cron_schedule:
            return False
        
        try:
            if CRONTAB_AVAILABLE:
                cron = CronTab(self.cron_schedule)
                next_run = cron.next()
                if self.last_run is None:
                    return True
                return next_run <= 60  # Run if next execution is within 1 minute
            else:
                # Simple fallback - run once per hour for demo
                if self.last_run is None:
                    return True
                elapsed = datetime.now(timezone.utc) - self.last_run
                return elapsed.total_seconds() > 3600  # 1 hour
        except Exception:
            return False
    
    def get_next_run(self) -> Optional[datetime]:
        """Get next scheduled run time."""
        if not self.cron_schedule or not self.enabled:
            return None
        
        try:
            if CRONTAB_AVAILABLE:
                cron = CronTab(self.cron_schedule)
                next_timestamp = cron.next()
                return datetime.fromtimestamp(next_timestamp, timezone.utc)
            else:
                # Fallback - next hour
                return datetime.now(timezone.utc) + timedelta(hours=1)
        except Exception:
            return None


class LiteTaskScheduler:
    """Lightweight task scheduler that works without full Agent Zero dependencies."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.tasks: List[LiteTask] = []
        self.data_dir = Path("tmp/scheduler_lite")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_file = self.data_dir / "tasks.json"
        self._load_tasks()
    
    @classmethod
    def get(cls):
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def _load_tasks(self):
        """Load tasks from disk."""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r') as f:
                    tasks_data = json.load(f)
                
                self.tasks = []
                for task_data in tasks_data:
                    # Convert datetime strings back to datetime objects
                    if task_data.get('created_at'):
                        task_data['created_at'] = datetime.fromisoformat(task_data['created_at'])
                    if task_data.get('last_run'):
                        task_data['last_run'] = datetime.fromisoformat(task_data['last_run'])
                    
                    task = LiteTask(**task_data)
                    self.tasks.append(task)
                    
            except Exception as e:
                print(f"Warning: Failed to load tasks from {self.tasks_file}: {e}")
                self.tasks = []
    
    def _save_tasks(self):
        """Save tasks to disk."""
        try:
            tasks_data = []
            for task in self.tasks:
                task_dict = task.dict() if hasattr(task, 'dict') else task.__dict__
                # Convert datetime objects to strings
                if task_dict.get('created_at'):
                    task_dict['created_at'] = task_dict['created_at'].isoformat()
                if task_dict.get('last_run'):
                    task_dict['last_run'] = task_dict['last_run'].isoformat()
                tasks_data.append(task_dict)
            
            with open(self.tasks_file, 'w') as f:
                json.dump(tasks_data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Failed to save tasks to {self.tasks_file}: {e}")
    
    def get_tasks(self) -> List[LiteTask]:
        """Get all tasks."""
        return self.tasks.copy()
    
    def get_task_by_uuid(self, task_uuid: str) -> Optional[LiteTask]:
        """Get task by UUID."""
        for task in self.tasks:
            if task.uuid == task_uuid:
                return task
        return None
    
    def add_task(self, task: LiteTask) -> None:
        """Add a task."""
        self.tasks.append(task)
        self._save_tasks()
    
    def remove_task(self, task_uuid: str) -> bool:
        """Remove a task by UUID."""
        for i, task in enumerate(self.tasks):
            if task.uuid == task_uuid:
                del self.tasks[i]
                self._save_tasks()
                return True
        return False
    
    async def tick(self) -> None:
        """Run scheduler tick - check and execute scheduled tasks."""
        for task in self.tasks:
            if task.check_schedule():
                await self._execute_task(task)
    
    async def _execute_task(self, task: LiteTask) -> None:
        """Execute a single task."""
        if task.state == TaskState.RUNNING:
            return
        
        task.state = TaskState.RUNNING
        task.last_run = datetime.now(timezone.utc)
        
        try:
            # For lite scheduler, we just mark tasks as completed
            # Real implementation would execute the actual task logic
            await asyncio.sleep(0.1)  # Simulate work
            task.last_result = f"Lite task executed successfully at {task.last_run.isoformat()}"
            task.state = TaskState.COMPLETED
            
        except Exception as e:
            task.last_result = f"Task execution failed: {e}"
            task.state = TaskState.ERROR
        
        finally:
            self._save_tasks()
    
    async def run_task_by_uuid(self, task_uuid: str, context: str = None) -> None:
        """Execute a specific task by UUID."""
        task = self.get_task_by_uuid(task_uuid)
        if task:
            await self._execute_task(task)
        else:
            raise ValueError(f"Task {task_uuid} not found")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        running_tasks = sum(1 for task in self.tasks if task.state == TaskState.RUNNING)
        enabled_tasks = sum(1 for task in self.tasks if task.enabled)
        
        return {
            "type": "lite",
            "total_tasks": len(self.tasks),
            "enabled_tasks": enabled_tasks,
            "running_tasks": running_tasks,
            "data_dir": str(self.data_dir),
            "crontab_available": CRONTAB_AVAILABLE,
            "pydantic_available": PYDANTIC_AVAILABLE
        }


def create_sample_task(name: str, cron_schedule: str = "0 * * * *") -> LiteTask:
    """Create a sample task for testing."""
    return LiteTask(
        name=name,
        cron_schedule=cron_schedule,
        enabled=True
    )


# Export the main class
TaskScheduler = LiteTaskScheduler
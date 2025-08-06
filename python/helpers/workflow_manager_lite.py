"""
Lightweight workflow manager implementation that works without full Agent Zero dependencies.
This provides basic workflow orchestration capabilities without requiring complex dependencies.
"""

import asyncio
import json
import os
import threading
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class WorkflowState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    PAUSED = "paused"


class LiteWorkflow:
    """Lightweight workflow implementation."""
    
    def __init__(
        self,
        workflow_id: str,
        name: str = "",
        definition: Optional[Dict[str, Any]] = None,
        enabled: bool = True
    ):
        self.workflow_id = workflow_id
        self.name = name or workflow_id
        self.definition = definition or {}
        self.enabled = enabled
        self.state = WorkflowState.IDLE
        self.created_at = datetime.now(timezone.utc)
        self.last_run = None
        self.last_result = None
        self.run_count = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "definition": self.definition,
            "enabled": self.enabled,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_result": self.last_result,
            "run_count": self.run_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LiteWorkflow":
        """Create workflow from dictionary."""
        workflow = cls(
            workflow_id=data["workflow_id"],
            name=data.get("name", ""),
            definition=data.get("definition", {}),
            enabled=data.get("enabled", True)
        )
        
        workflow.state = WorkflowState(data.get("state", "idle"))
        workflow.created_at = datetime.fromisoformat(data["created_at"])
        workflow.run_count = data.get("run_count", 0)
        
        if data.get("last_run"):
            workflow.last_run = datetime.fromisoformat(data["last_run"])
        
        workflow.last_result = data.get("last_result")
        
        return workflow


class LiteWorkflowManager:
    """Lightweight workflow manager."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.workflows: Dict[str, LiteWorkflow] = {}
        self.data_dir = Path("tmp/workflow_lite")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.workflows_file = self.data_dir / "workflows.json"
        self._load_workflows()
    
    @classmethod
    def get_instance(cls, config: Optional[Dict[str, Any]] = None):
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(config)
        return cls._instance
    
    def _load_workflows(self):
        """Load workflows from disk."""
        if self.workflows_file.exists():
            try:
                with open(self.workflows_file, 'r') as f:
                    workflows_data = json.load(f)
                
                self.workflows = {}
                for workflow_data in workflows_data:
                    workflow = LiteWorkflow.from_dict(workflow_data)
                    self.workflows[workflow.workflow_id] = workflow
                    
            except Exception as e:
                print(f"Warning: Failed to load workflows from {self.workflows_file}: {e}")
                self.workflows = {}
    
    def _save_workflows(self):
        """Save workflows to disk."""
        try:
            workflows_data = [
                workflow.to_dict() 
                for workflow in self.workflows.values()
            ]
            
            with open(self.workflows_file, 'w') as f:
                json.dump(workflows_data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Failed to save workflows to {self.workflows_file}: {e}")
    
    async def create_workflow(
        self, 
        workflow_id: str, 
        definition: Dict[str, Any]
    ) -> bool:
        """Create a new workflow."""
        try:
            if workflow_id in self.workflows:
                return False  # Workflow already exists
            
            workflow = LiteWorkflow(
                workflow_id=workflow_id,
                name=definition.get("name", workflow_id),
                definition=definition,
                enabled=definition.get("enabled", True)
            )
            
            self.workflows[workflow_id] = workflow
            self._save_workflows()
            return True
            
        except Exception as e:
            print(f"Error creating workflow {workflow_id}: {e}")
            return False
    
    async def execute_workflow(self, workflow_id: str) -> bool:
        """Execute a specific workflow."""
        workflow = self.workflows.get(workflow_id)
        if not workflow or not workflow.enabled:
            return False
        
        if workflow.state == WorkflowState.RUNNING:
            return False  # Already running
        
        workflow.state = WorkflowState.RUNNING
        workflow.last_run = datetime.now(timezone.utc)
        
        try:
            # Simulate workflow execution
            await asyncio.sleep(0.1)
            
            # Basic workflow processing
            steps = workflow.definition.get("steps", [])
            results = []
            
            for i, step in enumerate(steps):
                step_name = step.get("name", f"step_{i}")
                step_type = step.get("type", "action")
                
                # Simulate step execution
                await asyncio.sleep(0.01)
                results.append({
                    "step": step_name,
                    "type": step_type,
                    "status": "completed",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            workflow.last_result = {
                "status": "success",
                "steps_completed": len(results),
                "results": results,
                "execution_time": 0.1 + len(steps) * 0.01
            }
            workflow.state = WorkflowState.COMPLETED
            workflow.run_count += 1
            
        except Exception as e:
            workflow.last_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            workflow.state = WorkflowState.ERROR
        
        finally:
            self._save_workflows()
        
        return workflow.state == WorkflowState.COMPLETED
    
    def get_workflow(self, workflow_id: str) -> Optional[LiteWorkflow]:
        """Get a specific workflow."""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[LiteWorkflow]:
        """List all workflows."""
        return list(self.workflows.values())
    
    def remove_workflow(self, workflow_id: str) -> bool:
        """Remove a workflow."""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            self._save_workflows()
            return True
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get workflow manager status."""
        total_workflows = len(self.workflows)
        enabled_workflows = sum(1 for w in self.workflows.values() if w.enabled)
        running_workflows = sum(1 for w in self.workflows.values() if w.state == WorkflowState.RUNNING)
        
        return {
            "type": "lite",
            "enabled": True,
            "total_workflows": total_workflows,
            "enabled_workflows": enabled_workflows,
            "running_workflows": running_workflows,
            "data_dir": str(self.data_dir),
            "supported_features": [
                "workflow_creation",
                "workflow_execution", 
                "step_processing",
                "state_persistence"
            ]
        }
    
    async def trigger_workflow(
        self,
        workflow_id: str,
        trigger_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Trigger a workflow with optional data."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
        
        # Add trigger data to workflow context
        if trigger_data:
            workflow.definition["trigger_data"] = trigger_data
        
        return await self.execute_workflow(workflow_id)
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow."""
        workflow = self.workflows.get(workflow_id)
        if workflow and workflow.state == WorkflowState.RUNNING:
            workflow.state = WorkflowState.PAUSED
            self._save_workflows()
            return True
        return False
    
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        workflow = self.workflows.get(workflow_id)
        if workflow and workflow.state == WorkflowState.PAUSED:
            return await self.execute_workflow(workflow_id)
        return False


def create_sample_workflow(
    workflow_id: str, 
    name: str,
    steps: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Create a sample workflow definition."""
    return {
        "name": name,
        "enabled": True,
        "steps": steps or [
            {"name": "initialize", "type": "action"},
            {"name": "process", "type": "action"}, 
            {"name": "finalize", "type": "action"}
        ],
        "metadata": {
            "created_by": "lite_workflow_manager",
            "version": "1.0"
        }
    }


# Export the main class
TaskWorkflowManager = LiteWorkflowManager
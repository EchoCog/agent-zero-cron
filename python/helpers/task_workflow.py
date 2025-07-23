"""
Task workflow integration with Inngest.

This module provides workflow orchestration capabilities by integrating
the existing TaskScheduler with Inngest event-driven workflows.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List, Callable, Union

from python.helpers.task_scheduler import (
    TaskScheduler, BaseTask, ScheduledTask, AdHocTask, PlannedTask,
    TaskState, serialize_task, deserialize_task
)
from python.helpers.inngest_client import InngestManager, InngestConfig, get_inngest_manager
from python.helpers.print_style import PrintStyle


class TaskWorkflowManager:
    """
    Manages workflow orchestration for Agent Zero tasks using Inngest.
    
    This class bridges the existing TaskScheduler with Inngest's event-driven
    workflow system, enabling complex task orchestration patterns.
    """
    
    _instance: Optional['TaskWorkflowManager'] = None
    
    def __init__(self, inngest_config: Optional[InngestConfig] = None):
        self.inngest_manager = get_inngest_manager(inngest_config)
        self.task_scheduler = TaskScheduler.get()
        self._printer = PrintStyle(italic=True, font_color="blue", padding=False)
        self._setup_workflow_functions()
    
    @classmethod
    def get_instance(cls, inngest_config: Optional[InngestConfig] = None) -> 'TaskWorkflowManager':
        """Get singleton instance of TaskWorkflowManager."""
        if cls._instance is None:
            cls._instance = cls(inngest_config)
        return cls._instance
    
    def _setup_workflow_functions(self):
        """Set up Inngest workflow functions for task orchestration."""
        if not self.inngest_manager.is_enabled():
            self._printer.print("Inngest not enabled, skipping workflow function setup")
            return
        
        # Task execution workflow
        self.inngest_manager.create_function(
            fn_id="task-executor",
            name="Task Executor",
            trigger="task/execute",
            handler=self._handle_task_execution
        )
        
        # Task completion workflow
        self.inngest_manager.create_function(
            fn_id="task-completion",
            name="Task Completion Handler",
            trigger="task/completed",
            handler=self._handle_task_completion
        )
        
        # Task failure workflow
        self.inngest_manager.create_function(
            fn_id="task-failure",
            name="Task Failure Handler", 
            trigger="task/failed",
            handler=self._handle_task_failure
        )
        
        # Workflow orchestration
        self.inngest_manager.create_function(
            fn_id="workflow-orchestrator",
            name="Workflow Orchestrator",
            trigger="workflow/start",
            handler=self._handle_workflow_orchestration
        )
        
        self._printer.print("Inngest workflow functions registered")
    
    async def _handle_task_execution(self, ctx: Any, step: Any) -> Dict[str, Any]:
        """Handle task execution workflow."""
        try:
            event_data = ctx.event.data
            task_uuid = event_data.get("task_uuid")
            task_context = event_data.get("task_context")
            
            if not task_uuid:
                raise ValueError("task_uuid is required for task execution")
            
            self._printer.print(f"Inngest executing task: {task_uuid}")
            
            # Execute the task using existing scheduler
            await self.task_scheduler.run_task_by_uuid(task_uuid, task_context)
            
            # Send completion event
            await self.inngest_manager.send_event(
                "task/started",
                {
                    "task_uuid": task_uuid,
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "workflow_id": event_data.get("workflow_id")
                }
            )
            
            return {"status": "started", "task_uuid": task_uuid}
            
        except Exception as e:
            error_msg = str(e)
            self._printer.print(f"Task execution failed: {error_msg}")
            
            # Send failure event
            await self.inngest_manager.send_event(
                "task/failed",
                {
                    "task_uuid": task_uuid if 'task_uuid' in locals() else None,
                    "error": error_msg,
                    "failed_at": datetime.now(timezone.utc).isoformat(),
                    "workflow_id": event_data.get("workflow_id") if 'event_data' in locals() else None
                }
            )
            
            raise
    
    async def _handle_task_completion(self, ctx: Any, step: Any) -> Dict[str, Any]:
        """Handle task completion workflow."""
        event_data = ctx.event.data
        task_uuid = event_data.get("task_uuid")
        workflow_id = event_data.get("workflow_id")
        
        self._printer.print(f"Task completed: {task_uuid}")
        
        # Get updated task status
        task = self.task_scheduler.get_task_by_uuid(task_uuid)
        
        result = {
            "task_uuid": task_uuid,
            "workflow_id": workflow_id,
            "completed_at": event_data.get("completed_at"),
            "task_state": task.state if task else "unknown",
            "last_result": task.last_result if task else None
        }
        
        # Trigger next workflow steps if part of a larger workflow
        if workflow_id:
            await self.inngest_manager.send_event(
                "workflow/step-completed",
                {
                    "workflow_id": workflow_id,
                    "step_type": "task",
                    "step_id": task_uuid,
                    "result": result
                }
            )
        
        return result
    
    async def _handle_task_failure(self, ctx: Any, step: Any) -> Dict[str, Any]:
        """Handle task failure workflow."""
        event_data = ctx.event.data
        task_uuid = event_data.get("task_uuid")
        workflow_id = event_data.get("workflow_id")
        error = event_data.get("error")
        
        self._printer.print(f"Task failed: {task_uuid} - {error}")
        
        result = {
            "task_uuid": task_uuid,
            "workflow_id": workflow_id,
            "failed_at": event_data.get("failed_at"),
            "error": error
        }
        
        # Trigger workflow failure handling if part of a larger workflow
        if workflow_id:
            await self.inngest_manager.send_event(
                "workflow/step-failed",
                {
                    "workflow_id": workflow_id,
                    "step_type": "task",
                    "step_id": task_uuid,
                    "error": error
                }
            )
        
        return result
    
    async def _handle_workflow_orchestration(self, ctx: Any, step: Any) -> Dict[str, Any]:
        """Handle workflow orchestration."""
        event_data = ctx.event.data
        workflow_id = event_data.get("workflow_id")
        workflow_definition = event_data.get("workflow_definition", {})
        workflow_input = event_data.get("workflow_input", {})
        
        self._printer.print(f"Starting workflow: {workflow_id}")
        
        # Execute workflow steps
        results = []
        for step_config in workflow_definition.get("steps", []):
            step_result = await self._execute_workflow_step(
                workflow_id, step_config, workflow_input, results
            )
            results.append(step_result)
        
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "results": results,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _execute_workflow_step(
        self,
        workflow_id: str,
        step_config: Dict[str, Any],
        workflow_input: Dict[str, Any],
        previous_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step_type = step_config.get("type")
        step_id = step_config.get("id")
        
        if step_type == "task":
            # Execute a task step
            task_uuid = step_config.get("task_uuid")
            if not task_uuid:
                raise ValueError(f"task_uuid required for task step: {step_id}")
            
            await self.inngest_manager.send_event(
                "task/execute",
                {
                    "task_uuid": task_uuid,
                    "workflow_id": workflow_id,
                    "step_id": step_id,
                    "workflow_input": workflow_input
                }
            )
            
            return {
                "step_id": step_id,
                "step_type": step_type,
                "task_uuid": task_uuid,
                "status": "triggered"
            }
        
        elif step_type == "delay":
            # Delay step
            delay_seconds = step_config.get("delay_seconds", 0)
            await asyncio.sleep(delay_seconds)
            
            return {
                "step_id": step_id,
                "step_type": step_type,
                "delay_seconds": delay_seconds,
                "status": "completed"
            }
        
        elif step_type == "conditional":
            # Conditional step
            condition = step_config.get("condition", {})
            # Simple condition evaluation (can be extended)
            condition_met = self._evaluate_condition(condition, workflow_input, previous_results)
            
            if condition_met:
                next_steps = step_config.get("if_true", [])
            else:
                next_steps = step_config.get("if_false", [])
            
            # Execute conditional steps
            conditional_results = []
            for substep in next_steps:
                substep_result = await self._execute_workflow_step(
                    workflow_id, substep, workflow_input, previous_results
                )
                conditional_results.append(substep_result)
            
            return {
                "step_id": step_id,
                "step_type": step_type,
                "condition_met": condition_met,
                "results": conditional_results,
                "status": "completed"
            }
        
        else:
            raise ValueError(f"Unknown workflow step type: {step_type}")
    
    def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        workflow_input: Dict[str, Any],
        previous_results: List[Dict[str, Any]]
    ) -> bool:
        """Evaluate a workflow condition."""
        # Simple condition evaluation - can be extended for complex logic
        condition_type = condition.get("type", "always_true")
        
        if condition_type == "always_true":
            return True
        elif condition_type == "always_false":
            return False
        elif condition_type == "input_contains":
            key = condition.get("key")
            value = condition.get("value")
            return workflow_input.get(key) == value
        elif condition_type == "previous_step_success":
            step_id = condition.get("step_id")
            for result in previous_results:
                if result.get("step_id") == step_id:
                    return result.get("status") == "completed"
            return False
        
        return True
    
    async def create_workflow(
        self,
        workflow_id: str,
        workflow_definition: Dict[str, Any],
        workflow_input: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create and trigger a workflow.
        
        Args:
            workflow_id: Unique workflow identifier
            workflow_definition: Workflow configuration
            workflow_input: Input data for the workflow
            
        Returns:
            True if workflow was created successfully
        """
        if not self.inngest_manager.is_enabled():
            self._printer.print("Inngest not enabled, cannot create workflow")
            return False
        
        return await self.inngest_manager.send_event(
            "workflow/start",
            {
                "workflow_id": workflow_id,
                "workflow_definition": workflow_definition,
                "workflow_input": workflow_input or {},
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def execute_task_workflow(
        self,
        task_uuid: str,
        task_context: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> bool:
        """
        Execute a task through Inngest workflow.
        
        Args:
            task_uuid: Task to execute
            task_context: Optional task context
            workflow_id: Optional workflow ID for orchestration
            
        Returns:
            True if task workflow was triggered successfully
        """
        if not self.inngest_manager.is_enabled():
            # Fall back to direct task execution
            await self.task_scheduler.run_task_by_uuid(task_uuid, task_context)
            return True
        
        return await self.inngest_manager.send_event(
            "task/execute",
            {
                "task_uuid": task_uuid,
                "task_context": task_context,
                "workflow_id": workflow_id,
                "triggered_at": datetime.now(timezone.utc).isoformat()
            }
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get workflow manager status."""
        return {
            "inngest_enabled": self.inngest_manager.is_enabled(),
            "inngest_status": self.inngest_manager.get_status(),
            "workflow_functions": self.inngest_manager.list_functions()
        }


# Global helper function
def get_task_workflow_manager(inngest_config: Optional[InngestConfig] = None) -> TaskWorkflowManager:
    """Get the global task workflow manager instance."""
    return TaskWorkflowManager.get_instance(inngest_config)
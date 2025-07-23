"""
Inngest workflow orchestration tool for Agent Zero.

This tool provides workflow orchestration capabilities using Inngest,
extending the existing task scheduling functionality.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from python.helpers.tool import Tool, Response
from python.helpers.task_scheduler import TaskScheduler, serialize_task
from python.helpers.inngest_client import get_inngest_manager, InngestConfig, create_default_config
from python.helpers.task_workflow import get_task_workflow_manager


class InngestTool(Tool):
    """
    Tool for Inngest workflow orchestration.
    
    Methods:
    - status: Get Inngest and workflow manager status
    - send_event: Send an event to Inngest
    - create_workflow: Create and trigger a workflow
    - execute_task_workflow: Execute a task through Inngest workflow
    - list_functions: List registered Inngest functions
    - trigger_workflow: Trigger a predefined workflow
    """

    async def execute(self, **kwargs):
        if self.method == "status":
            return await self.get_status(**kwargs)
        elif self.method == "send_event":
            return await self.send_event(**kwargs)
        elif self.method == "create_workflow":
            return await self.create_workflow(**kwargs)
        elif self.method == "execute_task_workflow":
            return await self.execute_task_workflow(**kwargs)
        elif self.method == "list_functions":
            return await self.list_functions(**kwargs)
        elif self.method == "trigger_workflow":
            return await self.trigger_workflow(**kwargs)
        else:
            return Response(message=f"Unknown method '{self.name}:{self.method}'", break_loop=False)

    async def get_status(self, **kwargs) -> Response:
        """Get Inngest and workflow manager status."""
        try:
            # Get Inngest manager
            inngest_manager = get_inngest_manager()
            
            # Get workflow manager
            workflow_manager = get_task_workflow_manager()
            
            status = {
                "inngest": inngest_manager.get_status(),
                "workflow_manager": workflow_manager.get_status(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return Response(
                message=json.dumps(status, indent=2),
                break_loop=False
            )
            
        except Exception as e:
            return Response(
                message=f"Error getting Inngest status: {str(e)}",
                break_loop=False
            )

    async def send_event(self, **kwargs) -> Response:
        """
        Send an event to Inngest.
        
        Args:
            name: Event name (required)
            data: Event data (dict, required)
            user: Optional user context (dict)
            ts: Optional timestamp (int)
        """
        try:
            name = kwargs.get("name")
            data = kwargs.get("data")
            user = kwargs.get("user")
            ts = kwargs.get("ts")
            
            if not name:
                return Response(message="Event name is required", break_loop=False)
            
            if not data:
                return Response(message="Event data is required", break_loop=False)
            
            if not isinstance(data, dict):
                return Response(message="Event data must be a dictionary", break_loop=False)
            
            # Get Inngest manager
            inngest_manager = get_inngest_manager()
            
            if not inngest_manager.is_enabled():
                return Response(
                    message="Inngest is not enabled. Check configuration and INNGEST_EVENT_KEY.",
                    break_loop=False
                )
            
            # Send event
            success = await inngest_manager.send_event(name, data, user, ts)
            
            if success:
                return Response(
                    message=f"Event '{name}' sent successfully to Inngest",
                    break_loop=False
                )
            else:
                return Response(
                    message=f"Failed to send event '{name}' to Inngest",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"Error sending event: {str(e)}",
                break_loop=False
            )

    async def create_workflow(self, **kwargs) -> Response:
        """
        Create and trigger a workflow.
        
        Args:
            workflow_id: Unique workflow identifier (optional, auto-generated if not provided)
            workflow_definition: Workflow configuration (dict, required)
            workflow_input: Input data for the workflow (dict, optional)
        """
        try:
            workflow_id = kwargs.get("workflow_id") or str(uuid.uuid4())
            workflow_definition = kwargs.get("workflow_definition")
            workflow_input = kwargs.get("workflow_input", {})
            
            if not workflow_definition:
                return Response(message="Workflow definition is required", break_loop=False)
            
            if not isinstance(workflow_definition, dict):
                return Response(message="Workflow definition must be a dictionary", break_loop=False)
            
            # Get workflow manager
            workflow_manager = get_task_workflow_manager()
            
            # Create workflow
            success = await workflow_manager.create_workflow(
                workflow_id, workflow_definition, workflow_input
            )
            
            if success:
                return Response(
                    message=f"Workflow '{workflow_id}' created and triggered successfully",
                    break_loop=False
                )
            else:
                return Response(
                    message=f"Failed to create workflow '{workflow_id}'",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"Error creating workflow: {str(e)}",
                break_loop=False
            )

    async def execute_task_workflow(self, **kwargs) -> Response:
        """
        Execute a task through Inngest workflow.
        
        Args:
            task_uuid: Task UUID to execute (required)
            task_context: Optional task context (string)
            workflow_id: Optional workflow ID for orchestration (string)
        """
        try:
            task_uuid = kwargs.get("task_uuid")
            task_context = kwargs.get("task_context")
            workflow_id = kwargs.get("workflow_id")
            
            if not task_uuid:
                return Response(message="Task UUID is required", break_loop=False)
            
            # Verify task exists
            task_scheduler = TaskScheduler.get()
            task = task_scheduler.get_task_by_uuid(task_uuid)
            if not task:
                return Response(message=f"Task not found: {task_uuid}", break_loop=False)
            
            # Get workflow manager
            workflow_manager = get_task_workflow_manager()
            
            # Execute task workflow
            success = await workflow_manager.execute_task_workflow(
                task_uuid, task_context, workflow_id
            )
            
            if success:
                message = f"Task '{task.name}' ({task_uuid}) triggered through Inngest workflow"
                if workflow_id:
                    message += f" as part of workflow {workflow_id}"
                
                # Break loop if task is running in the same context
                break_loop = task.context_id == self.agent.context.id
                
                return Response(message=message, break_loop=break_loop)
            else:
                return Response(
                    message=f"Failed to trigger task workflow for {task_uuid}",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"Error executing task workflow: {str(e)}",
                break_loop=False
            )

    async def list_functions(self, **kwargs) -> Response:
        """List registered Inngest functions."""
        try:
            # Get Inngest manager
            inngest_manager = get_inngest_manager()
            
            if not inngest_manager.is_enabled():
                return Response(
                    message="Inngest is not enabled. No functions available.",
                    break_loop=False
                )
            
            functions = inngest_manager.list_functions()
            
            result = {
                "functions": functions,
                "count": len(functions),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return Response(
                message=json.dumps(result, indent=2),
                break_loop=False
            )
            
        except Exception as e:
            return Response(
                message=f"Error listing functions: {str(e)}",
                break_loop=False
            )

    async def trigger_workflow(self, **kwargs) -> Response:
        """
        Trigger a predefined workflow.
        
        Args:
            workflow_name: Name of the workflow to trigger (required)
            data: Workflow input data (dict, required)
            delay_seconds: Optional delay before execution (int)
        """
        try:
            workflow_name = kwargs.get("workflow_name")
            data = kwargs.get("data")
            delay_seconds = kwargs.get("delay_seconds")
            
            if not workflow_name:
                return Response(message="Workflow name is required", break_loop=False)
            
            if not data:
                return Response(message="Workflow data is required", break_loop=False)
            
            if not isinstance(data, dict):
                return Response(message="Workflow data must be a dictionary", break_loop=False)
            
            # Get Inngest manager
            inngest_manager = get_inngest_manager()
            
            if not inngest_manager.is_enabled():
                return Response(
                    message="Inngest is not enabled. Cannot trigger workflow.",
                    break_loop=False
                )
            
            # Trigger workflow
            success = await inngest_manager.trigger_workflow(
                workflow_name, data, delay_seconds
            )
            
            if success:
                message = f"Workflow '{workflow_name}' triggered successfully"
                if delay_seconds:
                    message += f" with {delay_seconds}s delay"
                
                return Response(message=message, break_loop=False)
            else:
                return Response(
                    message=f"Failed to trigger workflow '{workflow_name}'",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"Error triggering workflow: {str(e)}",
                break_loop=False
            )
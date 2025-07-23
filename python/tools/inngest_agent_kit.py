"""
Enhanced Inngest Agent Kit tool for Agent Zero.

This tool provides agent-specific workflow orchestration capabilities using
the Inngest Agent Kit, enabling sophisticated multi-agent coordination.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from python.helpers.tool import Tool, Response
from python.helpers.inngest_client import get_inngest_manager, get_inngest_agent_kit
from python.helpers.inngest_agent_kit import AgentState


class InngestAgentKitTool(Tool):
    """
    Enhanced tool for Inngest Agent Kit workflow orchestration.
    
    Methods:
    - status: Get agent kit status
    - update_agent_state: Update an agent's state
    - send_agent_message: Send message between agents
    - start_multi_agent_workflow: Start multi-agent coordination
    - create_agent_workflow: Create agent-specific workflow
    - get_agent_context: Get agent context information
    - list_active_workflows: List active agent workflows
    """

    async def execute(self, **kwargs):
        if self.method == "status":
            return await self.get_status(**kwargs)
        elif self.method == "update_agent_state":
            return await self.update_agent_state(**kwargs)
        elif self.method == "send_agent_message":
            return await self.send_agent_message(**kwargs)
        elif self.method == "start_multi_agent_workflow":
            return await self.start_multi_agent_workflow(**kwargs)
        elif self.method == "create_agent_workflow":
            return await self.create_agent_workflow(**kwargs)
        elif self.method == "get_agent_context":
            return await self.get_agent_context(**kwargs)
        elif self.method == "list_active_workflows":
            return await self.list_active_workflows(**kwargs)
        else:
            return Response(message=f"Unknown method '{self.name}:{self.method}'", break_loop=False)

    async def get_status(self, **kwargs) -> Response:
        """Get Inngest Agent Kit status."""
        try:
            agent_kit = get_inngest_agent_kit()
            status = agent_kit.get_status()
            
            return Response(
                message=json.dumps(status, indent=2),
                break_loop=False
            )
            
        except Exception as e:
            return Response(
                message=f"Error getting agent kit status: {str(e)}",
                break_loop=False
            )

    async def update_agent_state(self, **kwargs) -> Response:
        """
        Update an agent's state.
        
        Args:
            agent_id: Agent identifier (required)
            state: New state (required) - one of: idle, thinking, acting, waiting, complete, error
            metadata: Optional metadata dict
            session_id: Optional session ID
            workflow_id: Optional workflow ID
        """
        try:
            agent_id = kwargs.get("agent_id")
            state = kwargs.get("state")
            metadata = kwargs.get("metadata", {})
            session_id = kwargs.get("session_id")
            workflow_id = kwargs.get("workflow_id")
            
            if not agent_id:
                return Response(message="agent_id is required", break_loop=False)
            
            if not state:
                return Response(message="state is required", break_loop=False)
            
            # Validate state
            try:
                AgentState(state)
            except ValueError:
                valid_states = [s.value for s in AgentState]
                return Response(
                    message=f"Invalid state '{state}'. Valid states: {', '.join(valid_states)}",
                    break_loop=False
                )
            
            agent_kit = get_inngest_agent_kit()
            
            if not agent_kit.inngest_manager.is_enabled():
                return Response(
                    message="Inngest is not enabled. Check configuration and INNGEST_EVENT_KEY.",
                    break_loop=False
                )
            
            success = await agent_kit.update_agent_state(
                agent_id, state, metadata, session_id, workflow_id
            )
            
            if success:
                return Response(
                    message=f"Agent '{agent_id}' state updated to '{state}'",
                    break_loop=False
                )
            else:
                return Response(
                    message=f"Failed to update agent '{agent_id}' state",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"Error updating agent state: {str(e)}",
                break_loop=False
            )

    async def send_agent_message(self, **kwargs) -> Response:
        """
        Send a message between agents.
        
        Args:
            from_agent: Source agent ID (required)
            to_agent: Target agent ID (required)
            message_type: Message type (required) - e.g., task_delegation, status_update, request_assistance, share_result
            content: Message content dict (required)
        """
        try:
            from_agent = kwargs.get("from_agent")
            to_agent = kwargs.get("to_agent")
            message_type = kwargs.get("message_type")
            content = kwargs.get("content")
            
            if not from_agent:
                return Response(message="from_agent is required", break_loop=False)
            
            if not to_agent:
                return Response(message="to_agent is required", break_loop=False)
            
            if not message_type:
                return Response(message="message_type is required", break_loop=False)
            
            if not content:
                return Response(message="content is required", break_loop=False)
            
            if not isinstance(content, dict):
                return Response(message="content must be a dictionary", break_loop=False)
            
            agent_kit = get_inngest_agent_kit()
            
            if not agent_kit.inngest_manager.is_enabled():
                return Response(
                    message="Inngest is not enabled. Check configuration and INNGEST_EVENT_KEY.",
                    break_loop=False
                )
            
            success = await agent_kit.send_agent_message(
                from_agent, to_agent, message_type, content
            )
            
            if success:
                return Response(
                    message=f"Message sent from '{from_agent}' to '{to_agent}' (type: {message_type})",
                    break_loop=False
                )
            else:
                return Response(
                    message=f"Failed to send message from '{from_agent}' to '{to_agent}'",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"Error sending agent message: {str(e)}",
                break_loop=False
            )

    async def start_multi_agent_workflow(self, **kwargs) -> Response:
        """
        Start a multi-agent workflow.
        
        Args:
            workflow_id: Unique workflow identifier (required)
            agent_assignments: Dict mapping agent IDs to their assignments (required)
            coordination_strategy: Strategy for coordination (optional) - sequential, parallel, hierarchical
        """
        try:
            workflow_id = kwargs.get("workflow_id")
            agent_assignments = kwargs.get("agent_assignments")
            coordination_strategy = kwargs.get("coordination_strategy", "sequential")
            
            if not workflow_id:
                return Response(message="workflow_id is required", break_loop=False)
            
            if not agent_assignments:
                return Response(message="agent_assignments is required", break_loop=False)
            
            if not isinstance(agent_assignments, dict):
                return Response(message="agent_assignments must be a dictionary", break_loop=False)
            
            valid_strategies = ["sequential", "parallel", "hierarchical"]
            if coordination_strategy not in valid_strategies:
                return Response(
                    message=f"Invalid coordination_strategy. Valid options: {', '.join(valid_strategies)}",
                    break_loop=False
                )
            
            agent_kit = get_inngest_agent_kit()
            
            if not agent_kit.inngest_manager.is_enabled():
                return Response(
                    message="Inngest is not enabled. Check configuration and INNGEST_EVENT_KEY.",
                    break_loop=False
                )
            
            success = await agent_kit.start_multi_agent_workflow(
                workflow_id, agent_assignments, coordination_strategy
            )
            
            if success:
                agent_count = len(agent_assignments)
                return Response(
                    message=f"Multi-agent workflow '{workflow_id}' started with {agent_count} agents using {coordination_strategy} strategy",
                    break_loop=False
                )
            else:
                return Response(
                    message=f"Failed to start multi-agent workflow '{workflow_id}'",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"Error starting multi-agent workflow: {str(e)}",
                break_loop=False
            )

    async def create_agent_workflow(self, **kwargs) -> Response:
        """
        Create and start an agent-specific workflow.
        
        Args:
            workflow_id: Unique workflow identifier (required)
            name: Workflow name (required)
            description: Workflow description (optional)
            agent_roles: List of agent role names (required)
            steps: List of workflow steps (required)
            communication_patterns: Communication patterns dict (optional)
            state_management: State management config dict (optional)
        """
        try:
            workflow_id = kwargs.get("workflow_id")
            name = kwargs.get("name")
            description = kwargs.get("description", "")
            agent_roles = kwargs.get("agent_roles")
            steps = kwargs.get("steps")
            communication_patterns = kwargs.get("communication_patterns", {})
            state_management = kwargs.get("state_management", {})
            
            if not workflow_id:
                return Response(message="workflow_id is required", break_loop=False)
            
            if not name:
                return Response(message="name is required", break_loop=False)
            
            if not agent_roles:
                return Response(message="agent_roles is required", break_loop=False)
            
            if not isinstance(agent_roles, list):
                return Response(message="agent_roles must be a list", break_loop=False)
            
            if not steps:
                return Response(message="steps is required", break_loop=False)
            
            if not isinstance(steps, list):
                return Response(message="steps must be a list", break_loop=False)
            
            agent_kit = get_inngest_agent_kit()
            
            if not agent_kit.inngest_manager.is_enabled():
                return Response(
                    message="Inngest is not enabled. Check configuration and INNGEST_EVENT_KEY.",
                    break_loop=False
                )
            
            success = await agent_kit.create_agent_workflow(
                workflow_id, name, description, agent_roles, steps,
                communication_patterns, state_management
            )
            
            if success:
                step_count = len(steps)
                role_count = len(agent_roles)
                return Response(
                    message=f"Agent workflow '{name}' created with {step_count} steps for {role_count} agent roles",
                    break_loop=False
                )
            else:
                return Response(
                    message=f"Failed to create agent workflow '{name}'",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"Error creating agent workflow: {str(e)}",
                break_loop=False
            )

    async def get_agent_context(self, **kwargs) -> Response:
        """
        Get agent context information.
        
        Args:
            agent_id: Agent identifier (required)
        """
        try:
            agent_id = kwargs.get("agent_id")
            
            if not agent_id:
                return Response(message="agent_id is required", break_loop=False)
            
            agent_kit = get_inngest_agent_kit()
            context = agent_kit.get_agent_context(agent_id)
            
            if context:
                context_info = {
                    "agent_id": context.agent_id,
                    "session_id": context.session_id,
                    "workflow_id": context.workflow_id,
                    "state": context.state.value,
                    "metadata": context.metadata,
                    "created_at": context.created_at.isoformat(),
                    "updated_at": context.updated_at.isoformat()
                }
                
                return Response(
                    message=json.dumps(context_info, indent=2),
                    break_loop=False
                )
            else:
                return Response(
                    message=f"No context found for agent '{agent_id}'",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"Error getting agent context: {str(e)}",
                break_loop=False
            )

    async def list_active_workflows(self, **kwargs) -> Response:
        """List active agent workflows."""
        try:
            agent_kit = get_inngest_agent_kit()
            active_workflows = agent_kit.get_active_workflows()
            
            result = {
                "active_workflows": active_workflows,
                "count": len(active_workflows),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return Response(
                message=json.dumps(result, indent=2),
                break_loop=False
            )
            
        except Exception as e:
            return Response(
                message=f"Error listing active workflows: {str(e)}",
                break_loop=False
            )
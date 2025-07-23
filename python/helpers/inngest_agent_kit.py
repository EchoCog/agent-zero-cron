"""
Inngest Agent Kit integration for Agent Zero.

This module provides agent-specific abstractions and patterns for workflow
orchestration, implementing the functionality typically found in Inngest's agent-kit.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from python.helpers.inngest_client import InngestManager, InngestConfig
from python.helpers.print_style import PrintStyle


class AgentState(Enum):
    """Agent execution states."""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class AgentContext:
    """Agent execution context for workflow orchestration."""
    agent_id: str
    session_id: str
    workflow_id: Optional[str] = None
    state: AgentState = AgentState.IDLE
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AgentMessage:
    """Message for agent-to-agent communication."""
    from_agent: str
    to_agent: str
    message_type: str
    content: Dict[str, Any]
    context: Optional[AgentContext] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class AgentWorkflow:
    """Agent-specific workflow definition."""
    workflow_id: str
    name: str
    description: str
    agent_roles: List[str]
    steps: List[Dict[str, Any]]
    communication_patterns: Dict[str, Any] = field(default_factory=dict)
    state_management: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class InngestAgentKit:
    """
    Agent Kit for Inngest workflow orchestration.
    
    Provides agent-specific abstractions including:
    - Agent state management
    - Agent-to-agent communication
    - Agent workflow patterns
    - Multi-agent coordination
    """
    
    def __init__(self, inngest_manager: InngestManager):
        self.inngest_manager = inngest_manager
        self._printer = PrintStyle(italic=True, font_color="green", padding=False)
        self._agent_contexts: Dict[str, AgentContext] = {}
        self._active_workflows: Dict[str, AgentWorkflow] = {}
        self._setup_agent_functions()
    
    def _setup_agent_functions(self):
        """Set up agent-specific Inngest functions."""
        if not self.inngest_manager.is_enabled():
            self._printer.print("Inngest not enabled, skipping agent kit function setup")
            return
        
        # Agent state management
        self.inngest_manager.create_function(
            fn_id="agent-state-update",
            name="Agent State Update",
            trigger="agent/state-changed",
            handler=self._handle_agent_state_update
        )
        
        # Agent communication
        self.inngest_manager.create_function(
            fn_id="agent-communication",
            name="Agent-to-Agent Communication",
            trigger="agent/message",
            handler=self._handle_agent_message
        )
        
        # Multi-agent coordination
        self.inngest_manager.create_function(
            fn_id="multi-agent-coordinator",
            name="Multi-Agent Coordinator",
            trigger="workflow/multi-agent",
            handler=self._handle_multi_agent_workflow
        )
        
        # Agent workflow orchestration
        self.inngest_manager.create_function(
            fn_id="agent-workflow-orchestrator",
            name="Agent Workflow Orchestrator",
            trigger="agent/workflow-start",
            handler=self._handle_agent_workflow
        )
        
        self._printer.print("Agent Kit functions registered with Inngest")
    
    async def _handle_agent_state_update(self, ctx: Any, step: Any) -> Dict[str, Any]:
        """Handle agent state updates."""
        try:
            event_data = ctx.event.data
            agent_id = event_data.get("agent_id")
            new_state = event_data.get("state")
            metadata = event_data.get("metadata", {})
            
            if not agent_id or not new_state:
                raise ValueError("agent_id and state are required")
            
            # Update agent context
            if agent_id in self._agent_contexts:
                context = self._agent_contexts[agent_id]
                context.state = AgentState(new_state)
                context.metadata.update(metadata)
                context.updated_at = datetime.now(timezone.utc)
            else:
                # Create new context
                context = AgentContext(
                    agent_id=agent_id,
                    session_id=event_data.get("session_id", str(uuid.uuid4())),
                    workflow_id=event_data.get("workflow_id"),
                    state=AgentState(new_state),
                    metadata=metadata
                )
                self._agent_contexts[agent_id] = context
            
            self._printer.print(f"Agent {agent_id} state updated to {new_state}")
            
            # Trigger dependent workflows based on state
            await self._trigger_state_dependent_workflows(context)
            
            return {
                "agent_id": agent_id,
                "state": new_state,
                "updated_at": context.updated_at.isoformat()
            }
            
        except Exception as e:
            self._printer.print(f"Error updating agent state: {e}")
            raise
    
    async def _handle_agent_message(self, ctx: Any, step: Any) -> Dict[str, Any]:
        """Handle agent-to-agent communication."""
        try:
            event_data = ctx.event.data
            message = AgentMessage(
                from_agent=event_data["from_agent"],
                to_agent=event_data["to_agent"],
                message_type=event_data["message_type"],
                content=event_data["content"],
                context=self._agent_contexts.get(event_data["from_agent"])
            )
            
            self._printer.print(
                f"Agent message: {message.from_agent} -> {message.to_agent} "
                f"({message.message_type})"
            )
            
            # Process message based on type
            await self._process_agent_message(message)
            
            return {
                "message_id": message.message_id,
                "processed_at": message.timestamp.isoformat(),
                "status": "delivered"
            }
            
        except Exception as e:
            self._printer.print(f"Error handling agent message: {e}")
            raise
    
    async def _handle_multi_agent_workflow(self, ctx: Any, step: Any) -> Dict[str, Any]:
        """Handle multi-agent workflow coordination."""
        try:
            event_data = ctx.event.data
            workflow_id = event_data["workflow_id"]
            agent_assignments = event_data["agent_assignments"]
            coordination_strategy = event_data.get("coordination_strategy", "sequential")
            
            self._printer.print(f"Starting multi-agent workflow: {workflow_id}")
            
            if coordination_strategy == "parallel":
                await self._execute_parallel_agent_workflow(workflow_id, agent_assignments)
            elif coordination_strategy == "sequential":
                await self._execute_sequential_agent_workflow(workflow_id, agent_assignments)
            elif coordination_strategy == "hierarchical":
                await self._execute_hierarchical_agent_workflow(workflow_id, agent_assignments)
            else:
                raise ValueError(f"Unknown coordination strategy: {coordination_strategy}")
            
            return {
                "workflow_id": workflow_id,
                "status": "started",
                "agents": list(agent_assignments.keys()),
                "strategy": coordination_strategy
            }
            
        except Exception as e:
            self._printer.print(f"Error in multi-agent workflow: {e}")
            raise
    
    async def _handle_agent_workflow(self, ctx: Any, step: Any) -> Dict[str, Any]:
        """Handle agent-specific workflow orchestration."""
        try:
            event_data = ctx.event.data
            workflow = AgentWorkflow(
                workflow_id=event_data["workflow_id"],
                name=event_data["name"],
                description=event_data.get("description", ""),
                agent_roles=event_data["agent_roles"],
                steps=event_data["steps"],
                communication_patterns=event_data.get("communication_patterns", {}),
                state_management=event_data.get("state_management", {})
            )
            
            self._active_workflows[workflow.workflow_id] = workflow
            
            self._printer.print(f"Starting agent workflow: {workflow.name}")
            
            # Execute workflow steps with agent-specific logic
            results = await self._execute_agent_workflow_steps(workflow)
            
            return {
                "workflow_id": workflow.workflow_id,
                "status": "completed",
                "results": results
            }
            
        except Exception as e:
            self._printer.print(f"Error in agent workflow: {e}")
            raise
    
    async def _trigger_state_dependent_workflows(self, context: AgentContext):
        """Trigger workflows that depend on agent state changes."""
        if context.workflow_id and context.workflow_id in self._active_workflows:
            workflow = self._active_workflows[context.workflow_id]
            
            # Check for state-dependent triggers
            for pattern_name, pattern_config in workflow.communication_patterns.items():
                if pattern_config.get("trigger_on_state") == context.state.value:
                    await self.inngest_manager.send_event(
                        f"workflow/{pattern_name}",
                        {
                            "workflow_id": context.workflow_id,
                            "agent_id": context.agent_id,
                            "trigger_state": context.state.value,
                            "context": context.metadata
                        }
                    )
    
    async def _process_agent_message(self, message: AgentMessage):
        """Process agent-to-agent messages."""
        # Route message based on type
        if message.message_type == "task_delegation":
            await self._handle_task_delegation(message)
        elif message.message_type == "status_update":
            await self._handle_status_update(message)
        elif message.message_type == "request_assistance":
            await self._handle_assistance_request(message)
        elif message.message_type == "share_result":
            await self._handle_result_sharing(message)
        else:
            self._printer.print(f"Unknown message type: {message.message_type}")
    
    async def _handle_task_delegation(self, message: AgentMessage):
        """Handle task delegation between agents."""
        task_info = message.content.get("task")
        if task_info:
            await self.inngest_manager.send_event(
                "task/delegated",
                {
                    "from_agent": message.from_agent,
                    "to_agent": message.to_agent,
                    "task": task_info,
                    "delegation_id": str(uuid.uuid4())
                }
            )
    
    async def _handle_status_update(self, message: AgentMessage):
        """Handle status updates between agents."""
        status = message.content.get("status")
        if status:
            await self.update_agent_state(
                message.from_agent,
                status,
                message.content.get("metadata", {})
            )
    
    async def _handle_assistance_request(self, message: AgentMessage):
        """Handle requests for assistance between agents."""
        await self.inngest_manager.send_event(
            "agent/assistance-needed",
            {
                "requesting_agent": message.from_agent,
                "target_agent": message.to_agent,
                "assistance_type": message.content.get("type"),
                "details": message.content.get("details"),
                "priority": message.content.get("priority", "normal")
            }
        )
    
    async def _handle_result_sharing(self, message: AgentMessage):
        """Handle result sharing between agents."""
        await self.inngest_manager.send_event(
            "agent/result-shared",
            {
                "from_agent": message.from_agent,
                "to_agent": message.to_agent,
                "result": message.content.get("result"),
                "result_type": message.content.get("type"),
                "context": message.content.get("context")
            }
        )
    
    async def _execute_parallel_agent_workflow(self, workflow_id: str, agent_assignments: Dict[str, Any]):
        """Execute agents in parallel."""
        tasks = []
        for agent_id, assignment in agent_assignments.items():
            task = self.inngest_manager.send_event(
                "agent/execute-assignment",
                {
                    "workflow_id": workflow_id,
                    "agent_id": agent_id,
                    "assignment": assignment,
                    "execution_mode": "parallel"
                }
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def _execute_sequential_agent_workflow(self, workflow_id: str, agent_assignments: Dict[str, Any]):
        """Execute agents sequentially."""
        for agent_id, assignment in agent_assignments.items():
            await self.inngest_manager.send_event(
                "agent/execute-assignment",
                {
                    "workflow_id": workflow_id,
                    "agent_id": agent_id,
                    "assignment": assignment,
                    "execution_mode": "sequential"
                }
            )
    
    async def _execute_hierarchical_agent_workflow(self, workflow_id: str, agent_assignments: Dict[str, Any]):
        """Execute agents in hierarchical order."""
        # Sort by hierarchy level
        sorted_agents = sorted(
            agent_assignments.items(),
            key=lambda x: x[1].get("hierarchy_level", 0)
        )
        
        for agent_id, assignment in sorted_agents:
            await self.inngest_manager.send_event(
                "agent/execute-assignment",
                {
                    "workflow_id": workflow_id,
                    "agent_id": agent_id,
                    "assignment": assignment,
                    "execution_mode": "hierarchical",
                    "hierarchy_level": assignment.get("hierarchy_level", 0)
                }
            )
    
    async def _execute_agent_workflow_steps(self, workflow: AgentWorkflow) -> List[Dict[str, Any]]:
        """Execute agent workflow steps."""
        results = []
        
        for step in workflow.steps:
            step_type = step.get("type")
            
            if step_type == "agent_task":
                result = await self._execute_agent_task_step(workflow, step)
            elif step_type == "agent_communication":
                result = await self._execute_communication_step(workflow, step)
            elif step_type == "state_check":
                result = await self._execute_state_check_step(workflow, step)
            elif step_type == "agent_coordination":
                result = await self._execute_coordination_step(workflow, step)
            else:
                result = {"error": f"Unknown step type: {step_type}"}
            
            results.append(result)
        
        return results
    
    async def _execute_agent_task_step(self, workflow: AgentWorkflow, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent task step."""
        agent_id = step.get("agent_id")
        task_config = step.get("task_config", {})
        
        await self.inngest_manager.send_event(
            "agent/task-assigned",
            {
                "workflow_id": workflow.workflow_id,
                "agent_id": agent_id,
                "task_config": task_config,
                "step_id": step.get("id")
            }
        )
        
        return {
            "step_id": step.get("id"),
            "type": "agent_task",
            "agent_id": agent_id,
            "status": "assigned"
        }
    
    async def _execute_communication_step(self, workflow: AgentWorkflow, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent communication step."""
        from_agent = step.get("from_agent")
        to_agent = step.get("to_agent")
        message_config = step.get("message_config", {})
        
        await self.send_agent_message(
            from_agent,
            to_agent,
            message_config.get("type", "communication"),
            message_config.get("content", {})
        )
        
        return {
            "step_id": step.get("id"),
            "type": "agent_communication",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "status": "sent"
        }
    
    async def _execute_state_check_step(self, workflow: AgentWorkflow, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a state check step."""
        agent_id = step.get("agent_id")
        expected_state = step.get("expected_state")
        
        context = self._agent_contexts.get(agent_id)
        current_state = context.state.value if context else "unknown"
        
        return {
            "step_id": step.get("id"),
            "type": "state_check",
            "agent_id": agent_id,
            "expected_state": expected_state,
            "current_state": current_state,
            "status": "pass" if current_state == expected_state else "fail"
        }
    
    async def _execute_coordination_step(self, workflow: AgentWorkflow, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent coordination step."""
        coordination_type = step.get("coordination_type")
        participants = step.get("participants", [])
        
        await self.inngest_manager.send_event(
            "agent/coordination-event",
            {
                "workflow_id": workflow.workflow_id,
                "coordination_type": coordination_type,
                "participants": participants,
                "step_id": step.get("id")
            }
        )
        
        return {
            "step_id": step.get("id"),
            "type": "agent_coordination",
            "coordination_type": coordination_type,
            "participants": participants,
            "status": "initiated"
        }
    
    # Public API methods
    
    async def update_agent_state(
        self,
        agent_id: str,
        state: str,
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> bool:
        """Update an agent's state."""
        return await self.inngest_manager.send_event(
            "agent/state-changed",
            {
                "agent_id": agent_id,
                "state": state,
                "metadata": metadata or {},
                "session_id": session_id,
                "workflow_id": workflow_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def send_agent_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        content: Dict[str, Any]
    ) -> bool:
        """Send a message between agents."""
        return await self.inngest_manager.send_event(
            "agent/message",
            {
                "from_agent": from_agent,
                "to_agent": to_agent,
                "message_type": message_type,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def start_multi_agent_workflow(
        self,
        workflow_id: str,
        agent_assignments: Dict[str, Any],
        coordination_strategy: str = "sequential"
    ) -> bool:
        """Start a multi-agent workflow."""
        return await self.inngest_manager.send_event(
            "workflow/multi-agent",
            {
                "workflow_id": workflow_id,
                "agent_assignments": agent_assignments,
                "coordination_strategy": coordination_strategy,
                "started_at": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def create_agent_workflow(
        self,
        workflow_id: str,
        name: str,
        description: str,
        agent_roles: List[str],
        steps: List[Dict[str, Any]],
        communication_patterns: Optional[Dict[str, Any]] = None,
        state_management: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create and start an agent workflow."""
        return await self.inngest_manager.send_event(
            "agent/workflow-start",
            {
                "workflow_id": workflow_id,
                "name": name,
                "description": description,
                "agent_roles": agent_roles,
                "steps": steps,
                "communication_patterns": communication_patterns or {},
                "state_management": state_management or {},
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        )
    
    def get_agent_context(self, agent_id: str) -> Optional[AgentContext]:
        """Get agent context by ID."""
        return self._agent_contexts.get(agent_id)
    
    def get_active_workflows(self) -> List[str]:
        """Get list of active workflow IDs."""
        return list(self._active_workflows.keys())
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent kit status."""
        return {
            "enabled": self.inngest_manager.is_enabled(),
            "active_agents": len(self._agent_contexts),
            "active_workflows": len(self._active_workflows),
            "agent_contexts": {
                agent_id: {
                    "state": context.state.value,
                    "session_id": context.session_id,
                    "workflow_id": context.workflow_id,
                    "updated_at": context.updated_at.isoformat()
                }
                for agent_id, context in self._agent_contexts.items()
            },
            "workflows": {
                workflow_id: {
                    "name": workflow.name,
                    "agent_roles": workflow.agent_roles,
                    "created_at": workflow.created_at.isoformat()
                }
                for workflow_id, workflow in self._active_workflows.items()
            }
        }


# Global helper function
def get_inngest_agent_kit(inngest_manager: Optional[InngestManager] = None) -> InngestAgentKit:
    """Get or create Inngest Agent Kit instance."""
    if inngest_manager is None:
        from python.helpers.inngest_client import get_inngest_manager
        inngest_manager = get_inngest_manager()
    
    return InngestAgentKit(inngest_manager)
# Inngest Agent Kit Integration

This document describes the Inngest Agent Kit integration in Agent Zero, which provides advanced workflow orchestration capabilities specifically designed for AI agents.

## Overview

The Inngest Agent Kit extends the standard Inngest integration with agent-specific features:

- **Agent State Management**: Track and update agent states throughout workflows
- **Agent Communication**: Structured messaging between agents  
- **Multi-Agent Coordination**: Orchestrate multiple agents with different strategies
- **Agent Workflows**: Complex workflow patterns designed for AI agents
- **Real-time Monitoring**: Monitor agent states and workflow progress

## Features

### 1. Agent States

Agents can be in one of several states:
- `idle`: Agent is available for new tasks
- `thinking`: Agent is processing information
- `acting`: Agent is executing actions
- `waiting`: Agent is waiting for input or dependencies
- `complete`: Agent has completed its task
- `error`: Agent encountered an error

### 2. Agent Communication Patterns

Agents can communicate using predefined message types:
- `task_delegation`: Assign tasks to other agents
- `status_update`: Report progress or state changes
- `request_assistance`: Ask for help from other agents
- `share_result`: Share results with other agents

### 3. Multi-Agent Coordination Strategies

- **Sequential**: Agents execute one after another
- **Parallel**: Agents execute simultaneously
- **Hierarchical**: Agents execute based on hierarchy levels

### 4. Workflow Step Types

Agent workflows support specialized step types:
- `agent_task`: Execute a specific task with an agent
- `agent_communication`: Send messages between agents
- `state_check`: Verify agent states before proceeding
- `agent_coordination`: Coordinate multiple agents

## Configuration

Set these environment variables to enable the Agent Kit:

```bash
INNGEST_ENABLED=true
INNGEST_EVENT_KEY=your_event_key
INNGEST_SIGNING_KEY=your_signing_key  # optional
INNGEST_APP_ID=your_app_id  # optional, defaults to 'agent-zero'
```

## Usage

### Using the Tool Interface

The Agent Kit provides a tool interface for Agent Zero:

```json
{
  "tool_name": "inngest_agent_kit:update_agent_state",
  "tool_args": {
    "agent_id": "agent-001",
    "state": "thinking",
    "metadata": {
      "task": "data_analysis",
      "progress": 25
    }
  }
}
```

### Available Tool Methods

#### `inngest_agent_kit:status`
Get overall Agent Kit status

#### `inngest_agent_kit:update_agent_state`
Update an agent's state
- `agent_id`: Agent identifier (required)
- `state`: New state (required)
- `metadata`: Optional metadata dict
- `session_id`: Optional session ID
- `workflow_id`: Optional workflow ID

#### `inngest_agent_kit:send_agent_message`
Send messages between agents
- `from_agent`: Source agent ID (required)
- `to_agent`: Target agent ID (required)
- `message_type`: Message type (required)
- `content`: Message content dict (required)

#### `inngest_agent_kit:start_multi_agent_workflow`
Start multi-agent coordination
- `workflow_id`: Unique workflow identifier (required)
- `agent_assignments`: Dict mapping agent IDs to assignments (required)
- `coordination_strategy`: Strategy (sequential/parallel/hierarchical)

#### `inngest_agent_kit:create_agent_workflow`
Create sophisticated agent workflows
- `workflow_id`: Unique workflow identifier (required)
- `name`: Workflow name (required)
- `description`: Workflow description
- `agent_roles`: List of agent role names (required)
- `steps`: List of workflow steps (required)
- `communication_patterns`: Communication patterns dict
- `state_management`: State management config dict

#### `inngest_agent_kit:get_agent_context`
Get agent context information
- `agent_id`: Agent identifier (required)

#### `inngest_agent_kit:list_active_workflows`
List active agent workflows

### Direct API Usage

You can also use the Agent Kit directly in Python:

```python
from python.helpers.inngest_client import get_inngest_agent_kit

# Get agent kit instance
agent_kit = get_inngest_agent_kit()

# Update agent state
await agent_kit.update_agent_state(
    agent_id="agent-001",
    state="thinking",
    metadata={"task": "analysis"}
)

# Send message between agents
await agent_kit.send_agent_message(
    from_agent="supervisor",
    to_agent="worker",
    message_type="task_delegation",
    content={"task": "process_data"}
)

# Start multi-agent workflow
await agent_kit.start_multi_agent_workflow(
    workflow_id="parallel-processing",
    agent_assignments={
        "agent-1": {"role": "collector"},
        "agent-2": {"role": "processor"}
    },
    coordination_strategy="parallel"
)
```

## Example Workflows

### Simple Task Delegation

```json
{
  "tool_name": "inngest_agent_kit:send_agent_message",
  "tool_args": {
    "from_agent": "supervisor",
    "to_agent": "worker-001",
    "message_type": "task_delegation",
    "content": {
      "task": {
        "id": "data-analysis-001",
        "type": "analysis",
        "description": "Analyze sales data"
      }
    }
  }
}
```

### Multi-Agent Parallel Processing

```json
{
  "tool_name": "inngest_agent_kit:start_multi_agent_workflow",
  "tool_args": {
    "workflow_id": "parallel-analysis",
    "coordination_strategy": "parallel",
    "agent_assignments": {
      "data-collector": {
        "role": "collection",
        "sources": ["database", "api"]
      },
      "data-processor": {
        "role": "processing",
        "algorithms": ["clean", "transform"]
      },
      "data-validator": {
        "role": "validation",
        "rules": ["completeness", "accuracy"]
      }
    }
  }
}
```

### Complex Agent Workflow

```json
{
  "tool_name": "inngest_agent_kit:create_agent_workflow",
  "tool_args": {
    "workflow_id": "advanced-analysis",
    "name": "Advanced Data Analysis",
    "agent_roles": ["coordinator", "collector", "analyst"],
    "steps": [
      {
        "id": "init",
        "type": "agent_task",
        "agent_id": "coordinator",
        "task_config": {"action": "initialize"}
      },
      {
        "id": "delegate",
        "type": "agent_communication",
        "from_agent": "coordinator",
        "to_agent": "collector",
        "message_config": {
          "type": "task_delegation",
          "content": {"task": "collect_data"}
        }
      },
      {
        "id": "check_complete",
        "type": "state_check",
        "agent_id": "collector",
        "expected_state": "complete"
      }
    ],
    "communication_patterns": {
      "progress_updates": {
        "trigger_on_state": "acting",
        "message_type": "status_update"
      }
    }
  }
}
```

## API Endpoints

The Agent Kit also provides REST API endpoints:

- `GET /api/inngest-agent-kit-status` - Get Agent Kit status

## Integration with Task Scheduler

The Agent Kit integrates seamlessly with Agent Zero's existing task scheduler, allowing you to:

- Execute tasks through agent workflows
- Coordinate task execution across multiple agents
- Monitor task progress with agent state tracking
- Handle failures with agent-aware error handling

## Real-World Use Cases

### Customer Service Automation
- Multi-tier support with escalation
- Parallel investigation workflows
- Context-aware agent communication

### Data Processing Pipelines
- Parallel data collection and processing
- Quality assurance workflows
- Error handling and retry logic

### Research and Analysis
- Hierarchical research coordination
- Collaborative analysis workflows
- Result aggregation and validation

## Monitoring and Debugging

Use these tools to monitor agent workflows:

1. **Agent Kit Status**: Check overall system status
2. **Agent Context**: View individual agent states
3. **Active Workflows**: List running workflows
4. **Inngest Dashboard**: Monitor events and functions

## Best Practices

1. **State Management**: Always update agent states appropriately
2. **Error Handling**: Use state checks and error escalation patterns
3. **Communication**: Use structured message types for clarity
4. **Coordination**: Choose appropriate coordination strategies
5. **Monitoring**: Implement progress tracking and status updates

## Troubleshooting

Common issues and solutions:

1. **Inngest Not Enabled**: Ensure INNGEST_EVENT_KEY is set
2. **Agent State Issues**: Check agent context and state history
3. **Communication Failures**: Verify agent IDs and message formats
4. **Workflow Delays**: Check coordination strategy and dependencies

For more examples, see `examples/inngest_agent_kit_example.py`.
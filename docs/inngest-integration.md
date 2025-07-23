# Inngest Workflow Orchestration Integration

Agent Zero now includes Inngest integration for advanced workflow orchestration capabilities. This extends the existing task scheduling system with event-driven workflows, function composition, and reliable execution.

## Overview

The Inngest integration provides:

- **Event-driven workflows**: Trigger tasks and workflows based on events
- **Function composition**: Chain multiple tasks together in complex workflows
- **Reliable execution**: Built-in retries and error handling
- **Observability**: Track workflow execution and monitor performance
- **Scalability**: Handle complex multi-step workflows with dependencies

## Configuration

### Environment Variables

Add these variables to your `.env` file:

```bash
# Enable Inngest workflow orchestration
INNGEST_ENABLED=true

# Your Inngest app identifier (default: agent-zero)
INNGEST_APP_ID=agent-zero

# Your Inngest event key (required if enabled)
INNGEST_EVENT_KEY=your_event_key_here

# Your Inngest signing key (optional, for webhook security)
INNGEST_SIGNING_KEY=your_signing_key_here

# Inngest API base URL (default: https://api.inngest.com)
INNGEST_BASE_URL=https://api.inngest.com
```

### Getting Inngest Keys

1. Sign up at [Inngest](https://inngest.com)
2. Create a new app or use an existing one
3. Get your Event Key from the app settings
4. Optionally, get a Signing Key for webhook security

## Usage

### Using the Inngest Tool

The `inngest` tool provides workflow orchestration capabilities:

#### Check Status
```json
{
  "tool_name": "inngest:status"
}
```

#### Send Event
```json
{
  "tool_name": "inngest:send_event",
  "tool_args": {
    "name": "task/completed",
    "data": {
      "task_id": "123",
      "result": "success"
    },
    "user": {
      "id": "user123"
    }
  }
}
```

#### Execute Task Through Workflow
```json
{
  "tool_name": "inngest:execute_task_workflow",
  "tool_args": {
    "task_uuid": "task-uuid-here",
    "task_context": "Optional context",
    "workflow_id": "optional-workflow-id"
  }
}
```

#### Create Workflow
```json
{
  "tool_name": "inngest:create_workflow",
  "tool_args": {
    "workflow_id": "my-workflow-123",
    "workflow_definition": {
      "name": "Multi-step Data Processing",
      "steps": [
        {
          "id": "step1",
          "type": "task",
          "task_uuid": "data-extraction-task-uuid"
        },
        {
          "id": "step2", 
          "type": "delay",
          "delay_seconds": 30
        },
        {
          "id": "step3",
          "type": "task",
          "task_uuid": "data-processing-task-uuid"
        }
      ]
    },
    "workflow_input": {
      "source": "database",
      "format": "json"
    }
  }
}
```

#### Trigger Predefined Workflow
```json
{
  "tool_name": "inngest:trigger_workflow",
  "tool_args": {
    "workflow_name": "data-processing",
    "data": {
      "input_file": "data.csv",
      "output_format": "json"
    },
    "delay_seconds": 60
  }
}
```

### Workflow Definition Format

Workflows are defined using JSON with the following structure:

```json
{
  "name": "Workflow Name",
  "description": "Optional description",
  "steps": [
    {
      "id": "unique-step-id",
      "type": "task|delay|conditional",
      // Type-specific properties...
    }
  ]
}
```

#### Step Types

**Task Step**: Execute an existing Agent Zero task
```json
{
  "id": "execute-analysis",
  "type": "task",
  "task_uuid": "analysis-task-uuid"
}
```

**Delay Step**: Wait for a specified duration
```json
{
  "id": "wait-30s",
  "type": "delay", 
  "delay_seconds": 30
}
```

**Conditional Step**: Execute different paths based on conditions
```json
{
  "id": "check-result",
  "type": "conditional",
  "condition": {
    "type": "input_contains",
    "key": "status",
    "value": "success"
  },
  "if_true": [
    {
      "id": "success-task",
      "type": "task",
      "task_uuid": "success-handler-uuid"
    }
  ],
  "if_false": [
    {
      "id": "failure-task", 
      "type": "task",
      "task_uuid": "failure-handler-uuid"
    }
  ]
}
```

## API Endpoints

### GET /api/inngest/status
Get Inngest and workflow manager status.

### POST /api/inngest/send-event
Send an event to Inngest.

**Request Body:**
```json
{
  "name": "event/name",
  "data": {"key": "value"},
  "user": {"id": "user123"},
  "ts": 1234567890
}
```

### POST /api/inngest/create-workflow
Create and trigger a workflow.

**Request Body:**
```json
{
  "workflow_id": "optional-id",
  "workflow_definition": {...},
  "workflow_input": {...}
}
```

## Integration with Existing Tasks

The Inngest integration seamlessly works with the existing task scheduler:

1. **Enhanced Task Execution**: Tasks can be executed through Inngest workflows for better orchestration
2. **Event-Driven Scheduling**: Tasks can be triggered by events instead of just time-based schedules
3. **Workflow Composition**: Multiple tasks can be chained together in complex workflows
4. **Fallback Support**: If Inngest is disabled, tasks fall back to direct execution

## Example Workflows

### Data Processing Pipeline
```json
{
  "name": "Data Processing Pipeline",
  "steps": [
    {
      "id": "extract",
      "type": "task", 
      "task_uuid": "data-extraction-task"
    },
    {
      "id": "transform",
      "type": "task",
      "task_uuid": "data-transformation-task"
    },
    {
      "id": "load",
      "type": "task",
      "task_uuid": "data-loading-task"
    }
  ]
}
```

### Conditional Monitoring Workflow
```json
{
  "name": "System Monitoring with Alerts",
  "steps": [
    {
      "id": "check-health",
      "type": "task",
      "task_uuid": "health-check-task"
    },
    {
      "id": "evaluate-health",
      "type": "conditional",
      "condition": {
        "type": "previous_step_success",
        "step_id": "check-health"
      },
      "if_true": [
        {
          "id": "success-log",
          "type": "task", 
          "task_uuid": "log-success-task"
        }
      ],
      "if_false": [
        {
          "id": "send-alert",
          "type": "task",
          "task_uuid": "alert-task"
        },
        {
          "id": "escalate",
          "type": "task",
          "task_uuid": "escalation-task"
        }
      ]
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **Inngest not enabled**: Check that `INNGEST_ENABLED=true` and `INNGEST_EVENT_KEY` is set
2. **Authentication errors**: Verify your Event Key and Signing Key are correct
3. **Network issues**: Check that your environment can reach the Inngest API
4. **Workflow failures**: Check the task UUIDs in your workflow definition are valid

### Debug Information

Use the status endpoint to check configuration:

```json
{
  "tool_name": "inngest:status"
}
```

This will show:
- Whether Inngest is enabled and configured
- Available workflow functions
- Connection status
- Configuration details

## Security Considerations

1. **Environment Variables**: Store Inngest keys securely in environment variables
2. **Signing Keys**: Use signing keys to verify webhook authenticity
3. **Event Data**: Be careful not to include sensitive data in events
4. **Access Control**: Limit who can trigger workflows and access workflow data

## Limitations

1. **Python Client**: Currently uses the Python Inngest SDK
2. **Basic Conditions**: Conditional logic is currently simple (can be extended)
3. **Synchronous Steps**: Some workflow steps may block others
4. **Error Handling**: Basic error handling (Inngest provides advanced retry mechanisms)

## Future Enhancements

Planned improvements include:
- More sophisticated conditional logic
- Parallel step execution
- Integration with external services
- Workflow templates and presets
- Enhanced observability and monitoring
- Visual workflow designer
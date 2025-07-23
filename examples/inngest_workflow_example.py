#!/usr/bin/env python3
"""
Example usage of Inngest workflow orchestration in Agent Zero.

This script demonstrates how to:
1. Configure Inngest
2. Create and manage workflows
3. Execute tasks through workflows
4. Send events for workflow orchestration

Run with: python3 examples/inngest_workflow_example.py
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone


async def example_inngest_status():
    """Example: Check Inngest status."""
    print("=== Checking Inngest Status ===")
    
    # This would normally be done through the agent tool system
    # For demo purposes, we'll show the JSON that would be used
    
    tool_call = {
        "tool_name": "inngest:status"
    }
    
    print(f"Tool call: {json.dumps(tool_call, indent=2)}")
    print("Expected response: Status information about Inngest configuration")
    print()


async def example_send_event():
    """Example: Send an event to Inngest."""
    print("=== Sending Inngest Event ===")
    
    tool_call = {
        "tool_name": "inngest:send_event",
        "tool_args": {
            "name": "user/action",
            "data": {
                "action": "workflow_example",
                "user_id": "demo_user",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "user": {
                "id": "demo_user",
                "name": "Demo User"
            }
        }
    }
    
    print(f"Tool call: {json.dumps(tool_call, indent=2)}")
    print("This would send an event to Inngest that could trigger workflows")
    print()


async def example_execute_task_workflow():
    """Example: Execute a task through Inngest workflow."""
    print("=== Executing Task Through Workflow ===")
    
    # First, you would need to create a task using the scheduler tool
    create_task_call = {
        "tool_name": "scheduler:create_adhoc_task",
        "tool_args": {
            "name": "Demo Workflow Task",
            "system_prompt": "You are a helpful assistant that processes data.",
            "prompt": "Analyze the provided data and generate a summary report.",
            "attachments": [],
            "dedicated_context": True
        }
    }
    
    print("Step 1 - Create a task:")
    print(f"Tool call: {json.dumps(create_task_call, indent=2)}")
    print()
    
    # Then execute it through Inngest
    execute_workflow_call = {
        "tool_name": "inngest:execute_task_workflow",
        "tool_args": {
            "task_uuid": "task-uuid-from-creation-response",
            "task_context": "Processing quarterly sales data",
            "workflow_id": "sales-analysis-workflow"
        }
    }
    
    print("Step 2 - Execute through Inngest workflow:")
    print(f"Tool call: {json.dumps(execute_workflow_call, indent=2)}")
    print("This executes the task with Inngest orchestration and event handling")
    print()


async def example_create_complex_workflow():
    """Example: Create a complex multi-step workflow."""
    print("=== Creating Complex Workflow ===")
    
    workflow_definition = {
        "name": "Data Processing Pipeline",
        "description": "Extract, transform, and load data with error handling",
        "steps": [
            {
                "id": "extract-data",
                "type": "task",
                "task_uuid": "data-extraction-task-uuid"
            },
            {
                "id": "wait-for-processing",
                "type": "delay",
                "delay_seconds": 30
            },
            {
                "id": "check-extraction",
                "type": "conditional",
                "condition": {
                    "type": "previous_step_success",
                    "step_id": "extract-data"
                },
                "if_true": [
                    {
                        "id": "transform-data",
                        "type": "task",
                        "task_uuid": "data-transformation-task-uuid"
                    },
                    {
                        "id": "load-data",
                        "type": "task", 
                        "task_uuid": "data-loading-task-uuid"
                    }
                ],
                "if_false": [
                    {
                        "id": "handle-extraction-failure",
                        "type": "task",
                        "task_uuid": "error-handling-task-uuid"
                    }
                ]
            },
            {
                "id": "final-validation",
                "type": "task",
                "task_uuid": "validation-task-uuid"
            }
        ]
    }
    
    workflow_input = {
        "data_source": "sales_database",
        "output_format": "json",
        "notification_email": "admin@company.com"
    }
    
    tool_call = {
        "tool_name": "inngest:create_workflow",
        "tool_args": {
            "workflow_id": f"data-pipeline-{uuid.uuid4()}",
            "workflow_definition": workflow_definition,
            "workflow_input": workflow_input
        }
    }
    
    print(f"Tool call: {json.dumps(tool_call, indent=2)}")
    print("This creates a sophisticated workflow with:")
    print("- Task execution")
    print("- Delays")
    print("- Conditional logic")
    print("- Error handling paths")
    print()


async def example_trigger_predefined_workflow():
    """Example: Trigger a predefined workflow."""
    print("=== Triggering Predefined Workflow ===")
    
    tool_call = {
        "tool_name": "inngest:trigger_workflow",
        "tool_args": {
            "workflow_name": "daily-report-generation",
            "data": {
                "report_type": "sales",
                "date_range": "last_7_days",
                "recipients": ["manager@company.com", "analyst@company.com"],
                "format": "pdf"
            },
            "delay_seconds": 60
        }
    }
    
    print(f"Tool call: {json.dumps(tool_call, indent=2)}")
    print("This triggers a workflow with a 60-second delay")
    print()


async def example_monitoring_workflow():
    """Example: System monitoring workflow with alerts."""
    print("=== System Monitoring Workflow ===")
    
    monitoring_workflow = {
        "name": "System Health Monitor",
        "description": "Monitor system health and send alerts on issues",
        "steps": [
            {
                "id": "check-cpu",
                "type": "task",
                "task_uuid": "cpu-check-task-uuid"
            },
            {
                "id": "check-memory",
                "type": "task",
                "task_uuid": "memory-check-task-uuid"
            },
            {
                "id": "check-disk",
                "type": "task",
                "task_uuid": "disk-check-task-uuid"
            },
            {
                "id": "evaluate-health",
                "type": "conditional",
                "condition": {
                    "type": "input_contains",
                    "key": "alert_needed",
                    "value": True
                },
                "if_true": [
                    {
                        "id": "send-alert",
                        "type": "task",
                        "task_uuid": "alert-task-uuid"
                    },
                    {
                        "id": "escalate-if-critical",
                        "type": "conditional",
                        "condition": {
                            "type": "input_contains",
                            "key": "severity",
                            "value": "critical"
                        },
                        "if_true": [
                            {
                                "id": "escalate",
                                "type": "task",
                                "task_uuid": "escalation-task-uuid"
                            }
                        ],
                        "if_false": []
                    }
                ],
                "if_false": [
                    {
                        "id": "log-normal-status",
                        "type": "task",
                        "task_uuid": "log-status-task-uuid"
                    }
                ]
            }
        ]
    }
    
    tool_call = {
        "tool_name": "inngest:create_workflow",
        "tool_args": {
            "workflow_id": f"health-monitor-{uuid.uuid4()}",
            "workflow_definition": monitoring_workflow,
            "workflow_input": {
                "monitoring_interval": "5m",
                "alert_thresholds": {
                    "cpu": 80,
                    "memory": 90,
                    "disk": 85
                }
            }
        }
    }
    
    print(f"Tool call: {json.dumps(tool_call, indent=2)}")
    print("This creates a monitoring workflow with:")
    print("- Parallel health checks")
    print("- Nested conditional logic")
    print("- Alert escalation")
    print()


async def main():
    """Run all examples."""
    print("Inngest Workflow Orchestration Examples")
    print("=" * 50)
    print()
    
    await example_inngest_status()
    await example_send_event()
    await example_execute_task_workflow()
    await example_create_complex_workflow()
    await example_trigger_predefined_workflow()
    await example_monitoring_workflow()
    
    print("=== Configuration Notes ===")
    print("To enable Inngest, set these environment variables:")
    print("INNGEST_ENABLED=true")
    print("INNGEST_EVENT_KEY=your_event_key")
    print("INNGEST_SIGNING_KEY=your_signing_key  # optional")
    print("INNGEST_APP_ID=your_app_id  # optional, defaults to 'agent-zero'")
    print()
    print("Get your keys from: https://inngest.com")
    print()
    print("All examples above show the tool calls you would make in Agent Zero")
    print("to use Inngest workflow orchestration capabilities.")


if __name__ == "__main__":
    asyncio.run(main())
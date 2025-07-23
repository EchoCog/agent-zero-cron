#!/usr/bin/env python3
"""
Enhanced example demonstrating Inngest Agent Kit integration in Agent Zero.

This script shows how to use the agent kit features for:
1. Agent state management
2. Agent-to-agent communication
3. Multi-agent workflow coordination
4. Agent-specific workflow patterns

Run with: python3 examples/inngest_agent_kit_example.py
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone


async def example_agent_state_management():
    """Example: Managing agent states."""
    print("=== Agent State Management ===")
    
    # Update agent state
    state_update_call = {
        "tool_name": "inngest_agent_kit:update_agent_state",
        "tool_args": {
            "agent_id": "agent-001",
            "state": "thinking",
            "metadata": {
                "task": "data_analysis",
                "progress": 25,
                "current_step": "data_loading"
            },
            "session_id": "session-abc123",
            "workflow_id": "analysis-workflow-001"
        }
    }
    
    print(f"Tool call: {json.dumps(state_update_call, indent=2)}")
    print("This updates the agent's state to 'thinking' with progress metadata")
    print()


async def example_agent_communication():
    """Example: Agent-to-agent communication."""
    print("=== Agent Communication ===")
    
    # Task delegation message
    delegation_call = {
        "tool_name": "inngest_agent_kit:send_agent_message",
        "tool_args": {
            "from_agent": "supervisor-agent",
            "to_agent": "worker-agent-001", 
            "message_type": "task_delegation",
            "content": {
                "task": {
                    "id": "data-processing-001",
                    "type": "data_analysis",
                    "description": "Analyze quarterly sales data",
                    "priority": "high",
                    "deadline": "2024-01-15T18:00:00Z"
                },
                "resources": {
                    "dataset": "sales_q4_2023.csv",
                    "output_format": "json",
                    "required_tools": ["pandas", "matplotlib"]
                }
            }
        }
    }
    
    print("Task delegation:")
    print(f"Tool call: {json.dumps(delegation_call, indent=2)}")
    print()
    
    # Status update message
    status_call = {
        "tool_name": "inngest_agent_kit:send_agent_message",
        "tool_args": {
            "from_agent": "worker-agent-001",
            "to_agent": "supervisor-agent",
            "message_type": "status_update",
            "content": {
                "status": "acting",
                "progress": 50,
                "message": "Data loaded successfully, starting analysis",
                "metadata": {
                    "records_processed": 15000,
                    "estimated_completion": "2024-01-15T16:30:00Z"
                }
            }
        }
    }
    
    print("Status update:")
    print(f"Tool call: {json.dumps(status_call, indent=2)}")
    print()


async def example_multi_agent_workflow():
    """Example: Multi-agent workflow coordination."""
    print("=== Multi-Agent Workflow Coordination ===")
    
    # Parallel processing workflow
    parallel_workflow = {
        "tool_name": "inngest_agent_kit:start_multi_agent_workflow",
        "tool_args": {
            "workflow_id": f"parallel-analysis-{uuid.uuid4()}",
            "coordination_strategy": "parallel",
            "agent_assignments": {
                "data-collector": {
                    "role": "data_collection",
                    "task": "collect_external_data",
                    "sources": ["api_endpoint_1", "database_2"],
                    "timeout": 300
                },
                "data-processor": {
                    "role": "data_processing", 
                    "task": "clean_and_transform",
                    "input_format": "raw_json",
                    "output_format": "structured_csv"
                },
                "data-validator": {
                    "role": "quality_assurance",
                    "task": "validate_data_quality",
                    "validation_rules": ["completeness", "consistency", "accuracy"]
                }
            }
        }
    }
    
    print("Parallel workflow:")
    print(f"Tool call: {json.dumps(parallel_workflow, indent=2)}")
    print()
    
    # Hierarchical workflow
    hierarchical_workflow = {
        "tool_name": "inngest_agent_kit:start_multi_agent_workflow",
        "tool_args": {
            "workflow_id": f"hierarchical-review-{uuid.uuid4()}",
            "coordination_strategy": "hierarchical",
            "agent_assignments": {
                "senior-analyst": {
                    "role": "senior_analyst",
                    "hierarchy_level": 0,
                    "task": "strategic_analysis",
                    "responsibilities": ["oversee", "validate", "approve"]
                },
                "junior-analyst-1": {
                    "role": "junior_analyst",
                    "hierarchy_level": 1,
                    "task": "detailed_analysis",
                    "focus_area": "sales_trends"
                },
                "junior-analyst-2": {
                    "role": "junior_analyst",
                    "hierarchy_level": 1,
                    "task": "detailed_analysis",
                    "focus_area": "customer_behavior"
                }
            }
        }
    }
    
    print("Hierarchical workflow:")
    print(f"Tool call: {json.dumps(hierarchical_workflow, indent=2)}")
    print()


async def example_agent_workflow_creation():
    """Example: Creating sophisticated agent workflows."""
    print("=== Agent Workflow Creation ===")
    
    workflow_steps = [
        {
            "id": "initialization",
            "type": "agent_task",
            "agent_id": "coordinator",
            "task_config": {
                "action": "initialize_workflow",
                "parameters": {"workspace": "analysis_env"}
            }
        },
        {
            "id": "data-collection-communication",
            "type": "agent_communication",
            "from_agent": "coordinator",
            "to_agent": "data-collector",
            "message_config": {
                "type": "task_delegation",
                "content": {
                    "task": "collect_quarterly_data",
                    "sources": ["crm", "analytics", "surveys"]
                }
            }
        },
        {
            "id": "check-collection-complete",
            "type": "state_check",
            "agent_id": "data-collector",
            "expected_state": "complete"
        },
        {
            "id": "parallel-analysis",
            "type": "agent_coordination",
            "coordination_type": "parallel_execution",
            "participants": ["analyst-1", "analyst-2", "analyst-3"]
        },
        {
            "id": "results-aggregation",
            "type": "agent_task",
            "agent_id": "coordinator",
            "task_config": {
                "action": "aggregate_results",
                "wait_for_all": True
            }
        }
    ]
    
    communication_patterns = {
        "progress_updates": {
            "frequency": "every_30_seconds",
            "trigger_on_state": "acting",
            "message_type": "status_update"
        },
        "error_escalation": {
            "trigger_on_state": "error",
            "escalate_to": "coordinator",
            "include_context": True
        }
    }
    
    state_management = {
        "auto_retry": {
            "max_attempts": 3,
            "retry_delay": 60,
            "retry_states": ["error", "timeout"]
        },
        "timeout_handling": {
            "default_timeout": 1800,
            "timeout_action": "escalate"
        }
    }
    
    workflow_creation = {
        "tool_name": "inngest_agent_kit:create_agent_workflow",
        "tool_args": {
            "workflow_id": f"advanced-analysis-{uuid.uuid4()}",
            "name": "Advanced Data Analysis Workflow",
            "description": "Multi-stage analysis with error handling and state management",
            "agent_roles": ["coordinator", "data-collector", "analyst-1", "analyst-2", "analyst-3"],
            "steps": workflow_steps,
            "communication_patterns": communication_patterns,
            "state_management": state_management
        }
    }
    
    print(f"Tool call: {json.dumps(workflow_creation, indent=2)}")
    print("This creates a sophisticated workflow with:")
    print("- Multi-step execution")
    print("- Agent communication")
    print("- State validation")
    print("- Parallel coordination")
    print("- Automatic progress updates")
    print("- Error handling and retry logic")
    print()


async def example_agent_monitoring():
    """Example: Monitoring agent status and workflows."""
    print("=== Agent Monitoring ===")
    
    # Get agent context
    context_call = {
        "tool_name": "inngest_agent_kit:get_agent_context",
        "tool_args": {
            "agent_id": "agent-001"
        }
    }
    
    print("Get agent context:")
    print(f"Tool call: {json.dumps(context_call, indent=2)}")
    print()
    
    # List active workflows
    workflows_call = {
        "tool_name": "inngest_agent_kit:list_active_workflows"
    }
    
    print("List active workflows:")
    print(f"Tool call: {json.dumps(workflows_call, indent=2)}")
    print()
    
    # Get overall status
    status_call = {
        "tool_name": "inngest_agent_kit:status"
    }
    
    print("Get agent kit status:")
    print(f"Tool call: {json.dumps(status_call, indent=2)}")
    print()


async def example_real_world_scenario():
    """Example: Real-world customer service scenario."""
    print("=== Real-World Scenario: Customer Service Automation ===")
    
    # Scenario: Automated customer support with escalation
    print("Scenario: Multi-tier customer support with intelligent escalation")
    print()
    
    # Step 1: Initial customer interaction
    initial_interaction = {
        "tool_name": "inngest_agent_kit:update_agent_state",
        "tool_args": {
            "agent_id": "chatbot-001",
            "state": "acting",
            "metadata": {
                "customer_id": "cust-12345",
                "issue_type": "billing_inquiry",
                "channel": "web_chat",
                "priority": "normal"
            }
        }
    }
    
    print("Step 1 - Chatbot handles initial interaction:")
    print(f"Tool call: {json.dumps(initial_interaction, indent=2)}")
    print()
    
    # Step 2: Escalation to human agent
    escalation_message = {
        "tool_name": "inngest_agent_kit:send_agent_message",
        "tool_args": {
            "from_agent": "chatbot-001",
            "to_agent": "human-agent-tier1",
            "message_type": "request_assistance",
            "content": {
                "reason": "complex_billing_question",
                "customer_context": {
                    "id": "cust-12345",
                    "tier": "premium",
                    "history": "3_previous_inquiries",
                    "sentiment": "frustrated"
                },
                "conversation_summary": "Customer questions about multiple billing discrepancies",
                "priority": "high"
            }
        }
    }
    
    print("Step 2 - Escalation to human agent:")
    print(f"Tool call: {json.dumps(escalation_message, indent=2)}")
    print()
    
    # Step 3: Parallel workflow for complex case
    complex_case_workflow = {
        "tool_name": "inngest_agent_kit:start_multi_agent_workflow",
        "tool_args": {
            "workflow_id": f"customer-case-{uuid.uuid4()}",
            "coordination_strategy": "parallel",
            "agent_assignments": {
                "billing-specialist": {
                    "role": "billing_analysis",
                    "task": "analyze_billing_history",
                    "customer_id": "cust-12345",
                    "focus": "discrepancy_identification"
                },
                "account-manager": {
                    "role": "relationship_management",
                    "task": "customer_relationship_review",
                    "customer_id": "cust-12345",
                    "focus": "retention_strategy"
                },
                "technical-support": {
                    "role": "technical_analysis",
                    "task": "system_logs_review",
                    "customer_id": "cust-12345",
                    "focus": "billing_system_errors"
                }
            }
        }
    }
    
    print("Step 3 - Parallel investigation workflow:")
    print(f"Tool call: {json.dumps(complex_case_workflow, indent=2)}")
    print()
    
    print("This scenario demonstrates:")
    print("- State-driven escalation")
    print("- Context-aware agent communication")
    print("- Multi-agent parallel processing")
    print("- Real-time customer service coordination")
    print()


async def main():
    """Run all examples."""
    print("Inngest Agent Kit Integration Examples")
    print("=" * 50)
    print()
    
    await example_agent_state_management()
    await example_agent_communication()
    await example_multi_agent_workflow()
    await example_agent_workflow_creation()
    await example_agent_monitoring()
    await example_real_world_scenario()
    
    print("=== Configuration Notes ===")
    print("To enable Inngest Agent Kit, set these environment variables:")
    print("INNGEST_ENABLED=true")
    print("INNGEST_EVENT_KEY=your_event_key")
    print("INNGEST_SIGNING_KEY=your_signing_key  # optional")
    print("INNGEST_APP_ID=your_app_id  # optional, defaults to 'agent-zero'")
    print()
    print("The Agent Kit extends standard Inngest with:")
    print("- Agent state management")
    print("- Agent-to-agent communication patterns")
    print("- Multi-agent coordination strategies")
    print("- Sophisticated workflow orchestration")
    print("- Real-time monitoring and context tracking")
    print()
    print("Get your Inngest keys from: https://inngest.com")


if __name__ == "__main__":
    asyncio.run(main())
# Distributed Network of Agentic Cognitive Grammar

This document explains how to use the newly integrated distributed network of agentic cognitive grammar capabilities in Agent Zero.

## Overview

The cognitive grammar framework enables Agent Zero to function as a distributed network where agents communicate using meaningful linguistic structures that embody cognitive understanding. This implementation follows Cognitive Grammar principles from linguistic theory, applying them to multi-agent coordination.

## Key Concepts

### Cognitive Grammar
Cognitive Grammar views language as embodied cognition, where linguistic structures are meaningful conceptual patterns. In our implementation:

- **Communicative Intents**: The purpose behind communication (request, inform, coordinate, delegate, query, confirm, reject, negotiate)
- **Cognitive Roles**: Semantic roles in interactions (agent, patient, experiencer, instrument, location, time, manner, purpose)  
- **Cognitive Frames**: Conceptual structures for understanding interactions (task_delegation, information_sharing, coordination)

### Distributed Network
The network topology enables:

- **Agent Discovery**: Find agents based on capabilities and cognitive profiles
- **Dynamic Connections**: Establish and manage connections between agents
- **Capability Matching**: Match agents with tasks based on their abilities
- **Network Resilience**: Handle agent disconnections and network changes

## Usage Examples

### 1. Using the Cognitive Network Tool

The `cognitive_network` tool provides access to all cognitive grammar and networking capabilities:

```json
{
    "thoughts": [
        "I need to coordinate with other agents for a complex task",
        "First I'll register my capabilities"
    ],
    "tool_name": "cognitive_network",
    "tool_args": {
        "method": "register_agent_capabilities",
        "capabilities": ["reasoning", "coordination", "planning"],
        "cognitive_profile": {
            "communication_style": "structured",
            "coordination_preference": "hierarchical"
        }
    }
}
```

### 2. Discovering Network Agents

Find agents with specific capabilities:

```json
{
    "thoughts": [
        "I need to find agents capable of data analysis",
        "Let me discover what agents are available"
    ],
    "tool_name": "cognitive_network",
    "tool_args": {
        "method": "discover_network_agents",
        "capability_filter": "data_analysis",
        "include_details": true
    }
}
```

### 3. Sending Cognitive Messages

Send structured messages using cognitive grammar:

```json
{
    "thoughts": [
        "I need to delegate this task to a specialist",
        "Using cognitive grammar to structure the delegation"
    ],
    "tool_name": "cognitive_network", 
    "tool_args": {
        "method": "send_cognitive_message",
        "to_agent": "data_specialist_001",
        "intent": "delegate",
        "content": {
            "task": "Analyze user behavior patterns",
            "constraints": ["complete within 24 hours", "use anonymized data"],
            "expected_outcome": "Behavioral insights report",
            "resources": ["database_access", "analysis_tools"]
        },
        "frame_type": "task_delegation"
    }
}
```

### 4. Coordinating with Multiple Agents

Find and coordinate with optimal partners:

```json
{
    "thoughts": [
        "This complex project needs multiple specialists",
        "Let me coordinate with agents who have the right capabilities"
    ],
    "tool_name": "cognitive_network",
    "tool_args": {
        "method": "coordinate_with_agents", 
        "task_description": "Build distributed microservices architecture",
        "required_capabilities": ["computation", "planning", "coordination"],
        "max_partners": 3,
        "coordination_type": "synchronous"
    }
}
```

### 5. Broadcasting to Network

Send messages to multiple agents:

```json
{
    "thoughts": [
        "I need to inform all coordination agents about the new protocol",
        "Broadcasting this update to relevant agents"
    ],
    "tool_name": "cognitive_network",
    "tool_args": {
        "method": "broadcast_to_network",
        "intent": "inform",
        "content": {
            "update": "New coordination protocol v2.1 is now active",
            "changes": ["improved error handling", "better synchronization"],
            "effective_date": "2024-02-01"
        },
        "capability_filter": "coordination"
    }
}
```

## Available Methods

### Core Methods

- **send_cognitive_message**: Send structured cognitive message to another agent
- **discover_network_agents**: Discover agents in the distributed network
- **establish_agent_connection**: Establish connection with another agent
- **coordinate_with_agents**: Coordinate actions with multiple agents
- **register_agent_capabilities**: Register or update agent capabilities
- **get_network_topology**: Get current network topology information
- **find_coordination_partners**: Find optimal agents for collaboration
- **parse_cognitive_message**: Parse message using cognitive grammar
- **broadcast_to_network**: Broadcast message to multiple network agents

### Communicative Intents

- **request**: Requesting action or information
- **inform**: Providing information
- **coordinate**: Coordinating joint action
- **delegate**: Delegating subtasks
- **query**: Asking questions
- **confirm**: Confirming understanding
- **reject**: Rejecting proposals
- **negotiate**: Negotiating terms or conditions

### Agent Capabilities

- **computation**: Computational processing
- **data_analysis**: Data analysis and insights
- **communication**: Communication facilitation
- **scheduling**: Task and time management
- **coordination**: Multi-agent coordination
- **learning**: Machine learning and adaptation
- **reasoning**: Logical reasoning and inference
- **planning**: Strategic planning and optimization

### Cognitive Frame Types

- **task_delegation**: Delegating tasks to other agents
- **information_sharing**: Sharing information and knowledge
- **coordination**: Coordinating joint activities
- **information_query**: Querying for specific information

## Enhanced Call Subordinate

The existing `call_subordinate` tool has been enhanced with cognitive grammar support:

```json
{
    "thoughts": [
        "I need to create a subordinate for this specialized task",
        "The cognitive grammar will structure the delegation"
    ],
    "tool_name": "call_subordinate",
    "tool_args": {
        "message": "You are a data analysis specialist. Analyze the customer feedback data and provide insights.",
        "reset": "true",
        "cognitive_frame_type": "task_delegation"
    }
}
```

## Network Topology Management

The system supports multiple network topologies:

- **mesh**: Full mesh - all agents connected
- **star**: Star topology - hub and spokes  
- **ring**: Ring topology - circular connections
- **tree**: Hierarchical tree structure
- **hybrid**: Combination of topologies (default)

## Integration with Existing Features

The cognitive grammar framework integrates seamlessly with existing Agent Zero features:

- **Inngest Workflow Orchestration**: Enhanced with cognitive message routing
- **Task Scheduling**: Cognitive grammar for scheduled task coordination
- **Multi-Agent Hierarchy**: Structured communication between superior/subordinate agents
- **Memory System**: Cognitive messages can be stored and retrieved
- **Prompt System**: New prompts guide cognitive grammar usage

## Best Practices

1. **Use Appropriate Intents**: Choose the right communicative intent for your message purpose
2. **Provide Context**: Include relevant context in cognitive frames
3. **Match Capabilities**: Use capability-based discovery for optimal coordination
4. **Structure Content**: Organize message content clearly with constraints, resources, and outcomes
5. **Monitor Network**: Use topology information to understand agent relationships
6. **Handle Failures**: Implement graceful fallbacks for network issues

## Examples and Testing

- **demo_cognitive_grammar.py**: Comprehensive demonstration of all features
- **test_cognitive_comprehensive.py**: Full test suite with integration scenarios
- **test_cognitive_grammar_integration.py**: Basic integration testing

Run the demonstration to see the system in action:

```bash
python demo_cognitive_grammar.py
```

## Architecture

The cognitive grammar system consists of:

- **`python/helpers/cognitive_grammar.py`**: Core cognitive grammar framework
- **`python/helpers/distributed_network.py`**: Distributed network registry and management
- **`python/tools/cognitive_network.py`**: Agent tool for accessing cognitive capabilities
- **`prompts/default/agent.system.tool.cognitive_network.md`**: Tool documentation and usage guide
- **Enhanced `python/tools/call_subordinate.py`**: Backward-compatible cognitive grammar integration

This implementation enables Agent Zero to function as a true distributed network of agentic cognitive grammar, where agents communicate using meaningful linguistic structures that embody cognitive understanding and support sophisticated multi-agent coordination patterns.
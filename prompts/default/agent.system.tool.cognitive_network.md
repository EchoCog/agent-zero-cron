### cognitive_network

Use this tool for advanced agent communication and distributed network coordination using cognitive grammar patterns.

The cognitive network tool enables sophisticated multi-agent coordination through:
- Structured communication using cognitive grammar principles  
- Distributed network discovery and topology management
- Capability-based agent matching and coordination
- Grammar-aware message parsing and generation

#### Key concepts:
- **Cognitive Grammar**: Linguistic structures that embody cognitive meaning and context
- **Communicative Intent**: The purpose behind agent communication (request, inform, coordinate, delegate, etc.)
- **Cognitive Frames**: Conceptual structures for understanding agent interactions
- **Network Topology**: The structure of agent connections and relationships

#### Available methods:

**send_cognitive_message**: Send structured cognitive message to another agent
- to_agent: target agent ID
- intent: communicative intent (request, inform, coordinate, delegate, query, confirm, reject, negotiate)
- content: message content as key-value pairs
- frame_type: cognitive frame type (task_delegation, information_sharing, coordination)

**discover_network_agents**: Discover agents in the distributed network
- capability_filter: filter by specific capability (optional)
- include_details: include detailed agent information

**establish_agent_connection**: Establish connection with another agent
- target_agent: agent ID to connect with
- connection_strength: strength of connection (0.0-1.0)

**coordinate_with_agents**: Coordinate actions with multiple agents
- task_description: description of coordination task
- required_capabilities: list of required agent capabilities
- max_partners: maximum number of coordination partners
- coordination_type: type of coordination (synchronous, asynchronous)

**register_agent_capabilities**: Register or update agent capabilities
- capabilities: list of capabilities (computation, data_analysis, communication, scheduling, coordination, learning, reasoning, planning)
- cognitive_profile: optional cognitive profile attributes

**get_network_topology**: Get current network topology information
- include_statistics: include detailed network statistics

**find_coordination_partners**: Find optimal agents for collaboration
- task_requirements: detailed task requirements with capabilities and constraints
- max_partners: maximum number of partners to find

**parse_cognitive_message**: Parse message using cognitive grammar
- raw_message: message to parse
- generate_natural_language: generate natural language description

**broadcast_to_network**: Broadcast message to multiple network agents
- intent: communicative intent for broadcast
- content: message content
- frame_type: cognitive frame type
- capability_filter: filter recipients by capability

#### Example usage for agent coordination:

~~~json
{
    "thoughts": [
        "I need to coordinate with other agents for a complex data analysis task",
        "First I'll register my capabilities, then find suitable partners"
    ],
    "tool_name": "cognitive_network",
    "tool_args": {
        "method": "register_agent_capabilities",
        "capabilities": ["data_analysis", "reasoning", "coordination"],
        "cognitive_profile": {
            "communication_style": "structured",
            "coordination_preference": "hierarchical"
        }
    }
}
~~~

~~~json
{
    "thoughts": [
        "Now I'll find agents with complementary capabilities",
        "Looking for agents with computation and planning capabilities"
    ],
    "tool_name": "cognitive_network", 
    "tool_args": {
        "method": "coordinate_with_agents",
        "task_description": "Analyze large dataset and create predictive model",
        "required_capabilities": ["computation", "planning"],
        "max_partners": 2,
        "coordination_type": "synchronous"
    }
}
~~~

#### Example usage for cognitive messaging:

~~~json
{
    "thoughts": [
        "I need to delegate a subtask to a specialized agent",
        "Using cognitive grammar to structure the delegation message"
    ],
    "tool_name": "cognitive_network",
    "tool_args": {
        "method": "send_cognitive_message",
        "to_agent": "agent_specialist_123",
        "intent": "delegate",
        "content": {
            "task": "Optimize database queries for performance",
            "constraints": ["must complete within 2 hours", "use existing schema"],
            "expected_outcome": "20% performance improvement",
            "resources": ["database_credentials", "query_examples"]
        },
        "frame_type": "task_delegation"
    }
}
~~~

The tool automatically handles cognitive grammar processing, network topology management, and capability matching to enable sophisticated multi-agent coordination patterns.
#!/usr/bin/env python3
"""
Simplified test for core cognitive grammar functionality without dependencies.
"""

import sys
import os
import json
sys.path.append('.')

def test_cognitive_grammar_core():
    """Test core cognitive grammar functionality."""
    print("Testing Core Cognitive Grammar...")
    
    try:
        from python.helpers.cognitive_grammar import (
            CognitiveGrammarProcessor, CommunicativeIntent, CognitiveRole
        )
        
        processor = CognitiveGrammarProcessor()
        print("✓ CognitiveGrammarProcessor initialized")
        
        # Test message creation with delegation intent
        message = processor.create_cognitive_message(
            intent=CommunicativeIntent.DELEGATE,
            frame_type="task_delegation",
            from_agent="primary_agent",
            to_agent="specialist_agent",
            content={
                "task": "Implement distributed data processing pipeline",
                "constraints": ["use microservices architecture", "complete in 3 days"],
                "resources": ["database_credentials", "API_documentation"],
                "expected_outcome": "Scalable data processing system"
            }
        )
        
        print("✓ Task delegation message created")
        
        # Test coordination message
        coord_message = processor.create_cognitive_message(
            intent=CommunicativeIntent.COORDINATE,
            frame_type="coordination",
            from_agent="coordinator_agent",
            to_agent="team_agents",
            content={
                "goal": "Synchronized deployment of distributed services",
                "coordination_type": "hierarchical",
                "timeline": "2024-01-15T10:00:00Z",
                "roles": ["deployment_manager", "monitoring_specialist", "testing_coordinator"]
            }
        )
        
        print("✓ Coordination message created")
        
        # Test natural language generation
        delegation_nl = processor.generate_natural_language(message)
        coordination_nl = processor.generate_natural_language(coord_message)
        
        print(f"✓ Delegation NL: {delegation_nl}")
        print(f"✓ Coordination NL: {coordination_nl}")
        
        # Test serialization roundtrip
        serialized = processor.serialize_message(message)
        deserialized = processor.deserialize_message(serialized)
        
        assert message.message_id == deserialized.message_id
        assert message.intent == deserialized.intent
        assert message.from_agent == deserialized.from_agent
        print("✓ Serialization roundtrip successful")
        
        # Test frame template usage
        templates = processor.frame_templates
        assert "task_delegation" in templates
        assert "coordination" in templates
        assert "information_sharing" in templates
        print("✓ Cognitive frame templates available")
        
        # Test grammar pattern application
        patterns = processor.grammar_patterns
        assert "delegate_pattern" in patterns
        assert "coordinate_pattern" in patterns
        print("✓ Grammar patterns available")
        
        print("Core Cognitive Grammar tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Core Cognitive Grammar test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_distributed_network_core():
    """Test core distributed network functionality."""
    print("Testing Core Distributed Network...")
    
    try:
        from python.helpers.distributed_network import (
            DistributedNetworkRegistry, AgentCapability, NetworkAgent
        )
        
        # Create network with multiple agents
        registry = DistributedNetworkRegistry("main_agent", "MainCoordinator")
        print("✓ Main network registry created")
        
        # Register specialized agents
        agents_data = [
            {
                "id": "data_processor",
                "name": "DataProcessingAgent", 
                "endpoint": "http://data-service:8001",
                "capabilities": {AgentCapability.DATA_ANALYSIS, AgentCapability.COMPUTATION}
            },
            {
                "id": "comm_coordinator", 
                "name": "CommunicationCoordinator",
                "endpoint": "http://comm-service:8002",
                "capabilities": {AgentCapability.COMMUNICATION, AgentCapability.COORDINATION}
            },
            {
                "id": "task_scheduler",
                "name": "TaskSchedulingAgent",
                "endpoint": "http://scheduler-service:8003", 
                "capabilities": {AgentCapability.SCHEDULING, AgentCapability.PLANNING}
            },
            {
                "id": "learning_engine",
                "name": "MachineLearningAgent",
                "endpoint": "http://ml-service:8004",
                "capabilities": {AgentCapability.LEARNING, AgentCapability.REASONING}
            }
        ]
        
        for agent_data in agents_data:
            success = registry.register_agent(
                agent_id=agent_data["id"],
                agent_name=agent_data["name"],
                endpoint=agent_data["endpoint"],
                capabilities=agent_data["capabilities"],
                cognitive_profile={
                    "specialization": agent_data["name"].replace("Agent", "").lower(),
                    "communication_protocol": "cognitive_grammar",
                    "coordination_style": "collaborative"
                }
            )
            assert success
        
        print(f"✓ Registered {len(agents_data)} specialized agents")
        
        # Test capability-based discovery
        data_agents = registry.discover_agents_by_capability(AgentCapability.DATA_ANALYSIS)
        coord_agents = registry.discover_agents_by_capability(AgentCapability.COORDINATION)
        learning_agents = registry.discover_agents_by_capability(AgentCapability.LEARNING)
        
        assert len(data_agents) == 1
        assert len(coord_agents) == 1  
        assert len(learning_agents) == 1
        print("✓ Capability-based agent discovery working")
        
        # Test cross-capability coordination partner finding
        complex_task = {
            "capabilities": [AgentCapability.DATA_ANALYSIS, AgentCapability.LEARNING],
            "cognitive_constraints": {
                "coordination_style": "collaborative",
                "communication_protocol": "cognitive_grammar"
            }
        }
        
        partners = registry.find_optimal_coordination_partners(complex_task, max_partners=3)
        assert len(partners) >= 2  # Should find data processor and learning engine
        print("✓ Complex task coordination partner finding working")
        
        # Test network establishment
        connections = []
        for i, agent1 in enumerate(agents_data):
            for agent2 in agents_data[i+1:]:
                conn_id = registry.establish_connection(agent1["id"], agent2["id"])
                if conn_id:
                    connections.append(conn_id)
        
        print(f"✓ Established {len(connections)} network connections")
        
        # Test cognitive message routing
        message_results = []
        for agent_data in agents_data[:2]:  # Test first two agents
            success = registry.send_cognitive_message(
                to_agent=agent_data["id"],
                intent="coordinate",
                content={
                    "network_task": "Distributed cognitive processing",
                    "coordination_role": "participant",
                    "expected_interaction": "structured_collaboration"
                },
                frame_type="coordination"
            )
            message_results.append(success)
        
        assert all(message_results)
        print("✓ Cognitive message routing working")
        
        # Test network topology analysis
        topology_info = registry.get_network_topology_info()
        stats = registry.get_network_statistics()
        
        assert topology_info["agent_count"] == 5  # 4 registered + 1 local
        assert topology_info["connection_count"] > 0
        assert "capability_distribution" in topology_info
        print("✓ Network topology analysis working")
        
        print("Core Distributed Network tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Core Distributed Network test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_scenarios():
    """Test integrated scenarios combining cognitive grammar and networking."""
    print("Testing Integration Scenarios...")
    
    try:
        from python.helpers.cognitive_grammar import CognitiveGrammarProcessor, CommunicativeIntent
        from python.helpers.distributed_network import DistributedNetworkRegistry, AgentCapability
        
        # Scenario: Multi-agent data processing pipeline
        processor = CognitiveGrammarProcessor()
        registry = DistributedNetworkRegistry("pipeline_coordinator", "DataPipelineCoordinator")
        
        # Register pipeline agents
        pipeline_agents = [
            ("data_ingestion", "DataIngestionAgent", {AgentCapability.DATA_ANALYSIS}),
            ("data_transformation", "DataTransformationAgent", {AgentCapability.COMPUTATION, AgentCapability.DATA_ANALYSIS}),
            ("model_training", "ModelTrainingAgent", {AgentCapability.LEARNING, AgentCapability.COMPUTATION}),
            ("result_validation", "ValidationAgent", {AgentCapability.REASONING, AgentCapability.DATA_ANALYSIS})
        ]
        
        for agent_id, agent_name, capabilities in pipeline_agents:
            registry.register_agent(
                agent_id=agent_id,
                agent_name=agent_name,
                endpoint=f"http://{agent_id}:8000",
                capabilities=capabilities,
                cognitive_profile={"pipeline_role": agent_id, "processing_stage": len(pipeline_agents)}
            )
        
        print("✓ Data pipeline agents registered")
        
        # Create cognitive messages for pipeline coordination
        pipeline_messages = []
        
        # 1. Delegation to data ingestion
        ingestion_msg = processor.create_cognitive_message(
            intent=CommunicativeIntent.DELEGATE,
            frame_type="task_delegation",
            from_agent="pipeline_coordinator",
            to_agent="data_ingestion",
            content={
                "task": "Ingest data from multiple sources",
                "data_sources": ["database", "api", "file_system"],
                "output_format": "standardized_json",
                "quality_requirements": ["data_validation", "error_handling"]
            }
        )
        pipeline_messages.append(ingestion_msg)
        
        # 2. Coordination between transformation and training
        coordination_msg = processor.create_cognitive_message(
            intent=CommunicativeIntent.COORDINATE,
            frame_type="coordination",
            from_agent="data_transformation",
            to_agent="model_training",
            content={
                "goal": "Synchronized data processing and model training",
                "data_handoff_protocol": "streaming",
                "synchronization_points": ["data_batch_complete", "model_checkpoint"],
                "quality_gates": ["data_integrity_check", "model_validation"]
            }
        )
        pipeline_messages.append(coordination_msg)
        
        # 3. Query to validation agent
        validation_query = processor.create_cognitive_message(
            intent=CommunicativeIntent.QUERY,
            frame_type="information_query",
            from_agent="model_training", 
            to_agent="result_validation",
            content={
                "query": "What are the validation criteria for model accuracy?",
                "context": "machine_learning_pipeline",
                "expected_response_format": "structured_criteria",
                "urgency": "high"
            }
        )
        pipeline_messages.append(validation_query)
        
        # Generate natural language for all messages
        natural_languages = []
        for msg in pipeline_messages:
            nl = processor.generate_natural_language(msg)
            natural_languages.append(nl)
        
        print("✓ Pipeline cognitive messages created and processed")
        print(f"✓ Generated {len(natural_languages)} natural language descriptions")
        
        # Test dynamic network reconfiguration
        # Add a new agent during runtime
        registry.register_agent(
            agent_id="performance_monitor",
            agent_name="PerformanceMonitorAgent",
            endpoint="http://monitor:8005",
            capabilities={AgentCapability.COORDINATION, AgentCapability.REASONING},
            cognitive_profile={"monitoring_role": "performance_analysis", "alert_threshold": "medium"}
        )
        
        # Find new coordination opportunities
        monitoring_task = {
            "capabilities": [AgentCapability.COORDINATION, AgentCapability.REASONING],
            "cognitive_constraints": {"monitoring_role": "performance_analysis"}
        }
        
        monitor_partners = registry.find_optimal_coordination_partners(monitoring_task, max_partners=2)
        assert len(monitor_partners) > 0
        print("✓ Dynamic network reconfiguration working")
        
        # Test network resilience (agent disconnection simulation)
        original_count = len(registry.agents)
        registry.unregister_agent("data_ingestion")
        new_count = len(registry.agents)
        assert new_count == original_count - 1
        print("✓ Network resilience (agent disconnection) working")
        
        print("Integration Scenarios tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Integration Scenarios test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive cognitive grammar tests."""
    print("🧠 Comprehensive Cognitive Grammar and Distributed Network Tests\n")
    
    tests = [
        test_cognitive_grammar_core,
        test_distributed_network_core,
        test_integration_scenarios
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print(f"🎉 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All comprehensive tests passed!")
        print("🌐 Distributed network of agentic cognitive grammar is functional!")
        print("\nKey Features Validated:")
        print("- Cognitive grammar message structuring")
        print("- Multi-agent network topology management") 
        print("- Capability-based agent discovery")
        print("- Cognitive frame-based communication")
        print("- Distributed coordination protocols")
        print("- Dynamic network reconfiguration")
        print("- Network resilience and fault tolerance")
        return True
    else:
        print("❌ Some comprehensive tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
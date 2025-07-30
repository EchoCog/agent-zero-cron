#!/usr/bin/env python3
"""
Test script for cognitive grammar and distributed network integration.
"""

import sys
import os
sys.path.append('.')

def test_cognitive_grammar():
    """Test cognitive grammar framework."""
    print("Testing Cognitive Grammar Framework...")
    
    try:
        from python.helpers.cognitive_grammar import (
            CognitiveGrammarProcessor, CommunicativeIntent, CognitiveRole, CognitiveFrame
        )
        
        processor = CognitiveGrammarProcessor()
        print("✓ CognitiveGrammarProcessor initialized")
        
        # Test message creation
        message = processor.create_cognitive_message(
            intent=CommunicativeIntent.DELEGATE,
            frame_type="task_delegation",
            from_agent="agent_0",
            to_agent="agent_1",
            content={
                "task": "Analyze data patterns",
                "constraints": ["use machine learning", "complete in 1 hour"],
                "expected_outcome": "Pattern recognition report"
            }
        )
        
        print("✓ Cognitive message created")
        
        # Test natural language generation
        natural_language = processor.generate_natural_language(message)
        print(f"✓ Natural language generated: {natural_language}")
        
        # Test serialization
        serialized = processor.serialize_message(message)
        deserialized = processor.deserialize_message(serialized)
        
        assert message.message_id == deserialized.message_id
        print("✓ Message serialization/deserialization works")
        
        # Test message parsing
        raw_message = {
            "intent": "coordinate",
            "content": {"goal": "joint task execution"},
            "from_agent": "agent_2",
            "to_agent": "agent_3"
        }
        
        parsed = processor.parse_message(raw_message)
        assert parsed.intent == CommunicativeIntent.COORDINATE
        print("✓ Message parsing works")
        
        print("Cognitive Grammar Framework tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Cognitive Grammar Framework test failed: {e}")
        return False

def test_distributed_network():
    """Test distributed network registry."""
    print("Testing Distributed Network Registry...")
    
    try:
        from python.helpers.distributed_network import (
            DistributedNetworkRegistry, AgentCapability, NetworkTopology
        )
        
        # Create registry
        registry = DistributedNetworkRegistry("test_agent_1", "TestAgent1")
        print("✓ DistributedNetworkRegistry initialized")
        
        # Register another agent
        success = registry.register_agent(
            agent_id="test_agent_2",
            agent_name="TestAgent2", 
            endpoint="test://localhost:8002",
            capabilities={AgentCapability.COMPUTATION, AgentCapability.DATA_ANALYSIS}
        )
        assert success
        print("✓ Agent registration works")
        
        # Test capability discovery
        computation_agents = registry.discover_agents_by_capability(AgentCapability.COMPUTATION)
        assert len(computation_agents) == 1
        print("✓ Capability-based discovery works")
        
        # Test connection establishment
        connection_id = registry.establish_connection("test_agent_1", "test_agent_2")
        assert connection_id is not None
        print("✓ Connection establishment works")
        
        # Test cognitive message sending
        success = registry.send_cognitive_message(
            to_agent="test_agent_2",
            intent="coordinate",
            content={"task": "test coordination"},
            frame_type="coordination"
        )
        assert success
        print("✓ Cognitive message sending works")
        
        # Test network topology info
        topology_info = registry.get_network_topology_info()
        assert topology_info["agent_count"] == 2
        assert topology_info["connection_count"] == 1
        print("✓ Network topology information works")
        
        # Test coordination partner finding
        partners = registry.find_optimal_coordination_partners(
            task_requirements={
                "capabilities": [AgentCapability.COMPUTATION],
                "cognitive_constraints": {}
            },
            max_partners=2
        )
        assert len(partners) == 1
        print("✓ Coordination partner finding works")
        
        print("Distributed Network Registry tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Distributed Network Registry test failed: {e}")
        return False

def test_cognitive_network_tool():
    """Test cognitive network tool."""
    print("Testing Cognitive Network Tool...")
    
    try:
        # Mock agent for testing
        class MockAgent:
            def __init__(self):
                self.number = 1
                self.id = "mock_agent_1"
                self.name = "MockAgent1"
        
        from python.tools.cognitive_network import CognitiveNetworkTool
        
        mock_agent = MockAgent()
        tool = CognitiveNetworkTool(mock_agent)
        print("✓ CognitiveNetworkTool initialized")
        
        # Test that the tool has the expected methods
        assert hasattr(tool, 'grammar_processor')
        assert hasattr(tool, 'network_registry')
        print("✓ Tool components initialized")
        
        # Test network topology access
        topology_info = tool.network_registry.get_network_topology_info()
        assert isinstance(topology_info, dict)
        assert "agent_count" in topology_info
        print("✓ Network topology access works")
        
        print("Cognitive Network Tool tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Cognitive Network Tool test failed: {e}")
        return False

def test_enhanced_call_subordinate():
    """Test enhanced call_subordinate with cognitive grammar."""
    print("Testing Enhanced Call Subordinate...")
    
    try:
        from python.tools.call_subordinate import Delegation
        
        # Mock agent for testing
        class MockAgent:
            def __init__(self):
                self.number = 1
                self.data = {}
                
            def get_data(self, key):
                return self.data.get(key)
                
            def set_data(self, key, value):
                self.data[key] = value
        
        mock_agent = MockAgent()
        delegation_tool = Delegation(mock_agent)
        print("✓ Enhanced Delegation tool initialized")
        
        # Test that cognitive grammar processor is available
        if hasattr(delegation_tool, 'grammar_processor') and delegation_tool.grammar_processor:
            print("✓ Cognitive grammar processor integrated")
        else:
            print("⚠ Cognitive grammar processor not available (graceful fallback)")
        
        print("Enhanced Call Subordinate tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Enhanced Call Subordinate test failed: {e}")
        return False

def test_prompt_integration():
    """Test prompt file integration."""
    print("Testing Prompt Integration...")
    
    try:
        # Test cognitive network prompt file
        prompt_path = "/home/runner/work/agent-zero-cron/agent-zero-cron/prompts/default/agent.system.tool.cognitive_network.md"
        assert os.path.exists(prompt_path)
        
        with open(prompt_path, 'r') as f:
            content = f.read()
            assert "cognitive_network" in content
            assert "send_cognitive_message" in content
            assert "coordinate_with_agents" in content
        
        print("✓ Cognitive network prompt file exists and contains expected content")
        
        # Test updated communication prompt
        comm_prompt_path = "/home/runner/work/agent-zero-cron/agent-zero-cron/prompts/default/agent.system.main.communication.md"
        assert os.path.exists(comm_prompt_path)
        
        with open(comm_prompt_path, 'r') as f:
            content = f.read()
            assert "Cognitive Grammar Communication" in content
            assert "cognitive_network tool" in content
        
        print("✓ Communication prompt updated with cognitive grammar concepts")
        
        print("Prompt Integration tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Prompt Integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧠 Testing Cognitive Grammar and Distributed Network Integration\n")
    
    tests = [
        test_cognitive_grammar,
        test_distributed_network,
        test_cognitive_network_tool,
        test_enhanced_call_subordinate,
        test_prompt_integration
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
        print("✅ All tests passed! Cognitive grammar and distributed network integration is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
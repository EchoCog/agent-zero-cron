"""
Distributed Network Registry for Agent Zero

This module implements a distributed network registry system that allows agents
to discover each other, form networks, and coordinate using cognitive grammar patterns.
The system supports both local and remote agent discovery.
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable, Union
import threading
import hashlib

from python.helpers.cognitive_grammar import (
    CognitiveGrammarProcessor, CognitiveMessage, CommunicativeIntent
)

# Optional dependency for print styling
try:
    from python.helpers.print_style import PrintStyle as _PrintStyle
    class PrintStyle:
        def __init__(self, color=None, **kwargs):
            if color:
                self._printer = _PrintStyle(font_color=color, **kwargs)
            else:
                self._printer = _PrintStyle(**kwargs)
        def print(self, msg):
            self._printer.print(msg)
except ImportError:
    class PrintStyle:
        def __init__(self, **kwargs):
            pass
        def print(self, msg):
            print(f"[DistributedNetwork] {msg}")


class NetworkTopology(Enum):
    """Network topology types for agent networks."""
    MESH = "mesh"           # Full mesh - all agents connected
    STAR = "star"           # Star topology - hub and spokes
    RING = "ring"           # Ring topology - circular connections
    TREE = "tree"           # Hierarchical tree structure
    HYBRID = "hybrid"       # Combination of topologies


class AgentCapability(Enum):
    """Agent capabilities for network discovery and matching."""
    COMPUTATION = "computation"
    DATA_ANALYSIS = "data_analysis" 
    COMMUNICATION = "communication"
    SCHEDULING = "scheduling"
    COORDINATION = "coordination"
    LEARNING = "learning"
    REASONING = "reasoning"
    PLANNING = "planning"


@dataclass
class NetworkAgent:
    """Represents an agent in the distributed network."""
    agent_id: str
    agent_name: str
    endpoint: str  # Network endpoint for communication
    capabilities: Set[AgentCapability] = field(default_factory=set)
    cognitive_profile: Dict[str, Any] = field(default_factory=dict)
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    trust_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NetworkConnection:
    """Represents a connection between two agents."""
    connection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_a: str = ""
    agent_b: str = ""
    connection_strength: float = 1.0
    established_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_interaction: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    interaction_count: int = 0
    cognitive_compatibility: float = 1.0


class DistributedNetworkRegistry:
    """
    Registry for managing distributed agent networks with cognitive grammar support.
    """
    
    def __init__(self, local_agent_id: str, local_agent_name: str = None):
        self.local_agent_id = local_agent_id
        self.local_agent_name = local_agent_name or f"Agent-{local_agent_id[:8]}"
        
        # Network state
        self.agents: Dict[str, NetworkAgent] = {}
        self.connections: Dict[str, NetworkConnection] = {}
        self.topology = NetworkTopology.HYBRID
        
        # Cognitive grammar processor
        self.grammar_processor = CognitiveGrammarProcessor()
        
        # Network discovery
        self.discovery_enabled = True
        self.discovery_interval = 30  # seconds
        self.heartbeat_interval = 10  # seconds
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "agent_discovered": [],
            "agent_lost": [],
            "message_received": [],
            "network_topology_changed": []
        }
        
        # Threading
        self._lock = threading.RLock()
        self._discovery_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Register local agent
        self.register_local_agent()
    
    def register_local_agent(self):
        """Register the local agent in the network."""
        local_agent = NetworkAgent(
            agent_id=self.local_agent_id,
            agent_name=self.local_agent_name,
            endpoint="local://localhost",
            capabilities={
                AgentCapability.COMMUNICATION,
                AgentCapability.REASONING,
                AgentCapability.COORDINATION
            },
            cognitive_profile={
                "communication_style": "cognitive_grammar",
                "reasoning_model": "langchain",
                "coordination_protocol": "inngest"
            }
        )
        
        with self._lock:
            self.agents[self.local_agent_id] = local_agent
    
    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        endpoint: str,
        capabilities: Optional[Set[AgentCapability]] = None,
        cognitive_profile: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register a new agent in the network."""
        
        if not agent_id or not endpoint:
            return False
        
        agent = NetworkAgent(
            agent_id=agent_id,
            agent_name=agent_name,
            endpoint=endpoint,
            capabilities=capabilities or set(),
            cognitive_profile=cognitive_profile or {}
        )
        
        with self._lock:
            is_new = agent_id not in self.agents
            self.agents[agent_id] = agent
            
            if is_new:
                self._emit_event("agent_discovered", agent)
                PrintStyle(color="green").print(f"[DistributedNetwork] Agent discovered: {agent_name} ({agent_id[:8]})")
        
        return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the network."""
        
        with self._lock:
            agent = self.agents.pop(agent_id, None)
            if agent:
                # Remove connections involving this agent
                connections_to_remove = [
                    conn_id for conn_id, conn in self.connections.items()
                    if conn.agent_a == agent_id or conn.agent_b == agent_id
                ]
                
                for conn_id in connections_to_remove:
                    del self.connections[conn_id]
                
                self._emit_event("agent_lost", agent)
                PrintStyle(color="yellow").print(f"[DistributedNetwork] Agent lost: {agent.agent_name} ({agent_id[:8]})")
                return True
        
        return False
    
    def establish_connection(
        self,
        agent_a: str,
        agent_b: str,
        connection_strength: float = 1.0
    ) -> Optional[str]:
        """Establish a connection between two agents."""
        
        if agent_a not in self.agents or agent_b not in self.agents:
            return None
        
        # Check if connection already exists
        existing_conn = self.get_connection(agent_a, agent_b)
        if existing_conn:
            return existing_conn.connection_id
        
        # Calculate cognitive compatibility
        agent_a_profile = self.agents[agent_a].cognitive_profile
        agent_b_profile = self.agents[agent_b].cognitive_profile
        compatibility = self._calculate_cognitive_compatibility(agent_a_profile, agent_b_profile)
        
        connection = NetworkConnection(
            agent_a=agent_a,
            agent_b=agent_b,
            connection_strength=connection_strength,
            cognitive_compatibility=compatibility
        )
        
        with self._lock:
            self.connections[connection.connection_id] = connection
        
        PrintStyle(color="blue").print(
            f"[DistributedNetwork] Connection established: {agent_a[:8]} <-> {agent_b[:8]} "
            f"(compatibility: {compatibility:.2f})"
        )
        
        return connection.connection_id
    
    def get_connection(self, agent_a: str, agent_b: str) -> Optional[NetworkConnection]:
        """Get connection between two agents (bidirectional)."""
        
        with self._lock:
            for connection in self.connections.values():
                if ((connection.agent_a == agent_a and connection.agent_b == agent_b) or
                    (connection.agent_a == agent_b and connection.agent_b == agent_a)):
                    return connection
        
        return None
    
    def send_cognitive_message(
        self,
        to_agent: str,
        intent: Union[CommunicativeIntent, str],
        content: Dict[str, Any],
        frame_type: str = "information_sharing"
    ) -> bool:
        """Send a cognitive grammar message to another agent."""
        
        if to_agent not in self.agents:
            return False
        
        # Convert string intent to enum if needed
        if isinstance(intent, str):
            try:
                intent = CommunicativeIntent(intent.lower())
            except ValueError:
                intent = CommunicativeIntent.INFORM
        
        # Create cognitive message
        cognitive_message = self.grammar_processor.create_cognitive_message(
            intent=intent,
            frame_type=frame_type,
            from_agent=self.local_agent_id,
            to_agent=to_agent,
            content=content,
            context={"network_registry": True}
        )
        
        # Update connection interaction
        connection = self.get_connection(self.local_agent_id, to_agent)
        if connection:
            with self._lock:
                connection.last_interaction = datetime.now(timezone.utc)
                connection.interaction_count += 1
        
        # Emit message event
        self._emit_event("message_received", {
            "message": cognitive_message,
            "serialized": self.grammar_processor.serialize_message(cognitive_message)
        })
        
        return True
    
    def discover_agents_by_capability(
        self,
        capability: AgentCapability,
        exclude_self: bool = True
    ) -> List[NetworkAgent]:
        """Discover agents with specific capabilities."""
        
        agents = []
        with self._lock:
            for agent in self.agents.values():
                if exclude_self and agent.agent_id == self.local_agent_id:
                    continue
                if capability in agent.capabilities:
                    agents.append(agent)
        
        return agents
    
    def find_optimal_coordination_partners(
        self,
        task_requirements: Dict[str, Any],
        max_partners: int = 3
    ) -> List[NetworkAgent]:
        """Find optimal agents for coordination based on task requirements."""
        
        required_capabilities = set(task_requirements.get("capabilities", []))
        cognitive_constraints = task_requirements.get("cognitive_constraints", {})
        
        candidates = []
        
        with self._lock:
            for agent in self.agents.values():
                if agent.agent_id == self.local_agent_id:
                    continue
                
                # Check capability match
                capability_match = len(required_capabilities.intersection(agent.capabilities))
                if capability_match == 0:
                    continue
                
                # Check cognitive compatibility
                compatibility = self._evaluate_cognitive_match(
                    agent.cognitive_profile,
                    cognitive_constraints
                )
                
                score = (capability_match / len(required_capabilities)) * compatibility * agent.trust_score
                candidates.append((agent, score))
        
        # Sort by score and return top candidates
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [agent for agent, score in candidates[:max_partners]]
    
    def get_network_topology_info(self) -> Dict[str, Any]:
        """Get current network topology information."""
        
        with self._lock:
            agent_count = len(self.agents)
            connection_count = len(self.connections)
            
            # Calculate network metrics
            connectivity = (connection_count * 2) / (agent_count * (agent_count - 1)) if agent_count > 1 else 0
            
            agent_capabilities = {}
            for agent in self.agents.values():
                for cap in agent.capabilities:
                    agent_capabilities[cap.value] = agent_capabilities.get(cap.value, 0) + 1
            
            return {
                "topology": self.topology.value,
                "agent_count": agent_count,
                "connection_count": connection_count,
                "connectivity_ratio": connectivity,
                "local_agent": self.local_agent_id,
                "capability_distribution": agent_capabilities,
                "average_trust_score": sum(a.trust_score for a in self.agents.values()) / agent_count if agent_count > 0 else 0
            }
    
    def _calculate_cognitive_compatibility(
        self,
        profile_a: Dict[str, Any],
        profile_b: Dict[str, Any]
    ) -> float:
        """Calculate cognitive compatibility between two agent profiles."""
        
        # Simple compatibility calculation based on shared attributes
        shared_keys = set(profile_a.keys()).intersection(set(profile_b.keys()))
        if not shared_keys:
            return 0.5  # Default compatibility
        
        matches = 0
        for key in shared_keys:
            if profile_a[key] == profile_b[key]:
                matches += 1
        
        return matches / len(shared_keys)
    
    def _evaluate_cognitive_match(
        self,
        agent_profile: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> float:
        """Evaluate how well an agent profile matches cognitive constraints."""
        
        if not constraints:
            return 1.0
        
        matches = 0
        total_constraints = len(constraints)
        
        for key, required_value in constraints.items():
            agent_value = agent_profile.get(key)
            if agent_value == required_value:
                matches += 1
            elif isinstance(required_value, list) and agent_value in required_value:
                matches += 1
        
        return matches / total_constraints
    
    def _emit_event(self, event_type: str, data: Any):
        """Emit network event to registered handlers."""
        
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                PrintStyle(color="red").print(f"[DistributedNetwork] Event handler error: {e}")
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler for network events."""
        
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
    
    def start_discovery(self):
        """Start network discovery and heartbeat tasks."""
        
        self._running = True
        PrintStyle(color="green").print("[DistributedNetwork] Network discovery started")
    
    def stop_discovery(self):
        """Stop network discovery and heartbeat tasks."""
        
        self._running = False
        if self._discovery_task:
            self._discovery_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        
        PrintStyle(color="yellow").print("[DistributedNetwork] Network discovery stopped")
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an agent."""
        
        with self._lock:
            agent = self.agents.get(agent_id)
            if not agent:
                return None
            
            connections = [
                conn for conn in self.connections.values()
                if conn.agent_a == agent_id or conn.agent_b == agent_id
            ]
            
            return {
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "endpoint": agent.endpoint,
                "capabilities": [cap.value for cap in agent.capabilities],
                "cognitive_profile": agent.cognitive_profile,
                "trust_score": agent.trust_score,
                "last_seen": agent.last_seen.isoformat(),
                "connection_count": len(connections),
                "metadata": agent.metadata
            }
    
    def update_agent_capabilities(
        self,
        agent_id: str,
        capabilities: Set[AgentCapability]
    ) -> bool:
        """Update agent capabilities."""
        
        with self._lock:
            agent = self.agents.get(agent_id)
            if agent:
                agent.capabilities = capabilities
                agent.last_seen = datetime.now(timezone.utc)
                return True
        
        return False
    
    def get_network_statistics(self) -> Dict[str, Any]:
        """Get comprehensive network statistics."""
        
        with self._lock:
            topology_info = self.get_network_topology_info()
            
            # Connection statistics
            connection_strengths = [conn.connection_strength for conn in self.connections.values()]
            cognitive_compatibilities = [conn.cognitive_compatibility for conn in self.connections.values()]
            
            # Agent statistics
            trust_scores = [agent.trust_score for agent in self.agents.values()]
            
            return {
                **topology_info,
                "connection_stats": {
                    "avg_strength": sum(connection_strengths) / len(connection_strengths) if connection_strengths else 0,
                    "avg_cognitive_compatibility": sum(cognitive_compatibilities) / len(cognitive_compatibilities) if cognitive_compatibilities else 0,
                    "total_interactions": sum(conn.interaction_count for conn in self.connections.values())
                },
                "agent_stats": {
                    "avg_trust_score": sum(trust_scores) / len(trust_scores) if trust_scores else 0,
                    "active_agents": len([a for a in self.agents.values() if (datetime.now(timezone.utc) - a.last_seen).seconds < 60])
                }
            }
"""
Cognitive Network Tool for Agent Zero

This tool integrates the cognitive grammar framework with distributed networking
capabilities, enabling agents to communicate using structured cognitive patterns
and coordinate in distributed networks.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from python.helpers.cognitive_grammar import (
    CognitiveGrammarProcessor, CommunicativeIntent, CognitiveMessage
)
from python.helpers.distributed_network import (
    DistributedNetworkRegistry, AgentCapability, NetworkTopology
)

# Optional dependencies
try:
    from python.helpers.tool import Tool, Response
except ImportError:
    # Mock for testing
    class Tool:
        def __init__(self, agent):
            self.agent = agent
            self.method = getattr(self, 'method', None)
    
    class Response:
        def __init__(self, message="", break_loop=False):
            self.message = message
            self.break_loop = break_loop

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
            print(f"[CognitiveNetwork] {msg}")


class CognitiveNetworkTool(Tool):
    """
    Tool for cognitive grammar-based agent communication and distributed networking.
    
    Methods:
    - send_cognitive_message: Send structured cognitive message to another agent
    - discover_network_agents: Discover agents in the distributed network
    - establish_agent_connection: Establish connection with another agent
    - coordinate_with_agents: Coordinate actions with multiple agents
    - register_agent_capabilities: Register or update agent capabilities
    - get_network_topology: Get current network topology information
    - find_coordination_partners: Find optimal agents for collaboration
    - parse_cognitive_message: Parse message using cognitive grammar
    - broadcast_to_network: Broadcast message to multiple network agents
    """
    
    def __init__(self, agent):
        super().__init__(agent)
        
        # Initialize cognitive grammar processor
        self.grammar_processor = CognitiveGrammarProcessor()
        
        # Initialize distributed network registry
        agent_id = getattr(agent, 'id', str(agent.number))
        agent_name = getattr(agent, 'name', f"Agent-{agent.number}")
        self.network_registry = DistributedNetworkRegistry(
            local_agent_id=agent_id,
            local_agent_name=agent_name
        )
        
        # Set up event handlers
        self.network_registry.add_event_handler("message_received", self._handle_network_message)
        self.network_registry.add_event_handler("agent_discovered", self._handle_agent_discovered)
        
        # Start network discovery
        self.network_registry.start_discovery()
    
    async def execute(self, **kwargs):
        """Execute cognitive network operations."""
        
        method = self.method
        
        if method == "send_cognitive_message":
            return await self.send_cognitive_message(**kwargs)
        elif method == "discover_network_agents":
            return await self.discover_network_agents(**kwargs)
        elif method == "establish_agent_connection":
            return await self.establish_agent_connection(**kwargs)
        elif method == "coordinate_with_agents":
            return await self.coordinate_with_agents(**kwargs)
        elif method == "register_agent_capabilities":
            return await self.register_agent_capabilities(**kwargs)
        elif method == "get_network_topology":
            return await self.get_network_topology(**kwargs)
        elif method == "find_coordination_partners":
            return await self.find_coordination_partners(**kwargs)
        elif method == "parse_cognitive_message":
            return await self.parse_cognitive_message(**kwargs)
        elif method == "broadcast_to_network":
            return await self.broadcast_to_network(**kwargs)
        else:
            return Response(
                message=f"Unknown method '{self.name}:{method}'. Available methods: "
                       f"send_cognitive_message, discover_network_agents, establish_agent_connection, "
                       f"coordinate_with_agents, register_agent_capabilities, get_network_topology, "
                       f"find_coordination_partners, parse_cognitive_message, broadcast_to_network",
                break_loop=False
            )
    
    async def send_cognitive_message(
        self,
        to_agent: str,
        intent: str = "inform",
        content: Dict[str, Any] = None,
        frame_type: str = "information_sharing",
        **kwargs
    ) -> Response:
        """Send a cognitive grammar structured message to another agent."""
        
        try:
            # Parse intent
            try:
                comm_intent = CommunicativeIntent(intent.lower())
            except ValueError:
                comm_intent = CommunicativeIntent.INFORM
            
            # Send cognitive message
            success = self.network_registry.send_cognitive_message(
                to_agent=to_agent,
                intent=comm_intent,
                content=content or {},
                frame_type=frame_type
            )
            
            if success:
                # Generate natural language description
                cognitive_msg = self.grammar_processor.create_cognitive_message(
                    intent=comm_intent,
                    frame_type=frame_type,
                    from_agent=self.network_registry.local_agent_id,
                    to_agent=to_agent,
                    content=content or {}
                )
                
                natural_language = self.grammar_processor.generate_natural_language(cognitive_msg)
                
                return Response(
                    message=f"Cognitive message sent successfully.\n\n"
                           f"Intent: {intent}\n"
                           f"Frame: {frame_type}\n"
                           f"Target: {to_agent}\n"
                           f"Natural Language: {natural_language}\n"
                           f"Content: {json.dumps(content, indent=2)}",
                    break_loop=False
                )
            else:
                return Response(
                    message=f"Failed to send cognitive message to agent '{to_agent}'. "
                           f"Agent may not be registered in the network.",
                    break_loop=False
                )
        
        except Exception as e:
            return Response(
                message=f"Error sending cognitive message: {str(e)}",
                break_loop=False
            )
    
    async def discover_network_agents(
        self,
        capability_filter: Optional[str] = None,
        include_details: bool = False,
        **kwargs
    ) -> Response:
        """Discover agents in the distributed network."""
        
        try:
            if capability_filter:
                try:
                    capability = AgentCapability(capability_filter.lower())
                    agents = self.network_registry.discover_agents_by_capability(capability)
                except ValueError:
                    return Response(
                        message=f"Invalid capability '{capability_filter}'. Valid capabilities: "
                               f"{', '.join([cap.value for cap in AgentCapability])}",
                        break_loop=False
                    )
            else:
                agents = list(self.network_registry.agents.values())
            
            if not agents:
                return Response(
                    message="No agents discovered in the network.",
                    break_loop=False
                )
            
            # Format agent information
            agent_info = []
            for agent in agents:
                if include_details:
                    info = self.network_registry.get_agent_info(agent.agent_id)
                    agent_info.append(info)
                else:
                    agent_info.append({
                        "agent_id": agent.agent_id,
                        "agent_name": agent.agent_name,
                        "capabilities": [cap.value for cap in agent.capabilities],
                        "trust_score": agent.trust_score
                    })
            
            return Response(
                message=f"Discovered {len(agents)} network agents:\n\n" +
                       json.dumps(agent_info, indent=2),
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"Error discovering network agents: {str(e)}",
                break_loop=False
            )
    
    async def establish_agent_connection(
        self,
        target_agent: str,
        connection_strength: float = 1.0,
        **kwargs
    ) -> Response:
        """Establish a connection with another agent."""
        
        try:
            connection_id = self.network_registry.establish_connection(
                agent_a=self.network_registry.local_agent_id,
                agent_b=target_agent,
                connection_strength=connection_strength
            )
            
            if connection_id:
                return Response(
                    message=f"Connection established with agent '{target_agent}'.\n"
                           f"Connection ID: {connection_id}\n"
                           f"Connection strength: {connection_strength}",
                    break_loop=False
                )
            else:
                return Response(
                    message=f"Failed to establish connection with agent '{target_agent}'. "
                           f"Agent may not be registered in the network.",
                    break_loop=False
                )
        
        except Exception as e:
            return Response(
                message=f"Error establishing agent connection: {str(e)}",
                break_loop=False
            )
    
    async def coordinate_with_agents(
        self,
        task_description: str,
        required_capabilities: List[str] = None,
        max_partners: int = 3,
        coordination_type: str = "synchronous",
        **kwargs
    ) -> Response:
        """Coordinate actions with multiple agents based on task requirements."""
        
        try:
            # Prepare task requirements
            task_requirements = {
                "description": task_description,
                "capabilities": [AgentCapability(cap.lower()) for cap in (required_capabilities or [])],
                "cognitive_constraints": {
                    "coordination_protocol": "cognitive_grammar",
                    "communication_style": coordination_type
                }
            }
            
            # Find optimal coordination partners
            partners = self.network_registry.find_optimal_coordination_partners(
                task_requirements=task_requirements,
                max_partners=max_partners
            )
            
            if not partners:
                return Response(
                    message=f"No suitable coordination partners found for task: {task_description}",
                    break_loop=False
                )
            
            # Send coordination messages to partners
            coordination_results = []
            for partner in partners:
                success = self.network_registry.send_cognitive_message(
                    to_agent=partner.agent_id,
                    intent=CommunicativeIntent.COORDINATE,
                    content={
                        "task": task_description,
                        "coordination_type": coordination_type,
                        "role": "partner",
                        "capabilities_needed": required_capabilities or []
                    },
                    frame_type="coordination"
                )
                
                coordination_results.append({
                    "agent_id": partner.agent_id,
                    "agent_name": partner.agent_name,
                    "capabilities": [cap.value for cap in partner.capabilities],
                    "message_sent": success
                })
            
            return Response(
                message=f"Coordination initiated for task: {task_description}\n\n"
                       f"Partners contacted: {len(partners)}\n"
                       f"Coordination details:\n" +
                       json.dumps(coordination_results, indent=2),
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"Error coordinating with agents: {str(e)}",
                break_loop=False
            )
    
    async def register_agent_capabilities(
        self,
        capabilities: List[str],
        cognitive_profile: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Response:
        """Register or update agent capabilities and cognitive profile."""
        
        try:
            # Parse capabilities
            agent_capabilities = set()
            for cap in capabilities:
                try:
                    agent_capabilities.add(AgentCapability(cap.lower()))
                except ValueError:
                    PrintStyle(color="yellow").print(f"Warning: Unknown capability '{cap}' ignored")
            
            # Update capabilities
            success = self.network_registry.update_agent_capabilities(
                agent_id=self.network_registry.local_agent_id,
                capabilities=agent_capabilities
            )
            
            # Update cognitive profile if provided
            if cognitive_profile and success:
                agent = self.network_registry.agents[self.network_registry.local_agent_id]
                agent.cognitive_profile.update(cognitive_profile)
            
            if success:
                return Response(
                    message=f"Agent capabilities updated successfully.\n"
                           f"Capabilities: {[cap.value for cap in agent_capabilities]}\n" +
                           (f"Cognitive profile: {json.dumps(cognitive_profile, indent=2)}" if cognitive_profile else ""),
                    break_loop=False
                )
            else:
                return Response(
                    message="Failed to update agent capabilities.",
                    break_loop=False
                )
        
        except Exception as e:
            return Response(
                message=f"Error registering agent capabilities: {str(e)}",
                break_loop=False
            )
    
    async def get_network_topology(self, include_statistics: bool = False, **kwargs) -> Response:
        """Get current network topology information."""
        
        try:
            if include_statistics:
                info = self.network_registry.get_network_statistics()
            else:
                info = self.network_registry.get_network_topology_info()
            
            return Response(
                message=f"Network topology information:\n\n" +
                       json.dumps(info, indent=2),
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"Error getting network topology: {str(e)}",
                break_loop=False
            )
    
    async def find_coordination_partners(
        self,
        task_requirements: Dict[str, Any],
        max_partners: int = 3,
        **kwargs
    ) -> Response:
        """Find optimal agents for coordination based on detailed task requirements."""
        
        try:
            partners = self.network_registry.find_optimal_coordination_partners(
                task_requirements=task_requirements,
                max_partners=max_partners
            )
            
            partner_info = []
            for partner in partners:
                info = self.network_registry.get_agent_info(partner.agent_id)
                partner_info.append(info)
            
            return Response(
                message=f"Found {len(partners)} optimal coordination partners:\n\n" +
                       json.dumps(partner_info, indent=2),
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"Error finding coordination partners: {str(e)}",
                break_loop=False
            )
    
    async def parse_cognitive_message(
        self,
        raw_message: Dict[str, Any],
        generate_natural_language: bool = True,
        **kwargs
    ) -> Response:
        """Parse a raw message using cognitive grammar structure."""
        
        try:
            cognitive_message = self.grammar_processor.parse_message(raw_message)
            
            result = {
                "parsed_message": self.grammar_processor.serialize_message(cognitive_message),
            }
            
            if generate_natural_language:
                result["natural_language"] = self.grammar_processor.generate_natural_language(cognitive_message)
            
            return Response(
                message=f"Message parsed using cognitive grammar:\n\n" +
                       json.dumps(result, indent=2),
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"Error parsing cognitive message: {str(e)}",
                break_loop=False
            )
    
    async def broadcast_to_network(
        self,
        intent: str = "inform",
        content: Dict[str, Any] = None,
        frame_type: str = "information_sharing",
        capability_filter: Optional[str] = None,
        **kwargs
    ) -> Response:
        """Broadcast a cognitive message to multiple network agents."""
        
        try:
            # Get target agents
            if capability_filter:
                try:
                    capability = AgentCapability(capability_filter.lower())
                    target_agents = self.network_registry.discover_agents_by_capability(capability)
                except ValueError:
                    return Response(
                        message=f"Invalid capability filter '{capability_filter}'",
                        break_loop=False
                    )
            else:
                target_agents = [
                    agent for agent in self.network_registry.agents.values()
                    if agent.agent_id != self.network_registry.local_agent_id
                ]
            
            if not target_agents:
                return Response(
                    message="No target agents found for broadcast.",
                    break_loop=False
                )
            
            # Parse intent
            try:
                comm_intent = CommunicativeIntent(intent.lower())
            except ValueError:
                comm_intent = CommunicativeIntent.INFORM
            
            # Send to all target agents
            broadcast_results = []
            for agent in target_agents:
                success = self.network_registry.send_cognitive_message(
                    to_agent=agent.agent_id,
                    intent=comm_intent,
                    content=content or {},
                    frame_type=frame_type
                )
                
                broadcast_results.append({
                    "agent_id": agent.agent_id,
                    "agent_name": agent.agent_name,
                    "message_sent": success
                })
            
            successful_sends = sum(1 for result in broadcast_results if result["message_sent"])
            
            return Response(
                message=f"Broadcast completed to {len(target_agents)} agents.\n"
                       f"Successful sends: {successful_sends}\n"
                       f"Intent: {intent}\n"
                       f"Frame: {frame_type}\n\n"
                       f"Broadcast results:\n" +
                       json.dumps(broadcast_results, indent=2),
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"Error broadcasting to network: {str(e)}",
                break_loop=False
            )
    
    def _handle_network_message(self, message_data: Dict[str, Any]):
        """Handle incoming network messages."""
        
        try:
            cognitive_message = message_data.get("message")
            if cognitive_message:
                PrintStyle(color="cyan").print(
                    f"[CognitiveNetwork] Received message from {cognitive_message.from_agent}: "
                    f"{cognitive_message.intent.value}"
                )
        except Exception as e:
            PrintStyle(color="red").print(f"[CognitiveNetwork] Error handling message: {e}")
    
    def _handle_agent_discovered(self, agent):
        """Handle agent discovery events."""
        
        PrintStyle(color="green").print(
            f"[CognitiveNetwork] New agent discovered: {agent.agent_name} "
            f"with capabilities: {[cap.value for cap in agent.capabilities]}"
        )
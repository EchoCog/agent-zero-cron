"""
Cognitive Grammar Framework for Agent Zero

This module implements cognitive grammar patterns for distributed agent communication,
enabling agents to communicate using structured linguistic patterns that embody
cognitive meaning and context.

Cognitive Grammar (Langacker) views language as embodied cognition where linguistic
structures are meaningful conceptual patterns. This framework applies these principles
to agent-to-agent communication.
"""

import json
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class CognitiveRole(Enum):
    """Cognitive roles in agent communication following Cognitive Grammar principles."""
    AGENT = "agent"           # The entity performing an action
    PATIENT = "patient"       # The entity being acted upon
    EXPERIENCER = "experiencer"  # The entity experiencing something
    INSTRUMENT = "instrument"    # The tool or means used
    LOCATION = "location"        # The spatial/conceptual location
    TIME = "time"               # The temporal frame
    MANNER = "manner"           # The way something is done
    PURPOSE = "purpose"         # The goal or intention


class CommunicativeIntent(Enum):
    """Communicative intents in agent interactions."""
    REQUEST = "request"         # Requesting action or information
    INFORM = "inform"          # Providing information
    COORDINATE = "coordinate"   # Coordinating joint action
    DELEGATE = "delegate"      # Delegating subtasks
    QUERY = "query"            # Asking questions
    CONFIRM = "confirm"        # Confirming understanding
    REJECT = "reject"          # Rejecting proposals
    NEGOTIATE = "negotiate"     # Negotiating terms or conditions


@dataclass
class CognitiveFrame:
    """
    A cognitive frame represents a conceptual structure for understanding
    agent interactions and communications.
    """
    frame_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    frame_type: str = ""
    participants: Dict[CognitiveRole, str] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    temporal_profile: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass 
class CognitiveMessage:
    """
    A message structured according to cognitive grammar principles.
    """
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intent: CommunicativeIntent = CommunicativeIntent.INFORM
    cognitive_frame: CognitiveFrame = field(default_factory=CognitiveFrame)
    content: Dict[str, Any] = field(default_factory=dict)
    from_agent: str = ""
    to_agent: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CognitiveGrammarProcessor:
    """
    Processes agent communications using cognitive grammar patterns.
    """
    
    def __init__(self):
        self.frame_templates = self._load_frame_templates()
        self.grammar_patterns = self._load_grammar_patterns()
    
    def _load_frame_templates(self) -> Dict[str, CognitiveFrame]:
        """Load cognitive frame templates for common agent interactions."""
        templates = {}
        
        # Task delegation frame
        templates["task_delegation"] = CognitiveFrame(
            frame_type="task_delegation",
            participants={
                CognitiveRole.AGENT: "delegating_agent",
                CognitiveRole.PATIENT: "task_content", 
                CognitiveRole.EXPERIENCER: "receiving_agent"
            },
            properties={
                "task_complexity": "medium",
                "urgency": "normal",
                "required_capabilities": []
            }
        )
        
        # Information sharing frame
        templates["information_sharing"] = CognitiveFrame(
            frame_type="information_sharing",
            participants={
                CognitiveRole.AGENT: "sharing_agent",
                CognitiveRole.PATIENT: "information_content",
                CognitiveRole.EXPERIENCER: "receiving_agent"
            },
            properties={
                "information_type": "factual",
                "confidence_level": "high",
                "relevance": "direct"
            }
        )
        
        # Coordination frame
        templates["coordination"] = CognitiveFrame(
            frame_type="coordination", 
            participants={
                CognitiveRole.AGENT: "coordinating_agent",
                CognitiveRole.EXPERIENCER: "coordinated_agents",
                CognitiveRole.PURPOSE: "joint_goal"
            },
            properties={
                "coordination_type": "synchronous",
                "decision_making": "consensus",
                "timeline": "immediate"
            }
        )
        
        return templates
    
    def _load_grammar_patterns(self) -> Dict[str, str]:
        """Load linguistic patterns for cognitive grammar structures."""
        return {
            "request_pattern": "Agent {agent} requests that {target} {action} {object}",
            "inform_pattern": "Agent {agent} informs {target} that {proposition}",
            "delegate_pattern": "Agent {agent} delegates {task} to {target} with {constraints}",
            "coordinate_pattern": "Agent {agent} proposes coordination with {targets} for {goal}",
            "query_pattern": "Agent {agent} queries {target} about {topic}",
            "confirm_pattern": "Agent {agent} confirms {proposition} with {target}",
        }
    
    def create_cognitive_message(
        self,
        intent: CommunicativeIntent,
        frame_type: str,
        from_agent: str,
        to_agent: str,
        content: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> CognitiveMessage:
        """Create a structured cognitive message."""
        
        # Get frame template
        frame_template = self.frame_templates.get(frame_type)
        if not frame_template:
            frame_template = CognitiveFrame(frame_type=frame_type)
        
        # Create cognitive frame for this message
        cognitive_frame = CognitiveFrame(
            frame_type=frame_template.frame_type,
            participants=frame_template.participants.copy(),
            properties=frame_template.properties.copy(),
            temporal_profile=content.get("temporal_profile")
        )
        
        # Update participants with actual agents
        if CognitiveRole.AGENT in cognitive_frame.participants:
            cognitive_frame.participants[CognitiveRole.AGENT] = from_agent
        if CognitiveRole.EXPERIENCER in cognitive_frame.participants:
            cognitive_frame.participants[CognitiveRole.EXPERIENCER] = to_agent
        
        return CognitiveMessage(
            intent=intent,
            cognitive_frame=cognitive_frame,
            content=content,
            from_agent=from_agent,
            to_agent=to_agent,
            context=context or {}
        )
    
    def parse_message(self, raw_message: Dict[str, Any]) -> CognitiveMessage:
        """Parse a raw message into cognitive grammar structure."""
        
        # Extract intent from message
        intent = CommunicativeIntent.INFORM
        if "intent" in raw_message:
            try:
                intent = CommunicativeIntent(raw_message["intent"])
            except ValueError:
                pass
        
        # Determine frame type from content
        frame_type = self._infer_frame_type(raw_message)
        
        return self.create_cognitive_message(
            intent=intent,
            frame_type=frame_type,
            from_agent=raw_message.get("from_agent", "unknown"),
            to_agent=raw_message.get("to_agent", "unknown"),
            content=raw_message.get("content", {}),
            context=raw_message.get("context", {})
        )
    
    def _infer_frame_type(self, message: Dict[str, Any]) -> str:
        """Infer cognitive frame type from message content."""
        
        content = message.get("content", {})
        tool_name = message.get("tool_name", "")
        
        # Infer from tool usage
        if tool_name == "call_subordinate":
            return "task_delegation"
        elif "query" in content or "question" in content:
            return "information_query"
        elif "coordinate" in str(content).lower():
            return "coordination"
        else:
            return "information_sharing"
    
    def generate_natural_language(self, cognitive_message: CognitiveMessage) -> str:
        """Generate natural language from cognitive message structure."""
        
        pattern_key = f"{cognitive_message.intent.value}_pattern"
        pattern = self.grammar_patterns.get(pattern_key, "Agent {agent} communicates with {target}")
        
        # Extract participants for pattern substitution
        participants = cognitive_message.cognitive_frame.participants
        
        substitutions = {
            "agent": cognitive_message.from_agent,
            "target": cognitive_message.to_agent,
            "action": cognitive_message.content.get("action", "perform"),
            "object": cognitive_message.content.get("object", "task"),
            "proposition": cognitive_message.content.get("proposition", "information"),
            "task": cognitive_message.content.get("task", "assigned task"),
            "constraints": cognitive_message.content.get("constraints", "standard constraints"),
            "goal": cognitive_message.content.get("goal", "shared objective"),
            "topic": cognitive_message.content.get("topic", "specified topic"),
            "targets": cognitive_message.to_agent
        }
        
        try:
            return pattern.format(**substitutions)
        except KeyError:
            return f"Agent {cognitive_message.from_agent} sends {cognitive_message.intent.value} to {cognitive_message.to_agent}"
    
    def serialize_message(self, cognitive_message: CognitiveMessage) -> Dict[str, Any]:
        """Serialize cognitive message to dictionary."""
        return {
            "message_id": cognitive_message.message_id,
            "intent": cognitive_message.intent.value if hasattr(cognitive_message.intent, 'value') else str(cognitive_message.intent),
            "cognitive_frame": {
                "frame_id": cognitive_message.cognitive_frame.frame_id,
                "frame_type": cognitive_message.cognitive_frame.frame_type,
                "participants": {role.value if hasattr(role, 'value') else str(role): agent for role, agent in cognitive_message.cognitive_frame.participants.items()},
                "properties": cognitive_message.cognitive_frame.properties,
                "temporal_profile": cognitive_message.cognitive_frame.temporal_profile,
                "created_at": cognitive_message.cognitive_frame.created_at.isoformat()
            },
            "content": cognitive_message.content,
            "from_agent": cognitive_message.from_agent,
            "to_agent": cognitive_message.to_agent,
            "context": cognitive_message.context,
            "timestamp": cognitive_message.timestamp.isoformat()
        }
    
    def deserialize_message(self, data: Dict[str, Any]) -> CognitiveMessage:
        """Deserialize dictionary to cognitive message."""
        
        frame_data = data.get("cognitive_frame", {})
        participants = {
            CognitiveRole(role): agent 
            for role, agent in frame_data.get("participants", {}).items()
        }
        
        cognitive_frame = CognitiveFrame(
            frame_id=frame_data.get("frame_id", str(uuid.uuid4())),
            frame_type=frame_data.get("frame_type", ""),
            participants=participants,
            properties=frame_data.get("properties", {}),
            temporal_profile=frame_data.get("temporal_profile"),
            created_at=datetime.fromisoformat(frame_data.get("created_at", datetime.now(timezone.utc).isoformat()))
        )
        
        return CognitiveMessage(
            message_id=data.get("message_id", str(uuid.uuid4())),
            intent=CommunicativeIntent(data.get("intent", "inform")),
            cognitive_frame=cognitive_frame,
            content=data.get("content", {}),
            from_agent=data.get("from_agent", ""),
            to_agent=data.get("to_agent", ""),
            context=data.get("context", {}),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now(timezone.utc).isoformat()))
        )
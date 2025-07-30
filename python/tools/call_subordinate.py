from agent import Agent, UserMessage
from python.helpers.tool import Tool, Response

# Enhanced with cognitive grammar support
try:
    from python.helpers.cognitive_grammar import CognitiveGrammarProcessor, CommunicativeIntent
    COGNITIVE_GRAMMAR_AVAILABLE = True
except ImportError:
    COGNITIVE_GRAMMAR_AVAILABLE = False

# Optional dependencies
try:
    from agent import Agent, UserMessage
    from python.helpers.tool import Tool, Response
except ImportError:
    # For testing purposes
    COGNITIVE_GRAMMAR_AVAILABLE = False


class Delegation(Tool):

    def __init__(self, agent):
        super().__init__(agent)
        # Initialize cognitive grammar processor if available
        if COGNITIVE_GRAMMAR_AVAILABLE:
            self.grammar_processor = CognitiveGrammarProcessor()
        else:
            self.grammar_processor = None

    async def execute(self, message="", reset="", cognitive_frame_type="task_delegation", **kwargs):
        # Enhanced delegation with cognitive grammar support
        
        # create subordinate agent using the data object on this agent and set superior agent to his data object
        if (
            self.agent.get_data(Agent.DATA_NAME_SUBORDINATE) is None
            or str(reset).lower().strip() == "true"
        ):
            sub = Agent(
                self.agent.number + 1, self.agent.config, self.agent.context
            )
            sub.set_data(Agent.DATA_NAME_SUPERIOR, self.agent)
            self.agent.set_data(Agent.DATA_NAME_SUBORDINATE, sub)

        subordinate: Agent = self.agent.get_data(Agent.DATA_NAME_SUBORDINATE)
        
        # Enhance message with cognitive grammar if available
        enhanced_message = message
        if self.grammar_processor and message:
            try:
                # Create cognitive message for delegation
                cognitive_msg = self.grammar_processor.create_cognitive_message(
                    intent=CommunicativeIntent.DELEGATE,
                    frame_type=cognitive_frame_type,
                    from_agent=f"Agent-{self.agent.number}",
                    to_agent=f"Agent-{subordinate.number}",
                    content={
                        "task": message,
                        "delegation_context": "subordinate_creation",
                        "cognitive_structure": True
                    }
                )
                
                # Generate natural language with cognitive structure
                natural_language = self.grammar_processor.generate_natural_language(cognitive_msg)
                enhanced_message = f"{message}\n\n[COGNITIVE_FRAME: {cognitive_frame_type}]\n[DELEGATION_PATTERN: {natural_language}]"
                
            except Exception as e:
                # Fallback to original message if cognitive processing fails
                enhanced_message = message

        # add enhanced user message to subordinate agent
        subordinate.hist_add_user_message(UserMessage(message=enhanced_message, attachments=[]))
        # run subordinate monologue
        result = await subordinate.monologue()
        
        # Process result with cognitive grammar if available
        if self.grammar_processor and result:
            try:
                # Parse the result using cognitive grammar
                result_message = self.grammar_processor.parse_message({
                    "content": {"result": result},
                    "from_agent": f"Agent-{subordinate.number}",
                    "to_agent": f"Agent-{self.agent.number}",
                    "intent": "inform"
                })
                
                cognitive_result = f"{result}\n\n[COGNITIVE_RESPONSE: Subordinate task completion reported using structured cognitive patterns]"
                return Response(message=cognitive_result, break_loop=False)
                
            except Exception:
                # Fallback to original result
                pass
        
        # result
        return Response(message=result, break_loop=False)

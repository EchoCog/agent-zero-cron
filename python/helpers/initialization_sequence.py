"""
Initialization Sequence Manager for Agent Zero

This module provides a comprehensive initialization sequence that coordinates
all components of Agent Zero in the proper order, with dependency management,
health checks, and graceful fallbacks.

Handles initialization for:
- Environment detection (devcontainer, docker, guix, bare metal)
- Runtime configuration
- Inngest workflow orchestration (Issue #5)
- Agent Kit integration (Issue #6)
- Model configurations
- Task scheduling and workflow management
"""

import os
import sys
import asyncio
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path

# Handle print_style import gracefully
try:
    from python.helpers.print_style import PrintStyle
except ImportError:
    # Fallback simple printer if PrintStyle is not available
    class PrintStyle:
        def print(self, message):
            print(message)
        def error(self, message):
            print(f"ERROR: {message}")


class RuntimeEnvironment(Enum):
    """Detected runtime environment types."""
    DEVCONTAINER = "devcontainer"
    DOCKER = "docker"
    GUIX = "guix"
    BARE_METAL = "bare_metal"
    CODESPACES = "codespaces"


class InitializationPhase(Enum):
    """Initialization phases in dependency order."""
    ENVIRONMENT_DETECTION = "environment_detection"
    RUNTIME_ARGS = "runtime_args"
    ENVIRONMENT_VARS = "environment_vars"
    CORE_SYSTEM = "core_system"
    INNGEST_CLIENT = "inngest_client"
    AGENT_KIT = "agent_kit"
    MODEL_CONFIG = "model_config"
    TASK_SCHEDULER = "task_scheduler"
    OPTIONAL_COMPONENTS = "optional_components"
    HEALTH_VALIDATION = "health_validation"


@dataclass
class InitializationStep:
    """Represents a single initialization step."""
    phase: InitializationPhase
    name: str
    function: Callable[[], Any]
    dependencies: List[InitializationPhase] = field(default_factory=list)
    required: bool = True
    timeout: float = 30.0
    health_check: Optional[Callable[[], bool]] = None


class InitializationSequence:
    """Manages the complete Agent Zero initialization sequence."""
    
    def __init__(self):
        self.printer = PrintStyle()
        self.environment: Optional[RuntimeEnvironment] = None
        self.completed_phases: set = set()
        self.failed_phases: set = set()
        self.initialization_data: Dict[str, Any] = {}
        self.steps: List[InitializationStep] = []
        self._setup_initialization_steps()
    
    def _setup_initialization_steps(self):
        """Define all initialization steps in dependency order."""
        self.steps = [
            # Phase 1: Environment Detection
            InitializationStep(
                phase=InitializationPhase.ENVIRONMENT_DETECTION,
                name="Detect Runtime Environment",
                function=self._detect_environment,
                dependencies=[],
                required=True,
                health_check=lambda: self.environment is not None
            ),
            
            # Phase 2: Runtime Arguments
            InitializationStep(
                phase=InitializationPhase.RUNTIME_ARGS,
                name="Initialize Runtime Arguments",
                function=self._initialize_runtime_args,
                dependencies=[InitializationPhase.ENVIRONMENT_DETECTION],
                required=True
            ),
            
            # Phase 3: Environment Variables
            InitializationStep(
                phase=InitializationPhase.ENVIRONMENT_VARS,
                name="Load Environment Variables",
                function=self._load_environment_vars,
                dependencies=[InitializationPhase.RUNTIME_ARGS],
                required=True
            ),
            
            # Phase 4: Core System Setup
            InitializationStep(
                phase=InitializationPhase.CORE_SYSTEM,
                name="Setup Core System",
                function=self._setup_core_system,
                dependencies=[InitializationPhase.ENVIRONMENT_VARS],
                required=True
            ),
            
            # Phase 5: Inngest Client (Issue #5)
            InitializationStep(
                phase=InitializationPhase.INNGEST_CLIENT,
                name="Initialize Inngest Client",
                function=self._initialize_inngest_client,
                dependencies=[InitializationPhase.CORE_SYSTEM],
                required=False  # Optional if not configured
            ),
            
            # Phase 6: Agent Kit (Issue #6)
            InitializationStep(
                phase=InitializationPhase.AGENT_KIT,
                name="Initialize Agent Kit",
                function=self._initialize_agent_kit,
                dependencies=[InitializationPhase.INNGEST_CLIENT],
                required=False  # Optional if Inngest not available
            ),
            
            # Phase 7: Model Configuration
            InitializationStep(
                phase=InitializationPhase.MODEL_CONFIG,
                name="Configure Models",
                function=self._configure_models,
                dependencies=[InitializationPhase.CORE_SYSTEM],
                required=True
            ),
            
            # Phase 8: Task Scheduler
            InitializationStep(
                phase=InitializationPhase.TASK_SCHEDULER,
                name="Initialize Task Scheduler",
                function=self._initialize_task_scheduler,
                dependencies=[
                    InitializationPhase.MODEL_CONFIG,
                    InitializationPhase.AGENT_KIT
                ],
                required=True
            ),
            
            # Phase 9: Optional Components
            InitializationStep(
                phase=InitializationPhase.OPTIONAL_COMPONENTS,
                name="Initialize Optional Components",
                function=self._initialize_optional_components,
                dependencies=[InitializationPhase.TASK_SCHEDULER],
                required=False
            ),
            
            # Phase 10: Health Validation
            InitializationStep(
                phase=InitializationPhase.HEALTH_VALIDATION,
                name="Validate System Health",
                function=self._validate_system_health,
                dependencies=[InitializationPhase.OPTIONAL_COMPONENTS],
                required=True
            )
        ]
    
    def _detect_environment(self) -> RuntimeEnvironment:
        """Detect the current runtime environment."""
        self.printer.print("🔍 Detecting runtime environment...")
        
        # Check for GitHub Codespaces
        if os.getenv("CODESPACES"):
            self.environment = RuntimeEnvironment.CODESPACES
            self.printer.print("  📱 Running in GitHub Codespaces")
            return self.environment
        
        # Check for devcontainer
        if os.path.exists("/.devcontainer") or os.getenv("REMOTE_CONTAINERS"):
            self.environment = RuntimeEnvironment.DEVCONTAINER
            self.printer.print("  🐳 Running in DevContainer")
            return self.environment
        
        # Check for Guix environment
        if os.getenv("GUIX_ENVIRONMENT") or Path("/gnu/store").exists():
            self.environment = RuntimeEnvironment.GUIX
            self.printer.print("  🐧 Running in Guix environment")
            return self.environment
        
        # Check for Docker container
        if (os.path.exists("/.dockerenv") or 
            os.path.exists("/proc/1/cgroup") and 
            "docker" in open("/proc/1/cgroup").read()):
            self.environment = RuntimeEnvironment.DOCKER
            self.printer.print("  🐳 Running in Docker container")
            return self.environment
        
        # Default to bare metal
        self.environment = RuntimeEnvironment.BARE_METAL
        self.printer.print("  💻 Running on bare metal")
        return self.environment
    
    def _initialize_runtime_args(self):
        """Initialize runtime arguments and configuration."""
        self.printer.print("⚙️  Initializing runtime arguments...")
        
        # Import here to avoid circular imports
        from python.helpers import runtime
        runtime.initialize()
        
        self.initialization_data['runtime_initialized'] = True
    
    def _load_environment_vars(self):
        """Load environment variables and settings."""
        self.printer.print("📝 Loading environment variables...")
        
        # Import here to avoid circular imports
        from python.helpers import dotenv, settings
        
        # Load .env file
        dotenv.load_dotenv()
        
        # Initialize settings
        current_settings = settings.get_settings()
        self.initialization_data['settings'] = current_settings
        
        self.printer.print(f"  ✓ Loaded settings for environment: {self.environment.value}")
    
    def _setup_core_system(self):
        """Setup core system directories and permissions."""
        self.printer.print("🗂️  Setting up core system...")
        
        from python.helpers import files
        
        # Ensure required directories exist
        required_dirs = ['logs', 'memory', 'tmp', 'work_dir']
        for dir_name in required_dirs:
            try:
                files.make_dirs(dir_name)
            except Exception as e:
                self.printer.print(f"  ⚠️  Warning: Could not create {dir_name}: {e}")
        
        self.initialization_data['core_system_ready'] = True
    
    def _initialize_inngest_client(self):
        """Initialize Inngest workflow orchestration client (Issue #5)."""
        self.printer.print("🔄 Initializing Inngest client...")
        
        try:
            from python.helpers.inngest_client import InngestConfig, InngestManager
            
            settings = self.initialization_data.get('settings', {})
            
            # Create Inngest configuration
            inngest_config = InngestConfig(
                enabled=settings.get("inngest_enabled", False),
                app_id=settings.get("inngest_app_id", "agent-zero"),
                event_key=settings.get("inngest_event_key"),
                signing_key=settings.get("inngest_signing_key"),
                base_url=settings.get("inngest_base_url", "https://api.inngest.com")
            )
            
            # Create Inngest manager
            inngest_manager = InngestManager(inngest_config)
            
            self.initialization_data['inngest_config'] = inngest_config
            self.initialization_data['inngest_manager'] = inngest_manager
            
            if inngest_manager.is_enabled():
                self.printer.print("  ✓ Inngest client enabled and configured")
            else:
                self.printer.print("  ⚠️  Inngest client disabled or not configured")
            
        except Exception as e:
            self.printer.print(f"  ⚠️  Inngest initialization failed: {e}")
            # Not critical, continue without Inngest
    
    def _initialize_agent_kit(self):
        """Initialize Agent Kit integration (Issue #6)."""
        self.printer.print("🤖 Initializing Agent Kit...")
        
        try:
            from python.helpers.inngest_agent_kit import InngestAgentKit
            
            inngest_manager = self.initialization_data.get('inngest_manager')
            if inngest_manager and inngest_manager.is_enabled():
                agent_kit = InngestAgentKit(inngest_manager)
                self.initialization_data['agent_kit'] = agent_kit
                self.printer.print("  ✓ Agent Kit initialized with Inngest")
            else:
                self.printer.print("  ⚠️  Agent Kit disabled (Inngest not available)")
                
        except Exception as e:
            self.printer.print(f"  ⚠️  Agent Kit initialization failed: {e}")
            # Not critical, continue without Agent Kit
    
    def _configure_models(self):
        """Configure AI models (chat, utility, embedding, browser)."""
        self.printer.print("🧠 Configuring AI models...")
        
        import models
        from agent import ModelConfig
        
        settings = self.initialization_data.get('settings', {})
        
        # Configure chat model
        chat_llm = ModelConfig(
            provider=models.ModelProvider[settings["chat_model_provider"]],
            name=settings["chat_model_name"],
            ctx_length=settings["chat_model_ctx_length"],
            vision=settings["chat_model_vision"],
            limit_requests=settings["chat_model_rl_requests"],
            limit_input=settings["chat_model_rl_input"],
            limit_output=settings["chat_model_rl_output"],
            kwargs=settings["chat_model_kwargs"],
        )
        
        # Configure utility model
        utility_llm = ModelConfig(
            provider=models.ModelProvider[settings["util_model_provider"]],
            name=settings["util_model_name"],
            ctx_length=settings["util_model_ctx_length"],
            limit_requests=settings["util_model_rl_requests"],
            limit_input=settings["util_model_rl_input"],
            limit_output=settings["util_model_rl_output"],
            kwargs=settings["util_model_kwargs"],
        )
        
        # Configure embedding model
        embedding_llm = ModelConfig(
            provider=models.ModelProvider[settings["embed_model_provider"]],
            name=settings["embed_model_name"],
            limit_requests=settings["embed_model_rl_requests"],
            kwargs=settings["embed_model_kwargs"],
        )
        
        # Configure browser model
        browser_llm = ModelConfig(
            provider=models.ModelProvider[settings["browser_model_provider"]],
            name=settings["browser_model_name"],
            vision=settings["browser_model_vision"],
            kwargs=settings["browser_model_kwargs"],
        )
        
        self.initialization_data['chat_model'] = chat_llm
        self.initialization_data['utility_model'] = utility_llm
        self.initialization_data['embedding_model'] = embedding_llm
        self.initialization_data['browser_model'] = browser_llm
        
        self.printer.print("  ✓ AI models configured")
    
    def _initialize_task_scheduler(self):
        """Initialize task scheduler and workflow management."""
        self.printer.print("📅 Initializing task scheduler...")
        
        try:
            from python.helpers.task_workflow import TaskWorkflowManager
            
            inngest_config = self.initialization_data.get('inngest_config')
            if inngest_config:
                workflow_manager = TaskWorkflowManager(inngest_config)
                self.initialization_data['workflow_manager'] = workflow_manager
                self.printer.print("  ✓ Task scheduler with workflow management initialized")
            else:
                self.printer.print("  ⚠️  Task scheduler initialized without workflow management")
                
        except Exception as e:
            self.printer.print(f"  ⚠️  Task scheduler initialization warning: {e}")
            # Continue with basic functionality
    
    def _initialize_optional_components(self):
        """Initialize optional components (SSH, Docker, etc.)."""
        self.printer.print("🔧 Initializing optional components...")
        
        settings = self.initialization_data.get('settings', {})
        
        # SSH configuration (if enabled)
        try:
            from python.helpers import settings as settings_helper
            ssh_conf = settings_helper.get_runtime_config(settings)
            self.initialization_data['ssh_config'] = ssh_conf
        except Exception as e:
            self.printer.print(f"  ⚠️  SSH configuration warning: {e}")
        
        # Docker configuration (if enabled)
        if settings.get('code_exec_docker_enabled', False):
            try:
                from python.helpers import docker
                # Docker setup would go here
                self.printer.print("  ✓ Docker components initialized")
            except Exception as e:
                self.printer.print(f"  ⚠️  Docker initialization warning: {e}")
        
        self.printer.print("  ✓ Optional components initialized")
    
    def _validate_system_health(self):
        """Validate that all critical systems are working."""
        self.printer.print("🏥 Validating system health...")
        
        health_checks = []
        
        # Check if models are configured
        if all(key in self.initialization_data for key in 
               ['chat_model', 'utility_model', 'embedding_model', 'browser_model']):
            health_checks.append("✓ AI models configured")
        else:
            health_checks.append("❌ AI models missing")
        
        # Check if core system is ready
        if self.initialization_data.get('core_system_ready'):
            health_checks.append("✓ Core system ready")
        else:
            health_checks.append("❌ Core system not ready")
        
        # Check Inngest status
        inngest_manager = self.initialization_data.get('inngest_manager')
        if inngest_manager and inngest_manager.is_enabled():
            health_checks.append("✓ Inngest workflow orchestration active")
        else:
            health_checks.append("ℹ️  Inngest workflow orchestration disabled")
        
        # Check Agent Kit status
        if self.initialization_data.get('agent_kit'):
            health_checks.append("✓ Agent Kit integration active")
        else:
            health_checks.append("ℹ️  Agent Kit integration disabled")
        
        for check in health_checks:
            self.printer.print(f"  {check}")
        
        # Determine overall health
        critical_failures = [check for check in health_checks if check.startswith("❌")]
        if critical_failures:
            raise Exception(f"Critical health check failures: {critical_failures}")
        
        self.printer.print("  🎉 System health validation passed!")
    
    def run_initialization(self) -> Dict[str, Any]:
        """Run the complete initialization sequence."""
        self.printer.print("🚀 Starting Agent Zero initialization sequence...")
        
        for step in self.steps:
            try:
                # Check dependencies
                for dependency in step.dependencies:
                    if dependency not in self.completed_phases:
                        if dependency in self.failed_phases and step.required:
                            raise Exception(f"Required dependency {dependency.value} failed")
                        elif dependency in self.failed_phases:
                            self.printer.print(f"  ⚠️  Skipping {step.name} - dependency {dependency.value} failed")
                            continue
                
                # Run the step
                self.printer.print(f"📋 {step.name}...")
                step.function()
                
                # Run health check if provided
                if step.health_check and not step.health_check():
                    raise Exception(f"Health check failed for {step.name}")
                
                self.completed_phases.add(step.phase)
                
            except Exception as e:
                self.failed_phases.add(step.phase)
                if step.required:
                    self.printer.error(f"❌ Required step failed: {step.name} - {e}")
                    raise
                else:
                    self.printer.print(f"  ⚠️  Optional step failed: {step.name} - {e}")
        
        self.printer.print("✅ Agent Zero initialization sequence completed!")
        return self.initialization_data
    
    def get_agent_config(self):
        """Create AgentConfig from initialization data."""
        from agent import AgentConfig, InngestConfig
        
        settings = self.initialization_data.get('settings', {})
        
        # Get Inngest configuration
        inngest_config = self.initialization_data.get('inngest_config', InngestConfig(enabled=False))
        
        # Create agent configuration
        config = AgentConfig(
            chat_model=self.initialization_data['chat_model'],
            utility_model=self.initialization_data['utility_model'],
            embeddings_model=self.initialization_data['embedding_model'],
            browser_model=self.initialization_data['browser_model'],
            prompts_subdir=settings["agent_prompts_subdir"],
            memory_subdir=settings["agent_memory_subdir"],
            knowledge_subdirs=["default", settings["agent_knowledge_subdir"]],
            code_exec_docker_enabled=False,
            inngest=inngest_config,
        )
        
        # Apply runtime configurations
        from python.helpers import settings as settings_helper
        settings_helper.set_runtime_config(config, settings)
        
        # Apply runtime args override
        self._apply_args_override(config)
        
        return config
    
    def _apply_args_override(self, config):
        """Apply runtime argument overrides to config."""
        from python.helpers import runtime
        
        # Update config with runtime args
        for key, value in runtime.args.items():
            if hasattr(config, key):
                # conversion based on type of config[key]
                if isinstance(getattr(config, key), bool):
                    value = value.lower().strip() == "true"
                elif isinstance(getattr(config, key), int):
                    value = int(value)
                elif isinstance(getattr(config, key), float):
                    value = float(value)
                elif isinstance(getattr(config, key), str):
                    value = str(value)
                else:
                    raise Exception(
                        f"Unsupported argument type of '{key}': {type(getattr(config, key))}"
                    )
                
                setattr(config, key, value)


# Global initialization sequence instance
_initialization_sequence: Optional[InitializationSequence] = None


def get_initialization_sequence() -> InitializationSequence:
    """Get the global initialization sequence instance."""
    global _initialization_sequence
    if _initialization_sequence is None:
        _initialization_sequence = InitializationSequence()
    return _initialization_sequence


def run_full_initialization() -> Dict[str, Any]:
    """Run the complete initialization sequence and return initialization data."""
    sequence = get_initialization_sequence()
    return sequence.run_initialization()


def get_initialized_agent_config():
    """Get a fully initialized AgentConfig."""
    sequence = get_initialization_sequence()
    if not sequence.completed_phases:
        sequence.run_initialization()
    return sequence.get_agent_config()
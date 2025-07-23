"""
Inngest client and workflow orchestration integration for Agent Zero.

This module provides event-driven workflow orchestration capabilities by integrating
Inngest with the existing TaskScheduler system.
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List, Union

try:
    from inngest import Inngest
    from inngest.function import InngestFunction
    from inngest.client import InngestClient
    INNGEST_AVAILABLE = True
except ImportError:
    INNGEST_AVAILABLE = False
    # Fallback classes for when Inngest is not installed
    class Inngest:
        def __init__(self, *args, **kwargs):
            pass
    
    class InngestFunction:
        pass
    
    class InngestClient:
        pass

from python.helpers.print_style import PrintStyle
from python.helpers.files import get_abs_path, make_dirs


class InngestConfig:
    """Configuration for Inngest client."""
    
    def __init__(
        self,
        app_id: str = "agent-zero",
        event_key: Optional[str] = None,
        signing_key: Optional[str] = None,
        base_url: str = "https://api.inngest.com",
        enabled: bool = True
    ):
        self.app_id = app_id
        self.event_key = event_key or os.getenv("INNGEST_EVENT_KEY")
        self.signing_key = signing_key or os.getenv("INNGEST_SIGNING_KEY")
        self.base_url = base_url
        self.enabled = enabled and INNGEST_AVAILABLE
        
        if self.enabled and not self.event_key:
            PrintStyle(font_color="yellow", padding=True).print(
                "Warning: Inngest is enabled but no event key provided. "
                "Set INNGEST_EVENT_KEY environment variable or disable Inngest."
            )
            self.enabled = False


class InngestManager:
    """
    Manages Inngest workflows and integrates with Agent Zero's task system.
    """
    
    _instance: Optional['InngestManager'] = None
    
    def __init__(self, config: InngestConfig):
        self.config = config
        self.client: Optional[Inngest] = None
        self._functions: Dict[str, InngestFunction] = {}
        self._printer = PrintStyle(italic=True, font_color="purple", padding=False)
        
        if self.config.enabled:
            self._initialize_client()
    
    @classmethod
    def get_instance(cls, config: Optional[InngestConfig] = None) -> 'InngestManager':
        """Get singleton instance of InngestManager."""
        if cls._instance is None:
            if config is None:
                config = InngestConfig()
            cls._instance = cls(config)
        return cls._instance
    
    def _initialize_client(self):
        """Initialize the Inngest client if available."""
        if not self.config.enabled:
            return
            
        try:
            self.client = Inngest(
                app_id=self.config.app_id,
                event_key=self.config.event_key,
                signing_key=self.config.signing_key,
                base_url=self.config.base_url
            )
            self._printer.print(f"Inngest client initialized for app: {self.config.app_id}")
        except Exception as e:
            self._printer.print(f"Failed to initialize Inngest client: {e}")
            self.config.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if Inngest is enabled and available."""
        return self.config.enabled and self.client is not None
    
    async def send_event(
        self,
        name: str,
        data: Dict[str, Any],
        user: Optional[Dict[str, Any]] = None,
        ts: Optional[int] = None
    ) -> bool:
        """
        Send an event to Inngest.
        
        Args:
            name: Event name (e.g., "task/created", "task/completed")
            data: Event payload
            user: Optional user context
            ts: Optional timestamp (defaults to current time)
            
        Returns:
            True if event was sent successfully, False otherwise
        """
        if not self.is_enabled():
            self._printer.print(f"Inngest not enabled, skipping event: {name}")
            return False
        
        try:
            event_data = {
                "name": name,
                "data": data,
                "ts": ts or int(datetime.now(timezone.utc).timestamp() * 1000)
            }
            
            if user:
                event_data["user"] = user
            
            # Send event to Inngest
            await self.client.send(event_data)  # type: ignore
            self._printer.print(f"Sent Inngest event: {name}")
            return True
            
        except Exception as e:
            self._printer.print(f"Failed to send Inngest event {name}: {e}")
            return False
    
    def create_function(
        self,
        fn_id: str,
        name: str,
        trigger: Union[str, Dict[str, Any]],
        handler: Any
    ) -> Optional[InngestFunction]:
        """
        Create an Inngest function.
        
        Args:
            fn_id: Unique function identifier
            name: Function display name
            trigger: Event trigger (event name or complex trigger config)
            handler: Function handler (async callable)
            
        Returns:
            InngestFunction instance or None if creation failed
        """
        if not self.is_enabled():
            return None
        
        try:
            # Convert simple event name to trigger config
            if isinstance(trigger, str):
                trigger_config = {"event": trigger}
            else:
                trigger_config = trigger
            
            # Create Inngest function
            fn = self.client.create_function(  # type: ignore
                fn_id=fn_id,
                name=name,
                trigger=trigger_config,
                handler=handler
            )
            
            self._functions[fn_id] = fn
            self._printer.print(f"Created Inngest function: {fn_id}")
            return fn
            
        except Exception as e:
            self._printer.print(f"Failed to create Inngest function {fn_id}: {e}")
            return None
    
    def get_function(self, fn_id: str) -> Optional[InngestFunction]:
        """Get an Inngest function by ID."""
        return self._functions.get(fn_id)
    
    def list_functions(self) -> List[str]:
        """List all registered function IDs."""
        return list(self._functions.keys())
    
    async def trigger_workflow(
        self,
        workflow_name: str,
        data: Dict[str, Any],
        delay_seconds: Optional[int] = None
    ) -> bool:
        """
        Trigger a workflow by sending an event.
        
        Args:
            workflow_name: Name of the workflow to trigger
            data: Workflow input data
            delay_seconds: Optional delay before execution
            
        Returns:
            True if workflow was triggered successfully
        """
        event_name = f"workflow/{workflow_name}"
        event_data = {
            "workflow": workflow_name,
            "input": data,
            "triggered_at": datetime.now(timezone.utc).isoformat()
        }
        
        if delay_seconds:
            event_data["delay_seconds"] = delay_seconds
        
        return await self.send_event(event_name, event_data)
    
    def get_status(self) -> Dict[str, Any]:
        """Get Inngest manager status information."""
        return {
            "enabled": self.is_enabled(),
            "app_id": self.config.app_id,
            "has_event_key": bool(self.config.event_key),
            "has_signing_key": bool(self.config.signing_key),
            "base_url": self.config.base_url,
            "functions_count": len(self._functions),
            "functions": list(self._functions.keys()),
            "inngest_available": INNGEST_AVAILABLE
        }


# Global helper functions
def get_inngest_manager(config: Optional[InngestConfig] = None) -> InngestManager:
    """Get the global Inngest manager instance."""
    return InngestManager.get_instance(config)


def create_default_config() -> InngestConfig:
    """Create default Inngest configuration."""
    return InngestConfig(
        app_id=os.getenv("INNGEST_APP_ID", "agent-zero"),
        event_key=os.getenv("INNGEST_EVENT_KEY"),
        signing_key=os.getenv("INNGEST_SIGNING_KEY"),
        base_url=os.getenv("INNGEST_BASE_URL", "https://api.inngest.com"),
        enabled=os.getenv("INNGEST_ENABLED", "true").lower() in ("true", "1", "yes")
    )
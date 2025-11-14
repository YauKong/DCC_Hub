"""Plugin base classes and tool context."""
from abc import ABC, abstractmethod
from typing import Any, Optional

from hub.core.qt_import import import_qt
QtWidgets = import_qt()


class ToolContext:
    """Context object passed to plugins, containing all system components.
    
    Provides access to DCC facade, settings, state, command/event buses,
    job center, and services.
    """
    
    def __init__(self, dcc, settings, state, cmd_bus, evt_bus, job_center=None, services=None):
        """Initialize tool context.
        
        Args:
            dcc: DCC facade instance
            settings: Settings instance
            state: StateStore instance
            cmd_bus: CommandBus instance
            evt_bus: EventBus instance
            job_center: JobCenter instance (optional, for future use)
            services: Services dict (optional, for future use)
        """
        self.dcc = dcc
        self.settings = settings
        self.state = state
        self.cmd_bus = cmd_bus
        self.evt_bus = evt_bus
        self.job_center = job_center
        self.services = services or {}


class BaseToolPlugin(ABC):
    """Base class for all tool plugins.
    
    Plugins must implement create_ui() and execute() methods.
    """
    
    def __init__(self, context: ToolContext):
        """Initialize plugin with tool context.
        
        Args:
            context: ToolContext instance providing access to system components
        """
        self.ctx = context
    
    @abstractmethod
    def create_ui(self, parent: Optional[Any] = None):
        """Create and return plugin UI widget.
        
        Args:
            parent: Parent widget (optional)
            
        Returns:
            QWidget or None if plugin doesn't have UI
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs):
        """Execute plugin functionality.
        
        Args:
            **kwargs: Plugin-specific parameters
            
        Returns:
            Plugin execution result (optional)
        """
        pass


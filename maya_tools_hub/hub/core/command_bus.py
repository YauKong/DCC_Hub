"""CommandBus - synchronous command dispatch system."""


class CommandBus:
    """Synchronous command bus for tool execution.
    
    Commands are registered with a name and can be dispatched with keyword arguments.
    """
    
    def __init__(self):
        """Initialize empty command registry."""
        self._commands = {}
    
    def register(self, name, func):
        """Register a command handler.
        
        Args:
            name: Command name (string)
            func: Callable that accepts **kwargs
        """
        self._commands[name] = func
    
    def dispatch(self, name, **kwargs):
        """Dispatch a command by name.
        
        Args:
            name: Command name
            **kwargs: Arguments to pass to the command handler
            
        Returns:
            Return value from the command handler
            
        Raises:
            KeyError: If command is not registered
        """
        if name not in self._commands:
            raise KeyError(f"Command '{name}' is not registered")
        
        handler = self._commands[name]
        return handler(**kwargs)


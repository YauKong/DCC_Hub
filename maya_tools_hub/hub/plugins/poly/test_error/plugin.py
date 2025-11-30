"""Test error plugin for testing exception handling."""
from hub.core.logging import get_logger
from hub.core.plugins import BaseToolPlugin
from hub.core.qt_import import import_qt

QtWidgets = import_qt()
logger = get_logger(__name__)


class TestErrorTool(BaseToolPlugin):
    """Tool for testing exception handling in the Hub."""
    
    def create_ui(self, parent=None):
        """Create UI widget with buttons to trigger different types of errors.
        
        Args:
            parent: Parent widget
            
        Returns:
            QWidget containing the plugin UI
        """
        widget = QtWidgets.QWidget(parent)
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Button to trigger ValueError
        self.value_error_button = QtWidgets.QPushButton("Trigger ValueError")
        self.value_error_button.clicked.connect(lambda: self._on_execute(error_type="value"))
        
        # Button to trigger RuntimeError
        self.runtime_error_button = QtWidgets.QPushButton("Trigger RuntimeError")
        self.runtime_error_button.clicked.connect(lambda: self._on_execute(error_type="runtime"))
        
        # Button to trigger division by zero
        self.zero_error_button = QtWidgets.QPushButton("Trigger ZeroDivisionError")
        self.zero_error_button.clicked.connect(lambda: self._on_execute(error_type="zero"))
        
        layout.addWidget(self.value_error_button)
        layout.addWidget(self.runtime_error_button)
        layout.addWidget(self.zero_error_button)
        layout.addStretch()
        
        logger.debug("Test error plugin UI created")
        return widget
    
    def _on_execute(self, error_type="value"):
        """Handle button click - dispatch through CommandBus."""
        logger.info(f"Test error button clicked: {error_type}")
        
        # Get plugin key
        plugin_key = getattr(self, '_plugin_key', None)
        if not plugin_key:
            logger.warning("_plugin_key not found, falling back to direct execute")
            self.execute(error_type=error_type)
            return
        
        # Dispatch command through CommandBus
        try:
            self.ctx.cmd_bus.dispatch("tool.execute", key=plugin_key, error_type=error_type)
        except Exception as e:
            logger.error(f"Error dispatching command: {e}", exc_info=True)
    
    def execute(self, **kwargs):
        """Execute test error - always raises an exception.
        
        Args:
            **kwargs: Plugin parameters (error_type)
        """
        error_type = kwargs.get('error_type', 'value')
        
        logger.warning(f"Test error plugin executing with error_type={error_type}")
        
        # Trigger different types of errors based on parameter
        if error_type == "value":
            raise ValueError("This is a test ValueError - invalid parameter value")
        elif error_type == "runtime":
            raise RuntimeError("This is a test RuntimeError - operation failed")
        elif error_type == "zero":
            # Trigger division by zero
            result = 1 / 0
            return result
        else:
            raise Exception(f"Unknown error type: {error_type}")


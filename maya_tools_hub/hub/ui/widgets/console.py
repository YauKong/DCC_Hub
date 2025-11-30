"""Console widget - displays event log from EventBus."""
from hub.core.logging import get_logger
from hub.core.qt_import import import_qt
QtWidgets = import_qt()

logger = get_logger(__name__)


class ConsoleWidget(QtWidgets.QWidget):
    """Console widget that subscribes to EventBus and displays event log."""

    def __init__(self, context=None, parent=None):
        """Initialize Console widget.

        Args:
            context: ToolContext instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.context = context

        # Create layout
        layout = QtWidgets.QVBoxLayout(self)

        # Create QTextEdit for event log
        self.console_text = QtWidgets.QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setPlaceholderText("Event log will appear here...")
        layout.addWidget(self.console_text)

        # Subscribe to events if context is available
        if self.context and hasattr(self.context, 'evt_bus'):
            self.context.evt_bus.subscribe("tool/done", self._on_tool_done)
            self.context.evt_bus.subscribe("tool/failed", self._on_tool_failed)
            self.context.evt_bus.subscribe("job/done", self._on_job_done)
            self.context.evt_bus.subscribe("aigc/done", self._on_aigc_done)
            logger.debug("Console subscribed to tool/done, tool/failed, job/done, and aigc/done events")

    def append(self, text):
        """Append text to console.

        Args:
            text: Text to append
        """
        self.console_text.append(text)
        # Auto-scroll to bottom
        scrollbar = self.console_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_tool_done(self, payload):
        """Handle tool/done event - display in console.

        Args:
            payload: Event payload dict with key, result, kwargs
        """
        tool_key = payload.get("key", "unknown")
        result = payload.get("result", None)
        kwargs = payload.get("kwargs", {})

        # Format message
        import json
        message = f"[tool/done] {tool_key}\n"
        if kwargs:
            message += f"  kwargs: {json.dumps(kwargs, indent=2)}\n"
        if result is not None:
            message += f"  result: {result}\n"
        message += "\n"

        # Append to console
        self.append(message)

        logger.debug(f"Console received tool/done event for {tool_key}")

    def _on_tool_failed(self, payload):
        """Handle tool/failed event - display error in console.

        Args:
            payload: Event payload dict with key, error, error_type, kwargs
        """
        tool_key = payload.get("key", "unknown")
        error = payload.get("error", "Unknown error")
        error_type = payload.get("error_type", "Exception")
        kwargs = payload.get("kwargs", {})

        # Format error message
        import json
        message = f"[tool/failed] {tool_key}\n"
        message += f"  error_type: {error_type}\n"
        message += f"  error: {error}\n"
        if kwargs:
            message += f"  kwargs: {json.dumps(kwargs, indent=2)}\n"
        message += "\n"

        # Append to console
        self.append(message)

        logger.debug(f"Console received tool/failed event for {tool_key}")

    def _on_job_done(self, payload):
        """Handle job/done event - display in console.

        Args:
            payload: Event payload dict with result and status
        """
        logger.debug(f"Console received job/done event: {payload}")

        # Note: AIGC jobs are handled by _on_aigc_done
        # This is for other job types if needed in the future

    def _on_aigc_done(self, payload):
        """Handle aigc/done event - display AIGC job completion in console.

        Args:
            payload: Event payload dict with job_id and status
        """
        job_id = payload.get("job_id", "unknown")
        status = payload.get("status", {})
        inputs = payload.get("inputs", {})

        logger.info(f"AIGC job completed: {job_id}")

        # Format message
        import json
        message = f"[aigc/done] AIGC Job Completed\n"
        message += f"  job_id: {job_id}\n"
        if inputs:
            message += f"  inputs: {json.dumps(inputs, indent=4)}\n"
        if status:
            message += f"  status: {json.dumps(status, indent=4)}\n"
        message += "\n"

        # Append to console
        self.append(message)

        logger.debug(f"Console displayed aigc/done event for {job_id}")

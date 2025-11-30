"""Poly panel - dynamically loads poly category tool plugins."""
from hub.core.logging import get_logger
from hub.core.qt_import import import_qt
QtWidgets = import_qt()

logger = get_logger(__name__)


class PolyPanel(QtWidgets.QWidget):
    """Poly panel that dynamically loads poly category plugins."""

    def __init__(self, registry=None, context=None, parent=None):
        """Initialize Poly panel.

        Args:
            registry: ToolRegistry instance
            context: ToolContext instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.registry = registry
        self.context = context

        # Create layout
        self.layout = QtWidgets.QVBoxLayout(self)

        # Load poly plugins dynamically
        if self.registry and self.context:
            self._load_poly_plugins()

        self.layout.addStretch()

    def _load_poly_plugins(self):
        """Load and add poly category plugins to the layout."""
        tools = self.registry.list_tools()

        for tool_key in tools:
            manifest = self.registry.get_manifest(tool_key)
            if not manifest:
                continue

            # Check if plugin matches poly category and has panel UI
            category = manifest.get('category')
            ui_config = manifest.get('ui', {})
            is_panel = ui_config.get('panel', False)

            if category == "poly" and is_panel:
                try:
                    # Instantiate plugin
                    logger.debug(f"Loading plugin UI: {tool_key}")
                    plugin_instance, _ = self.registry.instantiate(tool_key, self.context)

                    # Create UI
                    plugin_ui = plugin_instance.create_ui(parent=self)
                    if plugin_ui:
                        # Add label for plugin
                        label = QtWidgets.QLabel(manifest.get('label', tool_key))
                        self.layout.addWidget(label)
                        self.layout.addWidget(plugin_ui)

                        # Add separator
                        separator = QtWidgets.QFrame()
                        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
                        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
                        self.layout.addWidget(separator)
                        logger.debug(f"Successfully loaded plugin UI: {tool_key}")
                except Exception as e:
                    logger.error(f"Error loading plugin '{tool_key}': {e}", exc_info=True)

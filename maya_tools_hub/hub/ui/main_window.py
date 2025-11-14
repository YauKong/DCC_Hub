"""Main window implementation."""
from hub.core.qt_import import import_qt
QtWidgets = import_qt()

# Try to import QtCore for window flags
try:
    from Qt import QtCore
except ImportError:
    try:
        from PySide2 import QtCore
    except ImportError:
        try:
            from PySide6 import QtCore
        except ImportError:
            QtCore = None


class MainWindow(QtWidgets.QWidget):
    """Main application window."""

    def __init__(self, registry=None, context=None, parent=None):
        """Initialize main window.
        
        Args:
            registry: ToolRegistry instance
            context: ToolContext instance
            parent: Parent widget (typically None for top-level window).
        """
        super().__init__(parent)
        self.setWindowTitle("Hub MVP")
        
        # Set window flags to ensure it displays as an independent window
        # Even when parent is Maya main window, we want it as a separate window
        # This prevents the window from being embedded as a child widget
        if QtCore:
            try:
                # Use QtCore.Qt for window flags
                flags = (
                    QtCore.Qt.WindowType.Window |
                    QtCore.Qt.WindowType.WindowMinimizeButtonHint |
                    QtCore.Qt.WindowType.WindowMaximizeButtonHint |
                    QtCore.Qt.WindowType.WindowCloseButtonHint
                )
                self.setWindowFlags(flags)
                print(f"[MainWindow] Set window flags: Window (parent={parent is not None})")
            except AttributeError:
                # Fallback for older Qt versions - try without WindowType enum
                try:
                    flags = (
                        QtCore.Qt.Window |
                        QtCore.Qt.WindowMinimizeButtonHint |
                        QtCore.Qt.WindowMaximizeButtonHint |
                        QtCore.Qt.WindowCloseButtonHint
                    )
                    self.setWindowFlags(flags)
                    print(f"[MainWindow] Set window flags (legacy): Window (parent={parent is not None})")
                except Exception as e:
                    print(f"[MainWindow] Could not set window flags: {e}")
        
        self.registry = registry
        self.context = context
        
        # Create main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        
        # Create Home tab
        home_tab = QtWidgets.QWidget()
        home_layout = QtWidgets.QVBoxLayout(home_tab)
        home_label = QtWidgets.QLabel("Home")
        home_layout.addWidget(home_label)
        home_layout.addStretch()
        self.tab_widget.addTab(home_tab, "Home")
        
        # Create Poly tab
        poly_tab = QtWidgets.QWidget()
        poly_layout = QtWidgets.QVBoxLayout(poly_tab)
        
        # Load poly plugins
        if self.registry and self.context:
            self._load_poly_plugins(poly_layout)
        
        poly_layout.addStretch()
        self.tab_widget.addTab(poly_tab, "Poly")
        
        # Create Console tab
        console_tab = QtWidgets.QWidget()
        console_layout = QtWidgets.QVBoxLayout(console_tab)
        
        # Create QTextEdit for event log
        self.console_text = QtWidgets.QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setPlaceholderText("Event log will appear here...")
        console_layout.addWidget(self.console_text)
        
        self.tab_widget.addTab(console_tab, "Console")
        
        main_layout.addWidget(self.tab_widget)
        
        # Subscribe to tool/done events if context is available
        if self.context and hasattr(self.context, 'evt_bus'):
            self.context.evt_bus.subscribe("tool/done", self._on_tool_done)
            print("[MainWindow] Subscribed to tool/done events")
    
    def _load_poly_plugins(self, layout):
        """Load and add poly category plugins to the layout.
        
        Args:
            layout: QVBoxLayout to add plugins to
        """
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
                    plugin_instance, _ = self.registry.instantiate(tool_key, self.context)
                    
                    # Create UI
                    plugin_ui = plugin_instance.create_ui(parent=self)
                    if plugin_ui:
                        # Add label for plugin
                        label = QtWidgets.QLabel(manifest.get('label', tool_key))
                        layout.addWidget(label)
                        layout.addWidget(plugin_ui)
                        
                        # Add separator
                        separator = QtWidgets.QFrame()
                        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
                        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
                        layout.addWidget(separator)
                except Exception as e:
                    print(f"[MainWindow] Error loading plugin '{tool_key}': {e}")
    
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
        self.console_text.append(message)
        
        # Auto-scroll to bottom
        scrollbar = self.console_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        print(f"[MainWindow] Received tool/done event for {tool_key}")


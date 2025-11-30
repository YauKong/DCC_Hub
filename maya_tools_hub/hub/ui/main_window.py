"""Main window implementation."""
from hub.core.logging import get_logger
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

logger = get_logger(__name__)


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
        
        # Add AIGC test button (Task 25)
        if self.context and hasattr(self.context, 'job_center') and self.context.job_center:
            aigc_button = QtWidgets.QPushButton("Submit Fake AIGC Job")
            aigc_button.clicked.connect(self._on_submit_aigc_job)
            home_layout.addWidget(aigc_button)
            logger.debug("Added AIGC test button to Home tab")
        
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
            self.context.evt_bus.subscribe("tool/failed", self._on_tool_failed)
            self.context.evt_bus.subscribe("job/done", self._on_job_done)
            self.context.evt_bus.subscribe("aigc/done", self._on_aigc_done)
            logger.debug("Subscribed to tool/done, tool/failed, job/done, and aigc/done events")
    
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
                    logger.debug(f"Loading plugin UI: {tool_key}")
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
                        logger.debug(f"Successfully loaded plugin UI: {tool_key}")
                except Exception as e:
                    logger.error(f"Error loading plugin '{tool_key}': {e}", exc_info=True)
    
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
        
        logger.debug(f"Received tool/done event for {tool_key}")
    
    def _on_tool_failed(self, payload):
        """Handle tool/failed event - display error in console.
        
        Args:
            payload: Event payload dict with key, error, error_type, kwargs
        """
        tool_key = payload.get("key", "unknown")
        error = payload.get("error", "Unknown error")
        error_type = payload.get("error_type", "Exception")
        kwargs = payload.get("kwargs", {})
        
        # Format error message with red color
        import json
        message = f"[tool/failed] {tool_key}\n"
        message += f"  error_type: {error_type}\n"
        message += f"  error: {error}\n"
        if kwargs:
            message += f"  kwargs: {json.dumps(kwargs, indent=2)}\n"
        message += "\n"
        
        # Append to console with error styling
        self.console_text.append(message)
        
        # Auto-scroll to bottom
        scrollbar = self.console_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        logger.debug(f"Received tool/failed event for {tool_key}")
    
    def _on_submit_aigc_job(self):
        """Handle AIGC job submission button click.
        
        THREAD SAFETY:
        - Extracts all needed data in main thread
        - Passes only simple data types to worker thread
        - Worker function doesn't access Qt widgets or self
        - Callback executes in main thread for safe Qt/EventBus access
        """
        logger.info("AIGC job submission requested")
        
        if not self.context or not hasattr(self.context, 'services'):
            logger.error("Services not available")
            return
        
        if not hasattr(self.context, 'job_center') or not self.context.job_center:
            logger.error("JobCenter not available")
            return
        
        # Extract needed objects in MAIN thread
        aigc_client = self.context.services.get("aigc")
        if not aigc_client:
            logger.error("AIGC client not found in services")
            return
        
        evt_bus = self.context.evt_bus
        
        # Define AIGC job function - capture only the aigc_client, no self or Qt objects
        def aigc_job():
            """Fake AIGC job that simulates submission and polling.
            
            THREAD SAFE: Only accesses aigc_client (thread-safe stub),
            no Qt widgets, no Maya scene access.
            """
            import time
            
            logger.info("AIGC job started in background thread")
            
            # Submit job (aigc_client methods are thread-safe stubs)
            inputs = {
                "prompt": "Generate a sci-fi spaceship model",
                "style": "realistic",
                "resolution": "2048x2048"
            }
            job_id = aigc_client.submit(inputs)
            logger.info(f"AIGC job submitted: {job_id}")
            
            # Simulate waiting for job completion
            time.sleep(2)
            
            # Poll job status
            status = aigc_client.poll(job_id)
            logger.info(f"AIGC job polling completed: {job_id}")
            
            # Return simple data (no objects, no Qt, no Maya)
            return {
                "job_id": job_id,
                "status": status,
                "inputs": inputs
            }
        
        # Define completion callback - executes in MAIN thread
        def on_complete(result):
            """Callback executed in main thread after job completes.
            
            MAIN THREAD: Safe to access Qt widgets and EventBus here.
            """
            logger.info(f"AIGC job callback in main thread: {result.get('job_id')}")
            
            # Publish aigc/done event (main thread, safe)
            aigc_payload = {
                "job_id": result.get("job_id"),
                "status": result.get("status"),
                "inputs": result.get("inputs")
            }
            evt_bus.publish("aigc/done", aigc_payload)
        
        # Submit to JobCenter
        try:
            self.context.job_center.run_in_thread(aigc_job, callback=on_complete)
            logger.info("AIGC job submitted to JobCenter")
            
            # Show user feedback (main thread, safe)
            self.console_text.append("[INFO] AIGC job submitted, please wait...\n")
        except Exception as e:
            logger.error(f"Error submitting AIGC job: {e}", exc_info=True)
    
    def _on_job_done(self, payload):
        """Handle job/done event - forward to aigc/done if it's an AIGC job.
        
        This executes in MAIN thread (EventBus callbacks are in main thread).
        
        Args:
            payload: Event payload dict with result and status
        """
        logger.debug(f"Received job/done event: {payload}")
        
        result = payload.get("result", {})
        
        # Check if this is an AIGC job (has job_id)
        if isinstance(result, dict) and "job_id" in result:
            logger.info("Detected AIGC job completion from job/done event")
            
            # Note: The callback already published aigc/done, but if callback wasn't set,
            # we handle it here as fallback
            # This is redundant now but kept for robustness
    
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
        self.console_text.append(message)
        
        # Auto-scroll to bottom
        scrollbar = self.console_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        logger.debug(f"Displayed aigc/done event for {job_id}")


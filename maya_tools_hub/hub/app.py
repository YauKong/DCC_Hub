# Import Qt using unified import utility
from hub.core.qt_import import import_qt
QtWidgets = import_qt()

# Try to import QtCore for window attributes
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

from hub.core.command_bus import CommandBus
from hub.core.event_bus import EventBus
from hub.core.job_center import JobCenter
from hub.core.logging import get_logger, set_console_widget
from hub.core.plugins import BaseToolPlugin, ToolContext
from hub.core.registry import ToolRegistry
from hub.core.settings import Settings
from hub.core.state_store import StateStore
from hub.dcc.maya_backend import MayaFacade
from hub.services.aigc_client import AigcClientStub
from hub.services.hda_bridge import HdaBridgeStub
from hub.ui.main_window import MainWindow

logger = get_logger(__name__)

# 模块级变量：保持窗口引用，避免被垃圾回收
_window_instance = None
# 模块级变量：保持 state 引用，避免 reload 时丢失
_state_instance = None


def get_maya_main_window():
    """Get Maya main window as Qt widget parent.
    
    Returns:
        Maya main window widget or None if not in Maya
    """
    try:
        import maya.OpenMayaUI as omui
        
        # Try to import Qt (Qt.py provides QtCompat.wrapInstance)
        try:
            from Qt import QtWidgets, QtCompat
            wrap_instance = QtCompat.wrapInstance
        except ImportError:
            # Fallback to direct PySide imports
            try:
                from PySide2 import QtWidgets
                import shiboken2
                wrap_instance = shiboken2.wrapInstance
            except ImportError:
                try:
                    from PySide6 import QtWidgets
                    import shiboken6
                    wrap_instance = shiboken6.wrapInstance
                except ImportError:
                    return None
        
        # Get Maya main window pointer
        main_window_ptr = omui.MQtUtil.mainWindow()
        if main_window_ptr:
            # Convert pointer to Qt widget
            # MQtUtil.mainWindow() returns a long in Python 2 or int in Python 3
            ptr = int(main_window_ptr)
            main_window = wrap_instance(ptr, QtWidgets.QWidget)
            logger.info(f"Got Maya main window as parent: {main_window}")
            return main_window
    except (ImportError, AttributeError, TypeError) as e:
        logger.warning(f"Could not get Maya main window: {e}")
    
    return None


def detect_dcc():
    """Detect DCC environment and return appropriate facade.
    
    Returns:
        DCCFacade instance (currently always MayaFacade stub).
    """
    return MayaFacade()  # stub


def run() -> int:
    """AppShell entry point - creates and shows main window."""
    global _window_instance, _state_instance
    
    logger.info("Starting Hub application")
    
    dcc = detect_dcc()
    logger.info(f"DCC detected: {dcc.name}")
    
    # Initialize CommandBus
    logger.debug("Initializing CommandBus")
    cmd_bus = CommandBus()
    
    # Register echo command
    def echo_handler(msg):
        """Echo command handler - prints the message."""
        logger.debug(f"Echo command: {msg}")
        return msg
    
    cmd_bus.register("echo", echo_handler)
    logger.debug("Registered 'echo' command")
    
    # Test echo command
    result = cmd_bus.dispatch("echo", msg="hi")
    
    # Initialize EventBus
    logger.debug("Initializing EventBus")
    evt_bus = EventBus()
    
    # Subscribe to test topic
    def test_handler(payload):
        """Test event handler - prints ok value from payload."""
        logger.debug(f"Test event received: ok={payload.get('ok', 'N/A')}")
    
    evt_bus.subscribe("mvp/test", test_handler)
    
    # Publish test event
    evt_bus.publish("mvp/test", {"ok": 1})
    
    # Initialize JobCenter
    logger.debug("Initializing JobCenter")
    job_center = JobCenter(event_bus=evt_bus)
    logger.info("JobCenter initialized and connected to EventBus")
    
    # Initialize Settings
    logger.debug("Initializing Settings")
    settings = Settings()
    
    # Test settings: set, save, load
    settings.set("ui.theme", "dark")
    settings.save()
    settings.load()
    
    # Verify settings
    theme = settings.get("ui.theme", "light")
    logger.info(f"Settings loaded: ui.theme = {theme}")
    
    # Initialize StateStore - reuse existing instance if available (for reload support)
    if _state_instance is None:
        _state_instance = StateStore()
        logger.debug("Created new StateStore instance")
    else:
        logger.debug("Reusing existing StateStore instance (preserved across reload)")
    state = _state_instance
    
    # Test state: set and retrieve
    state["last_panel"] = "home"
    last_panel = state.get("last_panel", "unknown")
    logger.debug(f"State retrieved: last_panel = {last_panel}")
    
    # Initialize Services
    logger.debug("Initializing Services")
    services = {
        "aigc": AigcClientStub(),
        "hda": HdaBridgeStub()
    }
    logger.info(f"Services initialized: {list(services.keys())}")
    
    # Test ToolContext and BaseToolPlugin
    ctx = ToolContext(dcc, settings, state, cmd_bus, evt_bus, job_center=job_center, services=services)
    
    # Create a test plugin subclass
    class TestPlugin(BaseToolPlugin):
        def create_ui(self, parent=None):
            return None
        
        def execute(self, **kwargs):
            return None
    
    test_plugin = TestPlugin(ctx)
    logger.debug(f"Test plugin instantiated: {type(test_plugin).__name__}")
    
    # Test ToolRegistry
    logger.debug("Initializing ToolRegistry")
    registry = ToolRegistry()
    tools = registry.list_tools()
    logger.info(f"Discovered {len(tools)} plugin(s): {tools}")
    
    # Register tool.execute command in CommandBus
    def tool_execute_handler(key, **kwargs):
        """Command handler for tool execution with exception handling.
        
        Args:
            key: Plugin key (e.g., "poly.smooth_normals")
            **kwargs: Plugin-specific parameters to pass to execute()
            
        Returns:
            Result from plugin.execute()
        """
        logger.info(f"Dispatching tool.execute for key: {key}, kwargs: {kwargs}")
        try:
            # Instantiate plugin and execute
            plugin_instance, manifest = registry.instantiate(key, ctx)
            logger.debug(f"Executing plugin: {key}")
            result = plugin_instance.execute(**kwargs)
            logger.info(f"Tool execution completed for key: {key}")
            
            # Publish tool/done event
            payload = {
                "key": key,
                "result": result,
                "kwargs": kwargs
            }
            evt_bus.publish("tool/done", payload)
            logger.debug(f"Published tool/done event for key: {key}")
            
            return result
        except Exception as e:
            # Log error with full stack trace
            logger.error(f"Error executing tool '{key}': {e}", exc_info=True)
            
            # Get plugin label for user-friendly error message
            manifest = registry.get_manifest(key)
            plugin_label = manifest.get("label", key) if manifest else key
            
            # Show user-friendly error message
            error_msg = f"Error in {plugin_label}: {str(e)}"
            dcc.show_message(error_msg, level="error")
            
            # Publish tool/failed event
            failed_payload = {
                "key": key,
                "error": str(e),
                "error_type": type(e).__name__,
                "kwargs": kwargs
            }
            evt_bus.publish("tool/failed", failed_payload)
            logger.debug(f"Published tool/failed event for key: {key}")
            
            # Re-raise the exception to maintain error propagation
            raise
    
    cmd_bus.register("tool.execute", tool_execute_handler)
    logger.debug("Registered 'tool.execute' command in CommandBus")
    
    # Get or create QApplication instance
    # In Maya, QApplication already exists, so instance() returns it
    # For standalone testing, we create a new one
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    
    # 如果窗口已存在且可见，只显示它（避免重复创建）
    if _window_instance is not None:
        try:
            # 检查窗口是否仍然有效（未被销毁）
            if hasattr(_window_instance, 'isVisible') and _window_instance.isVisible():
                # 窗口已存在且可见，不需要创建新的
                logger.debug("Window already exists and is visible, skipping creation")
                _window_instance.raise_()
                _window_instance.activateWindow()
                return 0
            else:
                # 窗口存在但不可见，显示它
                logger.debug("Window exists but not visible, showing it")
                _window_instance.show()
                if QtCore and hasattr(QtCore.Qt, 'WA_ShowOnScreen'):
                    try:
                        _window_instance.setAttribute(QtCore.Qt.WA_ShowOnScreen, True)
                    except Exception:
                        pass
                _window_instance.raise_()
                _window_instance.activateWindow()
                logger.debug(f"Window shown, visible: {_window_instance.isVisible()}")
                return 0
        except Exception as e:
            # 窗口对象已失效，需要创建新的
            logger.warning(f"Existing window instance is invalid: {e}, creating new one")
            _window_instance = None
    
    # Get Maya main window as parent
    maya_parent = get_maya_main_window()
    logger.debug(f"Creating MainWindow with parent: {maya_parent}")
    
    # Create main window
    _window_instance = MainWindow(registry=registry, context=ctx, parent=maya_parent)
    logger.info("MainWindow created successfully")
    
    # Set console widget for logging
    if hasattr(_window_instance, 'console_text'):
        set_console_widget(_window_instance.console_text)
        logger.debug("Console widget connected to logging system")
    
    # Set window attribute to ensure it shows on screen
    if QtCore and hasattr(QtCore.Qt, 'WA_ShowOnScreen'):
        try:
            _window_instance.setAttribute(QtCore.Qt.WA_ShowOnScreen, True)
            logger.debug("Set WA_ShowOnScreen attribute")
        except Exception as e:
            logger.warning(f"Could not set WA_ShowOnScreen: {e}")
    
    # Show the window
    _window_instance.show()
    logger.debug(f"Window shown, visible: {_window_instance.isVisible()}")
    
    # Bring window to front (important when parent is Maya main window)
    _window_instance.raise_()
    _window_instance.activateWindow()
    logger.info("Hub window displayed successfully")
    
    # In Maya, event loop is already running, so exec_() is not needed
    # For standalone testing with stub, exec_() is a no-op anyway
    
    return 0

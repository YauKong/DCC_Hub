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
from hub.core.plugins import BaseToolPlugin, ToolContext
from hub.core.registry import ToolRegistry
from hub.core.settings import Settings
from hub.core.state_store import StateStore
from hub.dcc.maya_backend import MayaFacade
from hub.ui.main_window import MainWindow

# 模块级变量：保持窗口引用，避免被垃圾回收
_window_instance = None


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
            print(f"[App] Got Maya main window as parent: {main_window}")
            return main_window
    except (ImportError, AttributeError, TypeError) as e:
        print(f"[App] Could not get Maya main window: {e}")
    
    return None


def detect_dcc():
    """Detect DCC environment and return appropriate facade.
    
    Returns:
        DCCFacade instance (currently always MayaFacade stub).
    """
    return MayaFacade()  # stub


def run() -> int:
    """AppShell entry point - creates and shows main window."""
    global _window_instance
    
    dcc = detect_dcc()
    print(f"DCC: {dcc.name}")
    
    # Initialize CommandBus
    cmd_bus = CommandBus()
    
    # Register echo command
    def echo_handler(msg):
        """Echo command handler - prints the message."""
        print(msg)
        return msg
    
    cmd_bus.register("echo", echo_handler)
    
    # Test echo command
    result = cmd_bus.dispatch("echo", msg="hi")
    
    # Initialize EventBus
    evt_bus = EventBus()
    
    # Subscribe to test topic
    def test_handler(payload):
        """Test event handler - prints ok value from payload."""
        print(f"ok:{payload.get('ok', 'N/A')}")
    
    evt_bus.subscribe("mvp/test", test_handler)
    
    # Publish test event
    evt_bus.publish("mvp/test", {"ok": 1})
    
    # Initialize Settings
    settings = Settings()
    
    # Test settings: set, save, load
    settings.set("ui.theme", "dark")
    settings.save()
    settings.load()
    
    # Verify settings
    theme = settings.get("ui.theme", "light")
    print(f"Settings loaded: ui.theme = {theme}")
    
    # Initialize StateStore
    state = StateStore()
    
    # Test state: set and retrieve
    state["last_panel"] = "home"
    last_panel = state.get("last_panel", "unknown")
    print(f"State retrieved: last_panel = {last_panel}")
    
    # Test ToolContext and BaseToolPlugin
    ctx = ToolContext(dcc, settings, state, cmd_bus, evt_bus, job_center=None, services=None)
    
    # Create a test plugin subclass
    class TestPlugin(BaseToolPlugin):
        def create_ui(self, parent=None):
            return None
        
        def execute(self, **kwargs):
            return None
    
    test_plugin = TestPlugin(ctx)
    print(f"Plugin instantiated: {type(test_plugin).__name__}")
    
    # Test ToolRegistry
    registry = ToolRegistry()
    tools = registry.list_tools()
    print(f"Discovered tools: {tools}")
    
    # Test plugin discovery (no instantiation or execution)
    if tools:
        print(f"Discovered {len(tools)} plugin(s): {tools}")
    
    # Register tool.execute command in CommandBus
    def tool_execute_handler(key, **kwargs):
        """Command handler for tool execution.
        
        Args:
            key: Plugin key (e.g., "poly.smooth_normals")
            **kwargs: Plugin-specific parameters to pass to execute()
            
        Returns:
            Result from plugin.execute()
        """
        print(f"[CommandBus] Dispatching tool.execute for key: {key}, kwargs: {kwargs}")
        try:
            # Instantiate plugin and execute
            plugin_instance, manifest = registry.instantiate(key, ctx)
            result = plugin_instance.execute(**kwargs)
            print(f"[CommandBus] Tool execution completed for key: {key}")
            
            # Publish tool/done event
            payload = {
                "key": key,
                "result": result,
                "kwargs": kwargs
            }
            evt_bus.publish("tool/done", payload)
            print(f"[CommandBus] Published tool/done event for key: {key}")
            
            return result
        except Exception as e:
            print(f"[CommandBus] Error executing tool '{key}': {e}")
            import traceback
            traceback.print_exc()
            raise
    
    cmd_bus.register("tool.execute", tool_execute_handler)
    print("[App] Registered 'tool.execute' command in CommandBus")
    
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
                print("[App] Window already exists and is visible, skipping creation")
                _window_instance.raise_()
                _window_instance.activateWindow()
                return 0
            else:
                # 窗口存在但不可见，显示它
                print("[App] Window exists but not visible, showing it")
                _window_instance.show()
                if QtCore and hasattr(QtCore.Qt, 'WA_ShowOnScreen'):
                    try:
                        _window_instance.setAttribute(QtCore.Qt.WA_ShowOnScreen, True)
                    except Exception:
                        pass
                _window_instance.raise_()
                _window_instance.activateWindow()
                print(f"[App] Window shown, visible: {_window_instance.isVisible()}")
                return 0
        except Exception as e:
            # 窗口对象已失效，需要创建新的
            print(f"[App] Existing window instance is invalid: {e}, creating new one")
            _window_instance = None
    
    # Get Maya main window as parent
    maya_parent = get_maya_main_window()
    print(f"[App] Creating MainWindow with parent: {maya_parent}")
    
    # Create main window
    _window_instance = MainWindow(registry=registry, context=ctx, parent=maya_parent)
    print(f"[App] MainWindow created: {_window_instance}")
    
    # Set window attribute to ensure it shows on screen
    if QtCore and hasattr(QtCore.Qt, 'WA_ShowOnScreen'):
        try:
            _window_instance.setAttribute(QtCore.Qt.WA_ShowOnScreen, True)
            print("[App] Set WA_ShowOnScreen attribute")
        except Exception as e:
            print(f"[App] Could not set WA_ShowOnScreen: {e}")
    
    # Show the window
    _window_instance.show()
    print(f"[App] Window shown, visible: {_window_instance.isVisible()}")
    
    # Bring window to front (important when parent is Maya main window)
    _window_instance.raise_()
    _window_instance.activateWindow()
    print(f"[App] Window raised and activated, visible: {_window_instance.isVisible()}")
    
    # Additional debug info
    if hasattr(_window_instance, 'windowFlags'):
        print(f"[App] Window flags: {_window_instance.windowFlags()}")
    if hasattr(_window_instance, 'parent'):
        print(f"[App] Window parent: {_window_instance.parent()}")
    if hasattr(_window_instance, 'geometry'):
        print(f"[App] Window geometry: {_window_instance.geometry()}")
    
    # In Maya, event loop is already running, so exec_() is not needed
    # For standalone testing with stub, exec_() is a no-op anyway
    
    return 0

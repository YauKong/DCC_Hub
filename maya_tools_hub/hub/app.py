# Import Qt using unified import utility
from hub.core.qt_import import import_qt
QtWidgets = import_qt()

from hub.core.command_bus import CommandBus
from hub.core.event_bus import EventBus
from hub.core.settings import Settings
from hub.core.state_store import StateStore
from hub.dcc.maya_backend import MayaFacade
from hub.ui.main_window import MainWindow

# 模块级变量：保持窗口引用，避免被垃圾回收
_window_instance = None


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
    
    # Test MayaFacade methods
    selection = dcc.get_selection()
    print(f"Selection: {selection}")
    
    dcc.show_message("hello", level="info")
    
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
                return 0
            else:
                # 窗口存在但不可见，显示它
                _window_instance.show()
                return 0
        except:
            # 窗口对象已失效，需要创建新的
            _window_instance = None
    
    # Create and show main window
    _window_instance = MainWindow()
    _window_instance.show()
    
    # In Maya, event loop is already running, so exec_() is not needed
    # For standalone testing with stub, exec_() is a no-op anyway
    
    return 0

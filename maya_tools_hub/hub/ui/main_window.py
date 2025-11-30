"""Main window implementation."""
from hub.core.logging import get_logger
from hub.core.qt_import import import_qt
from hub.ui.panels.panel_home import HomePanel
from hub.ui.panels.panel_poly import PolyPanel
from hub.ui.widgets.console import ConsoleWidget

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

        # Create Console widget first (Home panel needs it)
        self.console_widget = ConsoleWidget(context=self.context, parent=self)

        # Create and add panels
        # Home panel
        home_panel = HomePanel(
            context=self.context,
            console_widget=self.console_widget.console_text,
            parent=self
        )
        self.tab_widget.addTab(home_panel, "Home")

        # Poly panel
        poly_panel = PolyPanel(
            registry=self.registry,
            context=self.context,
            parent=self
        )
        self.tab_widget.addTab(poly_panel, "Poly")

        # Console panel
        self.tab_widget.addTab(self.console_widget, "Console")

        main_layout.addWidget(self.tab_widget)

        logger.debug("MainWindow initialized with modular panels")


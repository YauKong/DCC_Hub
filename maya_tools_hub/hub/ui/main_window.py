"""Main window implementation."""
from hub.core.qt_import import import_qt
QtWidgets = import_qt()


class MainWindow(QtWidgets.QWidget):
    """Main application window."""

    def __init__(self, parent=None):
        """Initialize main window.
        
        Args:
            parent: Parent widget (typically None for top-level window).
        """
        super().__init__(parent)
        self.setWindowTitle("Hub MVP")


"""Unified Qt import utility - prioritizes vendor Qt.py, falls back to DCC Qt or stub."""
import warnings
import sys


def import_qt():
    """Import Qt with fallback strategy.
    
    Priority:
    1. Vendor's Qt.py (if available and Qt bindings exist)
    2. Direct PySide2/PySide6 (in DCC environments)
    3. Minimal stub (for non-GUI testing)
    
    Returns:
        QtWidgets module or stub
    """
    # Try vendor's Qt.py first
    try:
        from Qt import QtWidgets
        return QtWidgets
    except ImportError:
        pass
    
    # Fallback: try direct PySide imports (Maya/Max environments)
    try:
        from PySide2 import QtWidgets
        return QtWidgets
    except ImportError:
        try:
            from PySide6 import QtWidgets
            return QtWidgets
        except ImportError:
            pass
    
    # No Qt available - create minimal stub for non-GUI testing
    warnings.warn(
        "Qt not available. Running in stub mode. "
        "For full functionality, run in Maya or install PySide2/PySide6.",
        UserWarning
    )
    
    # Minimal stub for testing
    class _QWidgetStub:
        def __init__(self, parent=None):
            self._parent = parent
            self._window_title = ""
        def setWindowTitle(self, title):
            self._window_title = title
        def show(self):
            pass
    
    class _QApplicationStub:
        _instance = None
        def __init__(self, argv=None):
            _QApplicationStub._instance = self
        @classmethod
        def instance(cls):
            return cls._instance
        def exec_(self):
            return 0
    
    class _QtWidgetsStub:
        QWidget = _QWidgetStub
        QApplication = _QApplicationStub
    
    return _QtWidgetsStub()


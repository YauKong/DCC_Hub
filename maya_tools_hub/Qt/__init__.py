"""Qt.py compatibility layer - uses project's Qt.py or Maya's Qt."""

# Try to import Qt.py from project vendor first
try:
    import Qt
    # Qt.py is available, use it
    from Qt import QtWidgets, QtCore, QtGui
    _qt_available = True
except ImportError:
    # Qt.py not found, try Maya's Qt directly
    try:
        import maya.OpenMayaUI as omui
        
        # Check if we're in Maya
        if hasattr(omui, 'MQtUtil'):
            # Maya uses PySide2 or PySide6
            try:
                from PySide2 import QtWidgets, QtCore, QtGui
                _qt_available = True
            except ImportError:
                try:
                    from PySide6 import QtWidgets, QtCore, QtGui
                    _qt_available = True
                except ImportError:
                    _qt_available = False
        else:
            _qt_available = False
    except (ImportError, AttributeError):
        _qt_available = False

# If Qt is still not available, raise an error
if not _qt_available:
    raise ImportError(
        "Qt not available. Please install Qt.py to hub/vendor/thirdparty_libs "
        "or ensure you're running in a DCC environment with Qt support."
    )

__all__ = ["QtWidgets", "QtCore", "QtGui"]

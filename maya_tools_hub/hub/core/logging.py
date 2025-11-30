"""Unified logging system for Hub."""
import logging
import sys
from typing import Optional


# Global console handler reference for MainWindow integration
_console_handler: Optional['ConsoleHandler'] = None


class ConsoleHandler(logging.Handler):
    """Custom logging handler that can write to MainWindow console panel."""
    
    def __init__(self):
        """Initialize console handler."""
        super().__init__()
        self._console_widget = None
    
    def set_console_widget(self, widget):
        """Set the QTextEdit widget to write logs to.
        
        Args:
            widget: QTextEdit widget instance
        """
        self._console_widget = widget
    
    def emit(self, record):
        """Emit a log record.
        
        Args:
            record: LogRecord instance
        """
        try:
            msg = self.format(record)
            
            # Write to stdout (always)
            print(msg)
            
            # Write to console widget if available
            if self._console_widget is not None:
                try:
                    # Append to console widget
                    self._console_widget.append(msg)
                    
                    # Auto-scroll to bottom
                    scrollbar = self._console_widget.verticalScrollBar()
                    if scrollbar:
                        scrollbar.setValue(scrollbar.maximum())
                except Exception:
                    # Widget might be destroyed, ignore
                    pass
        except Exception:
            # Prevent logging errors from breaking the application
            self.handleError(record)


def setup_logging(level=logging.INFO, console_widget=None):
    """Setup logging configuration.
    
    Args:
        level: Logging level (default: INFO)
        console_widget: Optional QTextEdit widget for console output
    """
    global _console_handler
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Create console handler
    _console_handler = ConsoleHandler()
    _console_handler.setFormatter(formatter)
    _console_handler.setLevel(level)
    
    # Set console widget if provided
    if console_widget is not None:
        _console_handler.set_console_widget(console_widget)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add console handler
    root_logger.addHandler(_console_handler)
    
    # Prevent propagation to avoid duplicate logs
    root_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_console_widget(widget):
    """Set the console widget for logging output.
    
    This can be called after MainWindow is created to redirect logs to the console panel.
    
    Args:
        widget: QTextEdit widget instance
    """
    global _console_handler
    if _console_handler is not None:
        _console_handler.set_console_widget(widget)


# Initialize logging on module import
setup_logging()


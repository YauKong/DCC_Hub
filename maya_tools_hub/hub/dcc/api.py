"""DCC-agnostic facade interface definition."""
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import List, Optional


class DCCFacade(ABC):
    """Abstract interface for DCC backend operations."""

    @abstractmethod
    def get_selection(self) -> List[str]:
        """Get currently selected objects in DCC.
        
        Returns:
            List of selected object names (full paths).
        """
        pass

    @abstractmethod
    @contextmanager
    def undo_chunk(self, label: str):
        """Context manager for undo chunk operations.
        
        Args:
            label: Label for the undo chunk.
            
        Yields:
            None (used as context manager).
        """
        pass

    @abstractmethod
    def show_message(self, text: str, level: str = "info") -> None:
        """Display a message to the user in DCC.
        
        Args:
            text: Message text to display.
            level: Message level ("info", "warning", "error").
        """
        pass


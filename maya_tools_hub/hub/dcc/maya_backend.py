"""Maya backend implementation of DCCFacade."""
from contextlib import contextmanager
from typing import List

from hub.core.undo import maya_undo_chunk
from hub.dcc.api import DCCFacade


class MayaFacade(DCCFacade):
    """Maya implementation of DCC facade."""

    name = "Maya"

    def get_selection(self) -> List[str]:
        """Get currently selected objects in Maya.
        
        Returns:
            List of selected object full paths, or empty list if nothing selected.
        """
        try:
            import maya.cmds as cmds
            return cmds.ls(sl=True, l=True) or []
        except ImportError:
            # Not in Maya environment
            return []

    @contextmanager
    def undo_chunk(self, label: str):
        """Context manager for Maya undo chunk operations.
        
        Args:
            label: Label for the undo chunk.
        """
        with maya_undo_chunk(label):
            yield

    def show_message(self, text: str, level: str = "info") -> None:
        """Display a message to the user in Maya.
        
        Args:
            text: Message text to display.
            level: Message level ("info", "warning", "error").
        """
        try:
            import maya.cmds as cmds
            
            # Use inViewMessage for simple popup
            cmds.inViewMessage(
                amg=text,
                pos='midCenter',
                fade=True,
                fst=2000,
                fts=10
            )
        except ImportError:
            # Not in Maya environment - just print
            print(f"[{level.upper()}] {text}")


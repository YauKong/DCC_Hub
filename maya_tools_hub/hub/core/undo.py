"""Undo - DCC undo chunk integration."""
from contextlib import contextmanager


@contextmanager
def maya_undo_chunk(label):
    """Context manager for Maya undo chunk.
    
    Opens an undo chunk when entering the context and closes it when exiting.
    Safe to import and use even when not running in Maya (will be a no-op).
    
    Args:
        label: Name for the undo chunk
        
    Example:
        with maya_undo_chunk("MyOperation"):
            cmds.polyCube()
            cmds.move(1, 0, 0)
    """
    try:
        import maya.cmds as cmds
        # Open undo chunk
        cmds.undoInfo(openChunk=True, chunkName=label)
        try:
            yield
        finally:
            # Close undo chunk
            cmds.undoInfo(closeChunk=True)
    except ImportError:
        # Not in Maya environment - no-op
        yield


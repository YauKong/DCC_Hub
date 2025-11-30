"""Houdini HDA bridge stub implementation."""
from hub.core.logging import get_logger

logger = get_logger(__name__)


class HdaBridgeStub:
    """Stub implementation of Houdini HDA bridge.
    
    This is a placeholder implementation that logs method calls.
    Replace with actual HDA execution when integrating with Houdini.
    """
    
    def __init__(self):
        """Initialize HDA bridge stub."""
        logger.info("HdaBridgeStub initialized")
    
    def run_hda(self, hda_path, parms):
        """Execute a Houdini HDA with given parameters.
        
        Args:
            hda_path: Path to HDA file (string)
            parms: HDA parameters (dict)
            
        Returns:
            outputs: Execution results (dict)
        """
        logger.info(f"HdaBridgeStub.run_hda() called")
        logger.info(f"  hda_path: {hda_path}")
        logger.info(f"  parms: {parms}")
        
        # Return fake outputs
        outputs = {
            "success": True,
            "output_geo": "/fake/path/to/output.bgeo",
            "log": "HDA execution completed (fake)",
            "execution_time": 1.23
        }
        
        logger.debug(f"Returning fake outputs: {outputs}")
        return outputs
    
    def list_hdas(self, directory):
        """List available HDAs in a directory.
        
        Args:
            directory: Directory path to search for HDAs (string)
            
        Returns:
            hdas: List of HDA file paths
        """
        logger.info(f"HdaBridgeStub.list_hdas() called with directory: {directory}")
        
        # Return fake HDA list
        hdas = [
            "/fake/path/hda1.hdanc",
            "/fake/path/hda2.hdanc",
            "/fake/path/hda3.hdanc"
        ]
        
        logger.debug(f"Returning fake HDA list: {hdas}")
        return hdas


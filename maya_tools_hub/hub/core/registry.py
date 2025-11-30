"""ToolRegistry - plugin discovery and instantiation."""
import importlib
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from hub.core.logging import get_logger
from hub.core.plugins import BaseToolPlugin, ToolContext

logger = get_logger(__name__)


class ToolRegistry:
    """Plugin registry for discovering and loading tools from manifest files."""
    
    def __init__(self, plugins_root: Optional[Path] = None):
        """Initialize registry.
        
        Args:
            plugins_root: Root directory for plugins (default: hub/plugins)
        """
        if plugins_root is None:
            # Default: hub/plugins relative to this file
            current_file = Path(__file__)
            hub_dir = current_file.parent.parent
            plugins_root = hub_dir / "plugins"
        
        self.plugins_root = Path(plugins_root)
        self._manifests = {}  # key -> manifest dict
        self._discover_plugins()
    
    def _discover_plugins(self):
        """Scan plugins directory for manifest.json files."""
        if not self.plugins_root.exists():
            logger.warning(f"Plugins root directory does not exist: {self.plugins_root}")
            return
        
        logger.debug(f"Scanning for plugins in: {self.plugins_root}")
        discovered_count = 0
        
        # Scan plugins/*/*/manifest.json
        for category_dir in self.plugins_root.iterdir():
            if not category_dir.is_dir():
                continue
            
            for plugin_dir in category_dir.iterdir():
                if not plugin_dir.is_dir():
                    continue
                
                manifest_path = plugin_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        
                        key = manifest.get('key')
                        if key:
                            manifest['_plugin_dir'] = str(plugin_dir)
                            self._manifests[key] = manifest
                            discovered_count += 1
                            logger.debug(f"Discovered plugin: {key} from {manifest_path}")
                    except (json.JSONDecodeError, IOError) as e:
                        logger.error(f"Error loading manifest from {manifest_path}: {e}")
        
        logger.info(f"Plugin discovery completed: found {discovered_count} plugin(s)")
    
    def get_manifest(self, key: str) -> Optional[Dict]:
        """Get manifest for a plugin key.
        
        Args:
            key: Plugin key
            
        Returns:
            Manifest dict or None if not found
        """
        return self._manifests.get(key)
    
    def list_tools(self) -> list:
        """List all discovered tool keys.
        
        Returns:
            List of tool keys
        """
        return list(self._manifests.keys())
    
    def instantiate(self, key: str, ctx: ToolContext) -> Tuple[BaseToolPlugin, Dict]:
        """Instantiate a plugin by key.
        
        Args:
            key: Plugin key
            ctx: ToolContext instance
            
        Returns:
            Tuple of (plugin_instance, manifest)
            
        Raises:
            KeyError: If plugin key not found
            ImportError: If module/class cannot be loaded
        """
        logger.debug(f"Instantiating plugin: {key}")
        manifest = self._manifests.get(key)
        if not manifest:
            logger.error(f"Plugin '{key}' not found in registry")
            raise KeyError(f"Plugin '{key}' not found in registry")
        
        entry = manifest.get('entry')
        if not entry:
            logger.error(f"Plugin '{key}' manifest missing 'entry' field")
            raise ValueError(f"Plugin '{key}' manifest missing 'entry' field")
        
        # Parse entry as "module:Class"
        if ':' not in entry:
            logger.error(f"Plugin '{key}' entry must be in format 'module:Class', got: {entry}")
            raise ValueError(f"Plugin '{key}' entry must be in format 'module:Class', got: {entry}")
        
        module_path, class_name = entry.split(':', 1)
        logger.debug(f"Loading plugin class: {module_path}.{class_name}")
        
        # Import module
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            logger.error(f"Failed to import module '{module_path}' for plugin '{key}': {e}")
            raise ImportError(f"Failed to import module '{module_path}' for plugin '{key}': {e}")
        
        # Get class
        if not hasattr(module, class_name):
            logger.error(f"Module '{module_path}' does not have class '{class_name}'")
            raise AttributeError(f"Module '{module_path}' does not have class '{class_name}'")
        
        plugin_class = getattr(module, class_name)
        
        # Instantiate plugin
        try:
            plugin_instance = plugin_class(ctx)
            # Store plugin key in instance for command dispatch
            plugin_instance._plugin_key = key
            logger.debug(f"Successfully instantiated plugin: {key}")
        except Exception as e:
            logger.error(f"Failed to instantiate plugin '{key}': {e}", exc_info=True)
            raise RuntimeError(f"Failed to instantiate plugin '{key}': {e}")
        
        return plugin_instance, manifest


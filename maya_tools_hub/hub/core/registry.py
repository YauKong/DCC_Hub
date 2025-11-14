"""ToolRegistry - plugin discovery and instantiation."""
import importlib
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from hub.core.plugins import BaseToolPlugin, ToolContext


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
            return
        
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
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"[ToolRegistry] Error loading manifest from {manifest_path}: {e}")
    
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
        manifest = self._manifests.get(key)
        if not manifest:
            raise KeyError(f"Plugin '{key}' not found in registry")
        
        entry = manifest.get('entry')
        if not entry:
            raise ValueError(f"Plugin '{key}' manifest missing 'entry' field")
        
        # Parse entry as "module:Class"
        if ':' not in entry:
            raise ValueError(f"Plugin '{key}' entry must be in format 'module:Class', got: {entry}")
        
        module_path, class_name = entry.split(':', 1)
        
        # Import module
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(f"Failed to import module '{module_path}' for plugin '{key}': {e}")
        
        # Get class
        if not hasattr(module, class_name):
            raise AttributeError(f"Module '{module_path}' does not have class '{class_name}'")
        
        plugin_class = getattr(module, class_name)
        
        # Instantiate plugin
        try:
            plugin_instance = plugin_class(ctx)
            # Store plugin key in instance for command dispatch
            plugin_instance._plugin_key = key
        except Exception as e:
            raise RuntimeError(f"Failed to instantiate plugin '{key}': {e}")
        
        return plugin_instance, manifest


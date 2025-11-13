"""Settings - user-level JSON configuration management."""
import json
from pathlib import Path


class Settings:
    """User-level settings manager with JSON persistence.
    
    Supports dot-notation keys (e.g., "ui.theme") and automatic file saving.
    """
    
    def __init__(self, file_path=None):
        """Initialize settings manager.
        
        Args:
            file_path: Path to settings file. If None, uses default:
                ~/.studio_name/maya_tools_hub/user_settings.json
        """
        if file_path is None:
            # Default path: ~/.studio_name/maya_tools_hub/user_settings.json
            home = Path.home()
            default_dir = home / ".studio_name" / "maya_tools_hub"
            default_dir.mkdir(parents=True, exist_ok=True)
            file_path = default_dir / "user_settings.json"
        
        self._file_path = Path(file_path)
        self._data = {}
        self.load()
    
    def _get_nested(self, key_path):
        """Get nested value using dot-notation key.
        
        Args:
            key_path: Dot-separated key (e.g., "ui.theme")
            
        Returns:
            Tuple (dict, final_key) where dict is the parent dict and final_key is the last key
        """
        keys = key_path.split('.')
        current = self._data
        
        # Navigate to parent dict
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        
        return current, keys[-1]
    
    def get(self, key, default=None):
        """Get a setting value.
        
        Args:
            key: Dot-separated key (e.g., "ui.theme")
            default: Default value if key doesn't exist
            
        Returns:
            Setting value or default
        """
        parent, final_key = self._get_nested(key)
        return parent.get(final_key, default)
    
    def set(self, key, value):
        """Set a setting value.
        
        Args:
            key: Dot-separated key (e.g., "ui.theme")
            value: Value to set
        """
        parent, final_key = self._get_nested(key)
        parent[final_key] = value
    
    def load(self):
        """Load settings from file."""
        if self._file_path.exists():
            try:
                with open(self._file_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[Settings] Error loading settings: {e}")
                self._data = {}
        else:
            self._data = {}
    
    def save(self):
        """Save settings to file."""
        try:
            # Ensure directory exists
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"[Settings] Error saving settings: {e}")


"""
Sync manager for Clyde.
Handles synchronization of configuration files and change detection.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import hashlib
from datetime import datetime

from .config import ClydeConfig
from .builder import ConfigBuilder, ConfigValidator


class SyncManager:
    """Manages synchronization of Clyde configuration files."""
    
    def __init__(self, config: ClydeConfig):
        self.config = config
        self.builder = ConfigBuilder(config)
        self.validator = ConfigValidator(config)
    
    def sync(self):
        """Synchronize configuration files."""
        # Validate configuration first
        issues = self.validator.validate()
        if issues and self.config.options.get("validation_level") == "strict":
            raise ValueError(f"Configuration validation failed:\n" + 
                           "\n".join(f"- {issue}" for issue in issues))
        elif issues:
            print("Warning: Configuration warnings:")
            for issue in issues:
                print(f"  - {issue}")
        
        # Generate and write the generated.md file
        generated_content = self.builder.build_generated_file()
        generated_file = self.config.project_path / ".claude" / "generated.md"
        
        # Ensure directory exists
        generated_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the generated file
        with open(generated_file, 'w', encoding='utf-8') as f:
            f.write(generated_content)
        
        # Update metadata
        self._update_sync_metadata()
    
    def preview_changes(self) -> List[str]:
        """Preview what changes would be made without applying them."""
        changes = []
        
        # Check if generated.md would change
        generated_file = self.config.project_path / ".claude" / "generated.md"
        new_content = self.builder.build_generated_file()
        
        if generated_file.exists():
            with open(generated_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            if current_content != new_content:
                changes.append(f"Update {generated_file.relative_to(self.config.project_path)}")
        else:
            changes.append(f"Create {generated_file.relative_to(self.config.project_path)}")
        
        # Check for configuration validation issues
        issues = self.validator.validate()
        if issues:
            changes.append(f"Fix {len(issues)} configuration issues")
        
        return changes
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current synchronization status."""
        metadata = self._load_sync_metadata()
        generated_file = self.config.project_path / ".claude" / "generated.md"
        
        status = {
            "last_sync": metadata.get("last_sync"),
            "config_hash": metadata.get("config_hash"),
            "current_hash": self.config.get_config_hash(),
            "generated_exists": generated_file.exists(),
            "needs_sync": False
        }
        
        # Determine if sync is needed
        if not generated_file.exists():
            status["needs_sync"] = True
            status["reason"] = "Generated file does not exist"
        elif status["config_hash"] != status["current_hash"]:
            status["needs_sync"] = True
            status["reason"] = "Configuration has changed"
        elif self._is_generated_file_stale():
            status["needs_sync"] = True
            status["reason"] = "Generated file is older than source modules"
        
        return status
    
    def _update_sync_metadata(self):
        """Update synchronization metadata."""
        metadata_file = self.config.project_path / ".claude" / ".sync_metadata"
        
        metadata = {
            "last_sync": datetime.now().isoformat(),
            "config_hash": self.config.get_config_hash(),
            "clyde_version": "1.0.0",
            "module_count": len(self.config.includes)
        }
        
        import json
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_sync_metadata(self) -> Dict[str, Any]:
        """Load synchronization metadata."""
        metadata_file = self.config.project_path / ".claude" / ".sync_metadata"
        
        if not metadata_file.exists():
            return {}
        
        try:
            import json
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _is_generated_file_stale(self) -> bool:
        """Check if generated file is older than any source modules."""
        generated_file = self.config.project_path / ".claude" / "generated.md"
        
        if not generated_file.exists():
            return True
        
        generated_mtime = generated_file.stat().st_mtime
        
        # Check if any module is newer than generated file
        for module_id in self.config.includes:
            module_path = self.config.get_module_path(module_id)
            if module_path.exists() and module_path.stat().st_mtime > generated_mtime:
                return True
        
        # Check if config file is newer
        config_file = self.config.project_path / ".claude" / "config.yaml"
        if config_file.exists() and config_file.stat().st_mtime > generated_mtime:
            return True
        
        return False


class ChangeDetector:
    """Detects changes in configuration and modules."""
    
    def __init__(self, config: ClydeConfig):
        self.config = config
    
    def detect_changes(self, since: Optional[datetime] = None) -> List[str]:
        """Detect changes since the specified time."""
        changes = []
        
        if since is None:
            # Use last sync time if available
            sync_manager = SyncManager(self.config)
            metadata = sync_manager._load_sync_metadata()
            if "last_sync" in metadata:
                since = datetime.fromisoformat(metadata["last_sync"])
        
        if since is None:
            return ["Initial sync - no previous timestamp available"]
        
        since_timestamp = since.timestamp()
        
        # Check configuration file
        config_file = self.config.project_path / ".claude" / "config.yaml"
        if config_file.exists() and config_file.stat().st_mtime > since_timestamp:
            changes.append("Configuration file modified")
        
        # Check module files
        for module_id in self.config.includes:
            module_path = self.config.get_module_path(module_id)
            if module_path.exists() and module_path.stat().st_mtime > since_timestamp:
                changes.append(f"Module modified: {module_id}")
        
        return changes
    
    def get_file_hash(self, file_path: Path) -> str:
        """Get hash of a file's content."""
        if not file_path.exists():
            return ""
        
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except IOError:
            return ""
    
    def compare_configs(self, other_config: ClydeConfig) -> List[str]:
        """Compare two configurations and return differences."""
        differences = []
        
        if self.config.project_name != other_config.project_name:
            differences.append(f"Project name: {self.config.project_name} -> {other_config.project_name}")
        
        if self.config.language != other_config.language:
            differences.append(f"Language: {self.config.language} -> {other_config.language}")
        
        if self.config.framework != other_config.framework:
            differences.append(f"Framework: {self.config.framework} -> {other_config.framework}")
        
        # Compare includes
        added_modules = set(other_config.includes) - set(self.config.includes)
        removed_modules = set(self.config.includes) - set(other_config.includes)
        
        for module in added_modules:
            differences.append(f"Added module: {module}")
        
        for module in removed_modules:
            differences.append(f"Removed module: {module}")
        
        return differences


class AutoSync:
    """Automatic synchronization functionality."""
    
    def __init__(self, config: ClydeConfig):
        self.config = config
        self.sync_manager = SyncManager(config)
    
    def should_auto_sync(self) -> bool:
        """Determine if auto-sync should be performed."""
        # Check if auto-sync is enabled
        if not self.config.options.get("auto_sync", False):
            return False
        
        # Check if sync is needed
        status = self.sync_manager.get_sync_status()
        return status.get("needs_sync", False)
    
    def perform_auto_sync(self) -> bool:
        """Perform automatic synchronization if conditions are met."""
        if not self.should_auto_sync():
            return False
        
        try:
            self.sync_manager.sync()
            return True
        except Exception as e:
            print(f"Auto-sync failed: {e}")
            return False
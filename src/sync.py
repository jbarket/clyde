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
    
    def sync(self, target: str = None):
        """Synchronize configuration files for all targets or a specific target."""
        # Validate configuration first
        issues = self.validator.validate()
        if issues and self.config.options.get("validation_level") == "strict":
            raise ValueError(f"Configuration validation failed:\n" + 
                           "\n".join(f"- {issue}" for issue in issues))
        elif issues:
            print("Warning: Configuration warnings:")
            for issue in issues:
                print(f"  - {issue}")
        
        # Sync specific target or all targets
        if target:
            if target not in self.config.targets:
                raise ValueError(f"Target '{target}' not configured. Available targets: {', '.join(self.config.targets)}")
            self.sync_target(target)
        else:
            # Sync all targets
            for target_name in self.config.targets:
                self.sync_target(target_name)
        
        # Update metadata
        self._update_sync_metadata()
    
    def sync_target(self, target: str):
        """Synchronize configuration files for a specific target."""
        # Generate target-specific content
        generated_content = self.builder.build_generated_file_for_target(target)
        generated_file = self.config.project_path / ".clyde" / f"generated-{target}.md"
        
        # Ensure directory exists
        generated_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the generated file for this target
        with open(generated_file, 'w', encoding='utf-8') as f:
            f.write(generated_content)
        
        print(f"Generated {generated_file.relative_to(self.config.project_path)} for {target}")
    
    def preview_changes(self, target: str = None) -> List[str]:
        """Preview what changes would be made without applying them."""
        changes = []
        
        # Check changes for specific target or all targets
        targets_to_check = [target] if target else self.config.targets
        
        for target_name in targets_to_check:
            # Check if target-specific generated file would change
            generated_file = self.config.project_path / ".clyde" / f"generated-{target_name}.md"
            new_content = self.builder.build_generated_file_for_target(target_name)
            
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
        
        status = {
            "last_sync": metadata.get("last_sync"),
            "config_hash": metadata.get("config_hash"),
            "current_hash": self.config.get_config_hash(),
            "needs_sync": False,
            "targets": {}
        }
        
        # Check each target
        for target in self.config.targets:
            generated_file = self.config.project_path / ".clyde" / f"generated-{target}.md"
            target_status = {
                "generated_exists": generated_file.exists(),
                "needs_sync": False
            }
            
            # Determine if sync is needed for this target
            if not generated_file.exists():
                target_status["needs_sync"] = True
                target_status["reason"] = f"Generated file for {target} does not exist"
                status["needs_sync"] = True
            elif status["config_hash"] != status["current_hash"]:
                target_status["needs_sync"] = True
                target_status["reason"] = "Configuration has changed"
                status["needs_sync"] = True
            elif self._is_generated_file_stale_for_target(target):
                target_status["needs_sync"] = True
                target_status["reason"] = f"Generated file for {target} is older than source modules"
                status["needs_sync"] = True
            
            status["targets"][target] = target_status
        
        return status
    
    def _update_sync_metadata(self):
        """Update synchronization metadata."""
        metadata_file = self.config.project_path / ".clyde" / ".sync_metadata"
        
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
        metadata_file = self.config.project_path / ".clyde" / ".sync_metadata"
        
        if not metadata_file.exists():
            return {}
        
        try:
            import json
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _is_generated_file_stale_for_target(self, target: str) -> bool:
        """Check if generated file for target is older than any source modules."""
        generated_file = self.config.project_path / ".clyde" / f"generated-{target}.md"
        
        if not generated_file.exists():
            return True
        
        generated_mtime = generated_file.stat().st_mtime
        
        # Check if any module (including AI-specific) is newer than generated file
        all_modules = self.config.get_all_modules_for_target(target)
        for module_id in all_modules:
            module_path = self.config.get_module_path(module_id)
            if module_path.exists() and module_path.stat().st_mtime > generated_mtime:
                return True
        
        # Check if config file is newer
        config_file = self.config.project_path / ".clyde" / "config.yaml"
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
        config_file = self.config.project_path / ".clyde" / "config.yaml"
        if config_file.exists() and config_file.stat().st_mtime > since_timestamp:
            changes.append("Configuration file modified")
        
        # Check module files (including AI-specific modules for all targets)
        checked_modules = set()
        for target in self.config.targets:
            all_modules = self.config.get_all_modules_for_target(target)
            for module_id in all_modules:
                if module_id not in checked_modules:
                    checked_modules.add(module_id)
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
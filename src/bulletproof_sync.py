"""
Bulletproof sync system for Clyde.
Provides comprehensive safety, validation, backup, and recovery mechanisms.
"""

import json
import shutil
import hashlib
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .config import ClydeConfig
from .sync import SyncManager
from .builder import ConfigBuilder, ConfigValidator
from . import __version__


class SyncOperation(Enum):
    """Types of sync operations."""
    VALIDATE = "validate"
    BACKUP = "backup"
    SYNC = "sync"
    VERIFY = "verify"
    ROLLBACK = "rollback"


@dataclass
class SyncSnapshot:
    """Represents a snapshot of the sync state for backup/restore."""
    timestamp: str
    config_hash: str
    operation: str
    files: Dict[str, str] = field(default_factory=dict)  # path -> content hash
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "config_hash": self.config_hash,
            "operation": self.operation,
            "files": self.files,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncSnapshot':
        return cls(
            timestamp=data["timestamp"],
            config_hash=data["config_hash"],
            operation=data["operation"],
            files=data.get("files", {}),
            metadata=data.get("metadata", {})
        )


@dataclass
class ValidationIssue:
    """Represents a validation issue found during pre-sync checks."""
    severity: str  # "error", "warning", "info"
    category: str  # "config", "file", "migration", "corruption"
    message: str
    file_path: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    operation: SyncOperation
    snapshot_id: Optional[str] = None
    issues: List[ValidationIssue] = field(default_factory=list)
    changes_made: List[str] = field(default_factory=list)
    rollback_available: bool = False
    message: str = ""


class BulletproofSyncManager:
    """
    Enhanced sync manager with comprehensive safety features:
    - Pre-sync validation and integrity checks
    - Automatic backup creation before any changes
    - Atomic operations with rollback capability
    - Migration detection and handling
    - Corruption detection and recovery
    - Detailed logging and audit trail
    """
    
    def __init__(self, config: ClydeConfig):
        self.config = config
        self.sync_manager = SyncManager(config)
        self.builder = ConfigBuilder(config)
        self.validator = ConfigValidator(config)
        
        # Paths for bulletproof sync data
        self.bulletproof_dir = config.project_path / ".clyde" / ".bulletproof"
        self.snapshots_dir = self.bulletproof_dir / "snapshots"
        self.audit_log = self.bulletproof_dir / "audit.log"
        
        # Ensure directories exist
        self.bulletproof_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    def bulletproof_sync(self, target: str = None, force: bool = False) -> SyncResult:
        """
        Perform a bulletproof sync with full safety measures.
        
        Args:
            target: Specific target to sync (None for all)
            force: Skip validation errors and proceed anyway
            
        Returns:
            SyncResult with details about the operation
        """
        operation_id = self._generate_operation_id()
        self._log_operation("SYNC_START", operation_id, {"target": target, "force": force})
        
        try:
            # Phase 1: Pre-sync validation
            validation_result = self._validate_pre_sync()
            if not force and any(issue.severity == "error" for issue in validation_result):
                return SyncResult(
                    success=False,
                    operation=SyncOperation.VALIDATE,
                    issues=validation_result,
                    message="Pre-sync validation failed. Use --force to override."
                )
            
            # Phase 2: Create backup snapshot
            snapshot_id = self._create_snapshot("pre_sync", operation_id)
            if not snapshot_id:
                return SyncResult(
                    success=False,
                    operation=SyncOperation.BACKUP,
                    message="Failed to create backup snapshot"
                )
            
            # Phase 3: Perform sync with monitoring
            sync_result = self._monitored_sync(target)
            if not sync_result.success:
                # Auto-rollback on sync failure
                rollback_result = self._rollback_to_snapshot(snapshot_id)
                return SyncResult(
                    success=False,
                    operation=SyncOperation.SYNC,
                    snapshot_id=snapshot_id,
                    rollback_available=rollback_result.success,
                    message=f"Sync failed: {sync_result.message}. Rollback {'successful' if rollback_result.success else 'failed'}."
                )
            
            # Phase 4: Post-sync verification
            verification_issues = self._verify_post_sync()
            if verification_issues and not force:
                # Rollback due to verification failure
                rollback_result = self._rollback_to_snapshot(snapshot_id)
                return SyncResult(
                    success=False,
                    operation=SyncOperation.VERIFY,
                    snapshot_id=snapshot_id,
                    issues=verification_issues,
                    rollback_available=rollback_result.success,
                    message="Post-sync verification failed. Changes rolled back."
                )
            
            # Success! Log and return result
            self._log_operation("SYNC_SUCCESS", operation_id, {
                "target": target,
                "snapshot_id": snapshot_id,
                "changes": sync_result.changes_made
            })
            
            return SyncResult(
                success=True,
                operation=SyncOperation.SYNC,
                snapshot_id=snapshot_id,
                issues=validation_result + verification_issues,
                changes_made=sync_result.changes_made,
                rollback_available=True,
                message="Sync completed successfully with full backup available."
            )
            
        except Exception as e:
            self._log_operation("SYNC_ERROR", operation_id, {"error": str(e)})
            return SyncResult(
                success=False,
                operation=SyncOperation.SYNC,
                message=f"Unexpected error during sync: {e}"
            )
    
    def _validate_pre_sync(self) -> List[ValidationIssue]:
        """Comprehensive pre-sync validation."""
        issues = []
        
        # 1. Configuration file validation
        config_file = self.config.project_path / ".clyde" / "config.yaml"
        if not config_file.exists():
            issues.append(ValidationIssue(
                severity="error",
                category="config",
                message="Configuration file does not exist",
                file_path=str(config_file),
                suggestion="Run 'clyde init' to create configuration"
            ))
        else:
            # Check if config file is valid YAML
            try:
                with open(config_file, 'r') as f:
                    yaml_data = yaml.safe_load(f.read())
                    if not yaml_data:
                        issues.append(ValidationIssue(
                            severity="error",
                            category="config",
                            message="Configuration file is empty or invalid",
                            file_path=str(config_file)
                        ))
            except yaml.YAMLError as e:
                issues.append(ValidationIssue(
                    severity="error",
                    category="config",
                    message=f"Configuration file contains invalid YAML: {e}",
                    file_path=str(config_file)
                ))
        
        # 2. Check for file corruption
        corruption_issues = self._detect_file_corruption()
        issues.extend(corruption_issues)
        
        # 3. Check for migration needs
        migration_issues = self._detect_migration_needs()
        issues.extend(migration_issues)
        
        # 4. Validate module references
        module_issues = self._validate_module_references()
        issues.extend(module_issues)
        
        # 5. Check disk space
        space_issues = self._check_disk_space()
        issues.extend(space_issues)
        
        return issues
    
    def _detect_file_corruption(self) -> List[ValidationIssue]:
        """Detect corrupted or tampered files."""
        issues = []
        
        # Check generated files for corruption
        for target in self.config.targets:
            generated_file = self.config.project_path / ".clyde" / f"generated-{target}.md"
            if generated_file.exists():
                # Check if file has clyde generation marker
                try:
                    content = generated_file.read_text(encoding='utf-8')
                    if "Generated by clyde" not in content:
                        issues.append(ValidationIssue(
                            severity="warning",
                            category="corruption",
                            message=f"Generated file may have been manually modified",
                            file_path=str(generated_file),
                            suggestion="Run sync to regenerate from source"
                        ))
                except Exception:
                    issues.append(ValidationIssue(
                        severity="error",
                        category="corruption",
                        message=f"Cannot read generated file",
                        file_path=str(generated_file)
                    ))
        
        return issues
    
    def _detect_migration_needs(self) -> List[ValidationIssue]:
        """Detect if project needs migration (like .claude -> .clyde)."""
        issues = []
        
        # Check for old .claude directory
        old_claude_dir = self.config.project_path / ".claude"
        if old_claude_dir.exists():
            issues.append(ValidationIssue(
                severity="warning", 
                category="migration",
                message="Old .claude directory detected",
                file_path=str(old_claude_dir),
                suggestion="Consider migrating to .clyde structure"
            ))
        
        # Check for version mismatches
        metadata = self.sync_manager._load_sync_metadata()
        if "clyde_version" in metadata:
            current_version = __version__
            if metadata["clyde_version"] != current_version:
                issues.append(ValidationIssue(
                    severity="info",
                    category="migration", 
                    message=f"Project created with different Clyde version ({metadata['clyde_version']} -> {current_version})",
                    suggestion="Sync will update to current version"
                ))
        
        return issues
    
    def _validate_module_references(self) -> List[ValidationIssue]:
        """Validate that all referenced modules exist."""
        issues = []
        
        for module_id in self.config.includes:
            if "*" in module_id:
                # Group reference - check if at least one module exists
                pattern = module_id.replace("*", "")
                modules_dir = Path(__file__).parent.parent / "modules"
                matching_modules = list(modules_dir.glob(f"{pattern.replace('.', '/')}**/*.md"))
                if not matching_modules:
                    issues.append(ValidationIssue(
                        severity="warning",
                        category="config",
                        message=f"No modules found matching pattern: {module_id}",
                        suggestion="Check module pattern or available modules"
                    ))
            else:
                # Specific module reference
                module_path = self.config.get_module_path(module_id)
                if not module_path.exists():
                    issues.append(ValidationIssue(
                        severity="error",
                        category="config",
                        message=f"Referenced module does not exist: {module_id}",
                        file_path=str(module_path),
                        suggestion="Remove from config or create the module"
                    ))
        
        return issues
    
    def _check_disk_space(self) -> List[ValidationIssue]:
        """Check if sufficient disk space is available."""
        issues = []
        
        try:
            # Check available space in .clyde directory
            clyde_dir = self.config.project_path / ".clyde"
            stat = shutil.disk_usage(clyde_dir)
            available_mb = stat.free / (1024 * 1024)
            
            if available_mb < 10:  # Less than 10MB
                issues.append(ValidationIssue(
                    severity="error",
                    category="file",
                    message=f"Low disk space: {available_mb:.1f}MB available",
                    suggestion="Free up disk space before syncing"
                ))
            elif available_mb < 50:  # Less than 50MB
                issues.append(ValidationIssue(
                    severity="warning",
                    category="file",
                    message=f"Low disk space: {available_mb:.1f}MB available"
                ))
        except Exception:
            # Ignore disk space check errors
            pass
        
        return issues
    
    def _create_snapshot(self, operation: str, operation_id: str) -> Optional[str]:
        """Create a snapshot of current state."""
        try:
            snapshot_id = f"{operation}_{operation_id}"
            snapshot_dir = self.snapshots_dir / snapshot_id
            snapshot_dir.mkdir(exist_ok=True)
            
            # Collect files to backup
            files_to_backup = []
            files_content_hashes = {}
            
            # Main config file
            config_file = self.config.project_path / ".clyde" / "config.yaml"
            if config_file.exists():
                files_to_backup.append(config_file)
            
            # Generated files
            for target in self.config.targets:
                generated_file = self.config.project_path / ".clyde" / f"generated-{target}.md"
                if generated_file.exists():
                    files_to_backup.append(generated_file)
            
            # Bootloader files
            bootloader_files = [
                self.config.project_path / "claude.md",
                self.config.project_path / "gemini.md"
            ]
            for bootloader in bootloader_files:
                if bootloader.exists():
                    files_to_backup.append(bootloader)
            
            # Project-specific files
            project_files = [
                self.config.project_path / ".clyde" / "project-claude.md",
                self.config.project_path / ".clyde" / "project-gemini.md",
                self.config.project_path / ".clyde" / "architecture.md"
            ]
            for proj_file in project_files:
                if proj_file.exists():
                    files_to_backup.append(proj_file)
            
            # Copy files and calculate hashes
            for file_path in files_to_backup:
                relative_path = file_path.relative_to(self.config.project_path)
                backup_path = snapshot_dir / relative_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(file_path, backup_path)
                
                # Calculate content hash
                with open(file_path, 'rb') as f:
                    content_hash = hashlib.sha256(f.read()).hexdigest()
                    files_content_hashes[str(relative_path)] = content_hash
            
            # Create snapshot metadata
            snapshot = SyncSnapshot(
                timestamp=datetime.now().isoformat(),
                config_hash=self.config.get_config_hash(),
                operation=operation,
                files=files_content_hashes,
                metadata={
                    "operation_id": operation_id,
                    "clyde_version": __version__,
                    "config": {
                        "project_name": self.config.project_name,
                        "language": self.config.language,
                        "framework": self.config.framework,
                        "targets": self.config.targets,
                        "module_count": len(self.config.includes)
                    }
                }
            )
            
            # Save snapshot metadata
            metadata_file = snapshot_dir / "snapshot.json"
            with open(metadata_file, 'w') as f:
                json.dump(snapshot.to_dict(), f, indent=2)
            
            self._log_operation("SNAPSHOT_CREATED", operation_id, {
                "snapshot_id": snapshot_id,
                "files_count": len(files_to_backup)
            })
            
            return snapshot_id
            
        except Exception as e:
            self._log_operation("SNAPSHOT_ERROR", operation_id, {"error": str(e)})
            return None
    
    def _monitored_sync(self, target: str = None) -> SyncResult:
        """Perform sync with monitoring and change tracking."""
        changes_made = []
        
        try:
            # Get preview of changes before applying
            preview_changes = self.sync_manager.preview_changes(target)
            
            # Perform the actual sync
            self.sync_manager.sync(target)
            
            # Track what was actually changed
            changes_made = preview_changes  # For now, assume preview matches reality
            
            return SyncResult(
                success=True,
                operation=SyncOperation.SYNC,
                changes_made=changes_made,
                message="Sync completed successfully"
            )
            
        except Exception as e:
            return SyncResult(
                success=False,
                operation=SyncOperation.SYNC,
                message=str(e)
            )
    
    def _verify_post_sync(self) -> List[ValidationIssue]:
        """Verify sync results and file integrity."""
        issues = []
        
        # 1. Verify generated files exist and are valid
        for target in self.config.targets:
            generated_file = self.config.project_path / ".clyde" / f"generated-{target}.md"
            if not generated_file.exists():
                issues.append(ValidationIssue(
                    severity="error",
                    category="file",
                    message=f"Generated file missing after sync: {target}",
                    file_path=str(generated_file)
                ))
            else:
                # Verify file contains expected markers
                try:
                    content = generated_file.read_text(encoding='utf-8')
                    if "Generated by clyde" not in content:
                        issues.append(ValidationIssue(
                            severity="error",
                            category="corruption",
                            message=f"Generated file missing clyde marker: {target}",
                            file_path=str(generated_file)
                        ))
                    # Check if file is not empty
                    if len(content.strip()) < 100:
                        issues.append(ValidationIssue(
                            severity="warning",
                            category="file",
                            message=f"Generated file seems unusually small: {target}",
                            file_path=str(generated_file)
                        ))
                except Exception as e:
                    issues.append(ValidationIssue(
                        severity="error",
                        category="file",
                        message=f"Cannot read generated file: {e}",
                        file_path=str(generated_file)
                    ))
        
        # 2. Verify sync metadata was updated
        metadata = self.sync_manager._load_sync_metadata()
        if not metadata or "last_sync" not in metadata:
            issues.append(ValidationIssue(
                severity="warning",
                category="file",
                message="Sync metadata was not updated properly"
            ))
        
        return issues
    
    def _rollback_to_snapshot(self, snapshot_id: str) -> SyncResult:
        """Rollback to a previous snapshot."""
        try:
            snapshot_dir = self.snapshots_dir / snapshot_id
            if not snapshot_dir.exists():
                return SyncResult(
                    success=False,
                    operation=SyncOperation.ROLLBACK,
                    message=f"Snapshot {snapshot_id} not found"
                )
            
            # Load snapshot metadata
            metadata_file = snapshot_dir / "snapshot.json"
            if not metadata_file.exists():
                return SyncResult(
                    success=False,
                    operation=SyncOperation.ROLLBACK,
                    message=f"Snapshot metadata not found: {snapshot_id}"
                )
            
            with open(metadata_file, 'r') as f:
                snapshot_data = json.load(f)
                snapshot = SyncSnapshot.from_dict(snapshot_data)
            
            # Restore files from snapshot
            restored_files = []
            for relative_path in snapshot.files.keys():
                source_path = snapshot_dir / relative_path
                target_path = self.config.project_path / relative_path
                
                if source_path.exists():
                    # Ensure target directory exists
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, target_path)
                    restored_files.append(str(relative_path))
            
            operation_id = self._generate_operation_id()
            self._log_operation("ROLLBACK_SUCCESS", operation_id, {
                "snapshot_id": snapshot_id,
                "restored_files": restored_files
            })
            
            return SyncResult(
                success=True,
                operation=SyncOperation.ROLLBACK,
                changes_made=restored_files,
                message=f"Successfully rolled back to snapshot {snapshot_id}"
            )
            
        except Exception as e:
            operation_id = self._generate_operation_id()
            self._log_operation("ROLLBACK_ERROR", operation_id, {
                "snapshot_id": snapshot_id,
                "error": str(e)
            })
            return SyncResult(
                success=False,
                operation=SyncOperation.ROLLBACK,
                message=f"Rollback failed: {e}"
            )
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List available snapshots."""
        snapshots = []
        
        if not self.snapshots_dir.exists():
            return snapshots
        
        for snapshot_dir in self.snapshots_dir.iterdir():
            if not snapshot_dir.is_dir():
                continue
                
            metadata_file = snapshot_dir / "snapshot.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        snapshot_data = json.load(f)
                        snapshots.append({
                            "id": snapshot_dir.name,
                            "timestamp": snapshot_data.get("timestamp", "unknown"),
                            "operation": snapshot_data.get("operation", "unknown"),
                            "files_count": len(snapshot_data.get("files", {})),
                            "config_hash": snapshot_data.get("config_hash", "unknown")
                        })
                except Exception:
                    continue
        
        # Sort by timestamp, newest first
        snapshots.sort(key=lambda x: x["timestamp"], reverse=True)
        return snapshots
    
    def cleanup_old_snapshots(self, keep_count: int = 10) -> Dict[str, Any]:
        """Clean up old snapshots, keeping only the most recent ones."""
        snapshots = self.list_snapshots()
        cleanup_result = {"removed": 0, "kept": len(snapshots), "errors": []}
        
        if len(snapshots) <= keep_count:
            return cleanup_result
        
        # Remove oldest snapshots
        snapshots_to_remove = snapshots[keep_count:]
        for snapshot in snapshots_to_remove:
            try:
                snapshot_dir = self.snapshots_dir / snapshot["id"]
                if snapshot_dir.exists():
                    shutil.rmtree(snapshot_dir)
                    cleanup_result["removed"] += 1
                    cleanup_result["kept"] -= 1
            except Exception as e:
                cleanup_result["errors"].append(f"Failed to remove {snapshot['id']}: {e}")
        
        return cleanup_result
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:17]
    
    def _log_operation(self, event: str, operation_id: str, data: Dict[str, Any]):
        """Log operation to audit trail."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": event,
                "operation_id": operation_id,
                "data": data
            }
            
            with open(self.audit_log, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            # Don't fail the operation if logging fails
            pass
    
    def get_audit_trail(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent audit trail entries."""
        entries = []
        
        if not self.audit_log.exists():
            return entries
        
        try:
            with open(self.audit_log, 'r') as f:
                content = f.read()
                
            # Split by lines and parse each JSON object
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Get last N lines
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            
            for line in recent_lines:
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
            
            return entries
            
        except Exception:
            return entries
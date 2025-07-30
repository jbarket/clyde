"""
MCP (Model Context Protocol) management for Clyde.
Handles installation, configuration, and management of MCP servers.
"""

import json
import yaml
import subprocess
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import platform

from .config import ClydeConfig


@dataclass
class MCPDefinition:
    """Defines how to install and configure an MCP."""
    name: str
    description: str
    category: str
    install_method: str
    package: str
    command: Optional[str] = None
    args: List[str] = None
    env: Dict[str, str] = None
    required_env: List[str] = None
    platforms: List[str] = None
    dependencies: List[Dict[str, Any]] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.env is None:
            self.env = {}
        if self.required_env is None:
            self.required_env = []
        if self.platforms is None:
            self.platforms = ["macos", "linux", "windows", "wsl"]
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class MCPInstallation:
    """Represents an existing MCP installation."""
    mcp_id: str
    name: str
    install_method: str
    version: Optional[str] = None
    command_path: Optional[str] = None
    config_source: Optional[str] = None  # claude-desktop, claude-code, clyde, manual
    working: bool = False


@dataclass
class MCPConflict:
    """Represents a conflict between existing and desired MCP installation."""
    mcp_id: str
    conflict_type: str  # duplicate, version_mismatch, method_conflict
    existing: MCPInstallation
    desired: MCPDefinition
    message: str
    resolution_options: List[str]


class MCPRegistry:
    """Registry of available MCPs and their installation methods."""
    
    def __init__(self):
        self.mcps: Dict[str, MCPDefinition] = {}
        self._load_registry()
    
    def _load_registry(self):
        """Load MCP definitions from registry file."""
        registry_file = Path(__file__).parent.parent / "design" / "mcp-registry.yaml"
        
        if not registry_file.exists():
            return
        
        with open(registry_file, 'r') as f:
            data = yaml.safe_load(f)
        
        for mcp_id, config in data.get('mcps', {}).items():
            # Extract install configuration
            install_config = config.get('install', {})
            
            self.mcps[mcp_id] = MCPDefinition(
                name=config.get('name', mcp_id),
                description=config.get('description', ''),
                category=config.get('category', 'development'),
                install_method=install_config.get('method', 'npx'),
                package=install_config.get('package', ''),
                command=install_config.get('command'),
                args=install_config.get('args', []),
                env=config.get('env', {}),
                required_env=config.get('required_env', []),
                platforms=config.get('platforms', ["macos", "linux", "windows", "wsl"]),
                dependencies=config.get('dependencies', []),
                notes=config.get('notes')
            )
    
    def get_mcp(self, mcp_id: str) -> Optional[MCPDefinition]:
        """Get MCP definition by ID."""
        return self.mcps.get(mcp_id)
    
    def list_mcps(self, category: Optional[str] = None) -> Dict[str, MCPDefinition]:
        """List available MCPs, optionally filtered by category."""
        if category:
            return {k: v for k, v in self.mcps.items() if v.category == category}
        return self.mcps
    
    def get_categories(self) -> List[str]:
        """Get all available categories."""
        return list(set(mcp.category for mcp in self.mcps.values()))


class MCPManager:
    """Manages MCP installation and configuration for Clyde projects."""
    
    def __init__(self, config: ClydeConfig):
        self.config = config
        self.registry = MCPRegistry()
        self.project_path = config.project_path
        self.clyde_dir = self.project_path / ".clyde"
        self.claude_desktop_config_path = self._get_claude_desktop_config_path()
        self.claude_code_config_path = self._get_claude_code_config_path()
        self.gemini_global_config_path = self._get_gemini_global_config_path()
        self.gemini_project_config_path = self._get_gemini_project_config_path()
        
    def _get_claude_desktop_config_path(self) -> Path:
        """Get the path to Claude Desktop configuration file."""
        system = platform.system().lower()
        if system == "darwin":  # macOS
            return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
        elif system == "linux":
            return Path.home() / ".config/claude/claude_desktop_config.json"
        elif system == "windows":
            return Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
        else:
            return Path.home() / ".config/claude/claude_desktop_config.json"
    
    def _get_claude_code_config_path(self) -> Path:
        """Get the path to Claude Code configuration file."""
        return Path.home() / ".config/claude/claude_code_config.json"
    
    def _get_gemini_global_config_path(self) -> Path:
        """Get the path to Gemini CLI global configuration file."""
        return Path.home() / ".gemini/settings.json"
    
    def _get_gemini_project_config_path(self) -> Path:
        """Get the path to Gemini CLI project configuration file."""
        return self.project_path / ".gemini/settings.json"
    
    def get_enabled_mcps(self) -> List[str]:
        """Get all enabled MCPs from config."""
        if not self.config.mcps.get('enabled', True):
            return []
        
        mcps = []
        mcps.extend(self.config.mcps.get('core', []))
        mcps.extend(self.config.mcps.get('development', []))
        mcps.extend(self.config.mcps.get('ai_tools', []))
        
        return mcps
    
    def scan_existing_installations(self) -> List[MCPInstallation]:
        """Scan for existing MCP installations across all sources."""
        installations = []
        
        # Check Claude Desktop config
        installations.extend(self._scan_claude_desktop_config())
        
        # Check Claude Code config  
        installations.extend(self._scan_claude_code_config())
        
        # Check Gemini CLI configs
        installations.extend(self._scan_gemini_global_config())
        installations.extend(self._scan_gemini_project_config())
        
        # Check global npm packages
        installations.extend(self._scan_npm_global_packages())
        
        # Check uvx installations
        installations.extend(self._scan_uvx_installations())
        
        return installations
    
    def _scan_claude_desktop_config(self) -> List[MCPInstallation]:
        """Scan Claude Desktop configuration for existing MCPs."""
        installations = []
        
        if not self.claude_desktop_config_path.exists():
            return installations
        
        try:
            with open(self.claude_desktop_config_path, 'r') as f:
                config = json.load(f)
            
            mcp_servers = config.get('mcpServers', {})
            for server_id, server_config in mcp_servers.items():
                command = server_config.get('command', '')
                args = server_config.get('args', [])
                
                # Determine install method and package
                install_method = None
                package = None
                if command == 'npx':
                    install_method = 'npx'
                    package = args[-1] if args else None
                elif command == 'uvx':
                    install_method = 'uvx'
                    # Extract package from uvx args
                    if len(args) >= 2 and args[0] == '--from':
                        package = args[1]
                
                installation = MCPInstallation(
                    mcp_id=server_id,
                    name=server_id,
                    install_method=install_method or 'manual',
                    command_path=command,
                    config_source='claude-desktop',
                    working=self._test_mcp_from_config(server_config)
                )
                installations.append(installation)
                
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Warning: Could not read Claude Desktop config: {e}")
        
        return installations
    
    def _scan_claude_code_config(self) -> List[MCPInstallation]:
        """Scan Claude Code configuration for existing MCPs."""
        installations = []
        
        if not self.claude_code_config_path.exists():
            return installations
        
        try:
            with open(self.claude_code_config_path, 'r') as f:
                config = json.load(f)
            
            # Similar logic to Claude Desktop scanning
            mcp_servers = config.get('mcpServers', {})
            for server_id, server_config in mcp_servers.items():
                command = server_config.get('command', '')
                args = server_config.get('args', [])
                
                install_method = None
                package = None
                if command == 'npx':
                    install_method = 'npx'
                    package = args[-1] if args else None
                elif command == 'uvx':
                    install_method = 'uvx'
                    if len(args) >= 2 and args[0] == '--from':
                        package = args[1]
                
                installation = MCPInstallation(
                    mcp_id=server_id,
                    name=server_id,
                    install_method=install_method or 'manual',
                    command_path=command,
                    config_source='claude-code',
                    working=self._test_mcp_from_config(server_config)
                )
                installations.append(installation)
                
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Warning: Could not read Claude Code config: {e}")
        
        return installations
    
    def _scan_gemini_global_config(self) -> List[MCPInstallation]:
        """Scan Gemini CLI global configuration for existing MCPs."""
        return self._scan_gemini_config(self.gemini_global_config_path, 'gemini-global')
    
    def _scan_gemini_project_config(self) -> List[MCPInstallation]:
        """Scan Gemini CLI project configuration for existing MCPs."""
        return self._scan_gemini_config(self.gemini_project_config_path, 'gemini-project')
    
    def _scan_gemini_config(self, config_path: Path, config_source: str) -> List[MCPInstallation]:
        """Scan a Gemini CLI settings.json file for MCP servers.
        
        Note: Gemini CLI merge behavior is assumed to be hierarchical (project overrides global).
        Users should verify this by testing with both global and project configurations and
        running 'gemini /mcp' to confirm which servers are active.
        """
        installations = []
        
        if not config_path.exists():
            return installations
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            mcp_servers = config.get('mcpServers', {})
            for server_id, server_config in mcp_servers.items():
                command = server_config.get('command', '')
                args = server_config.get('args', [])
                env_vars = server_config.get('env', {})
                
                # Determine install method and package
                install_method = None
                package = None
                if command == 'npx':
                    install_method = 'npx'
                    # Find the package name from args (last non-flag argument)
                    for arg in reversed(args):
                        if not arg.startswith('-'):
                            package = arg
                            break
                elif command == 'uvx':
                    install_method = 'uvx'
                    # Extract package from uvx args
                    if len(args) >= 2 and args[0] == '--from':
                        package = args[1]
                elif command in ['node', 'python', 'python3']:
                    install_method = 'manual'
                    package = args[0] if args else None
                else:
                    install_method = 'manual'
                
                installation = MCPInstallation(
                    mcp_id=server_id,
                    name=server_id,
                    install_method=install_method or 'manual',
                    command_path=command,
                    config_source=config_source,
                    working=self._test_mcp_from_gemini_config(server_config)
                )
                installations.append(installation)
                
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Warning: Could not read Gemini config {config_path}: {e}")
        
        return installations
    
    def _test_mcp_from_gemini_config(self, server_config: Dict[str, Any]) -> bool:
        """Test if a Gemini MCP server configuration is working."""
        try:
            command = server_config.get('command', '')
            args = server_config.get('args', [])
            env = server_config.get('env', {})
            
            # Merge environment variables
            test_env = os.environ.copy()
            test_env.update(env)
            
            # Test command with --help
            test_cmd = [command] + args + ['--help']
            result = subprocess.run(test_cmd, capture_output=True, text=True, 
                                  timeout=10, env=test_env)
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _scan_npm_global_packages(self) -> List[MCPInstallation]:
        """Scan for globally installed npm packages that might be MCPs."""
        installations = []
        
        try:
            result = subprocess.run(['npm', 'list', '-g', '--depth=0', '--json'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                dependencies = data.get('dependencies', {})
                
                for package_name, package_info in dependencies.items():
                    # Check if this looks like an MCP package
                    if any(mcp_keyword in package_name.lower() for mcp_keyword in ['mcp', 'context', 'server']):
                        installation = MCPInstallation(
                            mcp_id=package_name,
                            name=package_name,
                            install_method='npm-global',
                            version=package_info.get('version'),
                            config_source='npm-global'
                        )
                        installations.append(installation)
                        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError):
            pass  # npm not available or other issues
        
        return installations
    
    def _scan_uvx_installations(self) -> List[MCPInstallation]:
        """Scan for uvx installed packages that might be MCPs."""
        installations = []
        
        try:
            result = subprocess.run(['uvx', '--list'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line and not line.startswith('No'):
                        # Parse uvx list output (format may vary)
                        package_name = line.split()[0] if line.split() else line
                        if any(mcp_keyword in package_name.lower() for mcp_keyword in ['mcp', 'context', 'server']):
                            installation = MCPInstallation(
                                mcp_id=package_name,
                                name=package_name,
                                install_method='uvx',
                                config_source='uvx'
                            )
                            installations.append(installation)
                            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass  # uvx not available or other issues
        
        return installations
    
    def _test_mcp_from_config(self, server_config: Dict[str, Any]) -> bool:
        """Test if an MCP server configuration is working."""
        try:
            command = server_config.get('command', '')
            args = server_config.get('args', [])
            env = server_config.get('env', {})
            
            # Merge environment variables
            test_env = os.environ.copy()
            test_env.update(env)
            
            # Test command with --help
            test_cmd = [command] + args + ['--help']
            result = subprocess.run(test_cmd, capture_output=True, text=True, 
                                  timeout=10, env=test_env)
            return result.returncode == 0
            
        except Exception:
            return False
    
    def detect_conflicts(self, mcp_ids: List[str]) -> List[MCPConflict]:
        """Detect conflicts between desired MCPs and existing installations."""
        conflicts = []
        existing_installations = self.scan_existing_installations()
        
        for mcp_id in mcp_ids:
            mcp_def = self.registry.get_mcp(mcp_id)
            if not mcp_def:
                continue
            
            # Find existing installations of this MCP
            existing = [inst for inst in existing_installations if inst.mcp_id == mcp_id]
            
            for installation in existing:
                conflict = self._analyze_conflict(installation, mcp_def)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _analyze_conflict(self, existing: MCPInstallation, desired: MCPDefinition) -> Optional[MCPConflict]:
        """Analyze a potential conflict between existing and desired installation."""
        
        # Check for duplicate installation
        if existing.config_source in ['claude-desktop', 'claude-code']:
            return MCPConflict(
                mcp_id=existing.mcp_id,
                conflict_type='duplicate',
                existing=existing,
                desired=desired,
                message=f"{existing.name} is already configured in {existing.config_source}",
                resolution_options=['skip', 'replace', 'merge']
            )
        
        # Check for method conflicts
        if existing.install_method != desired.install_method and existing.install_method != 'manual':
            return MCPConflict(
                mcp_id=existing.mcp_id,
                conflict_type='method_conflict',
                existing=existing,
                desired=desired,
                message=f"{existing.name} is installed via {existing.install_method}, but Clyde wants to use {desired.install_method}",
                resolution_options=['skip', 'uninstall_and_reinstall', 'use_existing']
            )
        
        # Check for version conflicts (if version info available)
        if existing.version and hasattr(desired, 'version') and desired.version:
            if existing.version != desired.version:
                return MCPConflict(
                    mcp_id=existing.mcp_id,
                    conflict_type='version_mismatch',
                    existing=existing,
                    desired=desired,
                    message=f"{existing.name} version {existing.version} conflicts with desired version {desired.version}",
                    resolution_options=['skip', 'upgrade', 'downgrade']
                )
        
        return None
    
    def backup_config(self, config_path: Path) -> Optional[Path]:
        """Create a backup of a configuration file."""
        if not config_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = config_path.parent / f"{config_path.stem}_backup_{timestamp}{config_path.suffix}"
        
        try:
            shutil.copy2(config_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Warning: Could not backup {config_path}: {e}")
            return None
    
    def restore_config(self, backup_path: Path, original_path: Path) -> bool:
        """Restore a configuration file from backup."""
        try:
            if backup_path.exists():
                shutil.copy2(backup_path, original_path)
                return True
        except Exception as e:
            print(f"Error: Could not restore config from {backup_path}: {e}")
        return False
    
    def list_backups(self, config_path: Path) -> List[Path]:
        """List available backups for a configuration file."""
        if not config_path.parent.exists():
            return []
        
        backup_pattern = f"{config_path.stem}_backup_*{config_path.suffix}"
        return list(config_path.parent.glob(backup_pattern))
    
    def resolve_conflict_interactive(self, conflict: MCPConflict) -> str:
        """Interactively resolve a conflict with user input."""
        print(f"\n🚨 Conflict detected: {conflict.message}")
        print(f"   Existing: {conflict.existing.install_method} via {conflict.existing.config_source}")
        print(f"   Desired:  {conflict.desired.install_method} (Clyde managed)")
        print()
        
        print("Resolution options:")
        for i, option in enumerate(conflict.resolution_options, 1):
            option_desc = {
                'skip': 'Skip this MCP (keep existing)',
                'replace': 'Replace existing with Clyde version',
                'merge': 'Merge configurations (if possible)',
                'uninstall_and_reinstall': 'Uninstall existing and reinstall via Clyde',
                'use_existing': 'Use existing installation (add to Clyde config)',
                'upgrade': 'Upgrade to newer version',
                'downgrade': 'Downgrade to requested version'
            }
            print(f"  {i}. {option}: {option_desc.get(option, option)}")
        
        while True:
            try:
                choice = input(f"Choose option (1-{len(conflict.resolution_options)}): ").strip()
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(conflict.resolution_options):
                    return conflict.resolution_options[choice_idx]
                else:
                    print("Invalid choice. Please try again.")
            except (ValueError, KeyboardInterrupt):
                print("Invalid input. Please enter a number.")
    
    def install_dependencies(self, mcp_def: MCPDefinition) -> bool:
        """Install dependencies for an MCP."""
        if not mcp_def.dependencies:
            return True
        
        for dep in mcp_def.dependencies:
            name = dep.get('name')
            install_cmd = dep.get('install_cmd')
            verify_cmd = dep.get('verify_cmd')
            path_addition = dep.get('path_addition')
            
            # Check if dependency already exists
            if verify_cmd:
                try:
                    subprocess.run(verify_cmd.split(), check=True, capture_output=True)
                    print(f"✓ {name} already installed")
                    continue
                except subprocess.CalledProcessError:
                    pass
            
            # Install dependency
            print(f"Installing {name}...")
            try:
                subprocess.run(install_cmd, shell=True, check=True)
                
                # Add to PATH if needed
                if path_addition:
                    # Note: This only affects current session
                    # User may need to restart terminal for permanent effect
                    current_path = os.environ.get('PATH', '')
                    if path_addition not in current_path:
                        os.environ['PATH'] = f"{path_addition}:{current_path}"
                        print(f"Added {path_addition} to PATH for current session")
                
                print(f"✓ {name} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install {name}: {e}")
                return False
                
        return True
    
    def install_mcp(self, mcp_id: str, interactive: bool = True) -> bool:
        """Install a single MCP with conflict detection."""
        mcp_def = self.registry.get_mcp(mcp_id)
        if not mcp_def:
            print(f"✗ Unknown MCP: {mcp_id}")
            return False
        
        print(f"Installing {mcp_def.name}...")
        
        # Check platform compatibility
        current_platform = self._get_current_platform()
        if current_platform not in mcp_def.platforms:
            print(f"✗ {mcp_def.name} is not supported on {current_platform}")
            return False
        
        # Detect conflicts first
        conflicts = self.detect_conflicts([mcp_id])
        if conflicts and interactive:
            for conflict in conflicts:
                resolution = self.resolve_conflict_interactive(conflict)
                if resolution == 'skip':
                    print(f"⏭️  Skipping {mcp_def.name}")
                    return True
                elif resolution == 'replace':
                    # Backup and replace
                    if conflict.existing.config_source == 'claude-desktop':
                        backup = self.backup_config(self.claude_desktop_config_path)
                        if backup:
                            print(f"📦 Backed up Claude Desktop config to {backup}")
                elif resolution == 'use_existing':
                    print(f"✓ Using existing {mcp_def.name} installation")
                    return True
                # Handle other resolutions...
        
        # Install dependencies first
        if not self.install_dependencies(mcp_def):
            return False
        
        # Install the MCP
        try:
            if mcp_def.install_method == "npx":
                cmd = ["npx"] + mcp_def.args + [mcp_def.package]
            elif mcp_def.install_method == "uvx":
                cmd = ["uvx", "--from", mcp_def.package, mcp_def.command or mcp_def.package]
            else:
                print(f"✗ Unsupported install method: {mcp_def.install_method}")
                return False
            
            # Test the installation by running with --help or --version
            test_result = subprocess.run(cmd + ["--help"], capture_output=True, text=True)
            if test_result.returncode != 0:
                print(f"✗ Failed to install {mcp_def.name}")
                return False
            
            print(f"✓ {mcp_def.name} installed successfully")
            if mcp_def.notes:
                print(f"  Note: {mcp_def.notes}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to install {mcp_def.name}: {e}")
            return False
    
    def install_all_mcps(self) -> bool:
        """Install all enabled MCPs."""
        enabled_mcps = self.get_enabled_mcps()
        if not enabled_mcps:
            print("No MCPs enabled in configuration")
            return True
        
        print(f"Installing {len(enabled_mcps)} MCPs...")
        
        success = True
        for mcp_id in enabled_mcps:
            if not self.install_mcp(mcp_id):
                success = False
                
        return success
    
    def generate_claude_code_config(self) -> Dict[str, Any]:
        """Generate Claude Code MCP configuration."""
        config = {"mcpServers": {}}
        
        for mcp_id in self.get_enabled_mcps():
            mcp_def = self.registry.get_mcp(mcp_id)
            if not mcp_def:
                continue
            
            server_config = {}
            
            if mcp_def.install_method == "npx":
                server_config["command"] = "npx"
                server_config["args"] = mcp_def.args + [mcp_def.package]
            elif mcp_def.install_method == "uvx":
                server_config["command"] = "uvx"
                server_config["args"] = ["--from", mcp_def.package, mcp_def.command or mcp_def.package]
            
            # Add environment variables
            env_vars = {}
            for key, value in mcp_def.env.items():
                # Resolve environment variable references
                resolved_value = self._resolve_env_var(value)
                if resolved_value:
                    env_vars[key] = resolved_value
            
            # Add project-specific env vars
            project_env = self.config.mcps.get('env', {})
            for key, value in project_env.items():
                resolved_value = self._resolve_env_var(value)
                if resolved_value:
                    env_vars[key] = resolved_value
            
            if env_vars:
                server_config["env"] = env_vars
            
            config["mcpServers"][mcp_id] = server_config
        
        return config
    
    def generate_claude_desktop_config(self) -> Dict[str, Any]:
        """Generate Claude Desktop MCP configuration."""
        # For now, same as Claude Code config format
        return self.generate_claude_code_config()
    
    def save_configurations(self):
        """Save generated MCP configurations to files."""
        self.clyde_dir.mkdir(exist_ok=True)
        
        # Save Claude Code config
        claude_code_config = self.generate_claude_code_config()
        claude_code_file = self.clyde_dir / "generated-claude.json"
        with open(claude_code_file, 'w') as f:
            json.dump(claude_code_config, f, indent=2)
        
        # Save Claude Desktop config
        claude_desktop_config = self.generate_claude_desktop_config()
        claude_desktop_file = self.clyde_dir / "generated-claude-desktop.json"
        with open(claude_desktop_file, 'w') as f:
            json.dump(claude_desktop_config, f, indent=2)
        
        print(f"✓ MCP configurations saved to {self.clyde_dir}/")
    
    def _resolve_env_var(self, value: str) -> Optional[str]:
        """Resolve environment variable references in configuration values."""
        if not isinstance(value, str):
            return value
        
        # Handle ${VAR} and ${CLYDE_DIR} patterns
        if "${CLYDE_DIR}" in value:
            clyde_home = Path.home() / ".clyde"
            clyde_home.mkdir(exist_ok=True)
            value = value.replace("${CLYDE_DIR}", str(clyde_home))
        
        # Handle other environment variables
        import re
        env_vars = re.findall(r'\$\{([^}]+)\}', value)
        for var in env_vars:
            env_value = os.environ.get(var)
            if env_value:
                value = value.replace(f"${{{var}}}", env_value)
            else:
                # Variable not set, skip this configuration
                return None
        
        return value
    
    def _get_current_platform(self) -> str:
        """Get current platform identifier."""
        import platform
        system = platform.system().lower()
        
        if system == "darwin":
            return "macos"
        elif system == "linux":
            if "microsoft" in platform.uname().release.lower():
                return "wsl"
            return "linux"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"
    
    def status(self, detailed: bool = False):
        """Show comprehensive MCP status."""
        enabled_mcps = self.get_enabled_mcps()
        existing_installations = self.scan_existing_installations()
        
        print("🔧 MCP Status Report")
        print("=" * 50)
        
        if enabled_mcps:
            print(f"\n📋 Enabled MCPs ({len(enabled_mcps)}):")
            for mcp_id in enabled_mcps:
                mcp_def = self.registry.get_mcp(mcp_id)
                if not mcp_def:
                    print(f"  ❓ {mcp_id}: Unknown MCP")
                    continue
                
                # Find existing installations
                existing = [inst for inst in existing_installations if inst.mcp_id == mcp_id]
                
                # Test if MCP is working
                status = self._test_mcp(mcp_def)
                status_icon = "✅" if status else "❌"
                
                print(f"  {status_icon} {mcp_def.name}")
                if detailed:
                    print(f"      Category: {mcp_def.category}")
                    print(f"      Install method: {mcp_def.install_method}")
                    if mcp_def.description:
                        print(f"      Description: {mcp_def.description}")
                
                # Show existing installations
                if existing:
                    print(f"      Existing installations:")
                    for inst in existing:
                        working_icon = "🟢" if inst.working else "🔴"
                        print(f"        {working_icon} {inst.config_source} via {inst.install_method}")
                        if inst.version:
                            print(f"          Version: {inst.version}")
                
                # Show missing environment variables
                missing_env = []
                for env_var in mcp_def.required_env:
                    if not os.environ.get(env_var):
                        missing_env.append(env_var)
                
                if missing_env:
                    print(f"      ⚠️  Missing env vars: {', '.join(missing_env)}")
                
                print()
        
        # Show all detected installations
        other_installations = [inst for inst in existing_installations 
                             if inst.mcp_id not in enabled_mcps]
        
        if other_installations:
            print(f"\n🔍 Other detected MCP installations ({len(other_installations)}):")
            for inst in other_installations:
                working_icon = "🟢" if inst.working else "🔴"
                print(f"  {working_icon} {inst.name}")
                print(f"      Source: {inst.config_source}")
                print(f"      Method: {inst.install_method}")
                if inst.version:
                    print(f"      Version: {inst.version}")
                print()
        
        # Detect conflicts
        conflicts = self.detect_conflicts(enabled_mcps)
        if conflicts:
            print(f"\n⚠️  Conflicts detected ({len(conflicts)}):")
            for conflict in conflicts:
                print(f"  🚨 {conflict.mcp_id}: {conflict.conflict_type}")
                print(f"      {conflict.message}")
                print(f"      Options: {', '.join(conflict.resolution_options)}")
                print()
        
        # Show backup files
        backups = []
        backup_paths = [
            self.claude_desktop_config_path, 
            self.claude_code_config_path,
            self.gemini_global_config_path,
            self.gemini_project_config_path
        ]
        for config_path in backup_paths:
            backups.extend(self.list_backups(config_path))
        
        if backups and detailed:
            print(f"\n💾 Available backups ({len(backups)}):")
            for backup in sorted(backups, reverse=True)[:5]:  # Show latest 5
                print(f"  📦 {backup.name}")
            if len(backups) > 5:
                print(f"      ... and {len(backups) - 5} more")
            print()
    
    def _test_mcp(self, mcp_def: MCPDefinition) -> bool:
        """Test if an MCP is properly installed and configured."""
        try:
            if mcp_def.install_method == "npx":
                cmd = ["npx"] + mcp_def.args + [mcp_def.package, "--help"]
            elif mcp_def.install_method == "uvx":
                cmd = ["uvx", "--from", mcp_def.package, mcp_def.command or mcp_def.package, "--help"]
            else:
                return False
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
            
        except Exception:
            return False
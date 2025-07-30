"""
MCP (Model Context Protocol) management for Clyde.
Handles installation, configuration, and management of MCP servers.
"""

import json
import yaml
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

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
    
    def get_enabled_mcps(self) -> List[str]:
        """Get all enabled MCPs from config."""
        if not self.config.mcps.get('enabled', True):
            return []
        
        mcps = []
        mcps.extend(self.config.mcps.get('core', []))
        mcps.extend(self.config.mcps.get('development', []))
        mcps.extend(self.config.mcps.get('ai_tools', []))
        
        return mcps
    
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
    
    def install_mcp(self, mcp_id: str) -> bool:
        """Install a single MCP."""
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
    
    def status(self):
        """Show status of all MCPs."""
        enabled_mcps = self.get_enabled_mcps()
        
        if not enabled_mcps:
            print("No MCPs enabled")
            return
        
        print(f"MCP Status ({len(enabled_mcps)} enabled):")
        print()
        
        for mcp_id in enabled_mcps:
            mcp_def = self.registry.get_mcp(mcp_id)
            if not mcp_def:
                print(f"✗ {mcp_id}: Unknown MCP")
                continue
            
            # Test if MCP is working
            status = self._test_mcp(mcp_def)
            status_icon = "✓" if status else "✗"
            
            print(f"{status_icon} {mcp_def.name} ({mcp_def.category})")
            if mcp_def.description:
                print(f"    {mcp_def.description}")
            
            # Show missing environment variables
            missing_env = []
            for env_var in mcp_def.required_env:
                if not os.environ.get(env_var):
                    missing_env.append(env_var)
            
            if missing_env:
                print(f"    Missing env vars: {', '.join(missing_env)}")
            
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
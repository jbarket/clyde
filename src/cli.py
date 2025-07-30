#!/usr/bin/env python3
"""
Clyde - Development Environment Configuration System
CLI interface for managing modular Claude configuration files.
"""

import click
import os
import sys
from pathlib import Path
from typing import Optional, List

from .config import ClydeConfig
from .builder import ConfigBuilder
from .sync import SyncManager
from .mcp import MCPManager, MCPRegistry


@click.group()
@click.version_option(version="1.0.0", prog_name="clyde")
@click.pass_context
def cli(ctx):
    """Clyde - Development Environment Configuration System
    
    Manage modular configuration files that define coding principles,
    framework conventions, and project-specific guidelines for Claude.
    """
    ctx.ensure_object(dict)


@cli.command()
@click.option('--language', type=click.Choice(['python', 'javascript', 'typescript']), 
              help='Primary programming language')
@click.option('--framework', help='Framework to use (fastapi, react, nextjs, etc.)')
@click.option('--database', type=click.Choice(['postgres', 'mongodb']), 
              help='Database system')
@click.option('--template', help='Predefined template (fastapi-react, etc.)')
@click.option('--name', help='Project name')
@click.argument('path', type=click.Path(), default='.')
def init(language: Optional[str], framework: Optional[str], database: Optional[str], 
         template: Optional[str], name: Optional[str], path: str):
    """Initialize a new clyde project in the specified directory."""
    
    project_path = Path(path).resolve()
    config_dir = project_path / '.clyde'
    
    if config_dir.exists():
        if not click.confirm(f"Configuration already exists in {path}. Overwrite?"):
            click.echo("❌ Initialization cancelled.")
            return
    
    # Create directories
    config_dir.mkdir(exist_ok=True)
    
    # Determine project settings
    if not name:
        name = project_path.name
    
    if template:
        language, framework = _parse_template(template)
    
    if not language:
        language = click.prompt('Primary language', 
                              type=click.Choice(['python', 'javascript', 'typescript']))
    
    if not framework and language in ['javascript', 'typescript']:
        framework = click.prompt('Framework (optional)', default='', show_default=False)
    elif not framework and language == 'python':
        framework = click.prompt('Framework (optional)', default='', show_default=False)
    
    # Create configuration
    config = ClydeConfig(
        project_name=name,
        language=language,
        framework=framework or None,
        database=database,
        project_path=project_path
    )
    
    builder = ConfigBuilder(config)
    
    try:
        # Generate configuration files
        builder.create_config_file()
        builder.create_bootloader()
        builder.create_project_files()
        
        # Generate initial claude configuration
        sync_manager = SyncManager(config)
        sync_manager.sync()
        
        click.echo(f"✅ Initialized clyde project in {path}")
        click.echo(f"📝 Edit .clyde/config.yaml to customize configuration")
        click.echo(f"🔄 Run 'clyde sync' to regenerate configuration files")
        
    except Exception as e:
        click.echo(f"❌ Error during initialization: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--add', multiple=True, help='Add module(s) to configuration')
@click.option('--remove', multiple=True, help='Remove module(s) from configuration')
@click.option('--check', is_flag=True, help='Show what would change without applying')
@click.option('--all', 'sync_all', is_flag=True, help='Sync all projects in subdirectories')
@click.argument('path', type=click.Path(exists=True), default='.')
def sync(add: tuple, remove: tuple, check: bool, sync_all: bool, path: str):
    """Sync configuration files (rebuild generated.md from current config)."""
    
    if sync_all:
        _sync_all_projects(Path(path), check)
        return
    
    config_path = Path(path).resolve()
    
    if not _find_config_file(config_path):
        click.echo(f"❌ No clyde configuration found in {path}")
        click.echo("💡 Run 'clyde init' to initialize a new project")
        sys.exit(1)
    
    try:
        config = ClydeConfig.from_file(config_path / '.clyde' / 'config.yaml')
        
        # Apply module changes
        if add:
            for module in add:
                config.add_module(module)
                if not check:
                    click.echo(f"➕ Added module: {module}")
        
        if remove:
            for module in remove:
                config.remove_module(module)
                if not check:
                    click.echo(f"➖ Removed module: {module}")
        
        sync_manager = SyncManager(config)
        
        if check:
            changes = sync_manager.preview_changes()
            if changes:
                click.echo("📋 Would make the following changes:")
                for change in changes:
                    click.echo(f"  {change}")
            else:
                click.echo("✨ No changes needed")
        else:
            # Save updated config if modules were changed
            if add or remove:
                config.save()
            
            sync_manager.sync()
            click.echo("✅ Configuration synced successfully")
            
    except Exception as e:
        click.echo(f"❌ Error during sync: {e}", err=True)
        sys.exit(1)


@cli.command('list-modules')
@click.option('--groups', is_flag=True, help='Show available groups instead of individual modules')
def list_modules(groups: bool):
    """Show available modules or groups."""
    
    # Get modules directory from package
    modules_dir = Path(__file__).parent.parent / 'modules'
    
    if not modules_dir.exists():
        click.echo("❌ Modules directory not found")
        sys.exit(1)
    
    if groups:
        click.echo("📁 Available groups (use with .* suffix):")
        click.echo("")
        
        for category_dir in sorted(modules_dir.iterdir()):
            if not category_dir.is_dir():
                continue
            
            # Count modules in this group
            module_count = len(list(category_dir.glob('**/*.md')))
            if module_count == 0:
                continue
                
            click.echo(f"  {category_dir.name}.*")
            click.echo(f"    📊 Contains {module_count} modules")
            
            # Show a few example modules
            examples = []
            for module_file in sorted(category_dir.glob('*.md'))[:3]:
                relative_path = module_file.relative_to(modules_dir)
                module_id = str(relative_path.with_suffix('')).replace('/', '.')
                examples.append(module_id)
            
            if examples:
                click.echo(f"    📝 Examples: {', '.join(examples)}")
                if module_count > 3:
                    click.echo(f"    📝 ... and {module_count - 3} more")
            click.echo("")
            
        click.echo("💡 Usage examples:")
        click.echo("  clyde sync --add core.*         # Add all core modules")
        click.echo("  clyde sync --add patterns.*     # Add all pattern modules")
        click.echo("  clyde sync --remove core.*      # Remove all core modules")
        
    else:
        click.echo("📚 Available modules:")
        
        for category_dir in sorted(modules_dir.iterdir()):
            if not category_dir.is_dir():
                continue
                
            click.echo(f"\n{category_dir.name.title()}:")
            
            for module_file in sorted(category_dir.glob('**/*.md')):
                # Convert path to module ID
                relative_path = module_file.relative_to(modules_dir)
                module_id = str(relative_path.with_suffix('')).replace('/', '.')
                
                # Get description from first line if available
                try:
                    with open(module_file) as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('#'):
                            description = first_line[1:].strip()
                        else:
                            description = "No description available"
                except:
                    description = "No description available"
                
                click.echo(f"  {module_id:<30} {description}")
        
        click.echo("\n💡 Tip: Use 'clyde list-modules --groups' to see available groups")


@cli.command()
@click.argument('module_id')
def show(module_id: str):
    """Show the contents of a specific module."""
    
    modules_dir = Path(__file__).parent.parent / 'modules'
    module_path = modules_dir / f"{module_id.replace('.', '/')}.md"
    
    if not module_path.exists():
        click.echo(f"❌ Module not found: {module_id}")
        sys.exit(1)
    
    with open(module_path) as f:
        content = f.read()
    
    click.echo_via_pager(content)


@cli.command('create-module')
@click.argument('module_id')
@click.option('--template', help='Template to use for new module')
def create_module(module_id: str, template: Optional[str]):
    """Create a custom module."""
    
    if '.' not in module_id:
        click.echo("❌ Module ID must contain at least one dot (e.g. custom.my-patterns)")
        sys.exit(1)
    
    project_path = Path('.').resolve()
    custom_dir = project_path / '.clyde' / 'custom'
    custom_dir.mkdir(parents=True, exist_ok=True)
    
    module_file = custom_dir / f"{module_id.split('.', 1)[1]}.md"
    
    if module_file.exists():
        if not click.confirm(f"Module {module_id} already exists. Overwrite?"):
            click.echo("❌ Module creation cancelled.")
            return
    
    # Create basic module template
    content = f"""# {module_id.split('.', 1)[1].replace('-', ' ').title()}

## Overview

Describe the purpose and scope of this module.

## Guidelines

### Principle 1
- Explanation of the principle
- Examples and best practices

### Principle 2
- Another principle
- More examples

## Examples

```python
# Code examples demonstrating the guidelines
def example_function():
    pass
```

## Best Practices

- List important best practices
- Include do's and don'ts
- Reference other modules when relevant
"""
    
    with open(module_file, 'w') as f:
        f.write(content)
    
    click.echo(f"✅ Created custom module: {module_id}")
    click.echo(f"📝 Edit {module_file} to customize content")
    click.echo(f"🔄 Run 'clyde sync --add {module_id}' to include in configuration")


def _parse_template(template: str) -> tuple[str, str]:
    """Parse template string into language and framework."""
    templates = {
        'fastapi-react': ('python', 'fastapi'),
        'nextjs': ('typescript', 'nextjs'),
        'react': ('typescript', 'react'),
        'fastapi': ('python', 'fastapi'),
        'django': ('python', 'django'),
    }
    
    if template in templates:
        return templates[template]
    
    # Try to parse custom template format: language-framework
    parts = template.split('-')
    if len(parts) == 2:
        return parts[0], parts[1]
    
    raise click.BadParameter(f"Unknown template: {template}")


def _find_config_file(path: Path) -> Optional[Path]:
    """Find clyde configuration file in path or parent directories."""
    current = path
    while current != current.parent:
        config_file = current / '.clyde' / 'config.yaml'
        if config_file.exists():
            return config_file
        current = current.parent
    return None


def _sync_all_projects(base_path: Path, check: bool):
    """Sync all clyde projects in subdirectories."""
    projects_found = 0
    
    for item in base_path.iterdir():
        if item.is_dir() and (item / '.clyde' / 'config.yaml').exists():
            projects_found += 1
            click.echo(f"🔄 Syncing {item.name}...")
            
            try:
                config = ClydeConfig.from_file(item / '.clyde' / 'config.yaml')
                sync_manager = SyncManager(config)
                
                if check:
                    changes = sync_manager.preview_changes()
                    if changes:
                        click.echo(f"  📋 Would change: {len(changes)} files")
                    else:
                        click.echo("  ✨ No changes needed")
                else:
                    sync_manager.sync()
                    click.echo(f"  ✅ Synced successfully")
                    
            except Exception as e:
                click.echo(f"  ❌ Error: {e}")
    
    if projects_found == 0:
        click.echo("❌ No clyde projects found in subdirectories")
    else:
        click.echo(f"🎉 Processed {projects_found} projects")


@cli.group()
def mcp():
    """Manage Model Context Protocol (MCP) servers."""
    pass


@mcp.command('install')
@click.option('--mcp', 'mcp_ids', multiple=True, help='Install specific MCP(s)')
@click.option('--force', is_flag=True, help='Skip conflict detection and force install')
@click.option('--backup', is_flag=True, default=True, help='Create backup before making changes')
def mcp_install(mcp_ids: List[str], force: bool, backup: bool):
    """Install MCP servers with conflict detection and backup."""
    try:
        config_file = Path('.clyde/config.yaml')
        if not config_file.exists():
            click.echo("❌ No clyde project found. Run 'clyde init' first.")
            return
        
        config = ClydeConfig.from_file(config_file)
        manager = MCPManager(config)
        
        # Create backups if requested
        if backup and not force:
            backup_paths = [
                manager.claude_desktop_config_path, 
                manager.claude_code_config_path,
                manager.gemini_global_config_path,
                manager.gemini_project_config_path
            ]
            for config_path in backup_paths:
                if config_path.exists():
                    backup_path = manager.backup_config(config_path)
                    if backup_path:
                        click.echo(f"📦 Backed up {config_path.name} to {backup_path.name}")
        
        if mcp_ids:
            # Install specific MCPs
            success = True
            for mcp_id in mcp_ids:
                if not manager.install_mcp(mcp_id, interactive=not force):
                    success = False
        else:
            # Install all configured MCPs
            success = manager.install_all_mcps()
        
        if success:
            manager.save_configurations()
            click.echo("✅ MCP installation completed successfully")
        else:
            click.echo("❌ Some MCPs failed to install")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@mcp.command('list')
@click.option('--category', help='Filter by category (core, development, ai_tools)')
def mcp_list(category: Optional[str]):
    """List available MCP servers."""
    registry = MCPRegistry()
    mcps = registry.list_mcps(category)
    
    if not mcps:
        if category:
            click.echo(f"No MCPs found in category '{category}'")
        else:
            click.echo("No MCPs available")
        return
    
    if category:
        click.echo(f"Available MCPs in '{category}' category:")
    else:
        click.echo("Available MCPs:")
    
    click.echo()
    
    for mcp_id, mcp_def in mcps.items():
        click.echo(f"📦 {mcp_def.name} ({mcp_id})")
        click.echo(f"   {mcp_def.description}")
        click.echo(f"   Category: {mcp_def.category}")
        
        if mcp_def.required_env:
            click.echo(f"   Required env: {', '.join(mcp_def.required_env)}")
        
        platforms = ", ".join(mcp_def.platforms)
        click.echo(f"   Platforms: {platforms}")
        
        if mcp_def.notes:
            click.echo(f"   Note: {mcp_def.notes}")
        
        click.echo()


@mcp.command('status')
@click.option('--detailed', is_flag=True, help='Show detailed status including backups and versions')
def mcp_status(detailed: bool):
    """Show comprehensive status of MCP servers."""
    try:
        config_file = Path('.clyde/config.yaml')
        if not config_file.exists():
            click.echo("❌ No clyde project found. Run 'clyde init' first.")
            return
        
        config = ClydeConfig.from_file(config_file)
        manager = MCPManager(config)
        manager.status(detailed=detailed)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@mcp.command('add')
@click.argument('mcp_id')
@click.option('--category', type=click.Choice(['core', 'development', 'ai_tools']), 
              default='development', help='Category to add MCP to')
def mcp_add(mcp_id: str, category: str):
    """Add an MCP to the project configuration."""
    try:
        config_file = Path('.clyde/config.yaml')
        if not config_file.exists():
            click.echo("❌ No clyde project found. Run 'clyde init' first.")
            return
        
        # Check if MCP exists in registry
        registry = MCPRegistry()
        if not registry.get_mcp(mcp_id):
            click.echo(f"❌ Unknown MCP: {mcp_id}")
            click.echo("Run 'clyde mcp list' to see available MCPs")
            return
        
        config = ClydeConfig.from_file(config_file)
        
        # Add to appropriate category
        if category not in config.mcps:
            config.mcps[category] = []
        
        if mcp_id not in config.mcps[category]:
            config.mcps[category].append(mcp_id)
            config.save(config_file)
            click.echo(f"✅ Added {mcp_id} to {category} MCPs")
        else:
            click.echo(f"⚠️ {mcp_id} is already in {category} MCPs")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@mcp.command('remove')
@click.argument('mcp_id')
def mcp_remove(mcp_id: str):
    """Remove an MCP from the project configuration."""
    try:
        config_file = Path('.clyde/config.yaml')
        if not config_file.exists():
            click.echo("❌ No clyde project found. Run 'clyde init' first.")
            return
        
        config = ClydeConfig.from_file(config_file)
        
        # Remove from all categories
        removed = False
        for category in ['core', 'development', 'ai_tools']:
            if category in config.mcps and mcp_id in config.mcps[category]:
                config.mcps[category].remove(mcp_id)
                removed = True
                click.echo(f"✅ Removed {mcp_id} from {category} MCPs")
        
        if removed:
            config.save(config_file)
        else:
            click.echo(f"⚠️ {mcp_id} not found in any MCP category")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@mcp.command('config-only')
def mcp_config_only():
    """Generate MCP configuration files without installing."""
    try:
        config_file = Path('.clyde/config.yaml')
        if not config_file.exists():
            click.echo("❌ No clyde project found. Run 'clyde init' first.")
            return
        
        config = ClydeConfig.from_file(config_file)
        manager = MCPManager(config)
        manager.save_configurations()
        
        click.echo("✅ MCP configuration files generated")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@mcp.command('scan')
def mcp_scan():
    """Scan for existing MCP installations across all sources."""
    try:
        config_file = Path('.clyde/config.yaml')
        if not config_file.exists():
            click.echo("❌ No clyde project found. Run 'clyde init' first.")
            return
        
        config = ClydeConfig.from_file(config_file)
        manager = MCPManager(config)
        installations = manager.scan_existing_installations()
        
        if not installations:
            click.echo("No MCP installations found")
            return
        
        click.echo(f"🔍 Found {len(installations)} MCP installations:")
        click.echo()
        
        for inst in installations:
            working_icon = "🟢" if inst.working else "🔴"
            click.echo(f"  {working_icon} {inst.name}")
            click.echo(f"      Source: {inst.config_source}")
            click.echo(f"      Method: {inst.install_method}")
            if inst.version:
                click.echo(f"      Version: {inst.version}")
            if inst.command_path:
                click.echo(f"      Command: {inst.command_path}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@mcp.command('conflicts')
@click.option('--mcp', 'mcp_ids', multiple=True, help='Check conflicts for specific MCP(s)')
def mcp_conflicts(mcp_ids: List[str]):
    """Check for conflicts between desired and existing MCP installations."""
    try:
        config_file = Path('.clyde/config.yaml')
        if not config_file.exists():
            click.echo("❌ No clyde project found. Run 'clyde init' first.")
            return
        
        config = ClydeConfig.from_file(config_file)
        manager = MCPManager(config)
        
        # Use specified MCPs or all enabled MCPs
        if mcp_ids:
            check_mcps = list(mcp_ids)
        else:
            check_mcps = manager.get_enabled_mcps()
        
        if not check_mcps:
            click.echo("No MCPs to check for conflicts")
            return
        
        conflicts = manager.detect_conflicts(check_mcps)
        
        if not conflicts:
            click.echo("✅ No conflicts detected")
            return
        
        click.echo(f"⚠️  Found {len(conflicts)} conflicts:")
        click.echo()
        
        for conflict in conflicts:
            click.echo(f"🚨 {conflict.mcp_id}: {conflict.conflict_type}")
            click.echo(f"   {conflict.message}")
            click.echo(f"   Existing: {conflict.existing.install_method} via {conflict.existing.config_source}")
            click.echo(f"   Desired:  {conflict.desired.install_method} (Clyde managed)")
            click.echo(f"   Options: {', '.join(conflict.resolution_options)}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@mcp.command('backup')
@click.option('--restore', type=click.Path(exists=True), help='Restore from backup file')
@click.option('--list', 'list_backups', is_flag=True, help='List available backups')
def mcp_backup(restore: Optional[str], list_backups: bool):
    """Backup or restore MCP configuration files."""
    try:
        config_file = Path('.clyde/config.yaml')
        if not config_file.exists():
            click.echo("❌ No clyde project found. Run 'clyde init' first.")
            return
        
        config = ClydeConfig.from_file(config_file)
        manager = MCPManager(config)
        
        if list_backups:
            # List available backups
            all_backups = []
            backup_paths = [
                manager.claude_desktop_config_path, 
                manager.claude_code_config_path,
                manager.gemini_global_config_path,
                manager.gemini_project_config_path
            ]
            for config_path in backup_paths:
                backups = manager.list_backups(config_path)
                all_backups.extend([(backup, config_path.name) for backup in backups])
            
            if not all_backups:
                click.echo("No backups found")
                return
            
            click.echo("📦 Available backups:")
            for backup_path, config_name in sorted(all_backups, key=lambda x: x[0].stat().st_mtime, reverse=True):
                click.echo(f"  {backup_path.name} (for {config_name})")
            return
        
        if restore:
            # Restore from backup
            restore_path = Path(restore)
            
            # Determine which config this backup is for
            if 'claude_desktop_config' in restore_path.name:
                original_path = manager.claude_desktop_config_path
            elif 'claude_code_config' in restore_path.name:
                original_path = manager.claude_code_config_path
            elif 'settings' in restore_path.name and '.gemini' in str(restore_path):
                # Determine if it's global or project Gemini config
                if str(restore_path.parent).endswith('.gemini'):
                    original_path = manager.gemini_global_config_path
                else:
                    original_path = manager.gemini_project_config_path
            else:
                click.echo("❌ Cannot determine target configuration file from backup name")
                return
            
            success = manager.restore_config(restore_path, original_path)
            if success:
                click.echo(f"✅ Restored {original_path.name} from {restore_path.name}")
            else:
                click.echo(f"❌ Failed to restore {original_path.name}")
            return
        
        # Create backups
        backups_created = 0
        backup_paths = [
            manager.claude_desktop_config_path, 
            manager.claude_code_config_path,
            manager.gemini_global_config_path,
            manager.gemini_project_config_path
        ]
        for config_path in backup_paths:
            if config_path.exists():
                backup_path = manager.backup_config(config_path)
                if backup_path:
                    click.echo(f"📦 Backed up {config_path.name} to {backup_path.name}")
                    backups_created += 1
        
        if backups_created == 0:
            click.echo("No configuration files found to backup")
        else:
            click.echo(f"✅ Created {backups_created} backup(s)")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


if __name__ == '__main__':
    cli()
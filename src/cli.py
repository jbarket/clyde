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
    config_dir = project_path / '.claude'
    
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
        click.echo(f"📝 Edit .claude/config.yaml to customize configuration")
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
        config = ClydeConfig.from_file(config_path / '.claude' / 'config.yaml')
        
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
def list_modules():
    """Show available modules."""
    
    # Get modules directory from package
    modules_dir = Path(__file__).parent.parent / 'modules'
    
    if not modules_dir.exists():
        click.echo("❌ Modules directory not found")
        sys.exit(1)
    
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
    custom_dir = project_path / '.claude' / 'custom'
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
        config_file = current / '.claude' / 'config.yaml'
        if config_file.exists():
            return config_file
        current = current.parent
    return None


def _sync_all_projects(base_path: Path, check: bool):
    """Sync all clyde projects in subdirectories."""
    projects_found = 0
    
    for item in base_path.iterdir():
        if item.is_dir() and (item / '.claude' / 'config.yaml').exists():
            projects_found += 1
            click.echo(f"🔄 Syncing {item.name}...")
            
            try:
                config = ClydeConfig.from_file(item / '.claude' / 'config.yaml')
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


if __name__ == '__main__':
    cli()
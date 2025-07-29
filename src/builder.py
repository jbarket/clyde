"""
Configuration file builder for Clyde.
Handles creation of configuration files and project structure.
"""

from pathlib import Path
from typing import Dict, List
from jinja2 import Template
from datetime import datetime

from .config import ClydeConfig, ModuleResolver


class ConfigBuilder:
    """Builds configuration files for Clyde projects."""
    
    def __init__(self, config: ClydeConfig):
        self.config = config
        self.resolver = ModuleResolver(config)
    
    def create_config_file(self):
        """Create the main config.yaml file."""
        config_file = self.config.project_path / ".claude" / "config.yaml"
        self.config.save(config_file)
    
    def create_bootloader(self):
        """Create the bootloader claude.md file."""
        bootloader_file = self.config.project_path / "claude.md"
        template_file = Path(__file__).parent.parent / "templates" / "claude.md.template"
        
        if template_file.exists():
            with open(template_file, 'r') as f:
                template_content = f.read()
            
            template = Template(template_content)
            content = template.render(
                project_name=self.config.project_name,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        else:
            # Fallback content
            content = self._get_default_bootloader_content()
        
        with open(bootloader_file, 'w') as f:
            f.write(content)
    
    def create_project_files(self):
        """Create initial project-specific files."""
        claude_dir = self.config.project_path / ".claude"
        
        # Create project.md for project-specific instructions
        project_file = claude_dir / "project.md"
        if not project_file.exists():
            project_content = f"""# {self.config.project_name} - Project-Specific Instructions

## Project Overview

Describe the specific goals, requirements, and context for this project.

## Architecture Notes

Document key architectural decisions and patterns specific to this project.

## Custom Guidelines

Add any project-specific coding guidelines that extend or override the team standards.

## Development Workflow

Document the specific development workflow for this project:

- Branch naming conventions
- Code review process
- Deployment procedures
- Testing requirements

## Dependencies and Integration

Document key dependencies and how they should be used:

- External APIs
- Third-party libraries
- Internal services

---
*Edit this file to add project-specific instructions for Claude.*
"""
            with open(project_file, 'w') as f:
                f.write(project_content)
        
        # Create architecture.md for project structure documentation
        arch_file = claude_dir / "architecture.md"
        if not arch_file.exists():
            arch_content = f"""# {self.config.project_name} - Architecture Documentation

## Project Structure

```
{self.config.project_name}/
 README.md
 claude.md                  # Bootloader (don't edit)
 .claude/
    config.yaml           # Configuration (edit this)
    generated.md          # Auto-generated (don't edit)
    project.md            # Project-specific rules
    architecture.md       # This file
 src/                      # Source code
```

## Key Components

### Module 1
Description of key module or component.

### Module 2  
Description of another key module or component.

## Data Flow

Describe how data flows through the application.

## External Dependencies

List and describe key external dependencies:

- **Dependency 1**: Purpose and usage
- **Dependency 2**: Purpose and usage

## Development Environment

Document how to set up and run the development environment.

---
*Update this file as the project architecture evolves.*
"""
            with open(arch_file, 'w') as f:
                f.write(arch_content)
        
        # Create custom modules directory
        custom_dir = claude_dir / "custom"
        custom_dir.mkdir(exist_ok=True)
        
        # Create .gitignore for .claude directory
        gitignore_file = claude_dir / ".gitignore"
        if not gitignore_file.exists():
            with open(gitignore_file, 'w') as f:
                f.write("generated.md\n*.tmp\n*.cache\n")
    
    def build_generated_file(self) -> str:
        """Build the generated.md content from modules."""
        # Get all module content
        module_content = self.resolver.get_all_module_content()
        
        if not module_content:
            return self._get_empty_generated_content()
        
        # Build the generated file
        content_parts = []
        
        # Add header
        content_parts.append(self._get_generated_header())
        
        # Add table of contents if enabled
        if self.config.options.get("include_toc", True):
            content_parts.append(self._build_table_of_contents(module_content))
        
        # Add module content
        for module_id in self.config.includes:
            if module_id in module_content:
                content_parts.append(self._format_module_content(
                    module_id, 
                    module_content[module_id]
                ))
        
        # Add footer
        content_parts.append(self._get_generated_footer())
        
        return "\n\n".join(content_parts)
    
    def _get_generated_header(self) -> str:
        """Get the header for the generated file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config_hash = self.config.get_config_hash()
        
        return f"""<!-- Generated by clyde v1.0.0 on {timestamp} -->
<!-- DO NOT EDIT - Regenerate with 'clyde sync' -->
<!-- Config Hash: {config_hash} -->

# Development Standards - {self.config.project_name}

This file contains the consolidated development standards and patterns for this project.
It is automatically generated from the configuration in `.claude/config.yaml`.

**� Do not edit this file directly.** Changes will be overwritten.

- To modify standards: Edit `.claude/config.yaml` and run `clyde sync`
- To add project-specific rules: Edit `.claude/project.md`
- To document architecture: Edit `.claude/architecture.md`"""
    
    def _build_table_of_contents(self, module_content: Dict[str, str]) -> str:
        """Build table of contents from module content."""
        toc_lines = ["## Table of Contents"]
        
        for module_id in self.config.includes:
            if module_id not in module_content:
                continue
            
            # Extract title from module content
            content = module_content[module_id]
            lines = content.strip().split('\n')
            title = "Unknown Module"
            
            for line in lines:
                if line.strip().startswith('# '):
                    title = line.strip()[2:]
                    break
            
            # Create anchor link
            anchor = title.lower().replace(' ', '-').replace('(', '').replace(')', '')
            toc_lines.append(f"- [{title}](#{anchor})")
        
        return "\n".join(toc_lines)
    
    def _format_module_content(self, module_id: str, content: str) -> str:
        """Format module content with boundaries if enabled."""
        if not self.config.options.get("show_module_boundaries", True):
            return content
        
        # Add module boundary markers
        boundary_start = f"<!-- Module: {module_id} -->"
        boundary_end = f"<!-- End Module: {module_id} -->"
        
        return f"{boundary_start}\n\n{content}\n\n{boundary_end}"
    
    def _get_generated_footer(self) -> str:
        """Get the footer for the generated file."""
        module_count = len(self.config.includes)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""---

<!-- End Generated Content -->

*Generated from {module_count} modules on {timestamp}*  
*Configuration: `.claude/config.yaml`*  
*Generator: Clyde v1.0.0*"""
    
    def _get_empty_generated_content(self) -> str:
        """Get content for when no modules are configured."""
        return f"""<!-- Generated by clyde v1.0.0 -->
<!-- DO NOT EDIT - Regenerate with 'clyde sync' -->

# Development Standards - {self.config.project_name}

No modules are currently configured for this project.

## Getting Started

1. Edit `.claude/config.yaml` to add modules
2. Run `clyde sync` to regenerate this file
3. Run `clyde list-modules` to see available modules

Example modules to consider:
- `core.tdd` - Test-driven development principles
- `core.modularity` - Modular architecture guidelines
- `{self.config.language}.general` - {self.config.language.title()} coding standards

---

*Generated by Clyde v1.0.0*"""
    
    def _get_default_bootloader_content(self) -> str:
        """Get default bootloader content if template is not available."""
        return """# Claude Development Environment

This project uses a modular configuration system. Read these files in order:

1. `.claude/generated.md` - Team standards and patterns (auto-generated)
2. `.claude/project.md` - Project-specific instructions  
3. `.claude/architecture.md` - How this project is organized

Always treat these files as authoritative extensions of this file.

## Configuration Management

- To update team standards: Edit `.claude/config.yaml` and run `clyde sync`
- To add project-specific rules: Edit `.claude/project.md`
- Generated files are marked with timestamps and should not be hand-edited

---
*Generated by clyde - Development Environment Configuration System*"""


class ValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigValidator:
    """Validates Clyde configuration."""
    
    def __init__(self, config: ClydeConfig):
        self.config = config
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Check required fields
        if not self.config.project_name:
            issues.append("Project name is required")
        
        if not self.config.language:
            issues.append("Language is required")
        
        # Validate module references
        missing_modules = self.config.validate_modules()
        for module_id in missing_modules:
            issues.append(f"Module not found: {module_id}")
        
        # Validate options
        validation_level = self.config.options.get("validation_level", "normal")
        if validation_level not in ["strict", "normal", "permissive"]:
            issues.append(f"Invalid validation level: {validation_level}")
        
        return issues
    
    def validate_strict(self):
        """Validate configuration and raise exception if invalid."""
        issues = self.validate()
        if issues:
            raise ValidationError(f"Configuration validation failed:\n" + "\n".join(f"- {issue}" for issue in issues))
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
        config_file = self.config.project_path / ".clyde" / "config.yaml"
        self.config.save(config_file)
    
    def create_bootloader(self):
        """Create bootloader files for all targets."""
        for target in self.config.targets:
            self.create_bootloader_for_target(target)
    
    def create_bootloader_for_target(self, target: str):
        """Create the bootloader file for a specific target."""
        if target == "claude":
            bootloader_file = self.config.project_path / "claude.md"
            if len(self.config.targets) > 1:
                template_file = Path(__file__).parent.parent / "templates" / "claude-multi.md.template"
            else:
                template_file = Path(__file__).parent.parent / "templates" / "claude.md.template"
        elif target == "gemini":
            bootloader_file = self.config.project_path / "GEMINI.md"
            template_file = Path(__file__).parent.parent / "templates" / "GEMINI.md.template"
        else:
            # For future AI assistants, use a generic pattern
            bootloader_file = self.config.project_path / f"{target.upper()}.md"
            template_file = Path(__file__).parent.parent / "templates" / "claude.md.template"
        
        if template_file.exists():
            with open(template_file, 'r') as f:
                template_content = f.read()
            
            template = Template(template_content)
            content = template.render(
                project_name=self.config.project_name,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                targets=self.config.targets,
                target=target
            )
        else:
            # Fallback content
            content = self._get_default_bootloader_content_for_target(target)
        
        with open(bootloader_file, 'w') as f:
            f.write(content)
    
    def create_project_files(self):
        """Create initial project-specific files."""
        clyde_dir = self.config.project_path / ".clyde"
        
        # Create project-specific files for each target
        for target in self.config.targets:
            self.create_project_files_for_target(target, clyde_dir)
        
        # Create shared architecture file
        arch_file = clyde_dir / "architecture.md"
        if not arch_file.exists():
            arch_content = f"""# {self.config.project_name} - Architecture Documentation

## System Overview

Describe the high-level architecture and key components.

## Directory Structure

```
src/
  components/     # Reusable UI components
  services/       # Business logic and API calls
  utils/         # Helper functions and utilities
  types/         # Type definitions
tests/           # Test files
docs/           # Additional documentation
```

## Key Design Decisions

Document important architectural decisions and their rationale.

## Dependencies

List major dependencies and explain why they were chosen.
"""
            with open(arch_file, 'w') as f:
                f.write(arch_content)
    
    def create_project_files_for_target(self, target: str, clyde_dir: Path):
        """Create project-specific files for a target."""
        # Create project-specific file for this target
        project_file = clyde_dir / f"project-{target}.md"
        if not project_file.exists():
            project_content = f"""# {self.config.project_name} - Project-Specific Instructions ({target.title()})

## Project Overview

Describe the specific goals, requirements, and context for this project.

## {target.title()}-Specific Guidelines

Add any guidelines specific to {target.title()} for this project:

- Preferred response style
- {target.title()}-specific features to use/avoid
- Project context that {target.title()} should understand

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
*Edit this file to add project-specific instructions for {target.title()}.*
"""
            with open(project_file, 'w') as f:
                f.write(project_content)
        
        # Create architecture.md for project structure documentation
        arch_file = clyde_dir / "architecture.md"
        if not arch_file.exists():
            arch_content = f"""# {self.config.project_name} - Architecture Documentation

## Project Structure

```
{self.config.project_name}/
 README.md
 claude.md                  # Bootloader (don't edit)
 .clyde/
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
        custom_dir = clyde_dir / "custom"
        custom_dir.mkdir(exist_ok=True)
        
        # Create .gitignore for .clyde directory
        gitignore_file = clyde_dir / ".gitignore"
        if not gitignore_file.exists():
            with open(gitignore_file, 'w') as f:
                f.write("generated-*.md\n*.tmp\n*.cache\n")
    
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
        if self.config.options.get("include_toc", False):
            content_parts.append(self._build_table_of_contents(module_content))
        
        # Add module content (use expanded includes for groups)
        expanded_includes = self.config.expand_groups(self.config.includes)
        for module_id in expanded_includes:
            if module_id in module_content:
                content_parts.append(self._format_module_content(
                    module_id, 
                    module_content[module_id]
                ))
        
        # Add footer
        content_parts.append(self._get_generated_footer())
        
        return "\n\n".join(content_parts)
    
    def build_generated_file_for_target(self, target: str) -> str:
        """Build the generated content for a specific target."""
        # Get all module content for this target (includes AI-specific modules)
        module_content = self.resolver.get_all_module_content_for_target(target)
        
        if not module_content:
            return self._get_empty_generated_content_for_target(target)
        
        # Check if we should split files based on size
        max_tokens = self.config.options.get("max_tokens_per_file", 25000)
        split_strategy = self.config.options.get("split_strategy", "monolithic")
        
        if split_strategy == "includes":
            return self._build_includes_structure_for_target(target, module_content)
        elif split_strategy == "shared":
            return self._build_shared_files_structure_for_target(target, module_content)
        else:
            return self._build_monolithic_file_for_target(target, module_content)
    
    def _build_monolithic_file_for_target(self, target: str, module_content: Dict[str, str]) -> str:
        """Build a single monolithic file for the target, splitting if too large."""
        # Get all modules for this target
        all_modules = self.config.get_all_modules_for_target(target)
        expanded_includes = self.config.expand_groups(all_modules)
        
        # Calculate total content size
        total_lines = 0
        for module_id in expanded_includes:
            if module_id in module_content:
                total_lines += len(module_content[module_id].split('\n'))
        
        # If content is too large, create multiple files
        max_lines = self.config.options.get("max_lines_per_file", 800)
        if total_lines > max_lines:
            return self._build_split_monolithic_files(target, module_content, expanded_includes)
        
        # Build single file
        content_parts = []
        
        # Add header
        content_parts.append(self._get_generated_header_for_target(target))
        
        # Add table of contents if enabled
        if self.config.options.get("include_toc", False):
            content_parts.append(self._build_table_of_contents_for_target(target, module_content))
        
        # Add module content
        for module_id in expanded_includes:
            if module_id in module_content:
                content_parts.append(self._format_module_content(
                    module_id, 
                    module_content[module_id]
                ))
        
        # Add footer
        content_parts.append(self._get_generated_footer_for_target(target))
        
        return "\n\n".join(content_parts)
    
    def _build_shared_files_structure_for_target(self, target: str, module_content: Dict[str, str]) -> str:
        """Build shared files structure with explicit file references."""
        # Create shared and target-specific files
        self._create_shared_files(module_content)
        self._create_target_specific_files(target, module_content)
        
        # Return the main file with explicit references (not @ includes)
        return self._build_main_file_with_references(target)
    
    def _build_includes_structure_for_target(self, target: str, module_content: Dict[str, str]) -> str:
        """Build split files using @ includes for the target."""
        # Create shared and target-specific files
        self._create_shared_files(module_content)
        self._create_target_specific_files(target, module_content)
        
        # Return the main bootloader content with includes
        return self._build_bootloader_with_includes(target)
    
    def _get_generated_header(self) -> str:
        """Get the header for the generated file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config_hash = self.config.get_config_hash()
        
        return f"# Development Standards - {self.config.project_name}"

    
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
        # Never show module boundaries to reduce clutter
        return content
    
    def _get_generated_footer(self) -> str:
        """Get the footer for the generated file."""
        return ""
    
    def _get_empty_generated_content(self) -> str:
        """Get content for when no modules are configured."""
        return f"""<!-- Generated by clyde v1.0.0 -->
<!-- DO NOT EDIT - Regenerate with 'clyde sync' -->

# Development Standards - {self.config.project_name}

No modules are currently configured for this project.

## Getting Started

1. Edit `.clyde/config.yaml` to add modules
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

1. `.clyde/generated-claude.md` - Team standards and patterns (auto-generated)
2. `.clyde/project-claude.md` - Project-specific instructions  
3. `.clyde/architecture.md` - How this project is organized

Always treat these files as authoritative extensions of this file.

## Configuration Management

- To update team standards: Edit `.clyde/config.yaml` and run `clyde sync`
- To add project-specific rules: Edit `.clyde/project-claude.md`
- Generated files are marked with timestamps and should not be hand-edited

---
*Generated by clyde - Development Environment Configuration System*"""

    # Additional helper methods for multi-target support
    def _get_generated_header_for_target(self, target: str) -> str:
        """Get the header for the generated file for a specific target."""
        return f"# Development Standards - {self.config.project_name}"

    def _get_empty_generated_content_for_target(self, target: str) -> str:
        """Get default content when no modules are configured for a target."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""<!-- Generated by clyde v1.0.0 on {timestamp} -->
<!-- Target: {target.title()} -->
<!-- DO NOT EDIT - Regenerate with 'clyde sync' -->

# Development Standards - {self.config.project_name}

No modules are currently configured for {target.title()}.

To add modules:
1. Edit `.clyde/config.yaml`
2. Add modules to the `includes` section
3. Run `clyde sync` to regenerate this file

---
*Generated from 0 modules on {timestamp}*  
*Configuration: `.clyde/config.yaml`*  
*Generator: Clyde v1.0.0*"""

    def _build_table_of_contents_for_target(self, target: str, module_content: Dict[str, str]) -> str:
        """Build table of contents for a specific target."""
        if not self.config.options.get("include_toc", True):
            return ""
        
        toc_items = []
        all_modules = self.config.get_all_modules_for_target(target)
        expanded_includes = self.config.expand_groups(all_modules)
        
        for module_id in expanded_includes:
            if module_id in module_content:
                content = module_content[module_id]
                first_line = content.split('\n')[0] if content else ""
                
                if first_line.startswith('#'):
                    title = first_line.lstrip('#').strip()
                    anchor = title.lower().replace(' ', '-').replace('(', '').replace(')', '')
                    toc_items.append(f"- [{title}](#{anchor})")
        
        if not toc_items:
            return ""
        
        return "## Table of Contents\n" + "\n".join(toc_items)

    def _create_shared_files(self, module_content: Dict[str, str]):
        """Create shared files that both Claude and Gemini can use."""
        shared_dir = self.config.project_path / ".clyde" / "shared"
        shared_dir.mkdir(exist_ok=True)
        
        # Define file groupings
        file_groups = {
            "core-principles.md": ["core.dry", "core.code-quality", "core.systematic-thinking"],
            "development-standards.md": ["core.development-standards", "core.general-coding", "core.modular-architecture"],
            "professional-practices.md": ["core.professional-collaboration", "core.environment-management", "core.documentation-first"],
            "problem-solving.md": ["core.cognitive-framework", "core.error-handling", "patterns.problem-decomposition"],
            "development-patterns.md": ["patterns.iterative-development", "patterns.verification"],
            "tools-integration.md": ["tools.mcp-tools", "tools.development-workflow", "tools.git", "tools.docker"]
        }
        
        for filename, module_ids in file_groups.items():
            self._create_shared_file(shared_dir / filename, module_ids, module_content)
    
    def _create_shared_file(self, filepath: Path, module_ids: List[str], module_content: Dict[str, str]):
        """Create a single shared file from multiple modules."""
        content_parts = []
        
        # Add header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config_hash = self.config.get_config_hash()
        
        content_parts.append(f"""<!-- Generated by clyde v1.0.0 on {timestamp} -->
<!-- Shared Content -->
<!-- Config Hash: {config_hash} -->

# {filepath.stem.replace('-', ' ').title()}

This file contains shared development standards used by all AI targets.

**⚠ Do not edit this file directly.** Changes will be overwritten.

- To modify standards: Edit `.clyde/config.yaml` and run `clyde sync`""")
        
        # Add module content
        for module_id in module_ids:
            if module_id in module_content:
                content_parts.append(self._format_module_content(
                    module_id, 
                    module_content[module_id]
                ))
        
        # Write file
        with open(filepath, 'w') as f:
            f.write("\n\n".join(content_parts))
    
    def _create_target_specific_files(self, target: str, module_content: Dict[str, str]):
        """Create target-specific files."""
        target_file = self.config.project_path / ".clyde" / f"{target}-specific.md"
        
        # Get AI-specific modules
        ai_modules = []
        all_modules = self.config.get_all_modules_for_target(target)
        
        for module_id in all_modules:
            if f"{target}." in module_id or f"ai-specific.{target}" in module_id:
                ai_modules.append(module_id)
        
        if ai_modules:
            content_parts = []
            
            # Add header
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            config_hash = self.config.get_config_hash()
            
            content_parts.append(f"""<!-- Generated by clyde v1.0.0 on {timestamp} -->
<!-- Target: {target.title()} Specific -->
<!-- Config Hash: {config_hash} -->

# {target.title()}-Specific Guidelines

This file contains development standards specific to {target.title()}.

**⚠ Do not edit this file directly.** Changes will be overwritten.""")
            
            # Add AI-specific module content
            for module_id in ai_modules:
                if module_id in module_content:
                    content_parts.append(self._format_module_content(
                        module_id, 
                        module_content[module_id]
                    ))
            
            # Write file
            with open(target_file, 'w') as f:
                f.write("\n\n".join(content_parts))
    
    def _build_bootloader_with_includes(self, target: str) -> str:
        """Build bootloader content that uses @ includes."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config_hash = self.config.get_config_hash()
        
        includes = [
            "@./.clyde/shared/core-principles.md",
            "@./.clyde/shared/development-standards.md",
            "@./.clyde/shared/professional-practices.md", 
            "@./.clyde/shared/problem-solving.md",
            "@./.clyde/shared/development-patterns.md",
            "@./.clyde/shared/tools-integration.md",
            f"@./.clyde/{target}-specific.md",
            f"@./.clyde/project-{target}.md",
            "@./.clyde/architecture.md"
        ]
        
        return f"""<!-- Generated by clyde v1.0.0 on {timestamp} -->
<!-- Target: {target.title()} -->
<!-- Split File Structure -->
<!-- Config Hash: {config_hash} -->

# Development Standards - {self.config.project_name}

This file uses includes to load comprehensive development standards while staying under token limits.

**⚠ Do not edit this file directly.** Changes will be overwritten.

- To modify standards: Edit `.clyde/config.yaml` and run `clyde sync`
- To add project-specific rules: Edit `.clyde/project-{target}.md`
- To document architecture: Edit `.clyde/architecture.md`

## Included Files

{chr(10).join(includes)}

---
*Generated with split file structure on {timestamp}*
*Target: {target.title()}*
*Configuration: `.clyde/config.yaml`*
*Generator: Clyde v1.0.0*"""
    
    def _build_main_file_with_references(self, target: str) -> str:
        """Build main file that explicitly lists other files to read."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config_hash = self.config.get_config_hash()
        
        # Define the shared files that will be created
        shared_files = [
            ".clyde/shared/core-principles.md",
            ".clyde/shared/development-standards.md", 
            ".clyde/shared/professional-practices.md",
            ".clyde/shared/problem-solving.md",
            ".clyde/shared/development-patterns.md",
            ".clyde/shared/tools-integration.md"
        ]
        
        # Add target-specific file if it will be created
        target_file = f".clyde/{target}-specific.md"
        
        # Build file list with descriptions
        file_list = []
        file_descriptions = {
            "core-principles.md": "DRY principle, code quality, systematic thinking",
            "development-standards.md": "General coding standards and modular architecture",
            "professional-practices.md": "Collaboration, environment management, documentation",
            "problem-solving.md": "Cognitive frameworks, error handling, problem decomposition", 
            "development-patterns.md": "Iterative development and verification patterns",
            "tools-integration.md": "MCP tools, development workflow, git, docker"
        }
        
        for file_path in shared_files:
            filename = file_path.split('/')[-1]
            description = file_descriptions.get(filename, "Development standards")
            file_list.append(f"- **{file_path}** - {description}")
        
        # Add target-specific file
        file_list.append(f"- **{target_file}** - {target.title()}-specific guidelines and patterns")
        
        return f"""<!-- Generated by clyde v1.0.0 on {timestamp} -->
<!-- Target: {target.title()} -->
<!-- Shared File Structure -->
<!-- Config Hash: {config_hash} -->

# Development Standards - {self.config.project_name}

This file coordinates comprehensive development standards split across multiple files for easier reading.

**⚠ Do not edit this file directly.** Changes will be overwritten.

## Required Reading Files

**IMPORTANT:** After reading this file, you MUST also read each of the following files. They contain the actual development standards:

{chr(10).join(file_list)}

## Reading Strategy

1. **Read this file first** (you're doing that now)
2. **Read each file listed above** using the Read tool
3. **Read project files**: `.clyde/project-{target}.md` and `.clyde/architecture.md`

## File Organization

The standards are organized by category:
- **Core Principles**: Fundamental development principles (DRY, quality, thinking)
- **Development Standards**: Coding standards and architecture patterns  
- **Professional Practices**: Collaboration, environment, documentation
- **Problem Solving**: Frameworks for analysis and error handling
- **Development Patterns**: Iterative development and verification approaches
- **Tools Integration**: MCP tools, workflow, git, docker usage

## Configuration Management

- To modify standards: Edit `.clyde/config.yaml` and run `clyde sync`
- To add project-specific rules: Edit `.clyde/project-{target}.md`
- To document architecture: Edit `.clyde/architecture.md`

---
*Generated with shared file structure on {timestamp}*
*Target: {target.title()}*
*Configuration: `.clyde/config.yaml`*
*Generator: Clyde v1.0.0*"""
    
    def _get_generated_footer_for_target(self, target: str) -> str:
        """Get the footer for the generated file for a specific target."""
        return ""

    def _get_default_bootloader_content_for_target(self, target: str) -> str:
        """Get default bootloader content for a target."""
        if target == "claude":
            return f"""# Claude Development Environment

**🚨 CRITICAL: Read configuration files BEFORE any work**

MANDATORY: Before responding to ANY request, you MUST read these files in order:

1. **`.clyde/generated-claude.md`** - Main coordination file (read this first)
2. **Read ALL files referenced** in the generated-claude.md file 
3. **`.clyde/project-claude.md`** - Project-specific instructions
4. **`.clyde/architecture.md`** - Project organization

**IMPORTANT:** The generated-claude.md file will list additional files you must read. Read each one using the Read tool. These files contain ALL team standards and override any defaults. They are AUTHORITATIVE.**

## Configuration Management

- To update team standards: Edit `.clyde/config.yaml` and run `clyde sync`
- To add project-specific rules: Edit `.clyde/project-claude.md`
- Generated files are marked with timestamps and should not be hand-edited

---
*Generated by clyde - Development Environment Configuration System*"""

        elif target == "gemini":
            return f"""# Gemini Development Environment

This project uses a modular configuration system managed by Clyde.

## Context Files
The following files extend this configuration:
@./.clyde/generated-gemini.md
@./.clyde/project-gemini.md
@./.clyde/architecture.md

## Configuration Management
- To update team standards: Edit `.clyde/config.yaml` and run `clyde sync`
- To add project-specific rules: Edit `.clyde/project-gemini.md`
- Generated files are marked with timestamps and should not be hand-edited

---
*Generated by clyde - Development Environment Configuration System*"""

        else:
            return f"""# {target.title()} Development Environment

This project uses a modular configuration system managed by Clyde.

## Configuration Files
- `.clyde/generated-{target}.md` - Team standards and patterns (auto-generated)
- `.clyde/project-{target}.md` - Project-specific instructions  
- `.clyde/architecture.md` - How this project is organized

## Configuration Management
- To update team standards: Edit `.clyde/config.yaml` and run `clyde sync`
- To add project-specific rules: Edit `.clyde/project-{target}.md`

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

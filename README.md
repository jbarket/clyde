# Clyde - Development Environment Configuration System

Clyde is a tool that standardizes how Claude approaches software development across all projects. It manages modular configuration files that define coding principles, framework conventions, and project-specific guidelines.

## Core Concept

Projects using Clyde have a simple "bootloader" `claude.md` that never changes, which instructs Claude to read generated configuration files from a `.claude/` directory. This allows centralized management of development standards while supporting project-specific customizations.

## Quick Start

### Installation

```bash
pip install clyde
```

### Initialize a New Project

```bash
# Interactive setup
clyde init

# With specific options
clyde init --language python --framework fastapi --database postgres

# Use a predefined template
clyde init --template fastapi-react
```

### Sync Configuration

```bash
# Regenerate configuration files
clyde sync

# Add a module
clyde sync --add react.patterns

# Remove a module
clyde sync --remove docker

# Preview changes without applying
clyde sync --check
```

## Project Structure

After initialization, your project will have:

```
your-project/
├── claude.md                    # Bootloader (don't edit)
├── .claude/
│   ├── config.yaml             # Main configuration (edit this)
│   ├── generated.md            # Auto-generated standards (don't edit)
│   ├── project.md              # Project-specific instructions
│   ├── architecture.md         # Architecture documentation
│   └── custom/                 # Custom modules directory
└── src/                        # Your source code
```

## Available Modules

### Core Principles
- `core.tdd` - Test-driven development principles
- `core.modularity` - Modular architecture guidelines
- `core.dry` - DRY principle guidelines
- `core.general` - General coding standards

### Language-Specific
- `python.general` - Python coding conventions
- `python.testing` - Python testing patterns
- `javascript.general` - JavaScript/TypeScript guidelines
- `javascript.testing` - JavaScript testing patterns

### Framework-Specific
- `fastapi.structure` - FastAPI project structure
- `fastapi.patterns` - FastAPI patterns and conventions
- `react.structure` - React component organization
- `react.patterns` - React best practices
- `nextjs.structure` - Next.js App Router structure
- `nextjs.patterns` - Next.js patterns

### Database & Tools
- `postgres` - PostgreSQL guidelines
- `mongodb` - MongoDB best practices
- `docker` - Docker best practices
- `git` - Git workflow guidelines

## Configuration

Edit `.claude/config.yaml` to customize your project:

```yaml
# Clyde Configuration
version: 1.0

project:
  name: "My FastAPI Project"
  type: "api"
  language: "python"
  framework: "fastapi"

includes:
  # Core principles
  - core.tdd
  - core.modularity
  - core.dry
  - core.general
  
  # Language-specific
  - python.general
  - python.testing
  
  # Framework-specific
  - fastapi.structure
  - fastapi.patterns
  
  # Tools
  - docker
  - git

options:
  show_module_boundaries: true
  include_toc: true
  validation_level: "normal"
```

## CLI Commands

### Project Management
```bash
# Initialize new project
clyde init [OPTIONS] [PATH]

# Sync configuration files
clyde sync [OPTIONS] [PATH]

# Sync all projects in directory
clyde sync --all
```

### Module Management
```bash
# List available modules
clyde list-modules

# Show module content
clyde show core.tdd

# Create custom module
clyde create-module custom.my-patterns
```

## License

MIT License - see LICENSE file for details.

---

*Clyde - Standardizing development environments for AI-assisted coding.*
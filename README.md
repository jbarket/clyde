# Clyde - Development Environment Configuration System

Clyde is a powerful tool that standardizes how Claude AI approaches software development across all projects. It manages modular configuration files that define coding principles, framework conventions, and project-specific guidelines, while also providing seamless MCP (Model Context Protocol) server installation and management.

## 🚀 Core Features

- **Unified Development Standards**: Consistent coding principles across all projects
- **Token-Optimized**: 74% reduction in configuration size while preserving essential guidance
- **MCP Server Management**: Easy installation and configuration of MCP servers
- **Modular Architecture**: Mix and match development modules based on your stack
- **AI-First Design**: Optimized specifically for Claude AI interactions
- **Multi-Target Support**: Generate configurations for Claude, Gemini, and other AI models

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/jbarket/clyde.git
cd clyde

# Install in development mode
pip install -e .

# Verify installation
clyde --version
```

## 🏗️ Project Setup

### Initialize a New Project

```bash
# Interactive setup
clyde init

# Quick setup with defaults
clyde init --language python --framework fastapi

# Initialize in specific directory
clyde init /path/to/my-project
```

### Sync Configuration

```bash
# Generate configuration files
clyde sync

# Target specific AI model
clyde sync --target claude
clyde sync --target gemini

# Preview changes
clyde sync --check
```

## 📁 Project Structure

After initialization, your project will have:

```
your-project/
├── claude.md                     # Bootloader for Claude (don't edit)
├── gemini.md                     # Bootloader for Gemini (don't edit)
├── .clyde/
│   ├── config.yaml              # Main configuration (edit this)
│   ├── generated-claude.md      # Claude-optimized standards
│   ├── generated-gemini.md      # Gemini-optimized standards
│   ├── project-claude.md        # Claude-specific project rules
│   ├── architecture.md          # Architecture documentation
│   └── shared/                  # Shared configuration modules
└── src/                         # Your source code
```

## 🔌 MCP Server Management

Clyde makes it easy to install and configure MCP servers for enhanced AI capabilities:

### Install MCP Servers

```bash
# Install essential MCP servers
clyde mcp install zen-coding taskmaster context7

# Install specific server
clyde mcp install sequential-thinking

# List available servers
clyde mcp list

# Show server details
clyde mcp show zen-coding
```

### Configure MCP Servers

```bash
# Show current MCP status with detailed information
clyde mcp status --detailed

# Scan for existing MCP installations across all sources
clyde mcp scan

# Check for conflicts between desired and existing installations
clyde mcp conflicts

# Check specific MCPs for conflicts
clyde mcp conflicts --mcp zen-coding --mcp taskmaster

# Backup MCP configuration files
clyde mcp backup

# List available backups
clyde mcp backup --list

# Restore from backup
clyde mcp backup --restore path/to/backup_file.json
```

### Enhanced MCP Management

Clyde provides comprehensive MCP conflict detection and management:

#### Conflict Detection
- **Duplicate Detection**: Identifies MCPs already configured in Claude Desktop/Code
- **Version Conflicts**: Detects version mismatches between existing and desired installations
- **Installation Method Conflicts**: Handles differences between npm, uvx, and manual installations
- **Interactive Resolution**: Provides user prompts with multiple resolution options

#### Backup & Restore
- **Automatic Backups**: Creates timestamped backups before making changes
- **Selective Restore**: Restore specific configuration files from backups
- **Backup Management**: List and manage multiple backup versions

#### Installation Sources
Clyde scans for existing MCPs across:
- Claude Desktop configuration
- Claude Code configuration
- Gemini CLI global configuration (`~/.gemini/settings.json`)
- Gemini CLI project configuration (`<project>/.gemini/settings.json`)
- Global npm packages
- uvx installations

#### Gemini CLI Configuration Notes
- **Merge Behavior**: Gemini CLI uses hierarchical settings (project overrides global)
- **Verification Needed**: For accurate conflict detection, verify your Gemini CLI merge behavior:
  1. Create test MCP servers in both `~/.gemini/settings.json` and `<project>/.gemini/settings.json`
  2. Run `gemini /mcp` in the project directory to see which servers are active
  3. Report the behavior to improve Clyde's conflict detection accuracy

### Available MCP Servers

- **zen-coding**: Advanced code generation and refactoring
- **taskmaster**: Complex task management and breakdown  
- **sequential-thinking**: Structured problem-solving
- **context7**: Documentation and library integration
- **playwright**: Browser automation and testing
- **memory**: Knowledge graph and memory management

## 📚 Available Modules

### Core Development Standards
- `core.development-standards` - Unified TDD + Documentation-driven development
- `core.code-quality` - Code quality standards and practices
- `core.modular-architecture` - Modular design principles
- `core.error-handling` - Comprehensive error handling philosophy
- `core.systematic-thinking` - Problem-solving frameworks

### Language-Specific
- `python.general` - Python coding conventions and best practices
- `javascript.general` - JavaScript/TypeScript guidelines

### Framework-Specific
- `frameworks.fastapi` - FastAPI patterns and structure
- `frameworks.react` - React best practices and patterns
- `frameworks.nextjs` - Next.js App Router conventions

### Database & Infrastructure
- `databases.postgres` - PostgreSQL design and optimization
- `databases.mongodb` - MongoDB document design patterns

### AI-Specific
- `claude.model-strategy` - Claude model selection and prompting strategies

## ⚙️ Configuration

Edit `.clyde/config.yaml` to customize your project:

```yaml
# Clyde Configuration
version: 1.0

# Project metadata
project:
  name: "My FastAPI Project"
  type: "api"
  language: "python"
  framework: "fastapi"

# Module inclusions - optimized and consolidated
includes:
  # Core principles
  - core.development-standards
  - core.code-quality
  - core.modular-architecture
  - core.error-handling
  
  # Language-specific
  - python.general
  
  # Framework-specific
  - frameworks.fastapi
  
  # Database
  - databases.postgres

# Configuration options
options:
  show_module_boundaries: false
  include_toc: true
  validation_level: "normal"

# MCP server configuration
mcp:
  servers:
    - zen-coding
    - taskmaster
    - context7
  auto_configure: true
```

## 🛠️ CLI Commands

### Project Management
```bash
# Initialize new project
clyde init [OPTIONS] [PATH]

# Sync configuration files
clyde sync [OPTIONS]

# Check configuration without applying
clyde sync --check
```

### MCP Management
```bash
# Install MCP servers with conflict detection
clyde mcp install <server-name>

# Show comprehensive MCP status (includes Gemini CLI)
clyde mcp status --detailed

# Scan for existing MCP installations (Claude + Gemini CLI)
clyde mcp scan

# Check for conflicts with existing installations
clyde mcp conflicts

# Backup MCP configuration files
clyde mcp backup

# List available MCP servers
clyde mcp list

# Add/remove MCPs from project
clyde mcp add <server-name>
clyde mcp remove <server-name>
```

### Module Management
```bash
# List available modules
clyde list-modules

# Show module content
clyde show core.development-standards

# Add module to project
clyde sync --add frameworks.react

# Remove module from project
clyde sync --remove databases.mongodb
```

## 🎯 Token Optimization

Clyde is optimized for AI context windows:

- **74% size reduction**: From ~3,841 to 996 lines
- **Essential guidance preserved**: All development standards maintained
- **Verbose examples removed**: Claude already knows basic syntax
- **Consolidated modules**: Eliminated redundant standalone files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test them
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Issues**: [GitHub Issues](https://github.com/jbarket/clyde/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jbarket/clyde/discussions)

---

*Clyde - Maximizing AI-assisted development through intelligent configuration management*
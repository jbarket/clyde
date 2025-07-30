# Changelog

All notable changes to Clyde - Development Environment Configuration System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Bulletproof Sync System** - Comprehensive safety features for sync operations
  - Pre-sync validation with config file integrity checks
  - Automatic backup creation with timestamped snapshots
  - Atomic operations with automatic rollback on failure
  - Post-sync verification and corruption detection
  - Full audit trail with detailed operation logging
- **Smart Project Detection** - Intelligent analysis of existing codebases
  - Automatic detection of project types (Python CLI, FastAPI, React, Next.js, etc.)
  - Evidence-based confidence scoring with detailed analysis
  - Intelligent module and MCP suggestions based on detected stack
  - Support for setup.py, package.json, and other project files
- **Enhanced MCP Management** - Comprehensive MCP server installation and conflict detection
  - Multi-source scanning (Claude Desktop, Claude Code, Gemini CLI, npm, uvx)
  - Intelligent conflict detection and interactive resolution
  - Backup and restore functionality for MCP configurations
  - Cross-platform configuration management
- **Advanced CLI Commands**
  - `clyde detect` - Analyze existing projects and suggest configurations
  - `clyde snapshots` - Manage bulletproof sync snapshots and rollbacks
  - `clyde audit` - View comprehensive operation audit trail
  - Enhanced `clyde sync` with bulletproof features and safety options
  - Enhanced `clyde init` with smart project detection and auto-configuration
- **Gemini CLI Support** - Full integration with Google's Gemini CLI
  - Global and project-level configuration detection
  - Hierarchical settings management
  - Cross-AI-platform configuration synchronization

### Enhanced
- **Sync Command** - Now uses bulletproof sync by default with legacy fallback
  - Added `--force` flag to override validation errors
  - Added `--unsafe` flag for legacy sync behavior
  - Added `--target` flag for specific AI platform sync
  - Comprehensive error reporting with actionable suggestions
- **MCP Commands** - Enhanced with conflict detection and advanced management
  - `clyde mcp scan` - Scan for existing installations across all sources
  - `clyde mcp conflicts` - Check for conflicts between desired and existing MCPs
  - `clyde mcp backup` - Create and manage MCP configuration backups
  - Detailed status reporting with installation source tracking
- **Project Initialization** - Now includes smart detection and suggestion
  - Automatic project type detection when run in existing directories
  - Confidence-based suggestions with detailed evidence
  - Interactive configuration with intelligent defaults

### Fixed
- **Configuration Integrity** - Bulletproof sync prevents corruption and data loss
- **Module Reference Validation** - Validates all module references before sync
- **Cross-platform Compatibility** - Improved handling of different file systems
- **Error Recovery** - Comprehensive rollback and recovery mechanisms

### Security
- **Configuration Backup** - All changes are backed up before modification
- **Validation Checks** - Comprehensive pre-sync validation prevents corruption
- **Audit Trail** - Complete operation logging for security and debugging

## [1.0.0] - Initial Release

### Added
- **Core Configuration System**
  - Modular architecture with mix-and-match development modules
  - Multi-target support (Claude, Gemini, and extensible to other AI models)
  - YAML-based configuration with intelligent defaults
  - Token-optimized output (74% size reduction while preserving guidance)
- **Development Standards Modules**
  - Core principles: development standards, code quality, systematic thinking
  - Language-specific: Python and JavaScript/TypeScript guidelines
  - Framework-specific: FastAPI, React, Next.js best practices
  - Database integration: PostgreSQL and MongoDB patterns
  - AI-specific: Claude model strategy and prompting guidelines
- **MCP Server Integration**
  - Registry of essential MCP servers for enhanced AI capabilities
  - Automatic installation and configuration management
  - Support for zen-coding, taskmaster, sequential-thinking, context7, playwright, memory
- **CLI Interface**
  - `clyde init` - Initialize new projects with framework detection
  - `clyde sync` - Regenerate configuration files from modules
  - `clyde list-modules` - Browse available development modules
  - `clyde mcp` - Manage MCP server installations
- **Project Templates**
  - Pre-configured templates for common stacks
  - FastAPI + React, Next.js, Django, and more
  - Automatic module selection based on technology choices

### Technical Features
- **File Generation**
  - Bootloader system for seamless AI integration
  - Split file structure for better organization
  - Automatic timestamp and version tracking
- **Validation System**
  - Configuration validation with helpful error messages
  - Module dependency checking
  - Format and syntax validation
- **Cross-Platform Support**
  - Windows, macOS, and Linux compatibility
  - Consistent behavior across different environments

---

## Version Numbering

- **Major (X.0.0)**: Breaking changes to configuration format or CLI interface
- **Minor (1.X.0)**: New features, modules, or MCP integrations
- **Patch (1.1.X)**: Bug fixes, documentation updates, small improvements

## Migration Guide

### From 1.0.0 to Unreleased
- Bulletproof sync is now the default - use `--unsafe` for legacy behavior
- New snapshot and audit commands available for enhanced safety
- Project detection runs automatically during `clyde init`
- Enhanced MCP management with conflict detection
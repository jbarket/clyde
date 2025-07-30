# MCP Management System Design

## Configuration Schema

```yaml
# .clyde/config.yaml
mcps:
  enabled: true  # false = skip MCP management entirely
  
  # Core development MCPs (auto-installed)
  core:
    - sequential-thinking    # Advanced reasoning
    - memory                # Persistent memory 
    - context7              # Documentation lookup
    
  # Project-specific MCPs
  development:
    - playwright            # Browser automation (downloads ~170MB)
    - task-master          # Project management (requires GOOGLE_AI_STUDIO_API_KEY)
    
  # AI collaboration MCPs  
  ai_tools:
    - zen                  # Multi-AI orchestration (requires uv + GEMINI_API_KEY)
    - gemini              # Direct Gemini access (requires GEMINI_API_KEY)

  # Environment variables (will prompt if missing for required MCPs)
  env:
    GOOGLE_AI_STUDIO_API_KEY: ${GOOGLE_AI_STUDIO_API_KEY}
    GEMINI_API_KEY: ${GEMINI_API_KEY}
    MEMORY_DB_PATH: "${HOME}/.clyde/memory.db"  # Auto-generated path
```

## Installation Flow

1. **Dependency Check**: Check for Node.js, uv (install if missing)
2. **MCP Installation**: Install configured MCPs via npx/uvx
3. **Config Generation**: Generate both Claude Code + Claude Desktop configs
4. **Verification**: Test MCP connections
5. **Environment Setup**: Prompt for missing API keys

## File Structure

```
.clyde/
├── config.yaml          # User config with MCP selections
├── mcp-registry.yaml    # MCP definitions (shipped with clyde)
├── generated-claude.json   # Generated Claude Code config
├── generated-claude-desktop.json  # Generated Claude Desktop config
└── memory.db            # MCP memory storage
```

## CLI Commands

```bash
# Install/update MCPs based on config
clyde mcp install

# List available MCPs
clyde mcp list

# Check MCP status
clyde mcp status

# Add/remove specific MCP
clyde mcp add zen
clyde mcp remove playwright

# Generate configs without installing
clyde mcp config-only
```

## Platform Support

- ✅ macOS: Full support
- ✅ Linux: Full support  
- ✅ WSL2: Full support
- ❓ Windows: npx MCPs only (no uv-based MCPs like zen)
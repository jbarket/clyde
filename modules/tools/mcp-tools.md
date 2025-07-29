# MCP Tools Integration

## Essential MCP Tools Stack

Every project should integrate these **mandatory MCP tools**:
- **Zen Coding** - Automated code generation and refactoring
- **Taskmaster AI** - Complex task management and breakdown  
- **Sequential Thinking** - Structured problem-solving and analysis
- **Context7** - Documentation and library integration
- **Playwright** - Headless browser automation and testing

## Tool Usage Guidelines

### Zen Coding
**When to Use:**
- Multi-file code generation and refactoring
- Code scaffolding for new features or modules
- Pattern implementation across multiple files
- Large-scale architectural changes

**Integration:**
- Use proactively for qualifying tasks without user prompting
- Combine with research agents for informed generation
- Always validate with tests and linting after operations

### Sequential Thinking
**When to Use:**
- Complex problem analysis requiring multi-step reasoning
- Architectural decisions needing trade-off evaluation
- Debugging complex issues requiring root cause analysis
- Performance optimization and security analysis

**Integration:**
- Use before Zen Coding to plan approach
- Analyze task complexity before Taskmaster breakdown
- Structure research queries and analysis
- Systematic problem investigation during debugging

### Context7
**When to Use:**
- Research best practices before implementation
- Get up-to-date API documentation during development
- Find implementation patterns and code examples
- Understand library capabilities and constraints

**Best Practices:**
- Always research before implementing unfamiliar features
- Leverage real-world implementation examples
- Use for current documentation and community standards

### Playwright
**Critical Requirement:** Must **ALWAYS** run headless

```javascript
// MANDATORY configuration
const browser = await playwright.chromium.launch({
  headless: true,  // NEVER set to false
  args: ['--no-sandbox', '--disable-dev-shm-usage']
});

test.use({
  headless: true,  // REQUIRED for all tests
  video: 'off',    // No visual output
  trace: 'off'     // No trace UI
});
```

**When to Use:**
- End-to-end testing of complete user workflows
- Automated screenshot capture and web scraping
- Performance testing and accessibility checks
- Cross-browser compatibility testing

## Development Process Integration

### 1. Analysis Phase
- Use **Sequential Thinking** for problem breakdown
- Use **Context7** for research and documentation

### 2. Planning Phase
- Use **Taskmaster AI** for task management (see development-workflow.md)
- Create PRDs for complex features

### 3. Implementation Phase
- Use **Zen Coding** for automated code generation
- Use **Context7** for implementation examples

### 4. Testing Phase
- Use **Playwright** for E2E testing (headless only)
- Integrate with unit and integration testing

### 5. Validation Phase
- Use **Taskmaster** to track completion
- Use **Sequential Thinking** for final verification

## Quality Assurance

### MCP Tools Checklist
```bash
□ Sequential Thinking used for complex analysis
□ Context7 research completed for unfamiliar areas
□ Taskmaster tracking active for multi-step tasks
□ Zen Coding used for appropriate code generation
□ Playwright E2E tests running headless only
□ All MCP tool outputs validated and tested
```

## Configuration

### Environment Setup
```yaml
# .mcp-config.yaml
tools:
  zen_coding:
    enabled: true
    auto_format: true
    follow_conventions: true
    
  taskmaster:
    enabled: true
    prefer_prd: true
    complexity_analysis: true
    
  sequential_thinking:
    enabled: true
    auto_trigger: complex_analysis
    
  context7:
    enabled: true
    research_first: true
    
  playwright:
    enabled: true
    headless_only: true
    no_interruption: true
```

## Benefits

### Development Efficiency
- Automated code generation reduces repetitive work
- Structured task management improves project organization
- Research integration ensures informed decisions
- Comprehensive testing with headless automation

### Quality Assurance
- Systematic analysis through sequential thinking
- Current documentation via Context7 research
- Tracked progress through Taskmaster management
- Consistent patterns via Zen Coding automation
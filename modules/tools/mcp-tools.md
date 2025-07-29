# MCP Tools Integration

## Core MCP Tools Stack

### Essential Tools Configuration
Every project should integrate these **mandatory MCP tools**:
- **Zen Coding** - Automated code generation and refactoring
- **Taskmaster AI** - Complex task management and breakdown
- **Sequential Thinking** - Structured problem-solving and analysis
- **Context7** - Documentation and library integration  
- **Playwright** - Headless browser automation and testing

## Zen Coding Integration

### When to Use Zen Coding
- **Automated code generation** for repetitive patterns
- **Large-scale refactoring** across multiple files
- **Code scaffolding** for new features or modules
- **Pattern implementation** when applying architectural patterns
- **Complex transformations** that require multiple file edits

### Best Practices
```yaml
# Always use for complex coding tasks
- name: "Feature Implementation"
  trigger: "Multi-file changes required"
  action: "Use Zen Coding for automated generation"
  
- name: "Architecture Patterns"
  trigger: "Implementing design patterns"
  action: "Use Zen Coding for consistent pattern application"
  
- name: "Refactoring Tasks"
  trigger: "Large-scale code changes"
  action: "Use Zen Coding for safe, automated refactoring"
```

### Integration Guidelines
- **Proactive usage** - Use without user prompting for qualifying tasks
- **Research integration** - Combine with research agents for informed generation
- **Pattern consistency** - Ensure generated code follows project conventions
- **Validation** - Always run tests and linting after Zen Coding operations

## Taskmaster AI Integration

### Complex Task Management
**Preference Hierarchy for Task Management:**
1. **PRD + Taskmaster** - For all complex, multi-step tasks
2. **Taskmaster breakdown** - For tasks requiring planning and tracking
3. **Simple todos** - Only for trivial, single-step operations

### When to Use Taskmaster
```markdown
Use Taskmaster for:
✅ Multi-step feature implementation
✅ Complex bug fixes requiring analysis
✅ Architectural changes
✅ Integration projects
✅ Performance optimization tasks
✅ Security implementations

Avoid simple todos for:
❌ Single file edits
❌ Configuration changes
❌ Documentation updates
❌ Simple bug fixes
```

### PRD-Driven Development
```markdown
# Example PRD Structure
## Product Requirements Document

### Feature: User Authentication System

#### Overview
Implement secure user authentication with JWT tokens, password hashing, and session management.

#### Requirements
1. User registration with email validation
2. Secure login with password hashing
3. JWT token generation and validation
4. Session management and logout
5. Password reset functionality

#### Acceptance Criteria
- Users can register with valid email addresses
- Passwords are securely hashed before storage
- JWT tokens expire after configurable time
- Sessions are properly invalidated on logout
- Password reset sends secure email links

#### Technical Considerations
- Use bcrypt for password hashing
- Implement rate limiting for login attempts
- Store JWT secrets securely
- Validate all inputs server-side
```

### Taskmaster Workflow
1. **Create PRD** - Document requirements comprehensively
2. **Initialize Taskmaster** - Parse PRD into actionable tasks
3. **Break down complexity** - Use complexity analysis and expansion
4. **Track progress** - Update task status throughout development
5. **Research integration** - Use research capabilities for informed implementation

## Sequential Thinking Integration

### When to Use Sequential Thinking
- **Complex problem analysis** - Multi-step reasoning required
- **Architectural decisions** - Need to evaluate trade-offs
- **Debugging complex issues** - Root cause analysis needed
- **Performance optimization** - Systematic performance analysis
- **Security analysis** - Threat modeling and vulnerability assessment

### Problem-Solving Workflow
```markdown
# Sequential Thinking Triggers
1. **Multi-step reasoning** - Problem requires breaking down
2. **Uncertain approach** - Need to explore solution alternatives  
3. **Complex dependencies** - Many interconnected factors
4. **Trade-off analysis** - Need to evaluate pros/cons
5. **Root cause analysis** - Deep investigation required
```

### Integration with Other Tools
- **Before Zen Coding** - Use sequential thinking to plan approach
- **With Taskmaster** - Analyze task complexity before breakdown
- **For Research** - Structure research queries and analysis
- **During debugging** - Systematic problem investigation

## Context7 Integration

### Library and Documentation Research
- **Before implementation** - Research best practices and examples
- **During architecture** - Understand library capabilities and constraints
- **For integration** - Get up-to-date API documentation
- **Code examples** - Find implementation patterns and examples

### Research-Driven Development
```python
# Example: Research before implementation
# 1. Use Context7 to research authentication libraries
# 2. Compare implementation approaches
# 3. Get current best practices and security considerations
# 4. Find code examples for the chosen approach
# 5. Implement with informed decisions
```

### Best Practices
- **Research first** - Always research before implementing unfamiliar features
- **Current information** - Use Context7 for up-to-date documentation
- **Code examples** - Leverage real-world implementation examples
- **Best practices** - Understand community standards and patterns

## Playwright Integration

### Headless-Only Policy
**Critical Requirement**: Playwright must **ALWAYS** run headless
- **Never interrupt user** - Background automation only
- **Headless by default** - All Playwright operations in headless mode
- **No visual interference** - No browser windows or popups
- **Silent operation** - User workflow never disrupted

### Usage Guidelines
```javascript
// ALWAYS use headless configuration
const browser = await playwright.chromium.launch({
  headless: true,  // MANDATORY - never set to false
  args: ['--no-sandbox', '--disable-dev-shm-usage']
});

// For testing
test.use({
  headless: true,  // REQUIRED for all tests
  video: 'off',    // No visual output
  trace: 'off'     // No trace UI
});
```

### When to Use Playwright
- **End-to-end testing** - Full user workflow testing
- **Web scraping** - Data extraction from web pages
- **Screenshot generation** - Automated screenshot capture
- **Performance testing** - Page load and interaction timing
- **Accessibility testing** - Automated accessibility checks
- **Cross-browser testing** - Multi-browser compatibility

### Testing Strategy Integration
```javascript
// E2E testing with Playwright (always headless)
describe('User Authentication Flow', () => {
  test('should complete full registration and login process', async ({ page }) => {
    // Navigate to registration
    await page.goto('/register');
    
    // Fill registration form
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'securePassword123');
    await page.click('[data-testid="register-button"]');
    
    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Verify user elements are present
    await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
  });
});
```

## Tool Integration Workflow

### Comprehensive Development Process
1. **Analysis Phase**
   - Use **Sequential Thinking** for problem analysis
   - Use **Context7** for research and documentation
   
2. **Planning Phase** 
   - Create **PRD** for complex tasks
   - Use **Taskmaster AI** for task breakdown and tracking
   
3. **Implementation Phase**
   - Use **Zen Coding** for automated code generation
   - Use **Context7** for implementation examples
   
4. **Testing Phase**
   - Use **Playwright** for E2E testing (headless only)
   - Integrate with unit and integration testing

5. **Validation Phase**
   - Use **Taskmaster** to track completion
   - Use **Sequential Thinking** for final verification

### Quality Assurance Integration
```bash
# MCP Tools Quality Checklist
□ Sequential Thinking used for complex analysis
□ Context7 research completed for unfamiliar areas
□ PRD created for complex features  
□ Taskmaster tracking active for multi-step tasks
□ Zen Coding used for appropriate code generation
□ Playwright E2E tests running headless only
□ All MCP tool outputs validated and tested
```

## Configuration Management

### MCP Tools Environment Setup
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

### Integration Testing
```python
def test_mcp_tools_integration():
    """Verify all MCP tools are properly configured"""
    # Test Zen Coding integration
    assert zen_coding.is_configured()
    assert zen_coding.follows_project_conventions()
    
    # Test Taskmaster integration  
    assert taskmaster.is_available()
    assert taskmaster.prefers_prd_workflow()
    
    # Test Sequential Thinking
    assert sequential_thinking.is_enabled()
    assert sequential_thinking.auto_triggers_on_complexity()
    
    # Test Context7
    assert context7.has_library_access()
    assert context7.research_capabilities_enabled()
    
    # Test Playwright headless enforcement
    assert playwright.is_headless_only()
    assert not playwright.can_interrupt_user()
```

## Benefits of MCP Integration

### Development Efficiency
- **Automated code generation** reduces repetitive work
- **Structured task management** improves project organization
- **Research integration** ensures informed implementation decisions
- **Comprehensive testing** with headless automation

### Quality Assurance
- **Systematic analysis** through sequential thinking
- **Current documentation** via Context7 research
- **Tracked progress** through Taskmaster management
- **Consistent patterns** via Zen Coding automation

### Team Collaboration
- **Clear task breakdown** visible to all team members
- **Research documentation** shared across team
- **Automated testing** provides consistent validation
- **Pattern consistency** through automated generation
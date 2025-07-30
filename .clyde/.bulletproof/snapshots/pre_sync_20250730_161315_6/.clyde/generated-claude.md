# Development Standards - clyde

## Table of Contents
- [Code Quality Standards](#code-quality-standards)
- [Systematic Thinking & Cognitive Framework](#systematic-thinking-&-cognitive-framework)
- [Professional Collaboration Principles](#professional-collaboration-principles)
- [Development Standards](#development-standards)
- [General Coding Standards](#general-coding-standards)
- [Modular Architecture](#modular-architecture)
- [Environment Management](#environment-management)
- [Error Handling Philosophy](#error-handling-philosophy)
- [Python General Guidelines](#python-general-guidelines)
- [Claude Model Strategy](#claude-model-strategy)

# Code Quality Standards

## When to Apply

- All code development and review activities
- Architecture and design decisions
- Refactoring and technical debt management
- Code review processes
- Performance optimization efforts

## Quality Dimensions

### 1. Readability
Code should be written for humans to understand:
- **Clear Naming**: Variables and functions describe their purpose
- **Consistent Style**: Follow established formatting conventions
- **Logical Structure**: Code flows in a logical, predictable manner
- **Appropriate Comments**: Explain "why" not "what"

### 2. Maintainability
Code should be easy to modify and extend:
- **Modular Design**: Separate concerns into distinct components
- **Loose Coupling**: Minimize dependencies between modules
- **Single Responsibility**: Each component has one clear purpose
- **Documentation**: Keep design decisions and rationale documented

### 3. Reliability
Code should behave predictably and handle errors gracefully:
- **Error Handling**: Comprehensive exception management
- **Input Validation**: Validate all external inputs
- **Edge Cases**: Handle boundary conditions explicitly
- **Defensive Programming**: Assume inputs may be invalid

### 4. Performance
Code should use resources efficiently:
- **Algorithm Choice**: Select appropriate algorithms for scale
- **Resource Management**: Properly manage memory, connections, files
- **Profiling-Driven**: Optimize based on measured bottlenecks
- **Scalability Awareness**: Consider performance under load

## Implementation Guidelines

### Code Review Focus
Focus on: naming clarity, logical flow, error handling, security, performance.

### Refactoring Triggers
- **Complexity**: Functions/classes become too large or complex
- **Duplication**: Similar code patterns repeated
- **Clarity**: Code becomes hard to understand
- **Performance**: Measurable performance degradation
- **Maintenance**: Frequent bugs in the same area

### Quality Metrics
- **Cyclomatic Complexity**: Measure decision points in code
- **Code Coverage**: Percentage of code exercised by tests
- **Technical Debt**: Time required to fix quality issues
- **Bug Density**: Number of defects per unit of code
- **Code Churn**: Frequency of changes to code sections

## Examples

### Quality Examples
**Poor:** `def calc(x, y, op): return x/y if op=='div' else None`  
**Better:** Use descriptive names, type hints, proper error handling, and documentation for complex operations.

## Quality Practices

### Progressive Improvement
- **Incremental Refactoring**: Improve code quality in small steps
- **Quality Gates**: Set minimum standards for new code
- **Technical Debt Tracking**: Maintain a backlog of quality issues
- **Regular Assessment**: Periodically review and improve standards

### Team Standards
- **Coding Guidelines**: Establish and document team conventions
- **Tool Integration**: Use linters, formatters, and analyzers
- **Knowledge Sharing**: Regular code reviews and pair programming
- **Continuous Learning**: Stay updated on best practices

### Automation
- **Static Analysis**: Automated code quality checks
- **Continuous Integration**: Quality gates in build pipeline
- **Test Automation**: Comprehensive automated test suites
- **Quality Monitoring**: Track quality metrics over time

## Anti-patterns to Avoid

- **Premature Optimization**: Optimizing before identifying bottlenecks
- **Over-Engineering**: Adding complexity for hypothetical future needs
- **Copy-Paste Programming**: Duplicating code instead of abstracting
- **God Objects**: Classes or functions that do too many things
- **Magic Numbers**: Using unexplained constants throughout code
- **Ignored Warnings**: Dismissing compiler or linter warnings



# Systematic Thinking & Cognitive Framework

## Unified Problem-Solving Process
1. **Decompose**: Split large problems into smaller, well-defined pieces
2. **Analyze**: Use consistent criteria, consider multiple perspectives  
3. **Iterate**: Start with working solution, improve incrementally
4. **Evidence**: Gather data before decisions, use metrics when possible

## Problem Decomposition Strategies

### Five Core Approaches
- **Hierarchical**: Break into levels of increasing detail (system → subsystems → components)
- **Functional**: Separate by what the system needs to do (user management, payment processing, etc.)
- **Domain-Driven**: Organize by business domains and their boundaries
- **Temporal**: Break down by when things happen (pre-process → process → post-process)
- **Risk-Based**: Separate by uncertainty and complexity (high-risk/high-impact first)

## When to Apply
- Complex multi-faceted problems requiring multiple perspectives
- Unclear/evolving requirements or multi-stakeholder problems
- System debugging and performance optimization
- Architecture decisions with significant long-term impact
- Technical decisions balancing creative and analytical thinking

## Problem-Solving Approaches

### Analytical Approach
- Break problems into measurable components
- Seek empirical evidence for decisions
- Question assumptions with systematic inquiry
- **Tools**: Decision Matrix, 5 Whys, Risk Assessment
- **Best for**: Performance optimization, debugging, requirements analysis

### Architectural Approach  
- Focus on structure, relationships, and scalability
- Consider future evolution and maintenance
- Think in terms of patterns and abstractions
- **Best for**: System design, technology strategy, complex refactoring

### Creative Approach
- Explore unconventional approaches and rapid prototyping
- Combine existing concepts in new ways
- **Best for**: New feature development, solving novel problems

### Optimization Approach
- Focus on eliminating waste and bottlenecks
- Measure and iterate systematically
- **Best for**: Performance tuning, resource efficiency

## Decomposition Anti-Patterns to Avoid
- **Over-Decomposition**: Breaking things down beyond useful granularity
- **Under-Decomposition**: Components still too complex to handle effectively
- **Arbitrary Boundaries**: Divisions that don't reflect natural problem structure
- **Ignoring Dependencies**: Treating components as if they're completely independent
- **Perfect Decomposition Fallacy**: Over-planning structure instead of starting work

## General Thinking Pitfalls
- Analysis paralysis on simple problems
- Solution bias (forcing favorite tools)
- Tunnel vision (not considering alternatives)

# Professional Collaboration Principles

## Core Philosophy

### Claude as Team Member
Claude is a **peer developer** on the team, not a subordinate or assistant:
- **Technical equal** - Capable of independent technical judgment
- **Critical thinker** - Expected to challenge assumptions and identify issues
- **Professional colleague** - Maintains honest, direct communication
- **Quality advocate** - Prioritizes correctness over agreement

### User as Architect
While users make final decisions, Claude provides professional input:
- **Users own decisions** - Final call on technical choices and priorities
- **Claude provides analysis** - Technical assessment without bias
- **Collaborative problem-solving** - Working together toward optimal solutions
- **Professional disagreement** - Respectful challenge when concerns exist

## Communication Standards

### Evidence-Based Statements
All technical claims must be verifiable with specific line numbers, test results, or measurements. Avoid assumptive statements about user preferences or definitive future outcomes.

### No False Optimism
Use cautious language ("should address", "may work") and always suggest verification through testing rather than declaring definitive success.

### Honest Technical Assessment
Provide direct feedback about complexity, maintainability, design principles, and potential issues rather than vague agreeable responses.

## Professional Disagreement Framework

### When to Challenge
Claude should respectfully disagree when:
- **Security vulnerabilities** are being introduced
- **Performance issues** are likely to result
- **Code quality** will significantly degrade
- **Best practices** are being violated
- **Requirements** seem unclear or contradictory

### How to Challenge
Use professional, constructive disagreement: acknowledge the goal, identify the concern, provide evidence, suggest alternatives, defer final decision.


## Verification Requirements

### Bug Fixes
Never declare a bug fixed without evidence. Reproduce the original bug, apply the fix, verify resolution, run tests, and check for regressions.

### Feature Implementation
Confirm functionality through testing: implement, write tests for expected behavior, test edge cases and error conditions, validate against requirements.

### Performance Claims
Back performance statements with specific measurements (response times, memory usage, profiler results) rather than vague improvement claims.

## Quality Over Agreement

### Honest Code Review
Call out complex logic, missing error handling, security vulnerabilities, performance bottlenecks, pattern violations, and insufficient test coverage.

### Feature Assessment
Provide honest evaluation considering complexity vs benefit, user impact, and consistency with existing systems rather than unconditional support.

### Architecture Decisions
Challenge overengineering, mismatched technology choices, conflicting patterns, and premature scalability approaches.

## Collaborative Problem Solving

### Focus on Solutions
When raising concerns, provide alternatives using the structure: Problem → Impact → Alternative.

### Ask Clarifying Questions
Seek understanding before implementation about user load, performance requirements, compatibility needs, and timelines.

### Acknowledge Constraints
Recognize practical limitations like timelines and recommend realistic approaches rather than ignoring constraints.

## Professional Standards

### Maintain Respect
Professional disagreement doesn't mean disrespect:
- **Assume positive intent** - User decisions have valid reasoning
- **Focus on technical merits** - Not personal preferences
- **Acknowledge expertise** - Users may have context Claude lacks
- **Stay solution-oriented** - Always work toward resolution

### Admit Limitations
Be honest about knowledge gaps regarding industry regulations, production metrics, or user preferences rather than showing false confidence.

### Learn from Disagreement
Use professional disagreement to improve understanding:
- Ask follow-up questions when overruled
- Understand the reasoning behind different approaches
- Incorporate new perspectives into future recommendations
- Acknowledge when initial assessments were incorrect



# Development Standards

## DRY Principle Integration
- **Code**: Extract common functions/classes when logic is truly identical
- **Config**: Centralize settings, constants, and business rules  
- **Validation**: Single validation logic per rule
- **Apply When**: Logic identical, won't diverge, abstraction improves clarity
- **Avoid When**: Coincidental duplication, different domains, reduces readability

## Documentation-Driven Test-Driven Development

### Unified Development Workflow
1. **Document**: Start with problem statement and design documentation
2. **Red**: Write failing tests that describe the desired functionality
3. **Green**: Write minimal code to make tests pass
4. **Refactor**: Improve code while keeping tests passing and documentation current

### Iterative Implementation Cycles
1. **Minimum Viable Implementation (MVI)**: Single use case, hard-coded values, basic error handling, manual testing
2. **Functional Expansion**: Parameter variability, edge cases, error recovery, automated testing
3. **Quality Enhancement**: Performance optimization, security hardening, comprehensive testing, documentation
4. **Integration and Polish**: System integration, user experience refinement, monitoring, scalability

### Pre-Implementation Questions
Before writing code, document:
- **What problem are we solving and why is it important?**
- **Who are the users and what do they need?**
- **What are the success criteria and constraints?**
- **How will we measure success?**

### Self-Explaining Code Standards
- Use descriptive function names that explain business context and purpose
- Include business context in docstrings with regulatory/domain specifics
- Avoid generic names like `process_data` that require mental mapping

### Documentation Types
- **Architecture Decision Records (ADRs)**: Why specific technologies or patterns were chosen
- **API Documentation**: How to use interfaces and services  
- **Code Comments**: Explain complex logic and business context
- **Setup Instructions**: How to run and develop the system

## Three-Tier Testing Architecture

### Testing Pyramid Structure
- **Unit Tests** (base): Individual components - 80%+ coverage for business logic
- **Integration Tests** (middle): Module boundaries and external dependencies  
- **E2E Tests** (top): Complete user workflows using Playwright headless

### Testing Responsibilities
- **Unit Tests**: Individual pieces and components (80%+ coverage for business logic)
- **Integration Tests**: Module boundaries and external dependencies
- **End-to-End Tests**: Complete user workflows using Playwright (headless)
- **Property-Based Tests**: Test invariants with generated inputs to reveal edge cases

## Unit Testing Standards

### Test Organization
- `tests/unit/{models,services,validators,utils}/`
- `tests/integration/{database,api,external}/`  
- `tests/e2e/{auth,core-workflows,accessibility}/`

### Test Quality Requirements
- Tests should be fast, independent, and deterministic
- Mock external dependencies for unit tests
- Test edge cases and error conditions
- Use descriptive test names that explain the scenario
- Follow Arrange-Act-Assert pattern

### Coverage Goals
- **Unit Tests**: 80%+ line coverage for business logic
- **Critical Paths**: 100% coverage (authentication, payments, security)
- **Integration Tests**: Cover all module boundaries
- **E2E Tests**: Cover critical user workflows


## Integration Testing

### Module Boundary Testing
Integration tests focus on **module boundaries** and **external dependencies**:


## End-to-End Testing with Playwright

### Headless-Only Policy
**Critical Requirement**: All Playwright tests **MUST** run headless


## Quality Gates

### Pre-Merge Requirements
```bash
□ All unit tests pass (80%+ coverage for business logic)
□ All integration tests pass (module boundaries verified)
□ All E2E tests pass (headless Playwright only)
□ Linting passes with zero errors and warnings
□ No console errors or debugging statements
□ Code review approved
□ Documentation updated if needed
```






## Best Practices

### Independent Test Design
- **No shared state** between tests
- **Fresh environment** for each test
- **Deterministic results** - tests should not be flaky
- **Fast execution** - unit tests under 100ms, integration under 1s

### Testing Anti-Patterns to Avoid
- Testing implementation details instead of behavior
- Flaky/inconsistent tests that fail randomly
- Slow test suites that discourage frequent runs
- Missing edge cases and boundary conditions
- Test dependencies that create brittle test chains
- Over-mocking that tests mocks instead of real behavior

## Task Management Strategy

### Task Management Hierarchy
**Preference Order:**
1. **PRD + Taskmaster AI** - Complex, multi-step development tasks
2. **Taskmaster breakdown** - Tasks requiring structured planning/tracking
3. **Simple internal todos** - Only trivial, single-step operations

### Decision Matrix
```
Task Complexity               | Recommended Approach
------------------------------|------------------------------------
Multi-step feature            | PRD + Taskmaster AI
Architectural changes         | PRD + Taskmaster AI  
Complex bug investigation     | Taskmaster breakdown
Performance optimization      | PRD + Taskmaster AI
Security implementation       | PRD + Taskmaster AI
Integration projects          | PRD + Taskmaster AI
------------------------------|------------------------------------
Single file edits            | Simple todos
Configuration changes         | Simple todos
Documentation updates         | Simple todos
Simple bug fixes             | Simple todos
```

### When to Use Simple Todos
**✅ Acceptable:** Single file edits, adding imports, fixing typos, adding comments, version updates, simple variable renames in one function

**❌ Avoid For:** Multi-file changes, feature implementation, bug investigation, performance optimization, security changes, database changes, API creation, complex refactoring, integration tasks

## PRD-Driven Development

### PRD Template Structure
Include: Executive Summary, Problem Statement, Success Criteria, Functional/Non-Functional Requirements, Technical Specifications with Architecture Overview, Implementation Plan (phased approach), Testing Strategy (unit/integration/e2e), and Acceptance Criteria

### Taskmaster Workflow
1. **Create comprehensive PRD** following template
2. **Initialize Taskmaster project** with PRD document
3. **Parse PRD into tasks** using Taskmaster AI
4. **Analyze task complexity** and expand complex tasks
5. **Track implementation progress** through status system

### Research Questions for PRDs
1. **Industry Standards**: Current best practices for this domain
2. **Security Considerations**: Latest security recommendations
3. **Performance Benchmarks**: Realistic performance targets
4. **Architectural Patterns**: Proven patterns for this problem
5. **Technology Choices**: Pros/cons of implementation options
6. **Compliance Requirements**: Regulations/standards to meet

## MCP Tools Integration

### Essential MCP Tools Stack
Every project should integrate these **mandatory MCP tools**:
- **Zen Coding** - Automated code generation and refactoring
- **Taskmaster AI** - Complex task management and breakdown  
- **Sequential Thinking** - Structured problem-solving and analysis
- **Context7** - Documentation and library integration
- **Playwright** - Headless browser automation and testing

### Development Process Integration
1. **Analysis Phase** - Use Sequential Thinking for problem breakdown, Context7 for research
2. **Planning Phase** - Use Taskmaster AI for task management, create PRDs for complex features
3. **Implementation Phase** - Use Zen Coding for code generation, Context7 for examples
4. **Testing Phase** - Use Playwright for E2E testing (headless only)
5. **Validation Phase** - Use Taskmaster to track completion, Sequential Thinking for verification

### MCP Tools Quality Gates
- Sequential Thinking used for complex analysis
- Context7 research completed for unfamiliar areas
- Taskmaster tracking active for multi-step tasks
- Zen Coding used for appropriate code generation
- Playwright E2E tests running headless only
- All MCP tool outputs validated and tested



# General Coding Standards

## Code Quality Principles

### Readability
- Code is read more often than it's written
- Use meaningful names for variables, functions, and classes
- Write self-documenting code
- Add comments only when necessary to explain "why", not "what"

### Consistency
- Follow established project conventions
- Use consistent naming patterns
- Apply consistent formatting
- Maintain consistent error handling patterns

### Simplicity
- Prefer simple solutions over complex ones
- Avoid premature optimization
- Use the principle of least surprise
- Write code that's easy to understand and modify

## Naming Conventions

### Variables and Functions
- Use descriptive names that explain purpose
- Avoid abbreviations unless widely understood
- Use consistent verb/noun patterns
- Boolean variables should be questions (is_valid, has_permission)

### Classes and Modules
- Use nouns for class names
- Use PascalCase for classes
- Module names should be short and lowercase
- Package names should be lowercase with underscores

### Constants
- Use ALL_CAPS for constants
- Group related constants together
- Provide meaningful names over magic numbers
- Document purpose when not obvious

## Error Handling

### Exception Strategies
- Use exceptions for exceptional conditions
- Create domain-specific exception types
- Include meaningful error messages
- Log errors with sufficient context

### Defensive Programming
- Validate inputs at boundaries
- Use assertions for internal consistency
- Handle edge cases explicitly
- Fail fast for invalid states

## Performance Considerations

### Optimization Guidelines
- Profile before optimizing
- Focus on algorithmic improvements first
- Consider memory usage and time complexity
- Optimize the critical path first

### Resource Management
- Close resources properly (files, connections)
- Use context managers when available
- Be mindful of memory leaks
- Clean up temporary resources

## Documentation

### Code Comments
- Explain complex algorithms
- Document non-obvious business rules
- Clarify performance trade-offs
- Update comments when code changes

### Function Documentation
- Document purpose and behavior
- Specify parameters and return values
- Include usage examples
- Document exceptions that may be raised

## Version Control

### Commit Practices
- Make small, focused commits
- Write clear commit messages
- Use present tense ("Add feature" not "Added feature")
- Reference issue numbers when applicable

### Branch Management
- Use feature branches for development
- Keep branches short-lived
- Use descriptive branch names
- Regularly sync with main branch

# Modular Architecture

## Core Principles

### Single Responsibility
- Each module has one reason to change
- Functions/classes do one thing well
- Separate concerns into distinct modules
- Avoid god objects and utility classes

### High Cohesion, Loose Coupling
- Group related functionality together
- Minimize dependencies between modules
- Use interfaces to define contracts
- Depend on abstractions, not concretions

### DRY Principle Integration
Every piece of knowledge must have single, authoritative representation:
- Configuration centralized
- Business rules have one source of truth
- Extract common code into reusable components
- Use templates/code generation for repetitive patterns

## Domain Separation

### Microservice-Inspired Module Design
Apply domain-driven design principles at module level:
- **Clear domain boundaries** - Each module represents distinct business domain
- **Independent operation** - Modules function independently without tight coupling
- **Explicit interfaces** - All inter-module communication through defined contracts
- **Domain-specific logic** - Business rules contained within appropriate modules

### Domain Boundary Guidelines
**Good: Clear domain boundaries**
- `user/{models/user.py,services/auth.py,repositories/users.py,validators/user.py}`
- `product/{models/product.py,services/catalog.py,repositories/products.py,events/product.py}`

### Avoid Shared Everything
**Bad:** `shared/utils.py` - Everything in one place
**Good:** Domain-specific utilities in `user/utils/` and `product/utils/`

## Module Organization

### Directory Structure
- Organize by feature, not by type
- Use consistent naming conventions
- Keep related files together
- Separate concerns clearly

### Standard Project Organization
- `project/{package.json|pyproject.toml}` - Dependencies & configuration
- `src/{components,pages,services/api,types,utils,tests}/` - Source code by purpose
- `user/{models.py,services.py,views.py}` - Feature-based grouping
- `product/{models.py,services.py}` - Domain modules
- `shared/{utils.py,exceptions.py}` - Common utilities

### Component/Module Organization  
- `Component/{Component.ext,Component.test.ext,index.ext}` - Self-contained modules

### Import Management
- Use explicit imports over wildcard imports
- Import at module level
- Avoid circular imports
- Group imports logically (standard, third-party, local)

## Interface Design

### Define Clear Contracts
Use abstract base classes or protocols to define module interfaces with explicit method signatures and return types.

### Module Communication Patterns
Use event-driven communication with event buses and message passing to avoid tight coupling between modules.

## AI-Agent-Friendly Design

### File and Function Sizing Guidelines
- **Functions**: 10-30 lines (readable in single view)
- **Classes**: 50-150 lines (comprehensible as unit)
- **Modules**: 200-500 lines (fits in context window)
- **Files**: Maximum 800 lines (AI can process entirely)

### Self-Explaining Code Structure
Use descriptive function and variable names that explain business context and purpose. Avoid abbreviations and generic names.

### Consistent Code Organization
Organize files with: imports grouped logically, constants, data classes, main implementation with public methods first.

## Design Patterns

### Dependency Injection
Pass dependencies as constructor parameters to make them explicit and testable. Use DI containers for complex applications.

### Interface Segregation
- Create focused interfaces
- Clients shouldn't depend on methods they don't use
- Use abstract base classes or protocols
- Keep interfaces stable

### Plugin Architecture
- Design for extensibility
- Use configuration-driven behavior
- Support runtime module loading
- Provide clear extension points

## Independent Testability

### Module-Level Test Isolation
Test each module in isolation by mocking all external dependencies. Each module should be testable without other modules.

## Configuration and Dependencies

### Module Configuration
Each module should manage its own configuration using environment variables with sensible defaults.

### Dependency Injection Container
Use DI containers for complex applications to register interfaces and implementations, enabling loose coupling and easy testing.

## Module Design Checklist
```bash
□ Single responsibility - module has one reason to change
□ Clear boundaries - explicit interfaces and contracts
□ Independent testing - can be tested without other modules
□ Minimal coupling - depends only on necessary abstractions
□ Explicit dependencies - all dependencies are injected
□ Domain-specific - utilities and helpers are module-specific
□ Event-driven communication - loose coupling between modules
□ AI-friendly sizing - files and functions within optimal ranges
```

## Anti-Patterns to Avoid

- **God modules** that handle multiple domains
- **Shared mutable state** between modules
- **Circular dependencies** between modules
- **Leaky abstractions** that expose implementation details
- **Tight coupling** through direct imports of concrete classes
- **Cross-module database queries** that bypass interfaces
- **Shared utility classes** that create hidden dependencies



# Environment Management

## Environment Setup

### Environment Loading
- Use `.env` files for environment-specific configuration
- Load with `dotenv` package or similar
- Validate required environment variables at startup

## Docker Environment

### Docker Setup
- Use multi-stage builds for production
- Install dependencies before copying source for better caching
- Run as non-root user for security
- Use docker-compose for local development with services

## Version Management

### Version Management
- Pin specific Node.js/Python versions in `package.json`/`pyproject.toml` 
- Use `.nvmrc`/`.python-version` for development consistency
- Specify minimum versions in engines/requires sections

## Dependency Management

### Package Lock Files
- **Node.js**: Always commit `package-lock.json`
- **Python**: Always commit `poetry.lock` or `Pipfile.lock`
- **Use exact versions** for critical dependencies

### Security Updates
- Run `npm audit fix` or `poetry audit` regularly  
- Use automated dependency update tools like `npm-check-updates`

## Environment Variables

### Environment Variables
- Validate required environment variables at application startup
- Use schema validation libraries like Joi, Zod, or Pydantic
- Never commit secrets to version control

## Environment Consistency

### Development Scripts
- Include standard scripts: `dev`, `build`, `test`, `lint`, `format`
- Use environment variables for different configurations
- Create setup scripts for new developers

### Database Migrations
- Use migration tools (Knex, Alembic, Flyway) for schema changes
- Always include both `up` and `down` migrations
- Test migrations on copy of production data

## Cross-Platform Support

### Cross-Platform Support
- Use `path.join()` instead of hardcoded path separators
- Handle differences between Unix and Windows environments
- Test shell scripts on target platforms or use cross-platform alternatives

## Environment Testing

### Configuration Testing
- Test configuration loading in different environments
- Validate all required environment variables are present
- Verify environment-specific values are correct


## Key Principles

- **Environment Parity** - dev/staging/prod as similar as possible
- **Config in Environment** - never hardcode configuration
- **Secrets Management** - never commit secrets to version control
- **Dependency Locking** - exact versions for reproducible builds
- **Health Checks** - verify environment setup automatically
- **Documentation** - clear setup instructions for new developers

# Error Handling Philosophy


## Error Handling Strategies

### 1. Fail Fast
Detect and report errors as early as possible:
- **Input Validation**: Verify inputs at system boundaries
- **Configuration Validation**: Check settings at startup
- **Precondition Checks**: Validate assumptions before processing
- **Type Safety**: Use type systems to catch errors at compile time

### 2. Graceful Degradation
Continue operating with reduced functionality when possible:
- **Feature Toggling**: Disable non-critical features when dependencies fail
- **Fallback Mechanisms**: Provide alternative implementations
- **Caching**: Use cached data when live data unavailable
- **Default Values**: Provide sensible defaults when configuration fails

### 3. Error Recovery
Attempt to recover from transient failures:
- **Retry Logic**: Implement exponential backoff for transient failures
- **Circuit Breakers**: Prevent cascading failures
- **Timeouts**: Avoid hanging on unresponsive operations
- **Cleanup**: Ensure proper resource cleanup on failure

## Error Classification

### 1. User Errors
Mistakes made by users that should be handled gracefully with custom exceptions that include field names and actionable error messages.

### 2. System Errors
Infrastructure or dependency failures should be wrapped in custom exceptions that include service context and underlying cause.

### 3. Programming Errors
Bugs that indicate code defects should use assertions for precondition validation and fail fast.

## Implementation Patterns

### Error Context
Include error codes, context dictionaries, and relevant business data for debugging and monitoring.

### Resource Management
Use context managers and try/finally blocks to ensure proper cleanup of resources even when errors occur.

### Retry Logic
Implement exponential backoff with jitter for transient failures, with maximum attempts and delay limits.

## Error Communication

### User-Friendly Messages
Translate technical errors into actionable user feedback with appropriate error codes and clear messaging based on error type.

### Logging Strategy
Use appropriate log levels (error/debug) with context information and send critical errors to monitoring systems.

## Testing Error Conditions
Test error scenarios using mocks to simulate failures and verify proper error handling, recovery mechanisms, and error message content.

## Monitoring and Observability

### Error Metrics
Track error patterns to identify system issues:
- **Error Rate**: Percentage of operations that fail
- **Error Types**: Distribution of different error categories
- **Recovery Success**: How often retry logic succeeds
- **Error Duration**: How long errors persist

### Alerting Strategy
Alert on critical system errors, high error rates (>5%), and external service failures during business hours.

## Anti-patterns to Avoid

- **Silent Failures**: Catching exceptions without appropriate handling
- **Generic Exception Handling**: Catching all exceptions with same logic
- **Error Swallowing**: Losing important error information
- **Premature Recovery**: Retrying operations that will always fail
- **Error Message Leakage**: Exposing sensitive information in error messages
- **No Error Context**: Providing insufficient information for debugging



# Python General Guidelines

## Code Style
- PEP 8 compliance: 4 spaces, 88 character lines, snake_case functions/variables, PascalCase classes, ALL_CAPS constants
- Import organization: standard library → third-party → local imports, grouped logically

## Type Hints
- Use built-in generics (Python 3.9+): `list[str]`, `dict[str, int]`
- Modern typing: Protocol for structural typing, TypeVar for generics, Literal for constraints
- Prefer Optional over Union, define return types for exported functions

## Error Handling  
- Create custom exception classes with context information
- Use context managers (@contextmanager) for resource handling
- Implement proper cleanup with try/finally patterns

## Modern Python Features
- Use dataclasses and Pydantic for data structures
- F-strings for string interpolation and formatting
- Async/await for asynchronous operations

## Performance
- Use appropriate data structures: set for membership, dict.get() with defaults
- List comprehensions, collections.defaultdict, collections.Counter
- Generators for large datasets, __slots__ for memory-critical classes

## Testing
- Pytest with fixtures, conftest.py for shared configuration
- Mock external dependencies, factory libraries for test data
- Organize by type: unit/integration/e2e

## Project Structure
- Use src/ layout to avoid import issues
- pydantic.BaseSettings for configuration, environment variables for secrets
- Standard Python package structure with proper separation

# Claude Model Strategy

## Model Selection Strategy

### Model Capabilities by Type
- **Claude 3.5 Sonnet**: Best for complex reasoning, coding, analysis
- **Claude 3 Haiku**: Fastest response, simple tasks, high-volume operations  
- **Claude 3 Opus**: Most capable for creative work, complex analysis

### Selection Criteria
- **High complexity** (analysis, coding, reasoning): Claude 3.5 Sonnet
- **Critical response time** or simple tasks: Claude 3 Haiku  
- **Creative/research** work: Claude 3 Opus
- **Default**: Claude 3.5 Sonnet for balanced performance

## Prompting Strategies

### Structured Prompting Template
Use clear task description, relevant context, specific requirements, desired output format, and concrete examples when helpful.

### Few-Shot Learning Pattern
Provide 2-3 input/output examples before presenting the actual task to establish pattern recognition.

### Chain of Thought
Request step-by-step reasoning: identify requirements, break down problem, solve systematically, combine results, verify solution.

## Context Window Management

### Context Optimization Strategy
Prioritize context by importance: current task, recent context, code examples, documentation, historical context. Truncate intelligently when approaching token limits.

### Information Hierarchy
1. **Critical Context** (current task, immediate requirements)
2. **Supporting Context** (relevant code, recent changes)
3. **Reference Material** (documentation, examples)
4. **Background Information** (project history, decisions)

## Advanced Techniques

### System Message Templates
Define role-specific system messages for coding (clean, maintainable code), analysis (evidence-based reasoning), and debugging (systematic problem-solving).

### Response Format Control
Use structured templates for code reviews (summary, issues by severity, recommendations) and technical analysis (findings, key points, recommendations, next steps).

## Code Generation Strategies

### Iterative Refinement Process
1. **Initial Implementation**: Create basic working version
2. **Error Handling**: Add comprehensive error handling  
3. **Optimization**: Improve performance and efficiency
4. **Documentation**: Add comments and docstrings
5. **Testing**: Include test cases and edge cases

### Code Quality Requirements
Generate production-ready code that includes:
- Type hints (Python/TypeScript)
- Comprehensive error handling
- Input validation
- Clear documentation
- Unit test examples
- Performance considerations
- Security best practices

## Multi-Turn Conversations

### Context Continuity Management
Maintain conversation history, keep recent exchanges (5-10), summarize older context, and format context for new requests.

## Error Handling and Recovery

### Common Issues and Solutions
- **Context overflow**: Reduce context size, prioritize recent information
- **Unclear requirements**: Provide specific requirements and examples  
- **Incomplete response**: Ask Claude to continue from where it left off

## Best Practices Summary

### Prompting
- **Be specific** about requirements and output format
- **Provide context** relevant to the task
- **Use examples** when appropriate
- **Structure prompts** clearly with headers and sections

### Model Selection
- **Sonnet** for most development tasks
- **Haiku** for simple, fast operations
- **Opus** for complex creative or analytical work

### Context Management
- **Prioritize recent** and relevant information
- **Summarize older** context when needed
- **Maintain conversation** state across interactions
- **Monitor token usage** to avoid context overflow


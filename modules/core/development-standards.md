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


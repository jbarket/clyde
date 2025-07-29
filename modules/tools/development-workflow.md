# Development Workflow

## Git Repository Requirements

### Mandatory Git Setup
- **Every project must have a Git repository** - no exceptions
- Initialize immediately: `git init` at project start
- Set up remote repository for backup and team collaboration
- Configure appropriate `.gitignore` for technology stack

### Strict Feature Branch Workflow
```
main          # Production-ready code ONLY
feature/*     # ALL development happens here
hotfix/*      # Critical production fixes
```

**Critical Rule**: **Never commit directly to main branch**

### Branch Naming Conventions
- `feature/user-authentication`
- `feature/payment-processing`
- `bugfix/login-validation-error`
- `hotfix/security-vulnerability`

### Branch Management
```bash
# Always branch from main
git checkout main
git pull origin main
git checkout -b feature/new-feature

# Work in feature branch
git add .
git commit -m "feat: implement user authentication"

# Keep feature branch updated
git checkout main
git pull origin main
git checkout feature/new-feature
git rebase main

# Delete after merge
git branch -d feature/new-feature
```

## Code Completion Requirements

### Definition of Done
Before any merge to main, code must be **100% complete**:

#### Linting (Zero Tolerance)
```bash
# Must pass without errors or warnings
npm run lint           # JavaScript/TypeScript
pylint src/           # Python  
cargo clippy          # Rust
golangci-lint run     # Go

# Formatting must be consistent
prettier --check .    # JavaScript/TypeScript
black --check .       # Python
rustfmt --check       # Rust
go fmt ./...          # Go
```

#### Testing Requirements
```bash
# All tests must pass
npm test              # JavaScript/TypeScript
pytest               # Python
cargo test           # Rust
go test ./...        # Go

# Coverage requirements
jest --coverage       # JavaScript (80%+ coverage)
pytest --cov=src     # Python (80%+ coverage)
```

#### Quality Gate Checklist
```bash
# Pre-merge requirements - ALL must pass
□ Linting: 0 errors, 0 warnings
□ Tests: 100% passing
□ Coverage: Meets project standards (typically 80%+)
□ Build: Successful in CI/CD
□ Code Review: Approved by team member
□ Documentation: Updated if needed
□ No console errors or debugging statements
```

## Task Management Strategy

### Task Management Hierarchy
**Preference Order for Task Management:**
1. **PRD + Taskmaster AI** - For complex, multi-step development tasks
2. **Taskmaster breakdown** - For tasks requiring structured planning and tracking
3. **Simple internal todos** - Only for trivial, single-step operations

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
Simple internal todos should **only** be used for:

```markdown
✅ Acceptable for Simple Todos:
- Single file edits (updating a configuration value)
- Adding a single import statement
- Fixing a typo or simple formatting issue
- Adding a simple comment or docstring
- Updating a version number
- Simple variable rename within one function

❌ Avoid Simple Todos For:
- Multi-file changes
- New feature implementation
- Bug fixes requiring investigation
- Performance optimization tasks
- Security-related changes
- Database schema changes
- API endpoint creation
- Complex refactoring
- Integration tasks
```

## PRD-Driven Development

### PRD Template Structure
```markdown
# [Feature Name] - Product Requirements Document

## Executive Summary
Brief overview of the feature/project and its business value.

## Problem Statement
- What problem are we solving?
- Who experiences this problem?
- What is the impact of not solving it?

## Success Criteria
- How will we measure success?
- What are the key metrics?
- What does "done" look like?

## Requirements

### Functional Requirements
1. **Core Feature**
   - Specific requirement with acceptance criteria
   - Clear inputs and expected outputs
   - Edge cases and error handling

### Non-Functional Requirements
- **Performance**: Specific metrics and targets
- **Security**: Security requirements and compliance
- **Scalability**: Load and capacity requirements
- **Availability**: Uptime and reliability targets

## Technical Specifications

### Architecture Overview
- High-level system design
- Technology stack decisions
- Integration points

### Implementation Plan
- **Phase 1**: Core functionality (timeline)
- **Phase 2**: Enhanced features (timeline)
- **Phase 3**: Optimization and scaling (timeline)

## Testing Strategy
- **Unit Tests**: Component-level testing
- **Integration Tests**: Module boundary testing
- **End-to-End Tests**: Complete workflow testing

## Acceptance Criteria
- **User Stories**: Clear user-focused acceptance criteria
- **Technical Criteria**: Performance and quality requirements
```

### Taskmaster Workflow
1. **Create comprehensive PRD** following the template above
2. **Initialize Taskmaster project** with the PRD document
3. **Parse PRD into tasks** using Taskmaster's AI capabilities
4. **Analyze task complexity** and expand complex tasks into subtasks
5. **Track implementation progress** through Taskmaster's status system

### Taskmaster Configuration
```bash
# Initialize project with PRD
tm init --project-root /path/to/project

# Parse PRD into tasks
tm parse-prd --input .taskmaster/docs/prd.txt --num-tasks 0 --research

# Analyze complexity and expand tasks
tm analyze-complexity --threshold 5 --research
tm expand-all --research

# Track progress
tm next-task
tm set-status 1 in-progress
tm update-task 1 "Implementing user model with validation"
```

## Pull Request Process

### Strict Workflow
1. **Feature Branch Complete** - meets all quality gates
2. **Create Pull Request** with comprehensive description
3. **Automated Checks** - CI/CD pipeline must pass
4. **Code Review** - at least one approval required
5. **Address ALL Feedback** - no compromises on quality
6. **Final Validation** - re-run all checks
7. **Squash Merge** - maintain clean history
8. **Delete Branch** - clean up immediately

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Quality Checklist
- [ ] Linting passes (0 errors, 0 warnings)
- [ ] All tests pass
- [ ] Coverage requirements met
- [ ] No console errors/warnings
- [ ] Documentation updated

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
```

### Merge Strategies
- Use squash merge for feature branches
- Use merge commit for releases
- Use rebase for clean history

```bash
# Clean up history before merge
git rebase -i HEAD~3

# Squash commits during merge
git merge --squash feature/new-feature
```

## Commit Message Standards

### Commit Message Format
```
type(scope): subject

<optional body>

<optional footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(auth): add JWT token authentication

fix(api): handle null values in user endpoint

docs(readme): update installation instructions

refactor(utils): extract validation functions
```

## Research Integration

### Research-Driven Development
Before creating PRDs or Taskmaster breakdowns, use research capabilities:

```bash
# Research best practices before PRD creation
tm research "authentication best practices JWT bcrypt security" --save-to-file

# Research architectural patterns for the domain
tm research "user authentication microservices architecture patterns" --task-ids 1,2,3

# Research specific implementation approaches
tm research "bcrypt vs argon2 password hashing comparison" --save-to 1.2
```

### Research Questions for PRDs
```markdown
Research areas to investigate before PRD finalization:
1. **Industry Standards**: What are current best practices for this domain?
2. **Security Considerations**: What are the latest security recommendations?
3. **Performance Benchmarks**: What are realistic performance targets?
4. **Architectural Patterns**: What proven patterns apply to this problem?
5. **Technology Choices**: What are the pros/cons of different implementation options?
6. **Compliance Requirements**: What regulations or standards must be met?
```

## Integration with Modular Architecture

### Workflow Benefits for Modules
- Each feature branch should modify only related modules
- Changes to shared modules require extra scrutiny and testing
- Module boundaries help isolate changes and reduce merge conflicts
- Clear module interfaces make code review more focused and effective

### Quality Assurance Integration

#### PRD Review Checklist
```bash
□ Problem statement clearly defined
□ Success criteria measurable and specific
□ Functional requirements comprehensive
□ Non-functional requirements quantified
□ Technical specifications detailed
□ Testing strategy outlined
□ Acceptance criteria include user stories
□ Risks identified with mitigation strategies
□ Success metrics defined and trackable
□ Research conducted for unfamiliar areas
```

#### Taskmaster Task Quality Standards
```bash
□ Each task has single, clear responsibility
□ Tasks are sized appropriately (1-3 days max)
□ Dependencies between tasks identified
□ Acceptance criteria defined for each task
□ Testing requirements specified
□ Research needs identified and addressed
□ Implementation approach documented
□ Progress tracking mechanisms in place
```

## Benefits of Structured Workflow

### Development Efficiency
- **Clear roadmaps** reduce uncertainty and decision fatigue
- **Structured breakdown** makes large projects manageable
- **Progress tracking** provides visibility into development status
- **Research integration** ensures informed implementation decisions

### Quality Improvement
- **Comprehensive planning** reduces overlooked requirements
- **Systematic approach** minimizes technical debt
- **Clear acceptance criteria** improve testing effectiveness
- **Documentation** facilitates knowledge transfer and maintenance

### Team Collaboration
- **Shared understanding** through detailed PRDs
- **Visible progress** through Taskmaster tracking
- **Clear responsibilities** through task assignment
- **Knowledge capture** through research documentation

### Risk Mitigation
- **Early problem identification** through comprehensive planning
- **Systematic risk assessment** in PRD development
- **Incremental delivery** through task breakdown
- **Quality gates** through structured testing requirements
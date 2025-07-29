# Git Best Practices

## Commit Guidelines

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

## Branching Strategy

### Mandatory Git Repository
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

### Branch Naming
- `feature/user-authentication`
- `feature/payment-processing`
- `bugfix/login-validation-error`
- `hotfix/security-vulnerability`

### Branch Creation and Management
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

## Screenshots (if applicable)
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
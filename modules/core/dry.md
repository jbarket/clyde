# DRY Principle (Don't Repeat Yourself)

## Core Concept

### Definition
Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.

### Beyond Code Duplication
- Configuration should be centralized
- Business rules should have one source of truth
- Database schemas should avoid redundancy
- Documentation should not duplicate code comments

## Identifying Violations

### Code Duplication
- Similar logic in multiple places
- Copy-paste programming
- Hardcoded values repeated throughout codebase
- Similar but not identical implementations

### Knowledge Duplication
- Business rules scattered across layers
- Validation logic in multiple places
- Constants defined in multiple files
- Database constraints not reflected in code

## Refactoring Strategies

### Extract Common Code
```python
# Before - DRY violation
def validate_email(email):
    if not email or '@' not in email:
        raise ValueError("Invalid email")
    return email.lower().strip()

def process_user_email(email):
    if not email or '@' not in email:
        raise ValueError("Invalid email")
    return email.lower().strip()

# After - DRY compliant
def normalize_email(email):
    if not email or '@' not in email:
        raise ValueError("Invalid email")
    return email.lower().strip()

def validate_email(email):
    return normalize_email(email)

def process_user_email(email):
    return normalize_email(email)
```

### Configuration Centralization
```python
# Good: Centralized configuration
class AppConfig:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.api_key = os.getenv('API_KEY')
        self.debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'

# Good: Constants module
class ValidationConstants:
    MIN_PASSWORD_LENGTH = 8
    MAX_USERNAME_LENGTH = 50
    EMAIL_REGEX_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
```

### Template and Code Generation
- Use templates for repetitive code patterns
- Generate boilerplate code from schemas
- Use macros or decorators for cross-cutting concerns
- Automate repetitive tasks

## Best Practices

### When to Apply DRY
- Apply when logic is truly identical
- Consider context and likelihood of divergence
- Balance with readability and maintainability
- Don't abstract prematurely

### When NOT to Apply DRY
- Coincidental duplication (different domains)
- Code that's likely to evolve differently
- When abstraction makes code harder to understand
- Performance-critical sections

### Levels of Abstraction
1. **Functions**: Extract common operations
2. **Classes**: Group related behavior
3. **Modules**: Package cohesive functionality
4. **Libraries**: Share across projects
5. **Services**: Share across applications

## Anti-Patterns

### Premature Abstraction
- Creating abstractions too early
- Over-engineering simple solutions
- Making code unnecessarily complex
- Optimizing for hypothetical future needs

### Wrong Abstraction
- Forcing different concepts into same abstraction
- Creating leaky abstractions
- Coupling unrelated functionality
- Making abstractions too specific or too general

## Integration with Modular Architecture

DRY principles work hand-in-hand with modular design:
- Extract common code within module boundaries
- Share constants and configuration appropriately
- Avoid cross-module duplication through clear interfaces
- Balance DRY with module independence (see modular-architecture.md)
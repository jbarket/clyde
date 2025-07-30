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


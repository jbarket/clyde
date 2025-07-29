# Modular Architecture

## Core Principles

### Single Responsibility
- Each module should have one reason to change
- Functions and classes should do one thing well
- Separate concerns into distinct modules
- Avoid god objects and utility classes

### High Cohesion, Loose Coupling
- Group related functionality together
- Minimize dependencies between modules
- Use interfaces to define contracts
- Depend on abstractions, not concretions

### DRY Principle Integration
Every piece of knowledge must have a single, unambiguous, authoritative representation within a system:
- Configuration should be centralized
- Business rules should have one source of truth
- Extract common code into reusable components
- Use templates and code generation for repetitive patterns

## Domain Separation

### Microservice-Inspired Module Design
Apply **domain-driven design principles** at the module level:
- **Clear domain boundaries** - Each module represents a distinct business domain
- **Independent operation** - Modules should function independently without tight coupling
- **Explicit interfaces** - All inter-module communication through defined contracts
- **Domain-specific logic** - Business rules contained within appropriate domain modules

### Domain Boundary Guidelines
```
// Good: Clear domain boundaries
user/
├── models/user.py          # User data structures
├── services/auth.py        # Authentication logic
├── repositories/users.py   # Data access
└── validators/user.py      # Input validation

product/
├── models/product.py       # Product data structures
├── services/catalog.py     # Business logic
├── repositories/products.py # Data access
└── events/product.py       # Domain events
```

### Avoid Shared Everything
```
// Bad: Shared utilities become coupling points
shared/
├── utils.py               # Everything in one place
├── helpers.py             # Mixed domain logic
└── common.py              # Unclear responsibilities

// Good: Domain-specific utilities
user/
├── utils/user_helpers.py  # User-specific utilities
└── validators/email.py    # Domain-specific validation

product/
├── utils/pricing.py       # Product-specific utilities
└── formatters/currency.py # Domain-specific formatting
```

## Module Organization

### Directory Structure
- Organize by feature, not by type
- Use consistent naming conventions
- Keep related files together
- Separate concerns clearly

```
project/
├── user/
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   └── views.py
├── product/
│   ├── __init__.py
│   ├── models.py
│   └── services.py
└── shared/
    ├── utils.py
    └── exceptions.py
```

### Import Management
- Use explicit imports over wildcard imports
- Import at the module level
- Avoid circular imports
- Group imports logically (standard, third-party, local)

## Interface Design

### Define Clear Contracts
```python
from abc import ABC, abstractmethod
from typing import List, Optional

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> User:
        pass

class UserService:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self._user_repo.find_by_email(email)
        if user and user.verify_password(password):
            return user
        return None
```

### Module Communication Patterns
```python
# Event-driven communication between modules
class UserCreatedEvent:
    def __init__(self, user_id: str, email: str):
        self.user_id = user_id
        self.email = email
        self.timestamp = datetime.utcnow()

class UserService:
    def __init__(self, user_repo: UserRepository, event_bus: EventBus):
        self._user_repo = user_repo
        self._event_bus = event_bus
    
    def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        saved_user = self._user_repo.save(user)
        
        # Notify other modules without tight coupling
        self._event_bus.publish(UserCreatedEvent(
            user_id=saved_user.id,
            email=saved_user.email
        ))
        
        return saved_user
```

## AI-Agent-Friendly Design

### File and Function Sizing Guidelines
```python
# Optimal sizes for AI reasoning
- **Functions**: 10-30 lines (readable in single view)
- **Classes**: 50-150 lines (comprehensible as unit)
- **Modules**: 200-500 lines (fits in context window)
- **Files**: Maximum 800 lines (AI can process entirely)

# When files exceed limits:
# Split by responsibility, not by arbitrary line count
```

### Self-Explaining Code Structure
```python
# Good: Names that explain purpose and context
def send_welcome_email_to_new_user(user: User, email_template: EmailTemplate) -> EmailResult:
    pass

def calculate_monthly_subscription_renewal_date(subscription: Subscription) -> datetime:
    pass

# Avoid: Abbreviated or unclear names
def send_email(u, t):  # Unclear parameters
    pass

def calc_date(s):  # Abbreviated and unclear
    pass
```

### Consistent Code Organization
```python
"""
Module: user_service.py
Purpose: User-related business logic and operations
"""

# 1. Imports (grouped logically)
from typing import Optional, List
from datetime import datetime
from ..models import User
from ..repositories import UserRepository

# 2. Constants and configuration
MAX_LOGIN_ATTEMPTS = 3
PASSWORD_MIN_LENGTH = 8

# 3. Data classes and types
@dataclass
class UserCreationRequest:
    email: str
    password: str
    full_name: str

# 4. Main class implementation
class UserService:
    """Service class for user-related operations."""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    # Public methods first
    def create_user(self, request: UserCreationRequest) -> User:
        """Create a new user account."""
        self._validate_user_creation_request(request)
        
        user = User(
            email=request.email,
            password_hash=self._hash_password(request.password),
            full_name=request.full_name,
            created_at=datetime.utcnow()
        )
        
        return self._user_repository.save(user)
    
    # Private methods last
    def _validate_user_creation_request(self, request: UserCreationRequest) -> None:
        """Validate user creation request data."""
        if not self._is_valid_email(request.email):
            raise ValidationError("Invalid email format")
```

## Design Patterns

### Dependency Injection
- Pass dependencies as parameters
- Use dependency injection containers when appropriate
- Make dependencies explicit and testable
- Avoid hidden dependencies

```python
# Good: Explicit dependency injection
class OrderService:
    def __init__(self, payment_processor: PaymentProcessor, email_service: EmailService):
        self._payment_processor = payment_processor
        self._email_service = email_service
```

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
```python
# Each module should be testable in isolation
class TestUserService:
    def setup_method(self):
        # Mock all external dependencies
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.user_service = UserService(
            self.mock_user_repo,
            self.mock_event_bus
        )
    
    def test_create_user_success(self):
        # Test only the user service logic
        user_data = {"name": "John", "email": "john@example.com"}
        expected_user = User(**user_data)
        self.mock_user_repo.save.return_value = expected_user
        
        result = self.user_service.create_user(user_data)
        
        assert result == expected_user
        self.mock_event_bus.publish.assert_called_once()
```

## Configuration and Dependencies

### Module Configuration
```python
# Each module manages its own configuration
class UserModuleConfig:
    def __init__(self):
        self.password_min_length = int(os.getenv('USER_PASSWORD_MIN_LENGTH', '8'))
        self.session_timeout = int(os.getenv('USER_SESSION_TIMEOUT', '3600'))
        self.enable_2fa = os.getenv('USER_ENABLE_2FA', 'false').lower() == 'true'
```

### Dependency Injection Container
```python
class DIContainer:
    def __init__(self):
        self._services = {}
    
    def register(self, interface, implementation):
        self._services[interface] = implementation
    
    def get(self, interface):
        return self._services[interface]

# Module registration
def configure_user_module(container: DIContainer):
    container.register(UserRepository, SQLUserRepository())
    container.register(UserService, UserService(
        container.get(UserRepository),
        container.get(EventBus)
    ))
```

## Best Practices

### Module Boundaries
- Define clear public APIs
- Hide implementation details
- Use semantic versioning for breaking changes
- Document module contracts

### Error Handling
- Handle errors at appropriate boundaries
- Use custom exceptions for domain errors
- Log errors with sufficient context
- Fail fast for configuration errors

### Module Design Checklist
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

## Benefits

### Development Benefits
- **Faster development** - teams can work independently on modules
- **Easier reasoning** - smaller, focused codebases per module
- **Reduced merge conflicts** - changes isolated to specific modules
- **Better testing** - isolated unit tests and focused integration tests
- **AI collaboration** - modules sized for AI context windows

### Maintenance Benefits
- **Easier debugging** - issues confined to specific domains
- **Safer refactoring** - changes contained within module boundaries
- **Incremental upgrades** - modules can evolve independently
- **Technical debt isolation** - problems don't spread across domains
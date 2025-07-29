# Domain Separation Principles

## Core Philosophy

### Microservice-Inspired Module Design
- Design modules with **clear domain boundaries** even within monolithic applications
- Each module should have a **single, well-defined responsibility**
- Modules should be **independently testable** and **loosely coupled**
- Apply **separation of concerns** at the module level

### Module Independence
- **No shared mutable state** between modules
- **Explicit interfaces** for all inter-module communication
- **Dependency injection** over tight coupling
- **Event-driven communication** where appropriate

## Domain Boundary Guidelines

### Identify Domain Boundaries
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

## Interface Design

### Define Clear Contracts
```python
# Good: Explicit interface definition
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

## Testing Independence

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

### Integration Test Boundaries
```python
# Integration tests focus on module boundaries
class TestUserProductIntegration:
    def test_user_creation_triggers_welcome_product_recommendations(self):
        # Test the integration between user and product modules
        user_service = UserService(real_user_repo, real_event_bus)
        product_service = ProductService(real_product_repo, real_event_bus)
        
        # Subscribe product service to user events
        real_event_bus.subscribe(UserCreatedEvent, product_service.handle_new_user)
        
        # Create user and verify product module responds
        user = user_service.create_user({"name": "John", "email": "john@example.com"})
        
        # Verify cross-module integration
        recommendations = product_service.get_welcome_recommendations(user.id)
        assert len(recommendations) > 0
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

class ProductModuleConfig:
    def __init__(self):
        self.max_products_per_page = int(os.getenv('PRODUCT_MAX_PER_PAGE', '20'))
        self.enable_inventory_tracking = os.getenv('PRODUCT_INVENTORY', 'true').lower() == 'true'
```

### Dependency Injection Container
```python
# Use DI container to manage module dependencies
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
    container.register(PasswordHasher, BCryptHasher())
    container.register(UserService, UserService(
        container.get(UserRepository),
        container.get(EventBus)
    ))

def configure_product_module(container: DIContainer):
    container.register(ProductRepository, SQLProductRepository())
    container.register(ProductService, ProductService(
        container.get(ProductRepository),
        container.get(EventBus)
    ))
```

## Best Practices

### Module Design Checklist
```bash
□ Single responsibility - module has one reason to change
□ Clear boundaries - explicit interfaces and contracts  
□ Independent testing - can be tested without other modules
□ Minimal coupling - depends only on necessary abstractions
□ Explicit dependencies - all dependencies are injected
□ Domain-specific - utilities and helpers are module-specific
□ Event-driven communication - loose coupling between modules
□ Configuration isolation - module manages its own config
```

### Anti-Patterns to Avoid
- **God modules** that handle multiple domains
- **Shared mutable state** between modules
- **Circular dependencies** between modules
- **Leaky abstractions** that expose implementation details
- **Tight coupling** through direct imports of concrete classes
- **Cross-module database queries** that bypass interfaces
- **Shared utility classes** that create hidden dependencies

### Refactoring to Domain Separation
1. **Identify domains** - map business capabilities to modules
2. **Extract interfaces** - define contracts between modules
3. **Remove direct dependencies** - introduce abstraction layers
4. **Implement event communication** - replace direct calls with events
5. **Isolate configuration** - move module-specific config to modules
6. **Add integration tests** - verify module boundaries work correctly

## Benefits

### Development Benefits
- **Faster development** - teams can work independently on modules
- **Easier reasoning** - smaller, focused codebases per module
- **Reduced merge conflicts** - changes isolated to specific modules
- **Better testing** - isolated unit tests and focused integration tests

### Maintenance Benefits  
- **Easier debugging** - issues confined to specific domains
- **Safer refactoring** - changes contained within module boundaries
- **Incremental upgrades** - modules can evolve independently
- **Technical debt isolation** - problems don't spread across domains
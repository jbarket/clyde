# AI-Agent-Friendly Code Design

## Core Principles

### Human and AI Readability
Design code that can be **easily reasoned about** by both humans and AI agents:
- **Clear intent** - Code purpose should be immediately obvious
- **Logical sizing** - Components should fit within context windows
- **Self-documenting** - Code should explain itself without extensive comments
- **Consistent patterns** - Predictable structure across the codebase

### Cognitive Load Management
- **Single responsibility** - Each function/class does one thing well
- **Minimal complexity** - Avoid deeply nested logic
- **Clear boundaries** - Explicit interfaces and contracts
- **Predictable behavior** - No surprising side effects

## File and Function Sizing Guidelines

### File Size Boundaries
```python
# Optimal file sizes for AI reasoning
- **Functions**: 10-30 lines (readable in single view)
- **Classes**: 50-150 lines (comprehensible as unit)
- **Modules**: 200-500 lines (fits in context window)
- **Files**: Maximum 800 lines (AI can process entirely)

# When files exceed limits:
# Split by responsibility, not by arbitrary line count
```

### Function Complexity Guidelines
```python
# Good: Single responsibility, clear purpose
def validate_email_format(email: str) -> ValidationResult:
    """Validate email address format using regex pattern."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = re.match(pattern, email) is not None
    
    return ValidationResult(
        is_valid=is_valid,
        message="Valid email format" if is_valid else "Invalid email format"
    )

# Good: Clear parameters and return type
def calculate_shipping_cost(
    weight_kg: float,
    distance_km: float,
    shipping_method: ShippingMethod
) -> ShippingCost:
    """Calculate shipping cost based on weight, distance, and method."""
    base_rate = shipping_method.base_rate
    weight_rate = shipping_method.weight_multiplier * weight_kg
    distance_rate = shipping_method.distance_multiplier * distance_km
    
    total_cost = base_rate + weight_rate + distance_rate
    
    return ShippingCost(
        base_cost=base_rate,
        weight_cost=weight_rate,
        distance_cost=distance_rate,
        total_cost=total_cost
    )
```

### Class Design for AI Reasoning
```python
# Good: Clear responsibilities and interfaces
class UserAuthenticator:
    """Handles user authentication operations."""
    
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
    
    def authenticate(self, email: str, password: str) -> AuthResult:
        """Authenticate user with email and password."""
        user = self._user_repository.find_by_email(email)
        if not user:
            return AuthResult.failure("User not found")
        
        if not self._password_hasher.verify(password, user.password_hash):
            return AuthResult.failure("Invalid password")
        
        if not user.is_active:
            return AuthResult.failure("Account deactivated")
        
        return AuthResult.success(user)
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> ChangePasswordResult:
        """Change user password after verifying old password."""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            return ChangePasswordResult.failure("User not found")
        
        if not self._password_hasher.verify(old_password, user.password_hash):
            return ChangePasswordResult.failure("Current password incorrect")
        
        new_hash = self._password_hasher.hash(new_password)
        user.update_password_hash(new_hash)
        self._user_repository.save(user)
        
        return ChangePasswordResult.success()
```

## Naming Conventions for AI Comprehension

### Self-Explaining Names
```python
# Good: Names that explain purpose and context
def send_welcome_email_to_new_user(user: User, email_template: EmailTemplate) -> EmailResult:
    pass

def calculate_monthly_subscription_renewal_date(subscription: Subscription) -> datetime:
    pass

def validate_credit_card_number_format(card_number: str) -> bool:
    pass

# Avoid: Abbreviated or unclear names
def send_email(u, t):  # Unclear parameters
    pass

def calc_date(s):  # Abbreviated and unclear
    pass

def validate_cc(n):  # Unclear abbreviation
    pass
```

### Variable Naming Patterns
```python
# Use descriptive names that indicate type and purpose
user_email_address = "john@example.com"
total_order_amount = 149.99
is_user_authenticated = True
available_product_count = 45
shipping_address_list = []

# Avoid single letters except for well-known cases
for index, item in enumerate(product_list):  # Clear iteration
    process_product_item(item, index)

# Use intention-revealing names for booleans
user_has_premium_subscription = check_premium_status(user)
order_requires_approval = order.amount > APPROVAL_THRESHOLD
payment_was_successful = process_payment(payment_details)
```

## Structure for AI Pattern Recognition

### Consistent Code Organization
```python
# Standard module structure for AI recognition
"""
Module: user_service.py
Purpose: User-related business logic and operations
"""

# 1. Imports (grouped logically)
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime

from ..models import User
from ..repositories import UserRepository
from ..exceptions import UserNotFoundError, ValidationError

# 2. Constants and configuration
MAX_LOGIN_ATTEMPTS = 3
PASSWORD_MIN_LENGTH = 8

# 3. Data classes and types
@dataclass
class UserCreationRequest:
    email: str
    password: str
    full_name: str

@dataclass
class UserUpdateRequest:
    full_name: Optional[str] = None
    email: Optional[str] = None

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
    
    def update_user(self, user_id: str, request: UserUpdateRequest) -> User:
        """Update existing user information."""
        user = self._get_user_or_raise(user_id)
        
        if request.full_name:
            user.full_name = request.full_name
        if request.email:
            self._validate_email_uniqueness(request.email, exclude_user_id=user_id)
            user.email = request.email
        
        return self._user_repository.save(user)
    
    # Private methods last
    def _validate_user_creation_request(self, request: UserCreationRequest) -> None:
        """Validate user creation request data."""
        if not self._is_valid_email(request.email):
            raise ValidationError("Invalid email format")
        
        if len(request.password) < PASSWORD_MIN_LENGTH:
            raise ValidationError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
        
        if self._user_repository.find_by_email(request.email):
            raise ValidationError("Email already exists")
    
    def _get_user_or_raise(self, user_id: str) -> User:
        """Get user by ID or raise exception if not found."""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return user
```

### Predictable Error Handling
```python
# Consistent error handling patterns for AI recognition
class UserService:
    def get_user_profile(self, user_id: str) -> UserProfileResponse:
        """Get user profile with consistent error handling."""
        try:
            user = self._user_repository.find_by_id(user_id)
            if not user:
                return UserProfileResponse.not_found("User not found")
            
            if not user.is_active:
                return UserProfileResponse.forbidden("User account deactivated")
            
            profile = UserProfile.from_user(user)
            return UserProfileResponse.success(profile)
            
        except DatabaseError as e:
            logger.error(f"Database error getting user profile: {e}")
            return UserProfileResponse.server_error("Unable to retrieve user profile")
        
        except Exception as e:
            logger.error(f"Unexpected error getting user profile: {e}")
            return UserProfileResponse.server_error("An unexpected error occurred")
```

## Documentation for AI Understanding

### Self-Documenting Code Patterns
```python
# Code that explains itself without extensive comments
def calculate_late_payment_fee(
    original_amount: Decimal,
    days_overdue: int,
    late_fee_percentage: Decimal
) -> LateFeeCalculation:
    """Calculate late payment fee based on original amount and days overdue."""
    
    # Business rule: No fee for first 7 days grace period
    if days_overdue <= GRACE_PERIOD_DAYS:
        return LateFeeCalculation(
            original_amount=original_amount,
            days_overdue=days_overdue,
            fee_amount=Decimal('0.00'),
            total_amount=original_amount
        )
    
    # Calculate fee only on days beyond grace period
    billable_days = days_overdue - GRACE_PERIOD_DAYS
    daily_fee_rate = late_fee_percentage / 100 / 365
    fee_amount = original_amount * daily_fee_rate * billable_days
    
    # Cap fee at maximum allowed by regulations
    max_allowed_fee = original_amount * MAX_LATE_FEE_PERCENTAGE / 100
    actual_fee = min(fee_amount, max_allowed_fee)
    
    return LateFeeCalculation(
        original_amount=original_amount,
        days_overdue=days_overdue,
        fee_amount=actual_fee,
        total_amount=original_amount + actual_fee
    )
```

### Type Hints for AI Comprehension
```python
from typing import Dict, List, Optional, Union, Protocol

# Clear type definitions help AI understand interfaces
class PaymentProcessor(Protocol):
    def process_payment(self, payment_data: PaymentData) -> PaymentResult:
        ...

class OrderService:
    def __init__(self, payment_processor: PaymentProcessor):
        self._payment_processor = payment_processor
    
    def process_order(
        self,
        order_items: List[OrderItem],
        shipping_address: Address,
        payment_method: PaymentMethod
    ) -> OrderProcessingResult:
        """Process complete order with type-safe interfaces."""
        
        # Calculate totals
        item_total = self._calculate_items_total(order_items)
        shipping_cost = self._calculate_shipping_cost(order_items, shipping_address)
        tax_amount = self._calculate_tax(item_total, shipping_address)
        
        order_total = item_total + shipping_cost + tax_amount
        
        # Process payment
        payment_data = PaymentData(
            amount=order_total,
            currency='USD',
            method=payment_method
        )
        
        payment_result = self._payment_processor.process_payment(payment_data)
        
        if not payment_result.success:
            return OrderProcessingResult.payment_failed(payment_result.error_message)
        
        # Create order record
        order = Order(
            items=order_items,
            shipping_address=shipping_address,
            payment_reference=payment_result.transaction_id,
            total_amount=order_total,
            status=OrderStatus.CONFIRMED
        )
        
        return OrderProcessingResult.success(order)
```

## Modularity for AI Analysis

### Composable Components
```python
# Design components that can be easily understood and combined
class EmailValidator:
    """Validates email address format and domain."""
    
    @staticmethod
    def is_valid_format(email: str) -> bool:
        """Check if email matches valid format pattern."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_allowed_domain(email: str, allowed_domains: List[str]) -> bool:
        """Check if email domain is in allowed list."""
        domain = email.split('@')[1].lower()
        return domain in [d.lower() for d in allowed_domains]

class PasswordValidator:
    """Validates password strength and requirements."""
    
    def __init__(self, min_length: int = 8, require_special_chars: bool = True):
        self.min_length = min_length
        self.require_special_chars = require_special_chars
    
    def validate(self, password: str) -> PasswordValidationResult:
        """Validate password against all requirements."""
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if self.require_special_chars and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return PasswordValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )

# Compose validators for complex validation
class UserRegistrationValidator:
    """Validates complete user registration data."""
    
    def __init__(self, allowed_email_domains: Optional[List[str]] = None):
        self.email_validator = EmailValidator()
        self.password_validator = PasswordValidator()
        self.allowed_email_domains = allowed_email_domains or []
    
    def validate(self, registration_data: UserRegistrationData) -> ValidationResult:
        """Validate all aspects of user registration."""
        errors = []
        
        # Email validation
        if not self.email_validator.is_valid_format(registration_data.email):
            errors.append("Invalid email format")
        elif self.allowed_email_domains and not self.email_validator.is_allowed_domain(
            registration_data.email, self.allowed_email_domains
        ):
            errors.append("Email domain not allowed")
        
        # Password validation
        password_result = self.password_validator.validate(registration_data.password)
        if not password_result.is_valid:
            errors.extend(password_result.errors)
        
        # Name validation
        if not registration_data.full_name or len(registration_data.full_name.strip()) < 2:
            errors.append("Full name must be at least 2 characters")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
```

## AI-Friendly Testing Patterns

### Clear Test Structure
```python
# Tests that are easy for AI to understand and generate
class TestUserAuthenticator:
    """Test cases for user authentication functionality."""
    
    def setup_method(self):
        """Set up test dependencies and mock objects."""
        self.mock_user_repository = Mock(spec=UserRepository)
        self.mock_password_hasher = Mock(spec=PasswordHasher)
        self.authenticator = UserAuthenticator(
            self.mock_user_repository,
            self.mock_password_hasher
        )
    
    def test_authenticate_with_valid_credentials_returns_success(self):
        """Test successful authentication with valid email and password."""
        # Arrange
        user = User(id="123", email="john@example.com", password_hash="hashed", is_active=True)
        self.mock_user_repository.find_by_email.return_value = user
        self.mock_password_hasher.verify.return_value = True
        
        # Act
        result = self.authenticator.authenticate("john@example.com", "password123")
        
        # Assert
        assert result.is_success
        assert result.user == user
        assert result.error_message is None
        self.mock_user_repository.find_by_email.assert_called_once_with("john@example.com")
        self.mock_password_hasher.verify.assert_called_once_with("password123", "hashed")
    
    def test_authenticate_with_nonexistent_user_returns_failure(self):
        """Test authentication failure when user does not exist."""
        # Arrange
        self.mock_user_repository.find_by_email.return_value = None
        
        # Act
        result = self.authenticator.authenticate("nonexistent@example.com", "password123")
        
        # Assert
        assert not result.is_success
        assert result.user is None
        assert result.error_message == "User not found"
        self.mock_user_repository.find_by_email.assert_called_once_with("nonexistent@example.com")
        self.mock_password_hasher.verify.assert_not_called()
```

## Benefits for AI and Human Collaboration

### Predictable Patterns
- **Consistent structure** allows AI to understand and generate similar code
- **Clear naming** makes intent obvious to both humans and AI
- **Type safety** provides explicit contracts and interfaces
- **Modular design** enables AI to reason about components independently

### Maintainable Complexity
- **Bounded file sizes** fit within AI context windows
- **Single responsibility** makes reasoning about code easier
- **Explicit dependencies** make relationships clear
- **Self-documenting** reduces need for extensive documentation

### Collaborative Development
- **Human-readable** code remains accessible to developers
- **AI-parseable** structure enables automated assistance
- **Consistent patterns** speed up both human and AI understanding
- **Clear interfaces** facilitate integration and testing
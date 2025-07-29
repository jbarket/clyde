# Error Handling Philosophy

## Core Principle

Robust error handling involves anticipating failure modes, designing graceful degradation strategies, and providing clear feedback that enables appropriate responses from users and systems.

## When to Apply

- Input validation and boundary checking
- External system integrations (APIs, databases, file systems)
- Resource allocation and management
- User-facing operations that may fail
- Background processes and async operations
- System startup and configuration loading

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
- **Caching**: Use cached data when live data is unavailable
- **Default Values**: Provide sensible defaults when configuration fails

### 3. Error Recovery
Attempt to recover from transient failures:
- **Retry Logic**: Implement exponential backoff for transient failures
- **Circuit Breakers**: Prevent cascading failures
- **Timeouts**: Avoid hanging on unresponsive operations
- **Cleanup**: Ensure proper resource cleanup on failure

## Error Classification

### 1. User Errors
Mistakes made by users that should be handled gracefully:
```python
class ValidationError(Exception):
    """Raised when user input fails validation."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation failed for {field}: {message}")

def validate_email(email: str) -> str:
    """Validate email format and return normalized version."""
    if not email:
        raise ValidationError("email", "Email address is required")
    
    if "@" not in email:
        raise ValidationError("email", "Email address must contain @ symbol")
        
    return email.lower().strip()
```

### 2. System Errors
Infrastructure or dependency failures:
```python
class ExternalServiceError(Exception):
    """Raised when external service calls fail."""
    def __init__(self, service: str, operation: str, cause: Exception):
        self.service = service
        self.operation = operation
        self.cause = cause
        super().__init__(f"Failed to {operation} via {service}: {cause}")

def fetch_user_data(user_id: str) -> dict:
    """Fetch user data with proper error handling."""
    try:
        response = external_api.get_user(user_id)
        return response.json()
    except requests.ConnectionError as e:
        raise ExternalServiceError("user_api", "fetch_user", e)
    except requests.Timeout as e:
        raise ExternalServiceError("user_api", "fetch_user", e)
```

### 3. Programming Errors
Bugs that indicate code defects:
```python
def calculate_average(numbers: List[float]) -> float:
    """Calculate arithmetic mean of numbers."""
    assert numbers, "Cannot calculate average of empty list"
    assert all(isinstance(n, (int, float)) for n in numbers), "All items must be numeric"
    
    return sum(numbers) / len(numbers)
```

## Implementation Patterns

### Error Context
Provide sufficient information for debugging and user feedback:
```python
class PaymentError(Exception):
    """Base class for payment-related errors."""
    def __init__(self, message: str, error_code: str, context: dict = None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        super().__init__(message)

def process_payment(amount: float, payment_method: str) -> str:
    """Process payment and return transaction ID."""
    context = {
        "amount": amount,
        "payment_method": payment_method,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": get_current_user_id()
    }
    
    try:
        transaction_id = payment_gateway.charge(amount, payment_method)
        return transaction_id
    except PaymentGatewayError as e:
        raise PaymentError(
            message="Payment processing failed",
            error_code="PAYMENT_GATEWAY_ERROR",
            context={**context, "gateway_error": str(e)}
        )
```

### Resource Management
Ensure proper cleanup even when errors occur:
```python
from contextlib import contextmanager
import logging

@contextmanager
def database_transaction():
    """Context manager for database transactions with proper cleanup."""
    connection = None
    try:
        connection = get_database_connection()
        connection.begin()
        yield connection
        connection.commit()
        logging.info("Database transaction committed successfully")
    except Exception as e:
        if connection:
            connection.rollback()
            logging.error(f"Database transaction rolled back due to error: {e}")
        raise
    finally:
        if connection:
            connection.close()
```

### Retry Logic
Handle transient failures with exponential backoff:
```python
import time
import random
from typing import Callable, TypeVar, Any

T = TypeVar('T')

def retry_with_backoff(
    func: Callable[[], T],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
) -> T:
    """
    Retry function with exponential backoff.
    
    Args:
        func: Function to retry
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay between retries
        max_delay: Maximum delay between retries
        exceptions: Exceptions that trigger a retry
        
    Returns:
        Result of function call
        
    Raises:
        Last exception if all retries fail
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            if attempt == max_attempts - 1:
                raise  # Re-raise on final attempt
                
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = delay * 0.1 * random.random()  # Add 10% jitter
            time.sleep(delay + jitter)
            
            logging.warning(
                f"Attempt {attempt + 1} failed: {e}. "
                f"Retrying in {delay:.2f}s..."
            )
```

## Error Communication

### User-Friendly Messages
Translate technical errors into actionable user feedback:
```python
def format_user_error(error: Exception) -> dict:
    """Convert exceptions to user-friendly error responses."""
    if isinstance(error, ValidationError):
        return {
            "error_type": "validation_error",
            "message": f"Please check your {error.field}: {error.message}",
            "field": error.field,
            "code": "VALIDATION_FAILED"
        }
    elif isinstance(error, ExternalServiceError):
        return {
            "error_type": "service_error",
            "message": "We're experiencing technical difficulties. Please try again later.",
            "code": "SERVICE_UNAVAILABLE"
        }
    else:
        return {
            "error_type": "internal_error",
            "message": "An unexpected error occurred. Please contact support.",
            "code": "INTERNAL_ERROR"
        }
```

### Logging Strategy
Provide different levels of detail for different audiences:
```python
import logging
import traceback

def log_error(error: Exception, context: dict = None):
    """Log errors with appropriate detail level."""
    context = context or {}
    
    # Always log basic error info
    logging.error(f"Error occurred: {type(error).__name__}: {error}")
    
    # Log context for debugging
    if context:
        logging.error(f"Error context: {context}")
    
    # Log full traceback for debugging
    logging.debug(f"Full traceback: {traceback.format_exc()}")
    
    # Log to external monitoring system
    if should_report_to_monitoring(error):
        monitoring_system.report_error(error, context)
```

## Testing Error Conditions

### Error Scenario Testing
```python
import pytest
from unittest.mock import patch

def test_payment_processing_network_error():
    """Test payment processing handles network errors gracefully."""
    with patch('payment_gateway.charge') as mock_charge:
        mock_charge.side_effect = requests.ConnectionError("Network unreachable")
        
        with pytest.raises(PaymentError) as exc_info:
            process_payment(100.0, "credit_card")
            
        assert exc_info.value.error_code == "PAYMENT_GATEWAY_ERROR"
        assert "Network unreachable" in str(exc_info.value.context["gateway_error"])

def test_retry_mechanism_success_on_second_attempt():
    """Test retry logic succeeds after initial failure."""
    call_count = 0
    
    def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise requests.Timeout("Request timed out")
        return "success"
    
    result = retry_with_backoff(flaky_function, max_attempts=3)
    assert result == "success"
    assert call_count == 2
```

## Monitoring and Observability

### Error Metrics
Track error patterns to identify system issues:
- **Error Rate**: Percentage of operations that fail
- **Error Types**: Distribution of different error categories
- **Recovery Success**: How often retry logic succeeds
- **Error Duration**: How long errors persist

### Alerting Strategy
```python
def should_alert(error: Exception, context: dict) -> bool:
    """Determine if error should trigger an alert."""
    # Critical system errors always alert
    if isinstance(error, SystemCriticalError):
        return True
    
    # High frequency of user errors might indicate a system issue
    error_rate = get_recent_error_rate(type(error))
    if error_rate > 0.05:  # 5% error rate threshold
        return True
    
    # External service errors during business hours
    if isinstance(error, ExternalServiceError) and is_business_hours():
        return True
        
    return False
```

## Anti-patterns to Avoid

- **Silent Failures**: Catching exceptions without appropriate handling
- **Generic Exception Handling**: Catching all exceptions with the same logic
- **Error Swallowing**: Losing important error information
- **Premature Recovery**: Retrying operations that will always fail
- **Error Message Leakage**: Exposing sensitive information in error messages
- **No Error Context**: Providing insufficient information for debugging

## Benefits

### System Reliability
- **Predictable Behavior**: Systems handle errors consistently
- **Reduced Downtime**: Graceful degradation keeps systems operational
- **Faster Recovery**: Clear error information enables quick fixes
- **Better User Experience**: Meaningful error messages help users succeed

### Development Efficiency
- **Easier Debugging**: Rich error context speeds problem resolution
- **Improved Testing**: Error scenarios are explicitly tested
- **Better Monitoring**: Structured error handling enables better observability
- **Reduced Support Load**: Clear error messages reduce support requests

## Evolution and Improvement

### Error Pattern Analysis
- Review error logs to identify common failure modes
- Analyze user behavior around error conditions
- Measure recovery success rates and user satisfaction
- Identify opportunities for better error prevention

### Continuous Improvement
- Refine error messages based on user feedback
- Improve error recovery mechanisms based on real-world failures
- Enhance monitoring and alerting based on operational experience
- Update error handling patterns as systems evolve
# Verification and Validation Patterns

## Core Principle

Verification ensures that systems work correctly, meet requirements, and behave predictably under various conditions through systematic testing, validation, and quality assurance practices.

## When to Apply

- Before deploying code to production
- When integrating with external systems
- During refactoring or major changes
- When requirements change or evolve
- For critical system components
- When debugging complex issues

## Verification Strategies

### 1. Unit Testing
Test individual components in isolation:
- **Single Responsibility**: Each test verifies one specific behavior
- **Fast Execution**: Tests run quickly to enable frequent execution
- **Deterministic**: Same inputs always produce same outputs
- **Independent**: Tests don't depend on each other or external state

### 2. Integration Testing
Verify that components work together correctly:
- **Interface Testing**: Validate contracts between components
- **Data Flow**: Ensure information passes correctly through system
- **Error Propagation**: Verify error handling across boundaries
- **Performance**: Test system behavior under realistic conditions

### 3. End-to-End Testing
Validate complete user workflows:
- **User Scenarios**: Test real user journeys through system
- **System Integration**: Verify all components work together
- **External Dependencies**: Test with actual external services
- **Production-like Environment**: Use realistic data and configurations

### 4. Property-Based Testing
Test system properties rather than specific examples:
- **Invariants**: Properties that should always hold true
- **Generated Inputs**: Test with wide range of generated data
- **Edge Cases**: Automatically discover boundary conditions
- **Regression Prevention**: Catch failures with unexpected inputs

## Implementation Examples

### Unit Testing Patterns
```python
import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

class TestOrderCalculator:
    """Test order total calculations."""
    
    def test_calculate_total_with_tax(self):
        """Test basic tax calculation."""
        # Arrange
        calculator = OrderCalculator(tax_rate=Decimal('0.08'))
        items = [
            OrderItem(price=Decimal('10.00'), quantity=2),
            OrderItem(price=Decimal('5.00'), quantity=1)
        ]
        
        # Act
        total = calculator.calculate_total(items)
        
        # Assert
        expected = Decimal('25.00') * Decimal('1.08')  # $25 + 8% tax
        assert total == expected
    
    def test_calculate_total_with_discount(self):
        """Test discount application."""
        calculator = OrderCalculator(tax_rate=Decimal('0.08'))
        items = [OrderItem(price=Decimal('100.00'), quantity=1)]
        discount = Decimal('10.00')
        
        total = calculator.calculate_total(items, discount=discount)
        
        # $100 - $10 discount + 8% tax on discounted amount
        expected = (Decimal('100.00') - discount) * Decimal('1.08')
        assert total == expected
    
    @pytest.mark.parametrize("tax_rate,expected", [
        (Decimal('0.00'), Decimal('100.00')),
        (Decimal('0.05'), Decimal('105.00')),
        (Decimal('0.10'), Decimal('110.00')),
        (Decimal('0.15'), Decimal('115.00')),
    ])
    def test_various_tax_rates(self, tax_rate, expected):
        """Test calculation with different tax rates."""
        calculator = OrderCalculator(tax_rate=tax_rate)
        items = [OrderItem(price=Decimal('100.00'), quantity=1)]
        
        total = calculator.calculate_total(items)
        
        assert total == expected
    
    def test_empty_order_raises_error(self):
        """Test that empty orders are rejected."""
        calculator = OrderCalculator(tax_rate=Decimal('0.08'))
        
        with pytest.raises(ValueError, match="Order must contain at least one item"):
            calculator.calculate_total([])
```

### Integration Testing Patterns
```python
import pytest
from testcontainers.postgres import PostgresContainer
import requests

class TestUserService:
    """Integration tests for user service."""
    
    @pytest.fixture(scope="class")
    def database(self):
        """Set up test database."""
        with PostgresContainer("postgres:13") as postgres:
            database_url = postgres.get_connection_url()
            # Run migrations
            run_migrations(database_url)
            yield database_url
    
    @pytest.fixture
    def user_service(self, database):
        """Create user service with test database."""
        return UserService(database_url=database)
    
    def test_create_and_retrieve_user(self, user_service):
        """Test complete user creation and retrieval flow."""
        # Create user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "secure_password"
        }
        
        created_user = user_service.create_user(user_data)
        assert created_user.id is not None
        assert created_user.username == "testuser"
        
        # Retrieve user
        retrieved_user = user_service.get_user(created_user.id)
        assert retrieved_user.username == created_user.username
        assert retrieved_user.email == created_user.email
        # Password should be hashed
        assert retrieved_user.password_hash != "secure_password"
    
    def test_duplicate_username_raises_error(self, user_service):
        """Test that duplicate usernames are rejected."""
        user_data = {
            "username": "duplicate",
            "email": "user1@example.com",
            "password": "password1"
        }
        
        # First user creation should succeed
        user_service.create_user(user_data)
        
        # Second user with same username should fail
        duplicate_data = {
            "username": "duplicate",
            "email": "user2@example.com",
            "password": "password2"
        }
        
        with pytest.raises(DuplicateUsernameError):
            user_service.create_user(duplicate_data)
```

### End-to-End Testing Patterns
```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestUserRegistrationFlow:
    """End-to-end tests for user registration."""
    
    @pytest.fixture
    def browser(self):
        """Set up browser for tests."""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    def test_complete_registration_flow(self, browser):
        """Test complete user registration journey."""
        # Navigate to registration page
        browser.get("http://localhost:8000/register")
        
        # Fill out registration form
        username_field = browser.find_element(By.NAME, "username")
        email_field = browser.find_element(By.NAME, "email")
        password_field = browser.find_element(By.NAME, "password")
        confirm_password_field = browser.find_element(By.NAME, "confirm_password")
        
        username_field.send_keys("newuser")
        email_field.send_keys("newuser@example.com")
        password_field.send_keys("SecurePassword123!")
        confirm_password_field.send_keys("SecurePassword123!")
        
        # Submit form
        submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Wait for success message
        wait = WebDriverWait(browser, 10)
        success_message = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        
        assert "Registration successful" in success_message.text
        
        # Verify user can login
        browser.get("http://localhost:8000/login")
        
        login_username = browser.find_element(By.NAME, "username")
        login_password = browser.find_element(By.NAME, "password")
        
        login_username.send_keys("newuser")
        login_password.send_keys("SecurePassword123!")
        
        login_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Verify successful login
        dashboard_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "user-dashboard"))
        )
        
        assert "Welcome, newuser" in dashboard_element.text
```

### Property-Based Testing
```python
from hypothesis import given, strategies as st
import pytest

class TestEmailValidator:
    """Property-based tests for email validation."""
    
    @given(st.emails())
    def test_valid_emails_pass_validation(self, email):
        """Any valid email should pass validation."""
        result = validate_email(email)
        assert result.is_valid
        assert result.normalized_email is not None
    
    @given(st.text().filter(lambda x: '@' not in x))
    def test_emails_without_at_symbol_fail(self, text):
        """Text without @ symbol should fail email validation."""
        result = validate_email(text)
        assert not result.is_valid
        assert "missing @ symbol" in result.error_message.lower()
    
    @given(st.text(min_size=1, max_size=100))
    def test_normalization_preserves_validity(self, email_text):
        """Email normalization should preserve validity."""
        first_result = validate_email(email_text)
        
        if first_result.is_valid:
            # Normalize and validate again
            normalized = first_result.normalized_email
            second_result = validate_email(normalized)
            
            # Normalized email should still be valid
            assert second_result.is_valid
            # And should normalize to the same thing
            assert second_result.normalized_email == normalized

class TestCalculator:
    """Property-based tests for calculator functions."""
    
    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_addition_is_commutative(self, a, b):
        """Addition should be commutative: a + b = b + a"""
        calculator = Calculator()
        result1 = calculator.add(a, b)
        result2 = calculator.add(b, a)
        assert abs(result1 - result2) < 1e-10
    
    @given(st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6))
    def test_addition_identity(self, a):
        """Adding zero should return the original number."""
        calculator = Calculator()
        result = calculator.add(a, 0)
        assert abs(result - a) < 1e-10
    
    @given(st.floats(allow_nan=False, allow_infinity=False, min_value=1e-6))
    def test_division_by_self_equals_one(self, a):
        """Any number divided by itself should equal 1."""
        calculator = Calculator()
        result = calculator.divide(a, a)
        assert abs(result - 1.0) < 1e-10
```

## Verification Workflow

### Pre-Commit Verification
```bash
#!/bin/bash
# pre-commit hook script

echo "Running pre-commit verification..."

# Run unit tests
echo "Running unit tests..."
python -m pytest tests/unit/ --fast
if [ $? -ne 0 ]; then
    echo "Unit tests failed. Commit aborted."
    exit 1
fi

# Run linting
echo "Running code quality checks..."
python -m flake8 src/
python -m mypy src/
if [ $? -ne 0 ]; then
    echo "Code quality checks failed. Commit aborted."
    exit 1
fi

# Run security scan
echo "Running security scan..."
python -m bandit -r src/
if [ $? -ne 0 ]; then
    echo "Security issues found. Commit aborted."
    exit 1
fi

echo "All pre-commit checks passed!"
```

### Continuous Integration Pipeline
```yaml
# .github/workflows/verification.yml
name: Verification Pipeline

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run unit tests
        run: pytest tests/unit/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run integration tests
        run: pytest tests/integration/
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Start application
        run: |
          python app.py &
          sleep 10  # Wait for app to start
      - name: Run E2E tests
        run: pytest tests/e2e/
```

## Quality Metrics

### Test Coverage Analysis
```python
# conftest.py - pytest configuration
import pytest
import coverage

def pytest_configure(config):
    """Configure coverage reporting."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")

def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on path."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.slow)

@pytest.fixture(scope="session")
def coverage_report():
    """Generate coverage report after test run."""
    cov = coverage.Coverage()
    cov.start()
    yield
    cov.stop()
    cov.save()
    
    # Generate reports
    print("\nCoverage Report:")
    cov.report(show_missing=True)
    cov.html_report(directory="htmlcov")
```

### Performance Testing
```python
import time
import pytest
from contextlib import contextmanager

@contextmanager
def timer():
    """Context manager to measure execution time."""
    start = time.time()
    yield
    end = time.time()
    print(f"Execution time: {end - start:.4f} seconds")

class TestPerformance:
    """Performance verification tests."""
    
    def test_api_response_time(self):
        """Test that API responds within acceptable time."""
        with timer():
            response = requests.get("http://localhost:8000/api/users")
            
        assert response.status_code == 200
        # Response should be under 200ms
        assert response.elapsed.total_seconds() < 0.2
    
    @pytest.mark.parametrize("num_users", [100, 1000, 10000])
    def test_database_query_performance(self, num_users):
        """Test query performance with different data sizes."""
        # Set up test data
        setup_test_users(num_users)
        
        start_time = time.time()
        users = User.query.filter(User.active == True).all()
        query_time = time.time() - start_time
        
        # Query should complete within reasonable time
        expected_max_time = 0.001 * num_users  # 1ms per 1000 users
        assert query_time < expected_max_time
        assert len(users) <= num_users
```

## Anti-patterns to Avoid

- **Testing Implementation Details**: Tests should verify behavior, not internal structure
- **Flaky Tests**: Tests that pass or fail inconsistently undermine confidence
- **Slow Test Suites**: Tests that take too long discourage frequent execution
- **Missing Edge Cases**: Not testing boundary conditions and error scenarios
- **Test Dependencies**: Tests that require specific execution order or shared state
- **Over-Mocking**: Mocking so much that tests don't verify real behavior

## Benefits

### Quality Assurance
- **Bug Prevention**: Catch issues before they reach production
- **Regression Protection**: Prevent reintroduction of fixed bugs
- **Behavior Documentation**: Tests document expected system behavior
- **Refactoring Safety**: Change code with confidence that behavior is preserved

### Development Efficiency
- **Faster Debugging**: Tests help isolate and identify issues quickly
- **Design Feedback**: Writing tests reveals design problems early
- **Documentation**: Tests serve as executable documentation
- **Confidence**: Comprehensive testing enables confident code changes

## Continuous Improvement

### Test Strategy Evolution
- **Coverage Analysis**: Identify untested code and critical paths
- **Failure Analysis**: Learn from test failures and production issues
- **Performance Monitoring**: Track test execution time and reliability
- **Feedback Integration**: Incorporate team feedback on test effectiveness

### Tool and Process Enhancement
- **Automation Expansion**: Automate more verification steps over time
- **Test Environment Improvement**: Make test environments more production-like
- **Feedback Loop Optimization**: Reduce time from code change to feedback
- **Quality Metrics**: Track and improve verification effectiveness metrics
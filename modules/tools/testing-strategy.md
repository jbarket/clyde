# Comprehensive Testing Strategy

## Three-Tier Testing Architecture

### Testing Pyramid Structure
```
                     /\
                    /  \
                   / E2E \  <- Playwright (Headless Only)
                  /______\
                 /        \
                /Integration\ <- Module Boundaries
               /____________\
              /              \
             /   Unit Tests   \ <- Individual Components  
            /________________\
```

### Testing Responsibilities
- **Unit Tests**: Individual pieces and components (80%+ coverage for business logic)
- **Integration Tests**: Logical groupings and module boundaries
- **End-to-End Tests**: Complete user workflows using Playwright (headless)

## Unit Testing Guidelines

### Individual Component Testing
```python
# Test individual functions and classes in isolation
class TestUserValidator:
    def test_email_validation_success(self):
        validator = UserValidator()
        result = validator.validate_email("valid@example.com")
        assert result.is_valid
        assert result.errors == []
    
    def test_email_validation_failure(self):
        validator = UserValidator()
        result = validator.validate_email("invalid-email")
        assert not result.is_valid
        assert "Invalid email format" in result.errors
    
    def test_password_strength_requirements(self):
        validator = UserValidator()
        
        # Test weak password
        result = validator.validate_password("123")
        assert not result.is_valid
        assert "Password too short" in result.errors
        
        # Test strong password
        result = validator.validate_password("SecurePass123!")
        assert result.is_valid
```

### Business Logic Coverage Requirements
- **80%+ line coverage** for all business logic modules
- **100% coverage** for critical paths (authentication, payments, security)
- **Edge case testing** for all input validation
- **Error condition testing** for all failure modes

### Unit Test Organization
```
tests/
├── unit/
│   ├── models/
│   │   ├── test_user.py
│   │   └── test_product.py
│   ├── services/
│   │   ├── test_auth_service.py
│   │   └── test_product_service.py
│   ├── validators/
│   │   └── test_input_validators.py
│   └── utils/
│       └── test_helpers.py
```

### Mocking for Unit Tests
```python
# Mock all external dependencies for true unit isolation
class TestAuthService:
    def setup_method(self):
        # Mock all external dependencies
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_password_hasher = Mock(spec=PasswordHasher)
        self.mock_token_service = Mock(spec=TokenService)
        
        # Create service with mocked dependencies
        self.auth_service = AuthService(
            user_repo=self.mock_user_repo,
            password_hasher=self.mock_password_hasher,
            token_service=self.mock_token_service
        )
    
    def test_successful_authentication(self):
        # Setup mocks
        user = User(id=1, email="test@example.com", password_hash="hashed")
        self.mock_user_repo.find_by_email.return_value = user
        self.mock_password_hasher.verify.return_value = True
        self.mock_token_service.generate.return_value = "jwt-token"
        
        # Test authentication
        result = self.auth_service.authenticate("test@example.com", "password")
        
        # Verify behavior
        assert result.success
        assert result.token == "jwt-token"
        self.mock_user_repo.find_by_email.assert_called_once_with("test@example.com")
        self.mock_password_hasher.verify.assert_called_once_with("password", "hashed")
```

## Integration Testing Guidelines

### Module Boundary Testing
Integration tests focus on **module boundaries** and **external dependencies**:

```python
# Test interaction between modules
class TestUserProductIntegration:
    def setup_method(self):
        # Use real implementations for integration testing
        self.db_session = create_test_database_session()
        self.user_repo = SQLUserRepository(self.db_session)
        self.product_repo = SQLProductRepository(self.db_session)
        self.event_bus = InMemoryEventBus()
        
        # Services with real dependencies
        self.user_service = UserService(self.user_repo, self.event_bus)
        self.product_service = ProductService(self.product_repo, self.event_bus)
    
    def test_user_creation_triggers_welcome_recommendations(self):
        # Subscribe product service to user events
        self.event_bus.subscribe(UserCreatedEvent, self.product_service.handle_new_user)
        
        # Create user (real database interaction)
        user = self.user_service.create_user({
            "name": "John Doe",
            "email": "john@example.com",
            "preferences": {"category": "electronics"}
        })
        
        # Verify cross-module integration
        recommendations = self.product_service.get_welcome_recommendations(user.id)
        assert len(recommendations) > 0
        assert all(rec.category == "electronics" for rec in recommendations)
    
    def teardown_method(self):
        # Clean up test data
        self.db_session.rollback()
        self.db_session.close()
```

### External Dependency Integration
```python
# Test with real external services (in test environment)
class TestEmailServiceIntegration:
    def test_email_sending_integration(self):
        # Use test email service configuration
        email_service = EmailService(
            smtp_host="smtp.test.example.com",
            smtp_port=587,
            test_mode=True
        )
        
        # Test actual email sending
        result = email_service.send_welcome_email(
            to="test@example.com",
            user_name="John Doe"
        )
        
        assert result.success
        assert result.message_id is not None
        
        # Verify email was queued/sent in test environment
        sent_emails = email_service.get_test_sent_emails()
        assert len(sent_emails) == 1
        assert sent_emails[0]["to"] == "test@example.com"
```

### Integration Test Organization
```
tests/
├── integration/
│   ├── database/
│   │   ├── test_user_repository.py
│   │   └── test_product_repository.py
│   ├── api/
│   │   ├── test_auth_endpoints.py
│   │   └── test_product_endpoints.py
│   ├── services/
│   │   └── test_cross_module_interactions.py
│   └── external/
│       ├── test_email_service.py
│       └── test_payment_gateway.py
```

## End-to-End Testing with Playwright

### Headless-Only E2E Testing
**Critical Requirement**: All Playwright tests **MUST** run headless

```javascript
// playwright.config.js
module.exports = {
  testDir: './tests/e2e',
  use: {
    headless: true,  // MANDATORY - never set to false
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    video: 'off',    // No visual output to avoid interruption
    screenshot: 'only-on-failure',
    trace: 'off'     // No trace UI
  },
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        headless: true  // Enforce headless mode
      },
    },
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        headless: true  // Enforce headless mode
      },
    }
  ],
  // Never launch browsers visually
  webServer: {
    command: 'npm run start:test',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  }
};
```

### Complete User Workflow Testing
```javascript
// tests/e2e/user-authentication-flow.spec.js
const { test, expect } = require('@playwright/test');

test.describe('User Authentication Flow', () => {
  test('should complete full user registration and login workflow', async ({ page }) => {
    // Start at homepage
    await page.goto('/');
    
    // Navigate to registration
    await page.click('[data-testid="register-link"]');
    await expect(page).toHaveURL('/register');
    
    // Complete registration form
    await page.fill('[data-testid="email-input"]', 'newuser@example.com');
    await page.fill('[data-testid="password-input"]', 'SecurePassword123!');
    await page.fill('[data-testid="confirm-password-input"]', 'SecurePassword123!');
    await page.fill('[data-testid="name-input"]', 'John Doe');
    
    // Submit registration
    await page.click('[data-testid="register-submit"]');
    
    // Verify email verification notice
    await expect(page.locator('[data-testid="verification-notice"]')).toBeVisible();
    await expect(page.locator('[data-testid="verification-notice"]'))
      .toContainText('Please check your email');
    
    // Simulate email verification (in test environment)
    const verificationToken = await getTestVerificationToken('newuser@example.com');
    await page.goto(`/verify-email?token=${verificationToken}`);
    
    // Verify successful verification
    await expect(page.locator('[data-testid="verification-success"]')).toBeVisible();
    
    // Navigate to login
    await page.click('[data-testid="login-link"]');
    await expect(page).toHaveURL('/login');
    
    // Complete login
    await page.fill('[data-testid="email-input"]', 'newuser@example.com');
    await page.fill('[data-testid="password-input"]', 'SecurePassword123!');
    await page.click('[data-testid="login-submit"]');
    
    // Verify successful login and dashboard access
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="welcome-message"]'))
      .toContainText('Welcome, John Doe');
    
    // Verify user-specific elements are present
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    await expect(page.locator('[data-testid="logout-option"]')).toBeVisible();
    
    // Test logout functionality
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-option"]');
    
    // Verify logout and redirect
    await expect(page).toHaveURL('/');
    await expect(page.locator('[data-testid="login-link"]')).toBeVisible();
  });
  
  test('should handle invalid login attempts correctly', async ({ page }) => {
    await page.goto('/login');
    
    // Attempt login with invalid credentials
    await page.fill('[data-testid="email-input"]', 'invalid@example.com');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    await page.click('[data-testid="login-submit"]');
    
    // Verify error handling
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]'))
      .toContainText('Invalid email or password');
    
    // Verify user remains on login page
    await expect(page).toHaveURL('/login');
  });
});
```

### E2E Test Organization
```
tests/
├── e2e/
│   ├── auth/
│   │   ├── registration.spec.js
│   │   ├── login.spec.js
│   │   └── password-reset.spec.js
│   ├── core-workflows/
│   │   ├── user-onboarding.spec.js
│   │   ├── product-purchase.spec.js
│   │   └── account-management.spec.js
│   ├── accessibility/
│   │   └── a11y-compliance.spec.js
│   └── performance/
│       └── page-load-times.spec.js
```

### Accessibility Testing with Playwright
```javascript
// tests/e2e/accessibility/a11y-compliance.spec.js
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.describe('Accessibility Compliance', () => {
  test('should meet WCAG 2.1 standards on main pages', async ({ page }) => {
    // Test homepage accessibility
    await page.goto('/');
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
    
    // Test dashboard accessibility (after login)
    await loginAsTestUser(page);
    await page.goto('/dashboard');
    const dashboardScanResults = await new AxeBuilder({ page }).analyze();
    expect(dashboardScanResults.violations).toEqual([]);
  });
});
```

## Testing Strategy Implementation

### Test Execution Pipeline
```bash
# Development workflow testing order
1. Unit tests (fast feedback loop)
   npm run test:unit
   
2. Integration tests (module boundaries)
   npm run test:integration
   
3. E2E tests (complete workflows, headless only)
   npm run test:e2e:headless
   
# CI/CD pipeline (all tests must pass)
npm run test:all
```

### Coverage Requirements
```json
{
  "coverageThreshold": {
    "global": {
      "branches": 80,
      "functions": 80,
      "lines": 80,
      "statements": 80
    },
    "./src/core/": {
      "branches": 90,
      "functions": 90,
      "lines": 90,
      "statements": 90
    },
    "./src/security/": {
      "branches": 95,
      "functions": 95,
      "lines": 95,
      "statements": 95
    }
  }
}
```

### Quality Gates
```bash
# Pre-merge testing checklist
□ All unit tests pass (80%+ coverage for business logic)
□ All integration tests pass (module boundaries verified)
□ All E2E tests pass (headless Playwright only)
□ No test warnings or console errors
□ Performance tests meet benchmarks
□ Accessibility tests pass WCAG 2.1 standards
□ Security tests pass vulnerability scans
```

## Testing Best Practices

### Independent Test Design
- **No shared state** between tests
- **Fresh environment** for each test
- **Deterministic results** - tests should not be flaky
- **Fast execution** - unit tests under 100ms, integration under 1s

### Test Data Management
```python
# Use factories for consistent test data
class TestDataFactory:
    @staticmethod
    def create_user(overrides=None):
        data = {
            "name": "Test User",
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "password": "SecurePassword123!"
        }
        if overrides:
            data.update(overrides)
        return data
    
    @staticmethod
    def create_product(overrides=None):
        data = {
            "name": "Test Product",
            "price": 99.99,
            "category": "electronics",
            "in_stock": True
        }
        if overrides:
            data.update(overrides)
        return data
```

### Human and AI Agent Friendly Testing
- **Clear test names** that describe the scenario
- **Self-documenting assertions** that explain expected behavior
- **Logical test organization** that mirrors application structure
- **Comprehensive error messages** that aid debugging

### Continuous Testing Integration
```yaml
# CI/CD pipeline integration
stages:
  - lint
  - unit-tests
  - integration-tests
  - e2e-tests-headless
  - security-tests
  - performance-tests
  - deploy

unit-tests:
  script:
    - npm run test:unit
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'
  
e2e-tests:
  script:
    - npm run test:e2e:headless  # ALWAYS headless
  artifacts:
    reports:
      junit: test-results/e2e-results.xml
    paths:
      - test-results/screenshots/
    when: on_failure
```
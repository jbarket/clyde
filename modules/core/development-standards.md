# Development Standards

## Test-Driven Development (TDD)

### Red-Green-Refactor Cycle
1. **Red**: Write a failing test that describes the desired functionality
2. **Green**: Write the minimal code to make the test pass
3. **Refactor**: Improve the code while keeping tests passing

### Test-First Approach
- Write tests before implementing functionality
- Tests serve as living documentation
- Tests guide design decisions
- Failing tests prevent regressions

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
- **Integration Tests**: Module boundaries and external dependencies
- **End-to-End Tests**: Complete user workflows using Playwright (headless)

## Unit Testing Standards

### Test Organization
```
tests/
├── unit/
│   ├── models/
│   ├── services/
│   ├── validators/
│   └── utils/
├── integration/
│   ├── database/
│   ├── api/
│   └── external/
└── e2e/
    ├── auth/
    ├── core-workflows/
    └── accessibility/
```

### Test Quality Requirements
- Tests should be fast, independent, and deterministic
- Mock external dependencies for unit tests
- Test edge cases and error conditions
- Use descriptive test names that explain the scenario
- Follow Arrange-Act-Assert pattern

### Coverage Goals
- **Unit Tests**: 80%+ line coverage for business logic
- **Critical Paths**: 100% coverage (authentication, payments, security)
- **Integration Tests**: Cover all module boundaries
- **E2E Tests**: Cover critical user workflows

### Mocking Strategy
```python
class TestAuthService:
    def setup_method(self):
        # Mock all external dependencies
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_password_hasher = Mock(spec=PasswordHasher)
        self.auth_service = AuthService(
            user_repo=self.mock_user_repo,
            password_hasher=self.mock_password_hasher
        )
    
    def test_successful_authentication(self):
        # Arrange
        user = User(id=1, email="test@example.com", is_active=True)
        self.mock_user_repo.find_by_email.return_value = user
        self.mock_password_hasher.verify.return_value = True
        
        # Act
        result = self.auth_service.authenticate("test@example.com", "password")
        
        # Assert
        assert result.success
        assert result.user == user
```

## Integration Testing

### Module Boundary Testing
Integration tests focus on **module boundaries** and **external dependencies**:

```python
class TestUserProductIntegration:
    def setup_method(self):
        # Use real implementations for integration testing
        self.db_session = create_test_database_session()
        self.user_service = UserService(SQLUserRepository(self.db_session))
        self.product_service = ProductService(SQLProductRepository(self.db_session))
    
    def test_user_creation_triggers_product_recommendations(self):
        # Test cross-module integration
        user = self.user_service.create_user({"name": "John", "email": "john@example.com"})
        recommendations = self.product_service.get_welcome_recommendations(user.id)
        assert len(recommendations) > 0
```

## End-to-End Testing with Playwright

### Headless-Only Policy
**Critical Requirement**: All Playwright tests **MUST** run headless

```javascript
// playwright.config.js
module.exports = {
  use: {
    headless: true,  // MANDATORY - never set to false
    video: 'off',    // No visual output
    trace: 'off'     // No trace UI
  },
  projects: [
    {
      name: 'chromium',
      use: { headless: true }  // Enforce headless mode
    }
  ]
};
```

### E2E Test Examples
```javascript
test('should complete user registration workflow', async ({ page }) => {
  // Navigate and complete form
  await page.goto('/register');
  await page.fill('[data-testid="email"]', 'test@example.com');
  await page.fill('[data-testid="password"]', 'SecurePassword123');
  await page.click('[data-testid="register-button"]');
  
  // Verify success
  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
});
```

## Quality Gates

### Pre-Merge Requirements
```bash
□ All unit tests pass (80%+ coverage for business logic)
□ All integration tests pass (module boundaries verified)
□ All E2E tests pass (headless Playwright only)
□ Linting passes with zero errors and warnings
□ No console errors or debugging statements
□ Code review approved
□ Documentation updated if needed
```

### Test Execution Pipeline
```bash
# Development workflow
npm run test:unit           # Fast feedback loop
npm run test:integration    # Module boundaries
npm run test:e2e:headless   # Complete workflows

# CI/CD pipeline
npm run test:all           # All tests must pass
```

### Coverage Thresholds
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

## Test Data Management

### Factory Pattern
```python
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
```

## Accessibility Testing
```javascript
// A11y compliance testing
test('should meet WCAG 2.1 standards', async ({ page }) => {
  await page.goto('/');
  const scanResults = await new AxeBuilder({ page }).analyze();
  expect(scanResults.violations).toEqual([]);
});
```

## Performance Testing
```python
def test_operation_performance():
    start_time = time.time()
    result = expensive_operation()
    duration = time.time() - start_time
    
    assert duration < 1.0  # Should complete in less than 1 second
    assert result is not None
```

## Best Practices

### Independent Test Design
- **No shared state** between tests
- **Fresh environment** for each test
- **Deterministic results** - tests should not be flaky
- **Fast execution** - unit tests under 100ms, integration under 1s

### Continuous Testing Integration
```yaml
# CI/CD pipeline
stages:
  - lint
  - unit-tests
  - integration-tests
  - e2e-tests-headless
  - deploy

e2e-tests:
  script:
    - npm run test:e2e:headless  # ALWAYS headless
  artifacts:
    paths:
      - test-results/screenshots/
    when: on_failure
```
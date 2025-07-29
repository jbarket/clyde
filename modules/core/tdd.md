# Test-Driven Development (TDD)

## Core Principles

### Red-Green-Refactor Cycle
1. **Red**: Write a failing test that describes the desired functionality
2. **Green**: Write the minimal code to make the test pass
3. **Refactor**: Improve the code while keeping tests passing

### Test-First Approach
- Write tests before implementing functionality
- Tests serve as living documentation
- Tests guide design decisions
- Failing tests prevent regressions

## Testing Standards

### Test Organization
- One test file per module/class
- Group related tests in test classes
- Use descriptive test names that explain the scenario
- Follow the Arrange-Act-Assert pattern

### Test Quality
- Tests should be fast, independent, and deterministic
- Mock external dependencies
- Test edge cases and error conditions
- Maintain test code with the same quality as production code

### Coverage Goals
- Aim for high test coverage (80%+ line coverage)
- Focus on critical paths and complex logic
- Don't sacrifice test quality for coverage numbers
- Use coverage tools to identify untested code

## Best Practices

### Writing Good Tests
```python
def test_should_calculate_total_price_with_tax():
    # Arrange
    item = Item(price=100.0)
    tax_rate = 0.08
    
    # Act
    total = calculate_total_with_tax(item, tax_rate)
    
    # Assert
    assert total == 108.0
```

### Test Data Management
- Use factories or builders for test data
- Keep test data minimal and focused
- Use realistic but not production data
- Consider using fixtures for common setup

### Continuous Testing
- Run tests frequently during development
- Use test watchers for immediate feedback
- Integrate tests into CI/CD pipeline
- Never commit code with failing tests
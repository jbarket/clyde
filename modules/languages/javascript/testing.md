# JavaScript Testing Guidelines

## Testing Framework Setup

### Jest Configuration
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom', // for React components
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/index.js',
    '!src/**/*.d.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### Testing Library Setup
```javascript
// setupTests.js
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

configure({ testIdAttribute: 'data-testid' });

// Mock global objects
global.fetch = require('jest-fetch-mock');

// Suppress console warnings in tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (typeof args[0] === 'string' && args[0].includes('Warning:')) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});
```

## Unit Testing Patterns

### Testing Pure Functions
```javascript
// math.js
export const add = (a, b) => a + b;
export const calculateTotal = (items) => 
  items.reduce((sum, item) => sum + item.price, 0);

// math.test.js
import { add, calculateTotal } from './math';

describe('Math utilities', () => {
  describe('add', () => {
    test('should add two positive numbers', () => {
      expect(add(2, 3)).toBe(5);
    });

    test('should handle negative numbers', () => {
      expect(add(-1, 1)).toBe(0);
    });

    test('should handle zero', () => {
      expect(add(0, 5)).toBe(5);
    });
  });

  describe('calculateTotal', () => {
    test('should calculate total price of items', () => {
      const items = [
        { price: 10 },
        { price: 20 },
        { price: 5 }
      ];
      
      expect(calculateTotal(items)).toBe(35);
    });

    test('should return 0 for empty array', () => {
      expect(calculateTotal([])).toBe(0);
    });
  });
});
```

### Testing Classes and Objects
```javascript
// UserService.js
export class UserService {
  constructor(apiClient) {
    this.apiClient = apiClient;
  }

  async getUser(id) {
    const response = await this.apiClient.get(`/users/${id}`);
    return response.data;
  }

  validateEmail(email) {
    return email.includes('@') && email.includes('.');
  }
}

// UserService.test.js
import { UserService } from './UserService';

describe('UserService', () => {
  let userService;
  let mockApiClient;

  beforeEach(() => {
    mockApiClient = {
      get: jest.fn()
    };
    userService = new UserService(mockApiClient);
  });

  describe('getUser', () => {
    test('should fetch user data', async () => {
      const userData = { id: 1, name: 'John Doe' };
      mockApiClient.get.mockResolvedValue({ data: userData });

      const result = await userService.getUser(1);

      expect(result).toEqual(userData);
      expect(mockApiClient.get).toHaveBeenCalledWith('/users/1');
    });

    test('should handle API errors', async () => {
      mockApiClient.get.mockRejectedValue(new Error('Network error'));

      await expect(userService.getUser(1)).rejects.toThrow('Network error');
    });
  });

  describe('validateEmail', () => {
    test('should validate correct email', () => {
      expect(userService.validateEmail('test@example.com')).toBe(true);
    });

    test('should reject invalid email', () => {
      expect(userService.validateEmail('invalid-email')).toBe(false);
    });
  });
});
```

## React Component Testing

### Testing Components with React Testing Library
```javascript
// Button.jsx
import React from 'react';

export const Button = ({ onClick, disabled, children, variant = 'primary' }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant}`}
      data-testid="button"
    >
      {children}
    </button>
  );
};

// Button.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  test('should render button with text', () => {
    render(<Button>Click me</Button>);
    
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  test('should call onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('should be disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    
    expect(screen.getByRole('button')).toBeDisabled();
  });

  test('should apply variant class', () => {
    render(<Button variant="secondary">Click me</Button>);
    
    expect(screen.getByRole('button')).toHaveClass('btn-secondary');
  });
});
```

### Testing Hooks
```javascript
// useCounter.js
import { useState, useCallback } from 'react';

export const useCounter = (initialValue = 0) => {
  const [count, setCount] = useState(initialValue);

  const increment = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);

  const decrement = useCallback(() => {
    setCount(prev => prev - 1);
  }, []);

  const reset = useCallback(() => {
    setCount(initialValue);
  }, [initialValue]);

  return { count, increment, decrement, reset };
};

// useCounter.test.js
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  test('should initialize with default value', () => {
    const { result } = renderHook(() => useCounter());
    
    expect(result.current.count).toBe(0);
  });

  test('should initialize with custom value', () => {
    const { result } = renderHook(() => useCounter(10));
    
    expect(result.current.count).toBe(10);
  });

  test('should increment count', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });

  test('should decrement count', () => {
    const { result } = renderHook(() => useCounter(5));
    
    act(() => {
      result.current.decrement();
    });
    
    expect(result.current.count).toBe(4);
  });

  test('should reset to initial value', () => {
    const { result } = renderHook(() => useCounter(5));
    
    act(() => {
      result.current.increment();
      result.current.increment();
    });
    
    expect(result.current.count).toBe(7);
    
    act(() => {
      result.current.reset();
    });
    
    expect(result.current.count).toBe(5);
  });
});
```

## Mocking Strategies

### Module Mocking
```javascript
// api.js
export const fetchUser = async (id) => {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
};

// component.test.js
import { fetchUser } from './api';

// Mock the entire module
jest.mock('./api', () => ({
  fetchUser: jest.fn()
}));

describe('Component with API calls', () => {
  test('should handle successful API call', async () => {
    const userData = { id: 1, name: 'John' };
    fetchUser.mockResolvedValue(userData);

    // Test component that uses fetchUser
    // ...
  });
});
```

### Spy on Methods
```javascript
describe('LocalStorage interaction', () => {
  test('should save data to localStorage', () => {
    const setItemSpy = jest.spyOn(Storage.prototype, 'setItem');
    
    saveUserPreferences({ theme: 'dark' });
    
    expect(setItemSpy).toHaveBeenCalledWith(
      'userPreferences',
      JSON.stringify({ theme: 'dark' })
    );
    
    setItemSpy.mockRestore();
  });
});
```

## Async Testing

### Testing Promises and Async Functions
```javascript
describe('Async operations', () => {
  test('should resolve with data', async () => {
    const data = await fetchData();
    expect(data).toBeDefined();
  });

  test('should reject with error', async () => {
    await expect(fetchInvalidData()).rejects.toThrow('Invalid data');
  });

  test('should handle timeout', async () => {
    jest.useFakeTimers();
    
    const promise = fetchWithTimeout();
    
    jest.advanceTimersByTime(5000);
    
    await expect(promise).rejects.toThrow('Timeout');
    
    jest.useRealTimers();
  });
});
```

## Integration Testing

### Testing with MSW (Mock Service Worker)
```javascript
// handlers.js
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/users/:id', (req, res, ctx) => {
    const { id } = req.params;
    
    return res(
      ctx.json({
        id: parseInt(id),
        name: 'John Doe',
        email: 'john@example.com'
      })
    );
  }),

  rest.post('/api/users', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({ message: 'User created successfully' })
    );
  })
];

// integration.test.js
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('User API integration', () => {
  test('should fetch user data', async () => {
    const response = await fetch('/api/users/1');
    const user = await response.json();
    
    expect(user.name).toBe('John Doe');
  });
});
```
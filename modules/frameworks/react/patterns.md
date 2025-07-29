# React Patterns and Best Practices

## Component Design Patterns

### Composition over Inheritance
```tsx
// Good: Composition pattern
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
};

// Usage - compose different modal content
const ConfirmModal = ({ isOpen, onClose, onConfirm, message }) => (
  <Modal isOpen={isOpen} onClose={onClose}>
    <div className="p-6">
      <p className="mb-4">{message}</p>
      <div className="flex gap-2">
        <Button onClick={onConfirm}>Confirm</Button>
        <Button variant="secondary" onClick={onClose}>Cancel</Button>
      </div>
    </div>
  </Modal>
);
```

### Render Props Pattern
```tsx
interface DataFetcherProps<T> {
  url: string;
  children: (data: {
    data: T | null;
    loading: boolean;
    error: Error | null;
    refetch: () => void;
  }) => React.ReactNode;
}

function DataFetcher<T>({ url, children }: DataFetcherProps<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(url);
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return <>{children({ data, loading, error, refetch: fetchData })}</>;
}

// Usage
const UserList = () => (
  <DataFetcher<User[]> url="/api/users">
    {({ data, loading, error, refetch }) => {
      if (loading) return <div>Loading...</div>;
      if (error) return <div>Error: {error.message}</div>;
      if (!data) return <div>No data</div>;

      return (
        <div>
          <Button onClick={refetch}>Refresh</Button>
          {data.map(user => (
            <UserCard key={user.id} user={user} />
          ))}
        </div>
      );
    }}
  </DataFetcher>
);
```

### Higher-Order Components (HOCs)
```tsx
// HOC for authentication
function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>
) {
  return function WithAuthComponent(props: P) {
    const { user, loading } = useAuth();

    if (loading) {
      return <div>Loading...</div>;
    }

    if (!user) {
      return <Navigate to="/login" replace />;
    }

    return <WrappedComponent {...props} />;
  };
}

// Usage
const ProtectedPage = withAuth(({ user }: { user: User }) => (
  <div>Welcome, {user.name}!</div>
));
```

## State Management Patterns

### Context + Reducer Pattern
```tsx
// State management for complex forms
interface FormState {
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
}

type FormAction =
  | { type: 'SET_FIELD_VALUE'; field: string; value: any }
  | { type: 'SET_FIELD_ERROR'; field: string; error: string }
  | { type: 'SET_FIELD_TOUCHED'; field: string }
  | { type: 'SET_SUBMITTING'; isSubmitting: boolean }
  | { type: 'RESET_FORM' };

const formReducer = (state: FormState, action: FormAction): FormState => {
  switch (action.type) {
    case 'SET_FIELD_VALUE':
      return {
        ...state,
        values: { ...state.values, [action.field]: action.value },
        errors: { ...state.errors, [action.field]: '' },
      };
    case 'SET_FIELD_ERROR':
      return {
        ...state,
        errors: { ...state.errors, [action.field]: action.error },
      };
    case 'SET_FIELD_TOUCHED':
      return {
        ...state,
        touched: { ...state.touched, [action.field]: true },
      };
    case 'SET_SUBMITTING':
      return { ...state, isSubmitting: action.isSubmitting };
    case 'RESET_FORM':
      return {
        values: {},
        errors: {},
        touched: {},
        isSubmitting: false,
      };
    default:
      return state;
  }
};

const FormContext = createContext<{
  state: FormState;
  dispatch: React.Dispatch<FormAction>;
} | null>(null);

export const useForm = () => {
  const context = useContext(FormContext);
  if (!context) {
    throw new Error('useForm must be used within FormProvider');
  }
  return context;
};

export const FormProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [state, dispatch] = useReducer(formReducer, {
    values: {},
    errors: {},
    touched: {},
    isSubmitting: false,
  });

  return (
    <FormContext.Provider value={{ state, dispatch }}>
      {children}
    </FormContext.Provider>
  );
};
```

### Custom Hooks for Logic Reuse
```tsx
// Custom hook for API calls
function useApi<T>(url: string | null) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async () => {
    if (!url) return;

    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get<T>(url);
      setData(response);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => {
    execute();
  }, [execute]);

  return { data, loading, error, refetch: execute };
}

// Custom hook for form validation
function useValidation<T extends Record<string, any>>(
  values: T,
  validationRules: Record<keyof T, (value: any) => string | null>
) {
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});

  const validate = useCallback(() => {
    const newErrors: Partial<Record<keyof T, string>> = {};
    let isValid = true;

    Object.keys(validationRules).forEach((field) => {
      const rule = validationRules[field as keyof T];
      const error = rule(values[field as keyof T]);
      if (error) {
        newErrors[field as keyof T] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  }, [values, validationRules]);

  return { errors, validate, isValid: Object.keys(errors).length === 0 };
}
```

## Performance Optimization Patterns

### Memoization Strategies
```tsx
// Memoize expensive calculations
const ExpensiveComponent: React.FC<{ items: Item[] }> = ({ items }) => {
  const expensiveValue = useMemo(() => {
    return items.reduce((acc, item) => {
      // Complex calculation
      return acc + item.price * item.quantity;
    }, 0);
  }, [items]);

  return <div>Total: ${expensiveValue}</div>;
};

// Memoize callback functions
const TodoList: React.FC<{ todos: Todo[] }> = ({ todos }) => {
  const [filter, setFilter] = useState('all');

  const handleToggle = useCallback((id: string) => {
    // Toggle todo logic
  }, []);

  const handleDelete = useCallback((id: string) => {
    // Delete todo logic
  }, []);

  const filteredTodos = useMemo(() => {
    return todos.filter(todo => {
      if (filter === 'completed') return todo.completed;
      if (filter === 'active') return !todo.completed;
      return true;
    });
  }, [todos, filter]);

  return (
    <div>
      {filteredTodos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={handleToggle}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
};

// Memoize components
const TodoItem = React.memo<{
  todo: Todo;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}>(({ todo, onToggle, onDelete }) => {
  return (
    <div className="todo-item">
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id)}
      />
      <span>{todo.text}</span>
      <button onClick={() => onDelete(todo.id)}>Delete</button>
    </div>
  );
});
```

### Lazy Loading and Code Splitting
```tsx
// Lazy load components
const LazyUserProfile = lazy(() => import('./UserProfile'));
const LazyAdminPanel = lazy(() => import('./AdminPanel'));

const App = () => (
  <Router>
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/profile" element={<LazyUserProfile />} />
        <Route path="/admin" element={<LazyAdminPanel />} />
      </Routes>
    </Suspense>
  </Router>
);

// Dynamic imports with error boundaries
const useDynamicImport = (importFunc: () => Promise<any>) => {
  const [component, setComponent] = useState<React.ComponentType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    importFunc()
      .then((module) => {
        setComponent(() => module.default);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  }, [importFunc]);

  return { component, loading, error };
};
```

## Error Handling Patterns

### Error Boundaries
```tsx
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{
    fallback?: React.ComponentType<{ error: Error; resetError: () => void }>;
    onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  }>,
  ErrorBoundaryState
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      return (
        <FallbackComponent
          error={this.state.error!}
          resetError={this.resetError}
        />
      );
    }

    return this.props.children;
  }
}

const DefaultErrorFallback: React.FC<{
  error: Error;
  resetError: () => void;
}> = ({ error, resetError }) => (
  <div className="error-boundary">
    <h2>Something went wrong:</h2>
    <pre>{error.message}</pre>
    <button onClick={resetError}>Try again</button>
  </div>
);
```

### Async Error Handling
```tsx
// Hook for handling async operations with error states
function useAsyncOperation<T>() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async (asyncFn: () => Promise<T>) => {
    try {
      setLoading(true);
      setError(null);
      const result = await asyncFn();
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setError(null);
    setLoading(false);
  }, []);

  return { execute, loading, error, reset };
}

// Usage in component
const UserForm = () => {
  const { execute, loading, error, reset } = useAsyncOperation<User>();

  const handleSubmit = async (formData: CreateUserData) => {
    try {
      await execute(() => userService.createUser(formData));
      // Handle success
    } catch (error) {
      // Error is already set in the hook
      console.error('Failed to create user:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div className="error-message">
          {error.message}
          <button onClick={reset}>Dismiss</button>
        </div>
      )}
      {/* Form fields */}
      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create User'}
      </button>
    </form>
  );
};
```
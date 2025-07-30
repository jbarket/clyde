# React Development Guidelines

## React Project Structure

### Standard Directory Layout
- `src/{components,pages,hooks,contexts,services,utils,types}/`
- `src/components/{ComponentName/{index.tsx,ComponentName.tsx,ComponentName.test.tsx,ComponentName.module.css}}`
- `public/{index.html,favicon.ico,manifest.json}`
- `src/{App.tsx,index.tsx,setupTests.ts}`

## Core Patterns

### Component Organization
- Use functional components with hooks over class components
- Create custom hooks for reusable stateful logic
- Separate container components (data) from presentational components (UI)
- Use TypeScript for all components with proper interface definitions

### State Management
- Use useState for local component state
- Use useReducer for complex state logic with multiple sub-values
- Use Context API for global state that doesn't change frequently
- Consider Redux Toolkit for complex application state management

### Props and TypeScript
- Define interface for all component props
- Use optional props with default values where appropriate
- Avoid prop drilling by using Context or state management libraries
- Use generic types for reusable components

## Hook Patterns

### Built-in Hooks
- useState: Local component state management
- useEffect: Side effects, API calls, subscriptions
- useContext: Access context values without prop drilling
- useMemo: Expensive calculations with dependency array
- useCallback: Memoize function references to prevent unnecessary re-renders
- useRef: Access DOM elements or persist values across renders

### Custom Hooks
- Extract component logic into reusable custom hooks
- Use "use" prefix for custom hook naming
- Return objects or arrays for multiple values
- Handle cleanup in useEffect return functions

## Performance Optimization

### Re-render Optimization
- Use React.memo for expensive functional components
- Use useMemo for expensive calculations
- Use useCallback for function props to prevent child re-renders
- Avoid creating objects/functions in render methods

### Code Splitting
- Use React.lazy() for component-level code splitting
- Wrap with Suspense and provide fallback UI
- Split routes for page-level code splitting
- Consider bundle analysis to identify large dependencies

### List Optimization
- Always use stable, unique keys for list items
- Consider virtualization for very long lists
- Avoid array index as key when order can change

## State Management Patterns

### Local State
- Use useState for simple state values
- Use useReducer for state objects with multiple related values
- Lift state up only when multiple components need access
- Use state colocation to keep state close to where it's used

### Global State
- Use Context API for infrequently changing global state
- Create separate contexts for different domains
- Use useReducer with Context for complex global state
- Consider Redux Toolkit for complex state with time-travel debugging

### Server State
- Use React Query or SWR for server state management
- Implement proper caching strategies for API data
- Handle loading states, error states, and optimistic updates
- Use background refetching for fresh data

## Component Patterns

### Composition Patterns
- Use children prop for flexible component composition
- Create compound components for related UI elements
- Use render props pattern for flexible component behavior
- Implement higher-order components sparingly

### Form Handling
- Use controlled components for form inputs
- Consider React Hook Form for complex forms with validation
- Implement proper error handling and user feedback
- Use debouncing for search inputs and expensive validations

### Error Boundaries
- Implement error boundaries for graceful error handling
- Provide fallback UI for component errors
- Log errors for debugging and monitoring
- Use error boundaries at route level and critical component level

## Testing Patterns

### Component Testing
- Use React Testing Library for component testing
- Test user interactions rather than implementation details
- Use screen queries (getByRole, getByText) over container queries
- Mock external dependencies and API calls

### Hook Testing
- Use @testing-library/react-hooks for custom hook testing
- Test hook behavior in isolation from components
- Verify hook state changes and side effects
- Test error conditions and edge cases

## Styling Approaches

### CSS Strategies
- Use CSS Modules for component-scoped styles
- Consider styled-components for CSS-in-JS approach
- Use Tailwind CSS for utility-first styling
- Implement consistent design system with CSS custom properties

### Responsive Design
- Use CSS Grid and Flexbox for layout
- Implement mobile-first responsive design
- Use CSS custom properties for dynamic theming
- Consider CSS Container Queries for component-level responsiveness

## Performance Monitoring

### Profiling
- Use React DevTools Profiler for performance analysis
- Identify unnecessary re-renders and expensive operations
- Monitor component render frequency and duration
- Use Performance API for custom performance metrics

### Bundle Optimization
- Analyze bundle size with webpack-bundle-analyzer
- Implement tree shaking for unused code elimination
- Use dynamic imports for code splitting
- Optimize image loading with lazy loading and WebP format

## Accessibility

### ARIA and Semantic HTML
- Use semantic HTML elements for proper document structure
- Implement ARIA attributes for complex interactions
- Ensure proper focus management for keyboard navigation
- Test with screen readers and accessibility tools

### Form Accessibility
- Associate labels with form controls
- Provide error messages and validation feedback
- Use fieldset and legend for form grouping
- Implement proper tab order and keyboard navigation

## Development Workflow

### Development Tools
- Use React DevTools for component inspection and profiling
- Set up ESLint with React-specific rules
- Use Prettier for consistent code formatting
- Implement pre-commit hooks for code quality

### Build Optimization
- Use Create React App or Vite for optimal build configuration
- Implement proper environment variable management
- Configure source maps for production debugging
- Set up proper build caching strategies
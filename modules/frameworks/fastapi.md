# FastAPI Development Guidelines

## FastAPI Project Structure

### Standard Directory Layout
- `src/myapp/{main.py,config.py,dependencies.py,database.py}`
- `src/myapp/models/` - SQLAlchemy models
- `src/myapp/schemas/` - Pydantic schemas for request/response
- `src/myapp/crud/` - Database operations
- `src/myapp/api/api_v1/endpoints/` - Route handlers
- `src/myapp/core/` - Security, config, exceptions
- `tests/` - Test files mirroring src structure
- `alembic/` - Database migrations

## Core Patterns

### Application Factory
- Use factory function to create FastAPI app with configuration
- Add CORS middleware for cross-origin requests
- Include API routers with version prefixes
- Set up startup/shutdown event handlers

### Configuration Management
- Use Pydantic BaseSettings for environment-based config
- Cache settings with @lru_cache() decorator
- Define database URLs, security keys, and external service URLs
- Load from .env files with case_sensitive = True

## Data Layer Organization

### Database Models
- Use SQLAlchemy declarative_base for model base class
- Create TimestampMixin with created_at/updated_at fields
- Define models with proper __tablename__, primary keys, and indexes
- Use Column types: Integer, String, Boolean, DateTime, etc.

### Pydantic Schemas  
- Separate schemas: Base, Create, Update, InDB
- Use EmailStr, Field validation with min_length/max_length
- Set from_attributes = True in Config for ORM compatibility
- Use Optional[] for update schema fields

### CRUD Operations
- Create generic CRUDBase class with TypeVar for model types
- Implement standard methods: get, get_multi, create, update, delete
- Extend base CRUD for model-specific operations (e.g., get_by_email)
- Use Session dependency injection for database operations

## API Layer Organization

### Router Structure
- Create api_router that includes all endpoint routers
- Organize endpoints by domain (users, auth, etc.) with appropriate prefixes and tags
- Use APIRouter() for each domain module

### Endpoint Implementation
- Use dependency injection for database sessions and current user
- Set response_model for automatic serialization and documentation
- Include docstrings for OpenAPI documentation
- Handle business logic in CRUD layer, not in endpoints

## Dependencies

### Database Dependencies
- Create engine with SQLAlchemy using DATABASE_URL from settings
- Use sessionmaker with autocommit=False, autoflush=False
- Implement get_db() generator that yields session and closes on completion

### Authentication Dependencies
- Use HTTPBearer security for token authentication
- Create get_current_user dependency that decodes JWT and fetches user
- Create get_current_active_user that checks user.is_active status
- Raise HTTP 401 for invalid tokens, HTTP 400 for inactive users

### Permission Dependencies
- Create RequirePermissions class that accepts permission strings
- Check user.is_superuser or validate user has required permissions
- Raise HTTP 403 for insufficient permissions
- Use as dependency: Depends(RequirePermissions("delete_user"))

## Error Handling

### Custom Exceptions
- Create domain-specific HTTPException subclasses
- Include meaningful error messages and appropriate status codes
- Use consistent error response format across the API

### Global Exception Handlers
- Register exception handlers with @app.exception_handler()
- Handle validation errors, database errors, and custom exceptions
- Log errors appropriately and return user-friendly messages

## Security Patterns

### JWT Authentication
- Use python-jose for JWT token creation and validation
- Include user ID in token subject and expiration time
- Implement token refresh mechanism for long-lived sessions

### Password Security
- Use passlib with bcrypt for password hashing
- Never store plain text passwords
- Implement password strength validation

### CORS Configuration
- Configure allowed origins based on environment
- Use specific origins in production, avoid wildcard "*"
- Set appropriate allowed methods and headers

## Testing Patterns

### Test Setup
- Use pytest with pytest-asyncio for async testing
- Create test database with PostgreSQL TestContainers
- Use dependency overrides for test database and authentication

### API Testing
- Test endpoints with TestClient from fastapi.testclient
- Test authentication flows and permission checks
- Verify response models and status codes
- Test error conditions and edge cases

## Performance Optimization

### Database Optimization
- Use async SQLAlchemy for better concurrency
- Implement connection pooling with appropriate pool sizes
- Use database indexes on frequently queried columns
- Consider read replicas for heavy read workloads

### Caching Strategies
- Use Redis for session storage and frequently accessed data
- Implement response caching for slow endpoints
- Cache expensive database queries with appropriate TTL

### Background Tasks
- Use FastAPI background tasks for simple async operations
- Consider Celery for complex background job processing
- Implement proper error handling and retry logic

## Deployment Considerations

### Production Setup
- Use Gunicorn with Uvicorn workers for production deployment
- Configure proper logging levels and structured logging
- Set up health check endpoints for load balancer monitoring

### Environment Configuration
- Use separate configuration for development, staging, production
- Secure secret management with environment variables or secret managers
- Configure database connection pooling based on expected load

### Monitoring and Observability
- Implement request/response logging with correlation IDs
- Use metrics collection for performance monitoring
- Set up error tracking and alerting systems
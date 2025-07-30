# PostgreSQL Guidelines

## Database Design
- Use meaningful names with snake_case conventions
- Choose appropriate data types and define proper constraints
- Always use migrations for schema changes, make them reversible
- Test migrations on staging before production
- Document schema with comments

## Connection Management
- Use connection pooling (SQLAlchemy QueuePool) for performance
- Configure pool_size, max_overflow, pool_pre_ping, pool_recycle appropriately
- Use context managers (with db.begin()) for transaction management
- Implement proper error handling and rollback strategies
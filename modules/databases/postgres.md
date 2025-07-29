# PostgreSQL Guidelines

## Database Design Patterns

### Schema Organization
- Use meaningful table and column names
- Follow consistent naming conventions (snake_case)
- Use appropriate data types
- Define proper constraints and indexes
- Document schema with comments

### Migration Best Practices
```sql
-- Always use migrations for schema changes
-- Make migrations reversible when possible
-- Test migrations on staging before production

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

## Connection Management

### Connection Pooling
```python
# Use connection pooling for better performance
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Transaction Management
```python
# Use context managers for transactions
with db.begin() as trans:
    user = User(email=email)
    db.add(user)
    profile = Profile(user_id=user.id)
    db.add(profile)
    # Auto-commit or rollback
```
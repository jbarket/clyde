# Docker Best Practices

## Dockerfile Optimization

### Multi-stage Builds
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Production stage
FROM node:18-alpine AS production
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### Layer Optimization
- Order layers from least to most frequently changing
- Use .dockerignore to exclude unnecessary files
- Combine RUN commands to reduce layers
- Use specific base image tags

```dockerfile
# Good layer ordering
FROM python:3.11-slim

# Install system dependencies first (changes rarely)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (changes less than source code)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code last (changes frequently)
COPY . .

CMD ["python", "app.py"]
```

## Docker Compose

### Development Environment
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```
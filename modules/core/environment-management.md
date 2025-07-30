# Environment Management

## Environment Setup

### Environment Loading
- Use `.env` files for environment-specific configuration
- Load with `dotenv` package or similar
- Validate required environment variables at startup

## Docker Environment

### Docker Setup
- Use multi-stage builds for production
- Install dependencies before copying source for better caching
- Run as non-root user for security
- Use docker-compose for local development with services

## Version Management

### Version Management
- Pin specific Node.js/Python versions in `package.json`/`pyproject.toml` 
- Use `.nvmrc`/`.python-version` for development consistency
- Specify minimum versions in engines/requires sections

## Dependency Management

### Package Lock Files
- **Node.js**: Always commit `package-lock.json`
- **Python**: Always commit `poetry.lock` or `Pipfile.lock`
- **Use exact versions** for critical dependencies

### Security Updates
- Run `npm audit fix` or `poetry audit` regularly  
- Use automated dependency update tools like `npm-check-updates`

## Environment Variables

### Environment Variables
- Validate required environment variables at application startup
- Use schema validation libraries like Joi, Zod, or Pydantic
- Never commit secrets to version control

## Environment Consistency

### Development Scripts
- Include standard scripts: `dev`, `build`, `test`, `lint`, `format`
- Use environment variables for different configurations
- Create setup scripts for new developers

### Database Migrations
- Use migration tools (Knex, Alembic, Flyway) for schema changes
- Always include both `up` and `down` migrations
- Test migrations on copy of production data

## Cross-Platform Support

### Cross-Platform Support
- Use `path.join()` instead of hardcoded path separators
- Handle differences between Unix and Windows environments
- Test shell scripts on target platforms or use cross-platform alternatives

## Environment Testing

### Configuration Testing
- Test configuration loading in different environments
- Validate all required environment variables are present
- Verify environment-specific values are correct


## Key Principles

- **Environment Parity** - dev/staging/prod as similar as possible
- **Config in Environment** - never hardcode configuration
- **Secrets Management** - never commit secrets to version control
- **Dependency Locking** - exact versions for reproducible builds
- **Health Checks** - verify environment setup automatically
- **Documentation** - clear setup instructions for new developers
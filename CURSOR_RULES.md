# Cursor Development Rules for AI-Powered Student Counseling Platform

This document outlines the development rules configured in the `.cursor.json` file for our project. These rules help enforce consistency, best practices, and maintain high code quality.

> **Note:** These Cursor rules are specific to this project only and will not affect any other projects on your system.

## Project Scope

These rules apply only to:
- Project Name: AI-Powered Student Counseling Platform
- Project Files: All files within the project directory
- Excluded: `node_modules`, `venv`, `env`, `.venv`, `__pycache__`

## Project Structure

- **Backend**: All code is organized within the `app/` directory
  - Models: `app/models/`
  - Schemas: `app/schemas/`
  - Routers: `app/routers/`
  - Services: `app/services/`
  - Tests: `app/tests/`
  - All API routes use the `/api` prefix

## Coding Standards

### Python
- Follow PEP 8 guidelines
- Use type hints for all functions and variables
- Include docstrings for all functions, classes, and modules
- Keep functions small and focused (max 50 lines)
- Use meaningful variable and function names

### FastAPI
- Use Pydantic models for data validation
- Implement proper error handling
- Document all API endpoints
- Follow RESTful principles

## API Integration

### URL Handling
- Handle trailing slashes in URLs
- Validate complete URL paths
- Log URL attempts during development

### Error Handling
- Provide comprehensive error messages
- Include debugging information in development
- Handle connection errors gracefully
- Log failed API attempts

## Environment Configuration

### Development
- Use `.env` files for local development
- Set default values for non-critical variables
- Document all environment variables
- Include example configurations in `.env.example`

### Production
- Use platform-specific secrets management
- Handle missing variables gracefully
- Provide fallback configurations
- Validate required variables

## Data Management

### Storage
- Use atomic operations for file writes
- Validate data before saving
- Implement proper error handling
- Keep backups of important data

### Environment Variables
- Use `python-dotenv` for development
- Never commit sensitive data
- Document all required variables

## Testing

- Write unit tests for models
- Test API endpoints
- Mock external services
- Test error conditions
- Validate URL paths

## Security

- Never commit secrets
- Use environment variables for sensitive information
- Validate all user input
- Protect sensitive routes with authentication
- Implement rate limiting
- Log API usage

## Performance

- Use async operations where appropriate
- Implement caching strategies
- Optimize database queries
- Handle timeouts properly

## File Templates

The Cursor configuration includes templates for:
- Models
- Schemas
- Routers
- Services
- Tests

These templates provide consistent structure and patterns for new files. Use them when creating new components.

## Using Templates

To use a template in Cursor, create a new file with the appropriate name pattern and Cursor will apply the template automatically.

Example: Creating a new model file named `course.py` will generate a fully structured model class with proper imports, methods, and error handling. 
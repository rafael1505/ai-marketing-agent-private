# Contributing to AI Marketing Agent

Welcome! This guide will help you understand the project structure and how to contribute effectively.

## 📁 Project Structure

Our project follows a clean, organized structure. Please maintain this organization when adding new files.

### Root Directory
The root directory should contain **ONLY** essential configuration files:
- `Dockerfile` - Production Docker configuration
- `docker-compose.yml` - Docker orchestration
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation
- `CONTRIBUTING.md` - This file
- `provider_configs.json` - AI provider configurations
- Configuration files (`.env`, `.gitignore`, etc.)

**⚠️ DO NOT** add test files, scripts, or documentation to the root directory.

### Directory Structure

```
ai-marketing-agent/
├── app/                    # Backend FastAPI application
│   ├── api/               # API endpoints
│   ├── core/              # Core functionality (config, auth, i18n)
│   ├── db/                # Database models and connections
│   ├── models/            # Pydantic models
│   └── services/          # Business logic services
├── frontend/              # Next.js frontend application
│   ├── src/
│   │   ├── app/          # Next.js app directory
│   │   ├── components/   # React components
│   │   ├── i18n/         # Internationalization
│   │   └── services/     # Frontend services
│   └── public/           # Static assets
├── scripts/              # Development and deployment scripts
├── tests/                # All test files
│   ├── unit/            # Unit tests (isolated function tests)
│   ├── integration/     # Integration tests (API, database tests)
│   ├── e2e/             # End-to-end workflow tests
│   └── frontend/        # Frontend tests (HTML, JavaScript)
├── docs/                 # Documentation files
├── debug/                # Debugging utilities and scripts
│   └── archive/         # Old debug files
└── archive/              # Historical files and old implementations
```

## 📝 File Organization Guidelines

### Where to Place New Files

#### Shell Scripts
- **Location:** `/scripts`
- **Naming:** Use descriptive kebab-case names
- **Examples:** `start-backend.sh`, `restart-services.sh`, `check-ports.sh`
- **Make executable:** `chmod +x scripts/your-script.sh`

#### Test Files
- **Location:** `/tests` with appropriate subdirectory
- **Unit Tests:** `/tests/unit/` - Test individual functions/classes
  - Examples: `test_bcrypt.py`, `test_formdata.py`, `test_hash.py`
- **Integration Tests:** `/tests/integration/` - Test API endpoints, database operations
  - Examples: `test_api.py`, `test_company_api.py`, `test_persistence.py`
- **E2E Tests:** `/tests/e2e/` - Test complete workflows
  - Examples: `test_workflow.py`, `test_comprehensive.py`, `e2e_company_test.py`
- **Frontend Tests:** `/tests/frontend/` - HTML, JavaScript, browser tests
  - Examples: `test-frontend-api.js`, `material-test.html`

#### Documentation
- **Location:** `/docs`
- **Naming:** Use descriptive kebab-case with `.md` extension
- **Types:**
  - Implementation summaries: `feature-name-implementation.md`
  - Fix reports: `issue-name-fix-summary.md`
  - Guides: `feature-name-guide.md`
  - Architecture docs: `system-architecture.md`

#### Debug Scripts
- **Location:** `/debug`
- **Naming:** Prefix with `debug_` for clarity
- **Examples:** `debug_api.py`, `debug_authentication.py`
- **When obsolete:** Move to `/debug/archive/` instead of deleting

#### Archive Files
- **Location:** `/archive`
- **What to archive:**
  - Old implementations replaced by newer versions
  - Historical test results
  - Obsolete utilities
  - Backup files (`.bak`, `.backup`)
  - Old configuration files
- **⚠️ Important:** Archive, don't delete. Historical context is valuable.

## 🔧 Development Workflow

### Adding New Features

1. **Backend (FastAPI):**
   - API endpoints → `app/api/v1/endpoints/`
   - Business logic → `app/services/`
   - Data models → `app/models/`
   - Database operations → `app/db/`

2. **Frontend (Next.js):**
   - Pages → `frontend/src/app/[locale]/`
   - Components → `frontend/src/components/`
   - Services → `frontend/src/services/`
   - Translations → `frontend/src/i18n/locales/`

3. **Testing:**
   - Write unit tests first → `/tests/unit/`
   - Add integration tests → `/tests/integration/`
   - Create E2E tests for workflows → `/tests/e2e/`

4. **Documentation:**
   - Document new features → `/docs/`
   - Update README.md if needed
   - Add code comments for complex logic

### Code Style Guidelines

#### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for function signatures
- Write docstrings for classes and functions
- Use async/await for I/O operations
- Keep functions focused and small

```python
async def get_company_by_id(company_id: str) -> Optional[Company]:
    """
    Retrieve a company by its ID.
    
    Args:
        company_id: The unique identifier of the company
        
    Returns:
        Company object if found, None otherwise
    """
    # Implementation
```

#### TypeScript/JavaScript (Frontend)
- Use TypeScript for type safety
- Follow ESLint configuration
- Use functional components with hooks
- Keep components small and focused
- Extract reusable logic to custom hooks

```typescript
interface MaterialCardProps {
  material: Material;
  onEdit: (id: string) => void;
}

export function MaterialCard({ material, onEdit }: MaterialCardProps) {
  // Implementation
}
```

### Git Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `chore`: Maintenance tasks
- `style`: Code style changes (formatting)

**Examples:**
```
feat(materials): add image generation workflow
fix(auth): correct token validation logic
refactor: organize 384 files into proper directories
docs: update API documentation for providers
test: add unit tests for company service
```

## 🧪 Testing Guidelines

### Writing Good Tests

1. **Unit Tests:**
   - Test one function/method at a time
   - Mock external dependencies
   - Use descriptive test names
   - Cover edge cases and error conditions

2. **Integration Tests:**
   - Test API endpoints with real requests
   - Verify database operations
   - Test authentication flows
   - Check error handling

3. **E2E Tests:**
   - Test complete user workflows
   - Verify frontend-backend integration
   - Test critical business processes

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test type
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=app tests/
```

## 🚀 Deployment

### Development Setup

1. **Start MongoDB:**
   ```bash
   systemctl start mongod
   ```

2. **Start Backend:**
   ```bash
   uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload
   ```

3. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

### Using Helper Scripts

We provide convenience scripts in `/scripts`:

```bash
# Start both services
./scripts/start-all.sh

# Restart services
./scripts/restart-services.sh

# Check port availability
./scripts/check-ports.sh

# Run tests
./scripts/run-tests.sh
```

## 📊 Code Quality

### Before Committing

1. **Run linters:**
   ```bash
   # Python
   flake8 app/
   black app/
   
   # TypeScript
   cd frontend && npm run lint
   ```

2. **Run tests:**
   ```bash
   pytest tests/
   cd frontend && npm test
   ```

3. **Check types:**
   ```bash
   # Python
   mypy app/
   
   # TypeScript
   cd frontend && npm run type-check
   ```

## 🐛 Bug Fixes

When fixing bugs:

1. **Create a test that reproduces the bug** (in appropriate `/tests` subdirectory)
2. **Fix the bug**
3. **Verify the test passes**
4. **Document the fix** in `/docs` if significant
5. **Commit with descriptive message:** `fix(component): description of bug fix`

## 📚 Documentation

### When to Document

- New features or APIs
- Complex algorithms or logic
- Configuration changes
- Breaking changes
- Migration guides

### Where to Document

- **Code comments:** For complex logic
- **Docstrings:** For functions and classes
- **README.md:** For project overview and quick start
- **`/docs` folder:** For detailed documentation
- **Inline comments:** For non-obvious code

## 🤝 Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes following these guidelines**

3. **Write/update tests**

4. **Update documentation**

5. **Run quality checks**

6. **Commit with conventional commit messages**

7. **Push and create a Pull Request**

8. **Ensure CI/CD passes**

9. **Request review from maintainers**

## ❓ Questions?

If you're unsure where to place a file or how to structure something:

1. Look for similar existing files
2. Check this guide
3. Ask in the project discussions
4. When in doubt, prefer organization over speed

## 🎯 Key Principles

1. **Keep root directory clean** - Only essential config files
2. **Organize by type** - Scripts, tests, docs, debug in separate folders
3. **Test subdirectories** - Unit, integration, e2e, frontend
4. **Archive, don't delete** - Historical context matters
5. **Document as you go** - Future you will thank you
6. **Follow naming conventions** - Consistency helps everyone
7. **Write tests** - Prevents regressions
8. **Use descriptive names** - Code should be self-documenting

---

**Thank you for contributing to AI Marketing Agent!** 🚀

By following these guidelines, you help maintain a clean, professional, and maintainable codebase that benefits all contributors.

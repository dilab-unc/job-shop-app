# Development Guide

This guide provides information for developers working on the Job Shop Scheduling application.

## Development Setup

### Prerequisites

- Python 3.11 or 3.12
- Git
- Code editor (VS Code, PyCharm, etc.)

### Initial Setup

1. **Clone the repository** (if applicable)
2. **Set up backend**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Set up frontend**:
   ```bash
   cd frontend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Development Workflow

### Running in Development Mode

**Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

The `--reload` flag enables auto-reload on code changes.

**Frontend:**
```bash
cd frontend
source .venv/bin/activate
streamlit run streamlit_app.py
```

Streamlit automatically reloads on file changes.

### Code Organization

#### Backend

- **Models** (`app/models.py`): Database models and schemas
- **Endpoints** (`app/api/v1/endpoints/`): API route handlers
- **Solver** (`app/solver.py`): OR-Tools solver logic
- **Database** (`app/database.py`): Database configuration

#### Frontend

- **Components** (`components/`): UI component modules
- **Utils** (`utils/`): Utility functions (API, cache, UI)
- **Main** (`streamlit_app.py`): Application entry point

### Adding New Features

#### Backend

1. **Add/Update Models** in `app/models.py`
2. **Create Migrations** (if using Alembic in future)
3. **Add Endpoints** in `app/api/v1/endpoints/`
4. **Register Routes** in `app/api/v1/router.py`
5. **Update Seed Data** in `app/seed.py` (if needed)

#### Frontend

1. **Create Component** in `components/` (if new section)
2. **Add API Functions** in `utils/api.py` (if new endpoints)
3. **Add Cache Functions** in `utils/cache.py` (if needed)
4. **Register Component** in `streamlit_app.py`

### Database Changes

Currently using SQLite with automatic schema creation. For schema changes:

1. **Update Models** in `app/models.py`
2. **Delete Database** (`backend/jobshop.db`) for development
3. **Re-run Seed** (`python -m app.seed`)

**Note**: In production, use proper migrations (Alembic recommended).

## Code Style

### Python Style Guide

Follow PEP 8:
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints where possible
- Use docstrings for functions and classes

### Example

```python
def solve_job_order(job_id: int, session: Session) -> SolverResult:
    """
    Solve a job order using OR-Tools CP-SAT.
    
    Args:
        job_id: ID of the job order to solve
        session: Database session
        
    Returns:
        SolverResult with schedule and assignments
        
    Raises:
        ValueError: If job order not found
    """
    # Implementation
```

## Testing

### Manual Testing

1. **Backend**: Use FastAPI's automatic docs at `http://localhost:8000/docs`
2. **Frontend**: Test through Streamlit UI

### Automated Testing (Future)

**Backend Tests:**
```bash
pytest backend/tests/
```

**Frontend Tests:**
```bash
pytest frontend/tests/
```

## Debugging

### Backend Debugging

1. **Enable SQL Logging**: Set `echo_sql=True` in `app/config.py`
2. **Use FastAPI Docs**: Interactive API testing at `/docs`
3. **Add Logging**: Use Python's `logging` module

### Frontend Debugging

1. **Streamlit Debug Mode**: Check terminal output
2. **Use `st.write()`**: Debug variable values
3. **Check Browser Console**: For JavaScript errors (if any)

## Common Issues

### Import Errors

**Problem**: Module not found errors

**Solution**:
- Verify virtual environment is activated
- Check `sys.path` modifications in component files
- Ensure all dependencies are installed

### Database Locked

**Problem**: SQLite database locked errors

**Solution**:
- Close all database connections
- Restart backend server
- Delete and recreate database if needed

### Port Already in Use

**Problem**: Port 8000 or 8501 already in use

**Solution**:
```bash
# Backend
uvicorn app.main:app --reload --port 8001

# Frontend
streamlit run streamlit_app.py --server.port 8502
```

### Solver Infeasible

**Problem**: Solver always returns infeasible

**Solution**:
- Check machine capabilities match task requirements
- Verify task durations are positive
- Check for circular dependencies in task sequences
- Review solver constraints in `app/solver.py`

## Performance Optimization

### Backend

1. **Database Indexing**: Add indexes on frequently queried fields
2. **Query Optimization**: Use `selectinload` for eager loading
3. **Caching**: Consider Redis for frequently accessed data

### Frontend

1. **Streamlit Caching**: Already implemented with `@st.cache_data`
2. **Reduce API Calls**: Batch requests where possible
3. **Optimize Charts**: Limit data points in visualizations

## Git Workflow

### Branching Strategy

- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: Feature branches
- `fix/*`: Bug fix branches

### Commit Messages

Use conventional commits:
- `feat: Add CSV import functionality`
- `fix: Resolve solver infeasibility issue`
- `docs: Update API documentation`
- `refactor: Modularize Streamlit components`

## Dependencies

### Adding Dependencies

**Backend:**
```bash
cd backend
pip install <package>
pip freeze > requirements.txt
```

**Frontend:**
```bash
cd frontend
pip install <package>
pip freeze > requirements.txt
```

### Updating Dependencies

```bash
pip install --upgrade <package>
pip freeze > requirements.txt
```

## Documentation

### Code Documentation

- Use docstrings for all functions and classes
- Follow Google or NumPy docstring style
- Document complex algorithms

### API Documentation

- FastAPI automatically generates docs at `/docs`
- Update `docs/API_DOCUMENTATION.md` for manual changes

### User Documentation

- Update `README.md` for user-facing changes
- Update `docs/` for detailed documentation

## Deployment Checklist

### Backend

- [ ] Set production database URL
- [ ] Configure CORS for production
- [ ] Set up authentication
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Test all endpoints

### Frontend

- [ ] Set production API URL
- [ ] Test all features
- [ ] Optimize bundle size
- [ ] Configure caching
- [ ] Test on different browsers

## Resources

### Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
- [OR-Tools Docs](https://developers.google.com/optimization)

### Tools

- FastAPI Interactive Docs: `http://localhost:8000/docs`
- Streamlit Component Gallery: [streamlit.io/components](https://streamlit.io/components)

## Getting Help

1. Check existing documentation
2. Review code comments
3. Check FastAPI/Streamlit documentation
4. Review error messages carefully
5. Use debugging techniques above


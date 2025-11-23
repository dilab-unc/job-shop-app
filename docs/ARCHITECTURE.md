# Architecture Documentation

This document describes the architecture and design decisions of the Job Shop Scheduling application.

## Overview

The application follows a client-server architecture with a clear separation between frontend and backend:

```
┌─────────────┐         HTTP/REST         ┌─────────────┐
│  Streamlit │ ◄──────────────────────► │   FastAPI   │
│  Frontend  │                           │   Backend   │
└─────────────┘                           └─────────────┘
                                                  │
                                                  ▼
                                          ┌─────────────┐
                                          │   SQLite    │
                                          │  Database   │
                                          └─────────────┘
```

## Backend Architecture

### Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: Combines SQLAlchemy and Pydantic for type-safe database models
- **OR-Tools CP-SAT**: Constraint programming solver for optimization
- **SQLite**: Database (easily replaceable with PostgreSQL)

### Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and session management
│   ├── models.py            # SQLModel database models
│   ├── solver.py            # OR-Tools solver logic
│   ├── seed.py              # Sample data seeding
│   └── api/
│       ├── deps.py          # FastAPI dependencies
│       └── v1/
│           ├── router.py    # API router aggregation
│           └── endpoints/   # Individual endpoint modules
│               ├── factories.py
│               ├── machines.py
│               ├── task_templates.py
│               ├── job_orders.py
│               └── schedules.py
```

### Key Design Decisions

#### 1. SQLModel for Data Models

SQLModel provides:
- Type safety with Pydantic validation
- Database ORM capabilities
- Automatic schema generation
- Easy serialization/deserialization

#### 2. Modular API Structure

Endpoints are organized by resource type:
- Each resource has its own endpoint module
- Clear separation of concerns
- Easy to extend and maintain

#### 3. Solver Integration

The solver (`solver.py`) is separated from API logic:
- Can be tested independently
- Can be reused in other contexts
- Clear interface: `solve_job_order(job_id, session) -> SolverResult`

### Data Flow

1. **Request** → FastAPI endpoint
2. **Validation** → Pydantic models
3. **Database** → SQLModel session
4. **Business Logic** → Endpoint handler
5. **Solver** (if needed) → OR-Tools CP-SAT
6. **Response** → JSON serialization

### Database Schema

```
Factory
  ├── Machine (1:N)
  ├── TaskTemplate (1:N)
  └── JobOrder (1:N)
      └── JobTask (1:N)
          └── ScheduledTask (1:1)
              └── Machine (N:1)
      └── Schedule (1:N)
          └── ScheduledTask (1:N)
```

## Frontend Architecture

### Technology Stack

- **Streamlit**: Python-based web framework for data applications
- **Plotly**: Interactive charting library
- **Pandas**: Data manipulation
- **httpx**: HTTP client for API communication

### Project Structure

```
frontend/
├── streamlit_app.py         # Main application entry point
├── components/              # UI component modules
│   ├── factories.py
│   ├── machines.py
│   ├── task_templates.py
│   ├── job_orders.py
│   └── schedules.py
└── utils/                   # Utility modules
    ├── api.py               # API client functions
    ├── cache.py             # Cached data fetching
    └── ui.py                # UI helper functions
```

### Key Design Decisions

#### 1. Modular Component Architecture

Each tab/section is a separate component:
- **Factories**: Factory management UI
- **Machines**: Machine management UI
- **Task Templates**: Template management UI
- **Job Orders**: Job order and task management UI
- **Schedules**: Schedule visualization UI

#### 2. Utility Separation

- **api.py**: All HTTP client logic
- **cache.py**: Streamlit caching for API responses
- **ui.py**: Reusable UI components

#### 3. Caching Strategy

Streamlit's `@st.cache_data` is used to:
- Reduce API calls
- Improve performance
- Cache for 30 seconds (TTL)

### Data Flow

1. **User Action** → Streamlit widget
2. **API Call** → `utils/api.py` functions
3. **Cache Check** → `utils/cache.py` (if cached)
4. **HTTP Request** → FastAPI backend
5. **Response** → Streamlit display
6. **Cache Update** → Store for future use

## Solver Architecture

### OR-Tools CP-SAT Integration

The solver uses Google OR-Tools Constraint Programming SAT solver:

1. **Model Creation**:
   - Create interval variables for each task on each machine
   - Define domain constraints (duration, machine capabilities)

2. **Constraint Addition**:
   - **No-overlap**: Tasks on the same machine cannot overlap
   - **Precedence**: Tasks must follow sequence order
   - **Machine capabilities**: Tasks can only run on compatible machines

3. **Objective**:
   - Minimize makespan (total completion time)

4. **Solving**:
   - CP-SAT solver finds optimal or feasible solution
   - Returns status (optimal, feasible, infeasible)

5. **Result Persistence**:
   - Create Schedule record
   - Create ScheduledTask records with start/end times

### Solver Status Mapping

- `OPTIMAL`: Best solution found
- `FEASIBLE`: Valid solution found (may not be optimal)
- `INFEASIBLE`: No valid solution exists
- `MODEL_INVALID`: Model has errors
- `UNKNOWN`: Solver couldn't determine status

## Configuration Management

### Backend Configuration

Uses `pydantic-settings` for configuration:
- Environment variable support
- `.env` file support
- Type-safe settings

Key settings:
- `database_url`: Database connection string
- `debug`: Debug mode flag
- `echo_sql`: SQL query logging

### Frontend Configuration

Uses Streamlit secrets:
- `API_URL`: Backend API URL
- Stored in `.streamlit/secrets.toml`

## Database Design

### Relationships

- **Factory** → **Machine**: One-to-Many
- **Factory** → **TaskTemplate**: One-to-Many
- **Factory** → **JobOrder**: One-to-Many
- **JobOrder** → **JobTask**: One-to-Many
- **JobOrder** → **Schedule**: One-to-Many
- **Schedule** → **ScheduledTask**: One-to-Many
- **JobTask** → **ScheduledTask**: One-to-One
- **Machine** → **ScheduledTask**: One-to-Many
- **TaskTemplate** → **JobTask**: Many-to-One (optional)

### Timestamps

All models include:
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

Automatically managed by SQLModel.

## Error Handling

### Backend

- FastAPI automatic validation errors (422)
- HTTPException for business logic errors (404, 400)
- Try-catch for unexpected errors (500)

### Frontend

- Try-catch blocks around API calls
- User-friendly error messages
- Graceful degradation (fallback displays)

## Security Considerations

### Current State

- No authentication/authorization
- No input sanitization beyond Pydantic validation
- SQL injection protection via SQLModel ORM

### Future Improvements

- Add authentication (JWT tokens)
- Add authorization (user roles, factory ownership)
- Add rate limiting
- Add input sanitization
- Add CORS configuration for production

## Performance Considerations

### Backend

- Database indexing on foreign keys
- Efficient queries with SQLModel
- Solver timeout considerations (not currently implemented)

### Frontend

- Streamlit caching for API responses
- Efficient data structures (Pandas DataFrames)
- Lazy loading of components

## Testing Strategy

### Current State

- No automated tests
- Manual testing via UI

### Recommended Testing

1. **Backend**:
   - Unit tests for models
   - Unit tests for solver logic
   - Integration tests for API endpoints

2. **Frontend**:
   - Component tests
   - Integration tests for user flows

## Deployment Considerations

### Backend

- Use PostgreSQL for production
- Set up proper CORS configuration
- Add authentication/authorization
- Use environment variables for secrets
- Set up logging and monitoring

### Frontend

- Configure production API URL
- Set up Streamlit Cloud or similar hosting
- Consider caching strategies
- Optimize bundle size

## Future Enhancements

1. **Authentication & Authorization**
   - User accounts
   - Factory ownership
   - Role-based access control

2. **Advanced Scheduling**
   - Multi-objective optimization
   - Resource constraints
   - Time windows
   - Setup times

3. **Analytics**
   - Schedule comparison
   - Performance metrics
   - Historical analysis

4. **Integration**
   - Export to external systems
   - Import from ERP systems
   - API webhooks


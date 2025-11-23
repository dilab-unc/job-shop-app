# Job Shop Scheduling App

A full-stack application for solving job shop scheduling problems using Google OR-Tools CP-SAT solver. The app provides a user-friendly interface for managing factories, machines, tasks, and job orders, with automatic schedule optimization and visualization.

## Features

- 🏭 **Factory Management**: Create and manage factories with multiple machines
- ⚙️ **Machine Configuration**: Define machine capabilities and constraints
- 📋 **Task Templates**: Create reusable task templates with duration and machine requirements
- 📦 **Job Orders**: Create job orders with sequences of tasks and due dates
- 📊 **Schedule Optimization**: Automatic schedule generation using OR-Tools CP-SAT solver
- 📈 **Gantt Chart Visualization**: Interactive Plotly charts for schedule visualization
- 📥 **CSV Import**: Import job tasks from CSV files
- ✏️ **Task Management**: Edit, delete, and reorder tasks within job orders

## Architecture

- **Backend**: FastAPI + SQLModel + OR-Tools (CP-SAT)
- **Frontend**: Streamlit with modular component architecture
- **Database**: SQLite (development) / PostgreSQL (production ready)

## Project Structure

```
job-shop-app/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   ├── models.py         # SQLModel database models
│   │   ├── solver.py         # OR-Tools solver logic
│   │   ├── database.py       # Database configuration
│   │   └── seed.py           # Sample data seeding
│   └── requirements.txt
├── frontend/
│   ├── components/           # UI components (modular)
│   ├── utils/               # Utility functions
│   ├── streamlit_app.py     # Main Streamlit app
│   └── requirements.txt
├── shared/                  # Shared resources
│   └── job_tasks_template.csv
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11 or 3.12 (SQLAlchemy/SQLModel compatibility)
- pip package manager

### Backend Setup

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv .venv
   ```

2. **Activate virtual environment**:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend server**:
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000/api`

5. **Seed sample data** (optional):
   ```bash
   python -m app.seed
   ```

   This creates:
   - A demo factory
   - 3 machines (Machine 0, Machine 1, Machine 2)
   - 3 task templates (Cutting, Assembly, Painting)
   - 3 sample job orders (mirroring the OR-Tools example)

### Frontend Setup

1. **Create virtual environment**:
   ```bash
   cd frontend
   python -m venv .venv
   ```

2. **Activate virtual environment**:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API URL** (optional):
   Create `.streamlit/secrets.toml`:
   ```toml
   API_URL = "http://localhost:8000/api"
   ```

5. **Run the Streamlit app**:
   ```bash
   streamlit run streamlit_app.py
   ```

   The app will be available at `http://localhost:8501`

## Usage Guide

### Creating a Factory

1. Navigate to the **Factories** tab
2. Enter a factory name and description
3. Click "Create Factory"

### Adding Machines

1. Go to the **Machines** tab
2. Select a factory
3. Enter machine details:
   - Name and description
   - Capabilities (comma-separated)
   - Max parallel jobs
4. Click "Create Machine"

### Creating Task Templates

1. Go to the **Task Templates** tab
2. Select a factory
3. Enter template details:
   - Name and description
   - Task type (capability tag)
   - Default duration in minutes
   - Allowed machines (checkboxes)
4. Click "Create template"

### Managing Job Orders

#### Creating a Job Order

1. Go to the **Job Orders** tab → **Create New Job**
2. Enter job details:
   - Name (required)
   - Due date
   - Priority
   - Status
   - Description
3. Click "Create Job Order"

#### Adding Tasks to a Job

**Option 1: Manual Entry**
1. Go to **Manage Job Tasks** → **Add Task**
2. Select a task template
3. Set sequence index, custom name, duration, machine hint, and notes
4. Click "Add Task"

**Option 2: CSV Import**
1. Go to **Manage Job Tasks** → **Import CSV**
2. Upload a CSV file (see format below)
3. Preview the data
4. Click "Import CSV"

#### CSV Import Format

**Required columns:**
- `sequence_index`: Order of task (0-based integer)
- `task_name`: Name of the task (string)
- `duration_minutes`: Duration in minutes (integer > 0)

**Optional columns:**
- `machine_name`: Name of machine (will be looked up)
- `machine_id`: ID of machine (alternative to machine_name)
- `task_template_name`: Name of task template (will be looked up)
- `task_template_id`: ID of task template (alternative to task_template_name)
- `notes`: Additional notes (string)

**Example CSV:**
```csv
sequence_index,task_name,duration_minutes,machine_name,task_template_name,notes
0,Cutting,3,Machine 0,Cutting,Initial cut
1,Assembly,2,Machine 1,Assembly,Assemble parts
2,Painting,2,Machine 2,Painting,Final paint
```

#### Managing Tasks

- **View Tasks**: See all tasks in a job order
- **Edit Task**: Modify task properties
- **Delete Task**: Remove a task from a job order
- **Reorder Tasks**: Change the sequence of tasks

### Running the Solver

1. Go to **Job Orders** → **Run Solver**
2. Select a job order
3. Review job metrics (status, task count, makespan)
4. Click "🚀 Run Solver"
5. View the results:
   - **Feasible**: Schedule found with makespan value
   - **Infeasible**: No valid schedule exists (check constraints)

### Viewing Schedules

1. Go to the **Schedules** tab
2. Select a schedule from the dropdown
3. View:
   - Schedule metrics (status, makespan, solver status)
   - Interactive Gantt chart
   - Task details table

## API Documentation

The backend provides a RESTful API. See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for detailed endpoint documentation.

### Key Endpoints

- `GET /api/factories` - List all factories
- `POST /api/factories` - Create a factory
- `GET /api/machines` - List machines (optionally filtered by factory)
- `POST /api/job-orders` - Create a job order
- `POST /api/job-orders/{id}/tasks` - Add tasks to a job order
- `POST /api/job-orders/{id}/import-csv` - Import tasks from CSV
- `POST /api/job-orders/{id}/solve` - Run solver for a job order
- `GET /api/schedules/{id}/gantt` - Get Gantt chart data

## Database Models

### Factory
- `id`: Primary key
- `name`: Factory name
- `description`: Factory description
- `created_at`, `updated_at`: Timestamps

### Machine
- `id`: Primary key
- `factory_id`: Foreign key to Factory
- `name`: Machine name
- `description`: Machine description
- `capabilities`: List of capability strings (JSON)
- `max_parallel_jobs`: Maximum concurrent jobs
- `created_at`, `updated_at`: Timestamps

### TaskTemplate
- `id`: Primary key
- `factory_id`: Foreign key to Factory
- `name`: Template name
- `description`: Template description
- `task_type`: Capability tag
- `default_duration_minutes`: Default task duration
- `allowed_machine_ids`: List of allowed machine IDs (JSON)
- `created_at`, `updated_at`: Timestamps

### JobOrder
- `id`: Primary key
- `factory_id`: Foreign key to Factory
- `name`: Job name
- `description`: Job description
- `status`: Job status (draft, queued, etc.)
- `priority`: Priority value
- `due_date`: Due date (optional)
- `makespan_minutes`: Best makespan found
- `created_at`, `updated_at`: Timestamps

### JobTask
- `id`: Primary key
- `job_id`: Foreign key to JobOrder
- `task_template_id`: Foreign key to TaskTemplate (optional)
- `sequence_index`: Order in job sequence
- `custom_name`: Custom task name
- `custom_duration_minutes`: Custom duration
- `machine_hint_id`: Preferred machine (optional)
- `notes`: Additional notes
- `created_at`, `updated_at`: Timestamps

### Schedule
- `id`: Primary key
- `job_id`: Foreign key to JobOrder
- `status`: Schedule status (feasible, infeasible)
- `objective_value`: Makespan value
- `solver_status`: Solver status string
- `solver_metadata`: Additional solver info (JSON)
- `created_at`, `updated_at`: Timestamps

### ScheduledTask
- `id`: Primary key
- `schedule_id`: Foreign key to Schedule
- `job_task_id`: Foreign key to JobTask
- `machine_id`: Foreign key to Machine
- `start_time`: Task start time
- `end_time`: Task end time
- `created_at`, `updated_at`: Timestamps

## Solver Logic

The solver uses Google OR-Tools CP-SAT to find optimal schedules:

1. **Load job order** with all tasks and their constraints
2. **Create interval variables** for each task on each possible machine
3. **Add no-overlap constraints** to prevent machine conflicts
4. **Add precedence constraints** based on task sequence
5. **Minimize makespan** (total completion time)
6. **Persist results** as Schedule and ScheduledTask records

See `backend/app/solver.py` for implementation details.

## Development

### Running Tests

(Add test instructions when tests are added)

### Code Style

The project follows Python PEP 8 style guidelines.

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change port
uvicorn app.main:app --reload --port 8001
```

**Database errors:**
- Delete `backend/jobshop.db` to reset the database
- Run `python -m app.seed` to recreate sample data

### Frontend Issues

**Cannot connect to backend:**
- Verify backend is running on `http://localhost:8000`
- Check `.streamlit/secrets.toml` for correct `API_URL`

**Import errors:**
- Ensure you're using Python 3.11 or 3.12
- Verify all dependencies are installed: `pip install -r requirements.txt`

## License

(Add license information)

## Acknowledgments

- [Google OR-Tools](https://developers.google.com/optimization) for the CP-SAT solver
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Streamlit](https://streamlit.io/) for the frontend framework
- [SQLModel](https://sqlmodel.tiangolo.com/) for database models

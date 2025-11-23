# Quick Start Guide

Get up and running with the Job Shop Scheduling App in minutes.

## Prerequisites

- Python 3.11 or 3.12
- pip package manager

## 5-Minute Setup

### 1. Backend Setup (2 minutes)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
uvicorn app.main:app --reload
```

✅ Backend running at `http://localhost:8000`

### 2. Frontend Setup (2 minutes)

```bash
cd frontend
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
streamlit run streamlit_app.py
```

✅ Frontend running at `http://localhost:8501`

### 3. Seed Sample Data (1 minute)

```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python -m app.seed
```

✅ Sample factory, machines, and job orders created!

## First Steps

1. **Open the app**: Go to `http://localhost:8501`
2. **View sample data**: Check the "Factories", "Machines", and "Job Orders" tabs
3. **Run a solver**: 
   - Go to "Job Orders" → "Run Solver"
   - Select a job order
   - Click "🚀 Run Solver"
4. **View schedule**: Go to "Schedules" tab to see the Gantt chart

## Common Tasks

### Create a New Factory

1. Go to **Factories** tab
2. Enter name and description
3. Click "Create Factory"

### Add a Machine

1. Go to **Machines** tab
2. Select a factory
3. Fill in machine details
4. Click "Create Machine"

### Create a Job Order

1. Go to **Job Orders** → **Create New Job**
2. Fill in job details
3. Click "Create Job Order"

### Add Tasks to a Job

**Option 1: Manual**
- Go to **Job Orders** → **Manage Job Tasks** → **Add Task**
- Fill in task details
- Click "Add Task"

**Option 2: CSV Import**
- Go to **Job Orders** → **Manage Job Tasks** → **Import CSV**
- Upload CSV file (see format in main README)
- Click "Import CSV"

### Run Solver

1. Go to **Job Orders** → **Run Solver**
2. Select a job order
3. Click "🚀 Run Solver"
4. View results

### View Schedule

1. Go to **Schedules** tab
2. Select a schedule
3. View Gantt chart and task details

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify Python version (3.11 or 3.12)
- Check all dependencies are installed

### Frontend can't connect
- Verify backend is running
- Check `.streamlit/secrets.toml` has correct `API_URL`

### Solver returns infeasible
- Check machine capabilities match task requirements
- Verify task durations are positive
- Ensure tasks have valid machine assignments

## Next Steps

- Read the full [README.md](../README.md) for detailed information
- Check [API Documentation](API_DOCUMENTATION.md) for backend details
- Review [Architecture](ARCHITECTURE.md) for system design
- See [Development Guide](DEVELOPMENT.md) for contributing

## Need Help?

- Check the main [README.md](../README.md)
- Review [Troubleshooting section](../README.md#troubleshooting)
- See [Development Guide](DEVELOPMENT.md) for debugging tips


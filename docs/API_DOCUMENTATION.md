# API Documentation

This document describes the RESTful API endpoints provided by the Job Shop Scheduling backend.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently, the API does not require authentication. This may change in future versions.

## Endpoints

### Factories

#### List Factories
```http
GET /api/v1/factories
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Demo Factory",
    "description": "Sample factory",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### Create Factory
```http
POST /api/v1/factories
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "My Factory",
  "description": "Factory description"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "My Factory",
  "description": "Factory description",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### Get Factory
```http
GET /api/v1/factories/{factory_id}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "My Factory",
  "description": "Factory description",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

### Machines

#### List Machines
```http
GET /api/v1/machines?factory_id={factory_id}
```

**Query Parameters:**
- `factory_id` (optional): Filter machines by factory

**Response:**
```json
[
  {
    "id": 1,
    "factory_id": 1,
    "name": "Machine 0",
    "description": "Cutting machine",
    "capabilities": ["cutting"],
    "max_parallel_jobs": 1,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### Create Machine
```http
POST /api/v1/machines
Content-Type: application/json
```

**Request Body:**
```json
{
  "factory_id": 1,
  "name": "Machine 0",
  "description": "Cutting machine",
  "capabilities": ["cutting", "milling"],
  "max_parallel_jobs": 1
}
```

**Response:** `201 Created`

#### Get Machine
```http
GET /api/v1/machines/{machine_id}
```

---

### Task Templates

#### List Task Templates
```http
GET /api/v1/task-templates?factory_id={factory_id}
```

**Query Parameters:**
- `factory_id` (optional): Filter templates by factory

**Response:**
```json
[
  {
    "id": 1,
    "factory_id": 1,
    "name": "Cutting",
    "description": "Cutting operation",
    "task_type": "cutting",
    "default_duration_minutes": 3,
    "allowed_machine_ids": [1, 2],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### Create Task Template
```http
POST /api/v1/task-templates
Content-Type: application/json
```

**Request Body:**
```json
{
  "factory_id": 1,
  "name": "Cutting",
  "description": "Cutting operation",
  "task_type": "cutting",
  "default_duration_minutes": 3,
  "allowed_machine_ids": [1, 2]
}
```

**Response:** `201 Created`

#### Get Task Template
```http
GET /api/v1/task-templates/{template_id}
```

---

### Job Orders

#### List Job Orders
```http
GET /api/v1/job-orders?factory_id={factory_id}
```

**Query Parameters:**
- `factory_id` (optional): Filter job orders by factory

**Response:**
```json
[
  {
    "id": 1,
    "factory_id": 1,
    "name": "Job 0",
    "description": "First job",
    "status": "draft",
    "priority": 0,
    "due_date": "2024-12-31",
    "makespan_minutes": null,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### Create Job Order
```http
POST /api/v1/job-orders
Content-Type: application/json
```

**Request Body:**
```json
{
  "factory_id": 1,
  "name": "Job 0",
  "description": "First job",
  "status": "draft",
  "priority": 0,
  "due_date": "2024-12-31"
}
```

**Response:** `201 Created`

#### Get Job Order
```http
GET /api/v1/job-orders/{job_id}
```

#### List Job Tasks
```http
GET /api/v1/job-orders/{job_id}/tasks
```

**Response:**
```json
[
  {
    "id": 1,
    "job_id": 1,
    "task_template_id": 1,
    "sequence_index": 0,
    "custom_name": "Cutting",
    "custom_duration_minutes": 3,
    "machine_hint_id": 1,
    "notes": "Initial cut",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### Add Job Tasks
```http
POST /api/v1/job-orders/{job_id}/tasks
Content-Type: application/json
```

**Request Body:**
```json
[
  {
    "job_id": 1,
    "sequence_index": 0,
    "custom_name": "Cutting",
    "custom_duration_minutes": 3,
    "machine_hint_id": 1,
    "task_template_id": 1,
    "notes": "Initial cut"
  }
]
```

**Response:** `200 OK` (array of created tasks)

#### Import Job Tasks from CSV
```http
POST /api/v1/job-orders/{job_id}/import-csv
Content-Type: multipart/form-data
```

**Request:**
- `file`: CSV file with task data

**CSV Format:**
```csv
sequence_index,task_name,duration_minutes,machine_name,task_template_name,notes
0,Cutting,3,Machine 0,Cutting,Initial cut
1,Assembly,2,Machine 1,Assembly,Assemble parts
```

**Response:** `200 OK` (array of created tasks)

#### Get Job Task
```http
GET /api/v1/job-orders/{job_id}/tasks/{task_id}
```

#### Update Job Task
```http
PUT /api/v1/job-orders/{job_id}/tasks/{task_id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "sequence_index": 0,
  "custom_name": "Updated Cutting",
  "custom_duration_minutes": 4,
  "machine_hint_id": 1,
  "task_template_id": 1,
  "notes": "Updated notes"
}
```

**Response:** `200 OK`

#### Delete Job Task
```http
DELETE /api/v1/job-orders/{job_id}/tasks/{task_id}
```

**Response:** `204 No Content`

#### Reorder Job Tasks
```http
PUT /api/v1/job-orders/{job_id}/tasks/reorder
Content-Type: application/json
```

**Request Body:**
```json
[1, 3, 2, 4]
```

Array of task IDs in the desired order.

**Response:** `200 OK` (array of tasks in new order)

#### Solve Job Order
```http
POST /api/v1/job-orders/{job_id}/solve
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "job_id": 1,
  "status": "feasible",
  "objective_value": 11,
  "solver_status": "optimal",
  "solver_metadata": {
    "status": "optimal",
    "conflicts": 0,
    "branches": 100,
    "wall_time": 0.5
  },
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

### Schedules

#### List Schedules
```http
GET /api/v1/schedules?job_id={job_id}
```

**Query Parameters:**
- `job_id` (optional): Filter schedules by job order

**Response:**
```json
[
  {
    "id": 1,
    "job_id": 1,
    "status": "feasible",
    "objective_value": 11,
    "solver_status": "optimal",
    "solver_metadata": {...},
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### Get Schedule
```http
GET /api/v1/schedules/{schedule_id}
```

#### Get Schedule Tasks
```http
GET /api/v1/schedules/{schedule_id}/tasks
```

**Response:**
```json
[
  {
    "id": 1,
    "schedule_id": 1,
    "job_task_id": 1,
    "machine_id": 1,
    "start_time": "2024-01-01T00:00:00",
    "end_time": "2024-01-01T00:03:00",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### Get Schedule Gantt Data
```http
GET /api/v1/schedules/{schedule_id}/gantt
```

**Response:**
```json
[
  {
    "task_id": 1,
    "job_task_id": 1,
    "task_name": "Cutting",
    "machine_id": 1,
    "machine_name": "Machine 0",
    "start_time": "2024-01-01T00:00:00",
    "end_time": "2024-01-01T00:03:00",
    "duration_minutes": 3,
    "job_id": 1,
    "job_name": "Job 0"
  }
]
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error message",
      "type": "error_type"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## Rate Limiting

Currently, there are no rate limits. This may change in future versions.

## Versioning

The API is versioned using URL paths (`/api/v1/`). Future versions will use `/api/v2/`, etc.


# Robot Manufactory GraphQL API

Django backend with Strawberry GraphQL API for managing a fleet of heterogeneous industrial robots. This project demonstrates GraphQL API development using Django and Strawberry GraphQL, including advanced features like lambda expressions, complex queries, and comprehensive filtering.

## 🚀 Features

- **GraphQL API** built with Strawberry GraphQL
- **Django ORM** for database operations
- **PostgreSQL** database support
- **Comprehensive filtering** for queries
- **Lambda expression examples** for advanced filtering and transformations
- **Interactive GraphiQL interface** for testing
- **RESTful-like mutations** for CRUD operations
- **Complex queries** including statistics, search, and aggregations

## 📋 Table of Contents

- [Setup and Installation](#setup-and-installation)
- [Quick Start](#quick-start)
- [GraphQL Endpoint](#graphql-endpoint)
- [Available Queries](#available-queries)
- [Available Mutations](#available-mutations)
- [Example Usage](#example-usage)
- [Project Structure](#project-structure)
- [Documentation Files](#documentation-files)
- [Troubleshooting](#troubleshooting)

## Setup and Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- pipenv (for dependency management)

### 1. Install Dependencies

```bash
# Install pipenv if not already installed
pip install --user pipenv

# Install project dependencies
pipenv install

# Or install specific packages
pipenv install "Django>=5.0" "strawberry-graphql-django" "psycopg2-binary" "django-cors-headers" "requests"
```

### 2. Database Setup

Make sure PostgreSQL is running and create the database:

```bash
# Create database (if not exists)
createdb robot_db

# Or using psql:
psql -U postgres
CREATE DATABASE robot_db;
```

Update database credentials in `robot_manufactory_graphQL_api/settings.py` if needed.

### 3. Run Migrations

```bash
# Activate pipenv shell (optional, or use pipenv run)
pipenv shell

# Create migrations
pipenv run python manage.py makemigrations

# Apply migrations
pipenv run python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
pipenv run python manage.py createsuperuser
```

### 5. Run Development Server

```bash
pipenv run python manage.py runserver
```

The server will start at: `http://localhost:8000`

## Quick Start

1. **Start the server:**
   ```bash
   pipenv run python manage.py runserver
   ```

2. **Open GraphiQL interface:**
   Navigate to `http://localhost:8000/graphql/` in your browser

3. **Run a test query:**
   ```graphql
   query {
     robots {
       id
       serial
       model
       status
     }
   }
   ```

4. **Create a robot:**
   ```graphql
   mutation {
     createRobot(data: {
       serial: "RBT-001"
       model: "WeldingBot-3000"
       capabilities: ["welding", "pick-place"]
       location: "Factory Floor A"
     }) {
       id
       serial
       model
     }
   }
   ```

## GraphQL Endpoint

- **GraphQL API**: `http://localhost:8000/graphql/`
- **GraphiQL Interface**: `http://localhost:8000/graphql/` (interactive playground)
- **Django Admin**: `http://localhost:8000/admin`

## Available Queries

### Basic Queries

- `robots` - Get all robots (with optional filters: model, status, location, serial)
- `robot(id: ID!)` - Get a single robot by ID
- `robotBySerial(serial: String!)` - Get a robot by serial number
- `tasks` - Get all tasks (with optional filters: status, priorityMin, priorityMax, robotId, hasDeadline)
- `task(id: ID!)` - Get a single task by ID
- `telemetryPoints` - Get telemetry points (with optional filters: robotId, metricName, startDate, endDate, limit)
- `telemetryPoint(id: ID!)` - Get a single telemetry point by ID
- `maintenanceEvents` - Get maintenance events (with optional filters: robotId, type, startDate, endDate)
- `predictions` - Get predictions (with optional filters: robotId, predictionType, startDate, endDate)

### Specialized Queries

- `robotsByCapability(capability: String!)` - Find robots with specific capability
- `highPriorityTasks(minPriority: Int = 5)` - Get tasks with priority >= minPriority
- `overdueTasks` - Get tasks past deadline and not completed
- `searchRobots(searchTerm: String!)` - Search robots by serial, model, or location
- `robotStatistics` - Get aggregated robot statistics
- `telemetryStatistics` - Get telemetry statistics (count, avg, min, max)
- `robotWithDetails(id: ID!)` - Get robot with all related data (optimized with prefetch_related)

### Lambda Expression Queries

These queries demonstrate Python lambda expressions for advanced filtering:

- `robotsWithHighTelemetryCount(minTelemetryPoints: Int = 10)` - Robots with at least N telemetry points
- `robotsSortedByCapabilityCount(reverse: Boolean = false)` - Robots sorted by capability count
- `robotsWithRecentActivity(hours: Int = 24)` - Robots active in last N hours
- `telemetryAnomalies(robotId: ID, metricName: String, thresholdMultiplier: Float)` - Find anomaly telemetry
- `tasksByUrgencyScore(minScore: Float = 0.5)` - Tasks sorted by computed urgency score

## Available Mutations

### Robot Mutations

- `createRobot(data: CreateRobotInput!)` - Create a new robot
- `updateRobot(data: UpdateRobotInput!)` - Update an existing robot
- `deleteRobot(id: ID!)` - Delete a robot

### Task Mutations

- `createTask(data: CreateTaskInput!)` - Create a new task
- `updateTask(data: UpdateTaskInput!)` - Update an existing task
- `deleteTask(id: ID!)` - Delete a task

### Telemetry Mutations

- `createTelemetry(data: CreateTelemetryInput!)` - Create a telemetry point
- `updateTelemetry(data: UpdateTelemetryInput!)` - Update a telemetry point
- `deleteTelemetry(id: ID!)` - Delete a telemetry point

### Maintenance Mutations

- `createMaintenanceEvent(data: CreateMaintenanceEventInput!)` - Create a maintenance event
- `updateMaintenanceEvent(data: UpdateMaintenanceEventInput!)` - Update a maintenance event
- `deleteMaintenanceEvent(id: ID!)` - Delete a maintenance event

### Prediction Mutations

- `createPrediction(data: CreatePredictionInput!)` - Create a prediction
- `updatePrediction(data: UpdatePredictionInput!)` - Update a prediction
- `deletePrediction(id: ID!)` - Delete a prediction

### Advanced Mutations (Lambda Examples)

- `bulkUpdateRobotStatuses(robotIds: [ID!]!, newStatus: String!)` - Update multiple robots
- `createRobotsFromTemplates(templates: [CreateRobotInput!]!, locationPrefix: String)` - Batch create robots
- `assignTasksToRobotsByCapability(taskIds: [ID!]!)` - Auto-assign tasks to robots
- `cleanupOldTelemetry(daysToKeep: Int = 30, metricNames: [String!])` - Cleanup old telemetry

## Example Usage

### Using GraphiQL

1. Open `http://localhost:8000/graphql/` in your browser
2. Write queries in the left panel
3. Click the play button to execute
4. View results in the right panel

### Using Python

See `test_queries.py` for complete examples:

```python
import requests

url = "http://localhost:8000/graphql/"

# Query
query = """
{
  robots {
    id
    serial
    model
    status
  }
}
"""

response = requests.post(url, json={"query": query})
print(response.json())

# Mutation
mutation = """
mutation {
  createRobot(data: {
    serial: "RBT-003"
    model: "DemoBot"
    capabilities: ["welding", "inspection"]
    location: "Lab"
  }) {
    id
    serial
    model
  }
}
"""

response = requests.post(url, json={"query": mutation})
print(response.json())
```

Run the test script:
```bash
pipenv run python test_queries.py
```

### Using cURL

```bash
# Query
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ robots { id serial model status } }"}'

# Mutation
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { createRobot(data: { serial: \"RBT-002\", model: \"TestBot\", capabilities: [\"welding\"] }) { id serial model } }"}'
```

## Project Structure

```
robot_manufactory_graphQL_api/
├── robot/                          # Main Django app
│   ├── models.py                  # Django ORM models
│   ├── schema.py                  # Strawberry GraphQL schema (queries, mutations, types)
│   ├── enumerations.py            # Django TextChoices for model fields
│   ├── admin.py                   # Django admin configuration
│   └── migrations/                # Database migrations
├── robot_manufactory_graphQL_api/ # Django project settings
│   ├── settings.py                # Django settings (database, apps, middleware, logging, CORS)
│   ├── urls.py                    # URL routing (GraphQL endpoint)
│   ├── wsgi.py                    # WSGI configuration
│   └── asgi.py                    # ASGI configuration
├── manage.py                      # Django management script
├── Pipfile                        # Pipenv dependencies
├── README.md                      # This file
├── USAGE_GUIDE.md                 # Detailed usage guide
├── QUERY_BY_CRITERIA.md          # Filtering examples
├── test_queries.py                # Python test script
└── query_by_criteria_examples.py  # Filtering examples script
```

## Documentation Files

- **README.md** (this file) - Project overview and quick start
- **USAGE_GUIDE.md** - Comprehensive usage guide with all queries and mutations
- **QUERY_BY_CRITERIA.md** - Detailed filtering examples and reference
- **test_queries.py** - Python script with example queries and mutations
- **query_by_criteria_examples.py** - Python script demonstrating filtering

## Key Concepts

### GraphQL Types

The schema defines several types:

- **RobotType** - Robot entity with capabilities, status, location
- **TaskType** - Production tasks with priorities and deadlines
- **TelemetryPointType** - Sensor data points from robots
- **MaintenanceEventType** - Maintenance records
- **PredictionType** - ML predictions (anomaly scores, RUL)
- **RobotStatistics** - Aggregated statistics
- **TelemetryStatistics** - Telemetry aggregations

### Filtering

Queries support comprehensive filtering:

- **Robots**: Filter by model, status, location, serial (all case-insensitive partial match except status)
- **Tasks**: Filter by status, priority range, assigned robot, deadline presence
- **Telemetry**: Filter by robot, metric name, date range, limit results
- **Specialized**: Capability matching, search, statistics

### Lambda Expressions

Several queries demonstrate Python lambda expressions:

- **filter()** - Filter lists based on conditions
- **map()** - Transform data
- **sorted()** - Custom sorting
- **reduce()** - Aggregations

See `robot/schema.py` for detailed comments explaining lambda usage.

## Status Values

### Robot Status
- `IDLE` - Robot is idle
- `ACTIVE` - Robot is actively working
- `OFFLINE` - Robot is offline
- `ERROR` - Robot has an error
- `MAINTENANCE` - Robot is under maintenance

### Task Status
- `PENDING` - Task is pending assignment
- `ASSIGNED` - Task is assigned to a robot
- `RUNNING` - Task is currently running
- `COMPLETED` - Task is completed
- `FAILED` - Task failed
- `CANCELLED` - Task was cancelled

### Maintenance Type
- `PREVENTIVE` - Preventive maintenance
- `CORRECTIVE` - Corrective maintenance
- `INSPECTION` - Inspection
- `CALIBRATION` - Calibration

### Prediction Type
- `ANOMALY_SCORE` - Anomaly detection score
- `RUL` - Remaining Useful Life

## Troubleshooting

### Database Connection Error

Make sure PostgreSQL is running and credentials in `settings.py` are correct:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'robot_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Migration Errors

```bash
# Reset migrations (if needed)
pipenv run python manage.py migrate robot zero
pipenv run python manage.py makemigrations
pipenv run python manage.py migrate
```

### Port Already in Use

```bash
# Use a different port
pipenv run python manage.py runserver 8001
```

### GraphQL Schema Errors

If you see schema errors, make sure:
1. All migrations are applied
2. The server is restarted after schema changes
3. Check the GraphiQL interface for detailed error messages

### Import Errors

Make sure you're using pipenv:
```bash
pipenv shell
# or
pipenv run python manage.py <command>
```

## Development

### Running Tests

```bash
pipenv run python manage.py test
```

### Code Style

The project uses:
- Django coding style
- Type hints for better IDE support
- Comprehensive comments in `schema.py` explaining GraphQL concepts

### Adding New Queries/Mutations

1. Add the query/mutation method to `Query` or `Mutation` class in `robot/schema.py`
2. Use `@strawberry.field` for queries or `@strawberry.mutation` for mutations
3. Define input types using `@strawberry.input` if needed
4. Restart the server to see changes in GraphiQL

## License

This project is for educational purposes as part of the ISG Tunis curriculum.

## Author

Chaouki Bayoudhi - ISG Tunis

---

For more detailed examples and usage, see:
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Complete usage guide
- [QUERY_BY_CRITERIA.md](QUERY_BY_CRITERIA.md) - Filtering examples
- [test_queries.py](test_queries.py) - Python examples
- [query_by_criteria_examples.py](query_by_criteria_examples.py) - Filtering examples

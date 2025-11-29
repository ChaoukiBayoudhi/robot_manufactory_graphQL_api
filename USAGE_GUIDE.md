# GraphQL API Usage Guide

## Accessing the API

### 1. GraphiQL Interface (Recommended for Testing)
Open your browser and navigate to:
```
http://127.0.0.1:8000/graphql/
```

This provides an interactive GraphQL playground where you can:
- Write and test queries
- View the schema documentation
- See auto-completion suggestions
- Test mutations

---

## Available Queries

### 1. Get All Robots
```graphql
query {
  robots {
    id
    serial
    model
    capabilities
    status
    location
    lastSeen
    createdAt
    updatedAt
  }
}
```

### 2. Get Robots with Filters
```graphql
query {
  robots(model: "Industrial", status: "ACTIVE", location: "Factory Floor A") {
    id
    serial
    model
    status
    location
  }
}
```

### 3. Get Single Robot by ID
```graphql
query {
  robot(id: "1") {
    id
    serial
    model
    capabilities
    status
    location
  }
}
```

### 4. Get Robot by Serial Number
```graphql
query {
  robotBySerial(serial: "RBT-001") {
    id
    serial
    model
    status
  }
}
```

### 5. Get Robots by Capability
```graphql
query {
  robotsByCapability(capability: "welding") {
    id
    serial
    model
    capabilities
    status
  }
}
```

### 6. Search Robots
```graphql
query {
  searchRobots(searchTerm: "RBT") {
    id
    serial
    model
    location
    status
  }
}
```

### 7. Get All Tasks
```graphql
query {
  tasks {
    id
    requiredCapabilities
    status
    priority
    deadline
    createdAt
    assignedRobot {
      id
      serial
      model
    }
  }
}
```

### 8. Get Tasks with Filters
```graphql
query {
  tasks(status: "PENDING", priorityMin: 5, priorityMax: 10) {
    id
    requiredCapabilities
    status
    priority
    deadline
    assignedRobot {
      serial
    }
  }
}
```

### 9. Get High Priority Tasks
```graphql
query {
  highPriorityTasks(minPriority: 7) {
    id
    requiredCapabilities
    status
    priority
    deadline
  }
}
```

### 10. Get Overdue Tasks
```graphql
query {
  overdueTasks {
    id
    requiredCapabilities
    status
    priority
    deadline
    assignedRobot {
      serial
    }
  }
}
```

### 11. Get Telemetry Points
```graphql
query {
  telemetryPoints(robotId: "1", metricName: "temperature", limit: 100) {
    id
    robot {
      serial
    }
    timestamp
    metricName
    metricValue
    metadata
  }
}
```

### 12. Get Telemetry Statistics
```graphql
query {
  telemetryStatistics(robotId: "1", metricName: "temperature") {
    count
    averageValue
    minValue
    maxValue
    latestTimestamp
  }
}
```

### 13. Get Robot Statistics
```graphql
query {
  robotStatistics {
    totalRobots
    robotsByStatus
    averageTasksPerRobot
    robotsWithMaintenance
  }
}
```

### 14. Get Robot with All Details
```graphql
query {
  robotWithDetails(id: "1") {
    id
    serial
    model
    status
    assignedTasks {
      id
      status
      priority
    }
    telemetryPoints {
      metricName
      metricValue
      timestamp
    }
    maintenanceEvents {
      type
      timestamp
      notes
    }
    predictions {
      predictionType
      value
      timestamp
    }
  }
}
```

---

## Available Mutations

### 1. Create a Robot
```graphql
mutation {
  createRobot(data: {
    serial: "ROB-001"
    model: "Industrial Robot X1"
    capabilities: ["welding", "assembly"]
    location: "Factory Floor A"
    status: "IDLE"
    firmwareVersion: "v2.1.0"
  }) {
    id
    serial
    model
    capabilities
    status
    location
  }
}
```

### 2. Update a Robot
```graphql
mutation {
  updateRobot(data: {
    id: "1"
    status: "ACTIVE"
    location: "Factory Floor B"
    lastSeen: "2025-11-26T10:30:00Z"
  }) {
    id
    serial
    model
    status
    location
    lastSeen
  }
}
```

### 3. Delete a Robot
```graphql
mutation {
  deleteRobot(id: "1")
}
```

### 4. Create a Task
```graphql
mutation {
  createTask(data: {
    requiredCapabilities: ["welding", "precision"]
    priority: 5
    deadline: "2025-12-31T23:59:59Z"
    assignedRobotId: "1"
    status: "PENDING"
  }) {
    id
    requiredCapabilities
    status
    priority
    deadline
    assignedRobot {
      serial
    }
  }
}
```

### 5. Update a Task
```graphql
mutation {
  updateTask(data: {
    id: "1"
    status: "ASSIGNED"
    priority: 8
    assignedRobotId: "2"
  }) {
    id
    status
    priority
    assignedRobot {
      serial
    }
  }
}
```

### 6. Delete a Task
```graphql
mutation {
  deleteTask(id: "1")
}
```

### 7. Create Telemetry Point
```graphql
mutation {
  createTelemetry(data: {
    robotId: "1"
    metricName: "temperature"
    metricValue: 75.5
    timestamp: "2025-11-26T10:30:00Z"
    metadata: {"unit": "celsius", "sensor": "temp_sensor_1"}
  }) {
    id
    robot {
      serial
    }
    timestamp
    metricName
    metricValue
    metadata
  }
}
```

### 8. Create Telemetry (Current Timestamp)
```graphql
mutation {
  createTelemetry(data: {
    robotId: "1"
    metricName: "vibration"
    metricValue: 0.85
    metadata: {"anomaly": false}
  }) {
    id
    metricName
    metricValue
    timestamp
  }
}
```

### 9. Create Maintenance Event
```graphql
mutation {
  createMaintenanceEvent(data: {
    robotId: "1"
    type: "PREVENTIVE"
    notes: "Regular maintenance check"
    cost: 150.00
    timestamp: "2025-11-26T10:30:00Z"
  }) {
    id
    robot {
      serial
    }
    type
    timestamp
    notes
    cost
  }
}
```

### 10. Create Prediction
```graphql
mutation {
  createPrediction(data: {
    robotId: "1"
    predictionType: "ANOMALY_SCORE"
    value: 0.75
    modelVersion: "v1.2.0"
    timestamp: "2025-11-26T10:30:00Z"
  }) {
    id
    robot {
      serial
    }
    predictionType
    value
    modelVersion
    timestamp
  }
}
```

### 11. Bulk Update Robot Statuses
```graphql
mutation {
  bulkUpdateRobotStatuses(
    robotIds: ["1", "2", "3"]
    newStatus: "MAINTENANCE"
  ) {
    id
    serial
    status
  }
}
```

### 12. Create Robots from Templates
```graphql
mutation {
  createRobotsFromTemplates(
    templates: [
      {
        serial: "RBT-001"
        model: "WeldingBot"
        capabilities: ["welding"]
        location: "Floor A"
      },
      {
        serial: "RBT-002"
        model: "AssemblyBot"
        capabilities: ["assembly"]
        location: "Floor B"
      }
    ]
    locationPrefix: "Factory"
  ) {
    id
    serial
    model
    location
  }
}
```

### 13. Assign Tasks to Robots by Capability
```graphql
mutation {
  assignTasksToRobotsByCapability(taskIds: ["1", "2", "3"]) {
    id
    requiredCapabilities
    status
    assignedRobot {
      id
      serial
      capabilities
    }
  }
}
```

---

## Using cURL (Command Line)

### Query Example
```bash
curl -X POST http://127.0.0.1:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ robots { id serial model status } }"
  }'
```

### Mutation Example
```bash
curl -X POST http://127.0.0.1:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { createRobot(data: { serial: \"ROB-002\", model: \"Test Robot\", capabilities: [\"welding\"] }) { id serial model } }"
  }'
```

---

## Using Python Requests

```python
import requests

url = "http://127.0.0.1:8000/graphql/"

# Query
query = """
{
  robots {
    id
    serial
    model
  }
}
"""

response = requests.post(url, json={"query": query})
print(response.json())

# Mutation
mutation = """
mutation {
  createRobot(data: {
    serial: "ROB-003"
    model: "Python Robot"
    capabilities: ["testing"]
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

---

## Using JavaScript/Fetch

```javascript
const url = "http://127.0.0.1:8000/graphql/";

// Query
const query = `
  {
    robots {
      id
      serial
      model
    }
  }
`;

fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ query }),
})
  .then((res) => res.json())
  .then((data) => console.log(data));

// Mutation
const mutation = `
  mutation {
    createRobot(data: {
      serial: "ROB-004"
      model: "JS Robot"
    }) {
      id
      serial
    }
  }
`;

fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ query: mutation }),
})
  .then((res) => res.json())
  .then((data) => console.log(data));
```

---

## Status Values

### Task Status Values
- `PENDING`
- `ASSIGNED`
- `RUNNING`
- `COMPLETED`
- `FAILED`
- `CANCELLED`

### Robot Status Values
- `IDLE`
- `ACTIVE`
- `OFFLINE`
- `ERROR`
- `MAINTENANCE`

### Maintenance Type Values
- `PREVENTIVE`
- `CORRECTIVE`
- `INSPECTION`
- `CALIBRATION`

### Prediction Type Values
- `ANOMALY_SCORE`
- `RUL` (Remaining Useful Life)

---

## Tips

1. **Use GraphiQL** for interactive testing and exploring the schema
2. **Check the Docs panel** in GraphiQL to see all available fields and types
3. **Use variables** in GraphiQL for dynamic queries:
   ```graphql
   query GetRobots($modelFilter: String, $statusFilter: String) {
     robots(model: $modelFilter, status: $statusFilter) {
       id
       serial
       model
     }
   }
   ```
   Variables:
   ```json
   {
     "modelFilter": "Industrial",
     "statusFilter": "ACTIVE"
   }
   ```
4. **Use fragments** to reduce query duplication:
   ```graphql
   fragment RobotInfo on RobotType {
     id
     serial
     model
     status
   }
   
   query {
     robots {
       ...RobotInfo
       location
     }
   }
   ```
5. **Use aliases** when querying the same field multiple times:
   ```graphql
   query {
     activeRobots: robots(status: "ACTIVE") {
       id
       serial
     }
     idleRobots: robots(status: "IDLE") {
       id
       serial
     }
   }
   ```

---

## Advanced Features

### Lambda Expression Queries

The API includes several queries that demonstrate lambda expressions in Python:

- `robotsWithHighTelemetryCount(minTelemetryPoints: Int = 10)` - Filter robots by telemetry count
- `robotsSortedByCapabilityCount(reverse: Boolean = false)` - Sort robots by capability count
- `robotsWithRecentActivity(hours: Int = 24)` - Find recently active robots
- `telemetryAnomalies(robotId: ID, metricName: String, thresholdMultiplier: Float)` - Detect anomalies
- `tasksByUrgencyScore(minScore: Float = 0.5)` - Tasks sorted by computed urgency

These queries demonstrate advanced filtering and sorting using Python lambda expressions.

### Error Handling

GraphQL returns errors in a structured format:

```json
{
  "errors": [
    {
      "message": "Robot with id '999' does not exist",
      "locations": [{"line": 2, "column": 3}],
      "path": ["robot"]
    }
  ],
  "data": {
    "robot": null
  }
}
```

Always check the `errors` field in the response for error handling.

# Query by Criteria - Filtering Examples

## 🔍 Available Filtering Options

### 1. Query Robots

#### Filter by Model (Partial Match)
Filter robots by model name (case-insensitive partial match):

```graphql
query {
  robots(model: "Industrial") {
    id
    serial
    model
    status
    location
  }
}
```

**Example:** This will return all robots whose model contains "Industrial" (e.g., "Industrial Robot X1", "Industrial Robot Y2")

#### Filter by Status
Filter robots by status (exact match):

```graphql
query {
  robots(status: "ACTIVE") {
    id
    serial
    model
    status
    location
  }
}
```

**Available Status Values:**
- `IDLE`
- `ACTIVE`
- `OFFLINE`
- `ERROR`
- `MAINTENANCE`

#### Filter by Location (Partial Match)
Filter robots by location (case-insensitive partial match):

```graphql
query {
  robots(location: "Factory Floor") {
    id
    serial
    model
    location
  }
}
```

#### Filter by Serial Number (Partial Match)
Filter robots by serial number (case-insensitive partial match):

```graphql
query {
  robots(serial: "RBT-") {
    id
    serial
    model
  }
}
```

#### Combine Multiple Filters
You can combine multiple filters:

```graphql
query {
  robots(model: "Industrial", status: "ACTIVE", location: "Factory") {
    id
    serial
    model
    status
    location
  }
}
```

---

### 2. Query Tasks

#### Filter by Status
Filter tasks by their status:

```graphql
query {
  tasks(status: "PENDING") {
    id
    requiredCapabilities
    status
    priority
    assignedRobot {
      serial
      model
    }
  }
}
```

**Available Status Values:**
- `PENDING`
- `ASSIGNED`
- `RUNNING`
- `COMPLETED`
- `FAILED`
- `CANCELLED`

#### Filter by Priority Range
Filter tasks by priority range:

```graphql
query {
  tasks(priorityMin: 5, priorityMax: 10) {
    id
    requiredCapabilities
    status
    priority
    deadline
  }
}
```

#### Filter by Assigned Robot
Filter tasks assigned to a specific robot:

```graphql
query {
  tasks(robotId: "1") {
    id
    requiredCapabilities
    status
    priority
    assignedRobot {
      id
      serial
      model
    }
  }
}
```

#### Filter by Deadline Presence
Filter tasks that have or don't have a deadline:

```graphql
# Tasks with deadline
query {
  tasks(hasDeadline: true) {
    id
    requiredCapabilities
    priority
    deadline
  }
}

# Tasks without deadline
query {
  tasks(hasDeadline: false) {
    id
    requiredCapabilities
    priority
  }
}
```

---

### 3. Specialized Queries

#### Query Robots by Capability
Find robots that have a specific capability:

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

#### Query High Priority Tasks
Get tasks with priority >= min_priority:

```graphql
query {
  highPriorityTasks(minPriority: 7) {
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

#### Query Overdue Tasks
Get tasks that are past their deadline and not completed:

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

#### Search Robots
Search robots by serial, model, or location:

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

#### Robot Statistics
Get aggregated statistics about robots:

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

---

## 📝 Complete Examples

### Example 1: Find All Industrial Robots
```graphql
query GetIndustrialRobots {
  robots(model: "Industrial") {
    id
    serial
    model
    capabilities
    status
    location
  }
}
```

### Example 2: Find All Active Robots in Factory Floor A
```graphql
query GetActiveRobotsInFactoryA {
  robots(status: "ACTIVE", location: "Factory Floor A") {
    id
    serial
    model
    status
    location
    lastSeen
  }
}
```

### Example 3: Find All Pending Tasks
```graphql
query GetPendingTasks {
  tasks(status: "PENDING") {
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

### Example 4: Find High Priority Tasks (Priority >= 7)
```graphql
query GetHighPriorityTasks {
  highPriorityTasks(minPriority: 7) {
    id
    requiredCapabilities
    status
    priority
    deadline
    assignedRobot {
      serial
      status
    }
  }
}
```

### Example 5: Find Robots with Welding Capability
```graphql
query GetWeldingRobots {
  robotsByCapability(capability: "welding") {
    id
    serial
    model
    capabilities
    status
    location
  }
}
```

### Example 6: Combined Query with Multiple Filters
```graphql
query GetData {
  # Filter robots
  industrialRobots: robots(model: "Industrial", status: "ACTIVE") {
    id
    serial
    model
    status
  }
  
  # Get high priority tasks
  highPriorityTasks: highPriorityTasks(minPriority: 5) {
    id
    requiredCapabilities
    priority
    status
  }
  
  # Get overdue tasks
  overdueTasks: overdueTasks {
    id
    requiredCapabilities
    priority
    deadline
  }
  
  # Get statistics
  stats: robotStatistics {
    totalRobots
    robotsByStatus
    averageTasksPerRobot
  }
}
```

---

## 🧪 Testing with cURL

### Query Robots by Model
```bash
curl -X POST http://127.0.0.1:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { robots(model: \"Industrial\") { id serial model status } }"
  }'
```

### Query Tasks by Status
```bash
curl -X POST http://127.0.0.1:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { tasks(status: \"PENDING\") { id requiredCapabilities status priority } }"
  }'
```

### Query Robots by Capability
```bash
curl -X POST http://127.0.0.1:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { robotsByCapability(capability: \"welding\") { id serial model capabilities } }"
  }'
```

---

## 🐍 Python Example

```python
import requests

url = "http://127.0.0.1:8000/graphql/"

# Query robots by model
query = """
query GetRobotsByModel($model: String) {
  robots(model: $model) {
    id
    serial
    model
    status
  }
}
"""

variables = {"model": "Industrial"}

response = requests.post(url, json={"query": query, "variables": variables})
print(response.json())

# Query tasks by status and priority range
query = """
query GetTasksByCriteria($status: String, $minPriority: Int, $maxPriority: Int) {
  tasks(status: $status, priorityMin: $minPriority, priorityMax: $maxPriority) {
    id
    requiredCapabilities
    status
    priority
  }
}
"""

variables = {
    "status": "PENDING",
    "minPriority": 5,
    "maxPriority": 10
}

response = requests.post(url, json={"query": query, "variables": variables})
print(response.json())
```

---

## 💡 Using Variables in GraphiQL

In the GraphiQL interface, you can use variables for dynamic filtering:

**Query Panel:**
```graphql
query GetRobotsByModel($modelFilter: String, $statusFilter: String) {
  robots(model: $modelFilter, status: $statusFilter) {
    id
    serial
    model
    status
  }
}
```

**Variables Panel (bottom left):**
```json
{
  "modelFilter": "Industrial",
  "statusFilter": "ACTIVE"
}
```

**Query Panel:**
```graphql
query GetTasksByCriteria($statusFilter: String, $minPriority: Int) {
  tasks(status: $statusFilter, priorityMin: $minPriority) {
    id
    requiredCapabilities
    status
    priority
  }
}
```

**Variables Panel:**
```json
{
  "statusFilter": "PENDING",
  "minPriority": 5
}
```

---

## 📊 Complete Filtering Reference

### Robots Query Filters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `model` | String (optional) | Case-insensitive partial match on model name | `"Industrial"` |
| `status` | String (optional) | Exact match on robot status | `"ACTIVE"` |
| `location` | String (optional) | Case-insensitive partial match on location | `"Factory Floor"` |
| `serial` | String (optional) | Case-insensitive partial match on serial number | `"RBT-"` |

### Tasks Query Filters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | String (optional) | Exact match on task status | `"PENDING"` |
| `priorityMin` | Int (optional) | Minimum priority (>=) | `5` |
| `priorityMax` | Int (optional) | Maximum priority (<=) | `10` |
| `robotId` | ID (optional) | Filter by assigned robot ID | `"1"` |
| `hasDeadline` | Boolean (optional) | Filter by deadline presence | `true` |

### Specialized Queries

| Query | Parameters | Description |
|-------|-----------|-------------|
| `robotsByCapability` | `capability: String!` | Find robots with specific capability |
| `highPriorityTasks` | `minPriority: Int = 5` | Tasks with priority >= minPriority |
| `overdueTasks` | None | Tasks past deadline, not completed |
| `searchRobots` | `searchTerm: String!` | Search across serial, model, location |
| `robotStatistics` | None | Aggregated robot statistics |

---

## 🔮 Advanced Filtering Examples

### Lambda Expression Queries

The API also includes queries that use lambda expressions for complex filtering:

- `robotsWithHighTelemetryCount(minTelemetryPoints: Int = 10)` - Robots with at least N telemetry points
- `robotsSortedByCapabilityCount(reverse: Boolean = false)` - Robots sorted by capability count
- `robotsWithRecentActivity(hours: Int = 24)` - Robots active in last N hours
- `telemetryAnomalies(robotId: ID, metricName: String, thresholdMultiplier: Float)` - Find anomaly telemetry
- `tasksByUrgencyScore(minScore: Float = 0.5)` - Tasks sorted by computed urgency score

See the schema documentation for more details on these advanced queries.

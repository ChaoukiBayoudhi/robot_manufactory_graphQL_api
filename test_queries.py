"""
Example script to test GraphQL queries and mutations.
Run with: pipenv run python test_queries.py
"""
import json
import time
from datetime import datetime

import requests

API_URL = "http://localhost:8000/graphql/"


def execute_query(query: str, variables: dict = None):
    """Execute a GraphQL query or mutation."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(API_URL, json=payload)
    return response.json()


def print_response(title: str, response: dict):
    """Pretty print the response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(json.dumps(response, indent=2))


# 1. Query all robots
print("\n1. Querying all robots...")
query_robots = """
{
  robots {
    id
    serial
    model
    capabilities
    status
    location
    lastSeen
  }
}
"""
response = execute_query(query_robots)
print_response("All Robots", response)

# 2. Create a robot
print("\n2. Creating a robot...")
mutation_create_robot = """
mutation {
  createRobot(data: {
    serial: "RBT-LOAD-01"
    model: "TEST-1"
    capabilities: ["welding", "pick-place"]
    location: "Factory Floor A"
  }) {
    id
    serial
    model
    capabilities
    status
    location
  }
}
"""
response = execute_query(mutation_create_robot)
print_response("Create Robot", response)

# Extract robot ID if created
robot_id = None
if response.get("data") and response["data"].get("createRobot"):
    robot_id = response["data"]["createRobot"]["id"]
    print(f"\n✓ Robot created with ID: {robot_id}")

# 3. Create telemetry (if robot was created)
if robot_id:
    print("\n3. Creating telemetry points...")
    for i in range(5):
        mutation_telemetry = f"""
        mutation {{
          createTelemetry(data: {{
            robotId: "{robot_id}"
            metricName: "temperature"
            metricValue: {50 + i}
            timestamp: "{datetime.now().isoformat()}Z"
            metadata: {{"test": true, "iteration": {i}}}
          }}) {{
            id
            robot {{
              id
              serial
            }}
            metricName
            metricValue
            timestamp
          }}
        }}
        """
        response = execute_query(mutation_telemetry)
        print_response(f"Telemetry Point {i+1}", response)
        time.sleep(0.2)

# 4. Query robots again to see updates
print("\n4. Querying robots again...")
response = execute_query(query_robots)
print_response("All Robots (Updated)", response)

# 5. Create a task
print("\n5. Creating a task...")
mutation_create_task = """
mutation {
  createTask(data: {
    requiredCapabilities: ["welding"]
    priority: 5
    deadline: "2025-12-31T23:59:59Z"
  }) {
    id
    requiredCapabilities
    status
    priority
    deadline
    assignedRobot {
      id
      serial
      model
    }
  }
}
"""
response = execute_query(mutation_create_task)
print_response("Create Task", response)

# 6. Query all tasks
print("\n6. Querying all tasks...")
query_tasks = """
{
  tasks {
    id
    requiredCapabilities
    status
    priority
    deadline
    assignedRobot {
      id
      serial
      model
    }
  }
}
"""
response = execute_query(query_tasks)
print_response("All Tasks", response)

print("\n" + "="*60)
print("Testing complete!")
print("="*60)



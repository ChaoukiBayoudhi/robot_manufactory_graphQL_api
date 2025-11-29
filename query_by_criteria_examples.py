"""
Examples of querying by criteria/filters in the GraphQL API
"""

import requests
import json

GRAPHQL_URL = "http://127.0.0.1:8000/graphql/"


def execute_query(query: str, variables: dict = None):
    """Execute a GraphQL query."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    response = requests.post(GRAPHQL_URL, json=payload)
    response.raise_for_status()
    return response.json()


def print_section(title: str, response: dict):
    """Print a formatted section."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(json.dumps(response, indent=2, default=str))


# ==================== QUERY BY CRITERIA EXAMPLES ====================

def example_1_query_all_robots():
    """Example 1: Query all robots (no filter)"""
    query = """
    {
      robots {
        id
        serial
        model
        status
        location
      }
    }
    """
    return execute_query(query)


def example_2_query_robots_by_model():
    """Example 2: Query robots filtered by model (partial match)"""
    query = """
    query GetRobotsByModel($model: String) {
      robots(model: $model) {
        id
        serial
        model
        status
        capabilities
      }
    }
    """
    variables = {"model": "Industrial"}
    return execute_query(query, variables)


def example_3_query_robots_by_different_model():
    """Example 3: Query robots by different model"""
    query = """
    query {
      robots(model: "Precision") {
        id
        serial
        model
        status
      }
    }
    """
    return execute_query(query)


def example_4_query_all_tasks():
    """Example 4: Query all tasks (no filter)"""
    query = """
    {
      tasks {
        id
        requiredCapabilities
        status
        priority
        assignedRobot {
          serial
        }
      }
    }
    """
    return execute_query(query)


def example_5_query_tasks_by_status():
    """Example 5: Query tasks filtered by status"""
    query = """
    query GetTasksByStatus($status: String) {
      tasks(status: $status) {
        id
        requiredCapabilities
        status
        priority
        deadline
        assignedRobot {
          id
          serial
        }
      }
    }
    """
    variables = {"status": "PENDING"}
    return execute_query(query, variables)


def example_6_query_tasks_by_different_status():
    """Example 6: Query tasks by different status"""
    query = """
    query {
      tasks(status: "ASSIGNED") {
        id
        requiredCapabilities
        status
        priority
      }
    }
    """
    return execute_query(query)


def example_7_combined_query():
    """Example 7: Multiple queries with different criteria in one request"""
    query = """
    query CombinedQuery {
      # Get all robots
      allRobots: robots {
        id
        serial
        model
      }
      
      # Get industrial robots only
      industrialRobots: robots(model: "Industrial") {
        id
        serial
        model
      }
      
      # Get all tasks
      allTasks: tasks {
        id
        status
        priority
      }
      
      # Get pending tasks only
      pendingTasks: tasks(status: "PENDING") {
        id
        status
        priority
      }
    }
    """
    return execute_query(query)


def example_8_query_with_variables():
    """Example 8: Using variables for dynamic filtering"""
    query = """
    query DynamicQuery($modelFilter: String, $statusFilter: String) {
      robots(model: $modelFilter) {
        id
        serial
        model
      }
      tasks(status: $statusFilter) {
        id
        requiredCapabilities
        status
      }
    }
    """
    variables = {
        "modelFilter": "Industrial",
        "statusFilter": "PENDING"
    }
    return execute_query(query, variables)


def example_9_query_robots_by_status():
    """Example 9: Query robots filtered by status"""
    query = """
    query GetRobotsByStatus($status: String) {
      robots(status: $status) {
        id
        serial
        model
        status
        location
      }
    }
    """
    variables = {"status": "ACTIVE"}
    return execute_query(query, variables)


def example_10_query_tasks_by_priority_range():
    """Example 10: Query tasks by priority range"""
    query = """
    query GetTasksByPriority($minPriority: Int, $maxPriority: Int) {
      tasks(priorityMin: $minPriority, priorityMax: $maxPriority) {
        id
        requiredCapabilities
        status
        priority
        deadline
      }
    }
    """
    variables = {
        "minPriority": 5,
        "maxPriority": 10
    }
    return execute_query(query, variables)


def example_11_query_robots_by_capability():
    """Example 11: Query robots by capability"""
    query = """
    query GetRobotsByCapability($capability: String) {
      robotsByCapability(capability: $capability) {
        id
        serial
        model
        capabilities
        status
      }
    }
    """
    variables = {"capability": "welding"}
    return execute_query(query, variables)


def example_12_query_high_priority_tasks():
    """Example 12: Query high priority tasks"""
    query = """
    query GetHighPriorityTasks($minPriority: Int) {
      highPriorityTasks(minPriority: $minPriority) {
        id
        requiredCapabilities
        status
        priority
        deadline
        assignedRobot {
          serial
          model
        }
      }
    }
    """
    variables = {"minPriority": 7}
    return execute_query(query, variables)


def example_13_query_overdue_tasks():
    """Example 13: Query overdue tasks"""
    query = """
    query GetOverdueTasks {
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
    """
    return execute_query(query)


def example_14_query_robot_statistics():
    """Example 14: Query robot statistics"""
    query = """
    query GetRobotStatistics {
      robotStatistics {
        totalRobots
        robotsByStatus
        averageTasksPerRobot
        robotsWithMaintenance
      }
    }
    """
    return execute_query(query)


def example_15_query_search_robots():
    """Example 15: Search robots by term"""
    query = """
    query SearchRobots($searchTerm: String!) {
      searchRobots(searchTerm: $searchTerm) {
        id
        serial
        model
        location
        status
      }
    }
    """
    variables = {"searchTerm": "RBT"}
    return execute_query(query, variables)


if __name__ == "__main__":
    print("🔍 Query by Criteria Examples")
    print("=" * 70)
    
    try:
        # Example 1: Query all robots
        print_section("Example 1: Query All Robots (No Filter)", 
                     example_1_query_all_robots())
        
        # Example 2: Query robots by model
        print_section("Example 2: Query Robots by Model (Industrial)", 
                     example_2_query_robots_by_model())
        
        # Example 3: Query robots by different model
        print_section("Example 3: Query Robots by Model (Precision)", 
                     example_3_query_robots_by_different_model())
        
        # Example 4: Query all tasks
        print_section("Example 4: Query All Tasks (No Filter)", 
                     example_4_query_all_tasks())
        
        # Example 5: Query tasks by status
        print_section("Example 5: Query Tasks by Status (PENDING)", 
                     example_5_query_tasks_by_status())
        
        # Example 6: Query tasks by different status
        print_section("Example 6: Query Tasks by Status (ASSIGNED)", 
                     example_6_query_tasks_by_different_status())
        
        # Example 7: Combined query
        print_section("Example 7: Combined Query (Multiple Filters)", 
                     example_7_combined_query())
        
        # Example 8: Using variables
        print_section("Example 8: Dynamic Query with Variables", 
                     example_8_query_with_variables())
        
        # Example 9: Query robots by status
        print_section("Example 9: Query Robots by Status (ACTIVE)", 
                     example_9_query_robots_by_status())
        
        # Example 10: Query tasks by priority range
        print_section("Example 10: Query Tasks by Priority Range (5-10)", 
                     example_10_query_tasks_by_priority_range())
        
        # Example 11: Query robots by capability
        print_section("Example 11: Query Robots by Capability (welding)", 
                     example_11_query_robots_by_capability())
        
        # Example 12: Query high priority tasks
        print_section("Example 12: Query High Priority Tasks (min: 7)", 
                     example_12_query_high_priority_tasks())
        
        # Example 13: Query overdue tasks
        print_section("Example 13: Query Overdue Tasks", 
                     example_13_query_overdue_tasks())
        
        # Example 14: Query robot statistics
        print_section("Example 14: Query Robot Statistics", 
                     example_14_query_robot_statistics())
        
        # Example 15: Search robots
        print_section("Example 15: Search Robots (term: 'RBT')", 
                     example_15_query_search_robots())
        
        print("\n✅ All query-by-criteria examples executed successfully!")
        print("\n💡 Tips:")
        print("   - Use 'model', 'status', 'location', 'serial' to filter robots")
        print("   - Use 'status', 'priorityMin', 'priorityMax', 'robotId' to filter tasks")
        print("   - Use 'robotsByCapability' to find robots with specific capabilities")
        print("   - Use 'highPriorityTasks' and 'overdueTasks' for specialized queries")
        print("   - Use 'robotStatistics' for aggregated data")
        print("   - Use 'searchRobots' for full-text search across multiple fields")
        print("   - Omit filter parameters to get all records")
        print("   - Use variables for dynamic filtering in GraphiQL")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure the Django server is running: pipenv run python manage.py runserver")
    except Exception as e:
        print(f"\n❌ Error: {e}")


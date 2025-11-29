"""
URL configuration for robot_manufactory_graphQL_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from strawberry.django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from robot.schema import schema

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # ============================================================================
    # GRAPHQL ENDPOINT CONFIGURATION
    # ============================================================================
    # Two options are shown below. The active one (line 2) is recommended for
    # development and production use.
    
    # OPTION 1 (Commented - Basic Configuration):
    # --------------------------------------------
    # path("graphql", GraphQLView.as_view(schema=schema)),
    #
    # Differences from Option 2:
    # - No trailing slash: URL is "http://localhost:8000/graphql"
    #   (Django will redirect to "graphql/" if APPEND_SLASH=True)
    # - No csrf_exempt: Requires CSRF token for POST requests
    #   (This can cause issues with GraphQL clients and CORS)
    # - No graphiql=True: No interactive GraphQL playground in browser
    #   (You can only use it via API clients like Postman, cURL, etc.)
    #
    # When to use:
    # - If you need strict CSRF protection (rare for GraphQL APIs)
    # - If you don't want the GraphiQL interface (security concern in production)
    # - If you prefer URLs without trailing slashes
    
    # OPTION 2 (Active - Recommended Configuration):
    # -----------------------------------------------
    # path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=True))),
    #
    # Why this is better:
    # 1. Trailing slash ("graphql/"):
    #    - Matches Django's URL convention (APPEND_SLASH=True by default)
    #    - URL: "http://localhost:8000/graphql/"
    #    - Avoids redirects and is more RESTful
    #
    # 2. csrf_exempt wrapper:
    #    - Disables CSRF protection for this endpoint
    #    - GraphQL APIs typically don't use Django's CSRF tokens
    #    - Allows cross-origin requests (important for frontend apps)
    #    - Note: In production, use proper authentication (JWT, API keys, etc.)
    #      instead of relying on CSRF tokens
    #
    # 3. graphiql=True:
    #    - Enables the interactive GraphiQL playground at the endpoint
    #    - Allows testing queries/mutations directly in the browser
    #    - Provides schema documentation and auto-completion
    #    - Very useful for development and API exploration
    #    - In production, you may want to disable this (set graphiql=False)
    #      or restrict access based on authentication
    #
    # When to use:
    # - Development: Perfect for testing and exploring the API
    # - Production: Good, but consider:
    #   * Setting graphiql=False if you don't want public schema access
    #   * Adding authentication middleware
    #   * Using rate limiting for API protection
    #
    # Example usage:
    # - Browser: http://localhost:8000/graphql/ (opens GraphiQL interface)
    # - API client: POST http://localhost:8000/graphql/ with JSON body
    # - cURL: curl -X POST http://localhost:8000/graphql/ -H "Content-Type: application/json" -d '{"query": "{ robots { id } }"}'
    
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=True))),
]

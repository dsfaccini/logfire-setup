"""Integration categories and mappings for Logfire optional dependencies."""

from dataclasses import dataclass


@dataclass
class Integration:
    """Represents a single Logfire integration."""

    extra: str
    display_name: str
    description: str
    package_patterns: list[str]


@dataclass
class Category:
    """Represents a category of integrations."""

    name: str
    description: str
    integrations: list[Integration]


# Define all integration categories
CATEGORIES = [
    Category(
        name="Recommended",
        description="Most commonly used integrations",
        integrations=[
            Integration(
                extra="httpx",
                display_name="HTTPX",
                description="HTTPX HTTP client library",
                package_patterns=["httpx"],
            ),
            Integration(
                extra="fastapi",
                display_name="FastAPI",
                description="FastAPI framework instrumentation",
                package_patterns=["fastapi"],
            ),
            Integration(
                extra="pydantic-ai",
                display_name="Pydantic AI",
                description="Pydantic AI agent framework instrumentation",
                package_patterns=["pydantic-ai", "pydantic_ai"],
            ),
            Integration(
                extra="sqlalchemy",
                display_name="SQLAlchemy",
                description="SQLAlchemy ORM instrumentation",
                package_patterns=["sqlalchemy"],
            ),
        ],
    ),
    Category(
        name="Web Frameworks",
        description="Web framework instrumentation",
        integrations=[
            Integration(
                extra="django",
                display_name="Django",
                description="Django web framework (includes ASGI support)",
                package_patterns=["django"],
            ),
            Integration(
                extra="flask",
                display_name="Flask",
                description="Flask framework instrumentation",
                package_patterns=["flask"],
            ),
            Integration(
                extra="starlette",
                display_name="Starlette",
                description="Starlette framework instrumentation",
                package_patterns=["starlette"],
            ),
            Integration(
                extra="asgi",
                display_name="ASGI",
                description="ASGI application instrumentation",
                package_patterns=["asgi", "uvicorn", "hypercorn"],
            ),
            Integration(
                extra="wsgi",
                display_name="WSGI",
                description="WSGI application instrumentation",
                package_patterns=["wsgi", "gunicorn"],
            ),
        ],
    ),
    Category(
        name="HTTP Clients",
        description="HTTP client library instrumentation",
        integrations=[
            Integration(
                extra="requests",
                display_name="Requests",
                description="Python Requests library HTTP client",
                package_patterns=["requests"],
            ),
            Integration(
                extra="aiohttp-client",
                display_name="aiohttp Client",
                description="aiohttp HTTP client tracing",
                package_patterns=["aiohttp"],
            ),
            Integration(
                extra="aiohttp-server",
                display_name="aiohttp Server",
                description="aiohttp server/web framework",
                package_patterns=["aiohttp"],
            ),
        ],
    ),
    Category(
        name="Databases",
        description="Database client instrumentation",
        integrations=[
            Integration(
                extra="asyncpg",
                display_name="asyncpg",
                description="asyncpg PostgreSQL async driver",
                package_patterns=["asyncpg"],
            ),
            Integration(
                extra="psycopg",
                display_name="psycopg",
                description="psycopg PostgreSQL client (v3.x)",
                package_patterns=["psycopg"],
            ),
            Integration(
                extra="psycopg2",
                display_name="psycopg2",
                description="psycopg2 PostgreSQL client (legacy)",
                package_patterns=["psycopg2", "psycopg2-binary"],
            ),
            Integration(
                extra="pymongo",
                display_name="PyMongo",
                description="PyMongo MongoDB driver",
                package_patterns=["pymongo"],
            ),
            Integration(
                extra="redis",
                display_name="Redis",
                description="Redis client instrumentation",
                package_patterns=["redis"],
            ),
            Integration(
                extra="mysql",
                display_name="MySQL",
                description="MySQL database driver",
                package_patterns=["mysql-connector-python", "pymysql", "mysqlclient"],
            ),
            Integration(
                extra="sqlite3",
                display_name="SQLite3",
                description="SQLite3 database instrumentation",
                package_patterns=["sqlite3", "aiosqlite"],
            ),
        ],
    ),
    Category(
        name="Task Queues",
        description="Task queue and message broker instrumentation",
        integrations=[
            Integration(
                extra="celery",
                display_name="Celery",
                description="Celery task queue instrumentation",
                package_patterns=["celery"],
            ),
        ],
    ),
    Category(
        name="Cloud & Serverless",
        description="Cloud platform and serverless instrumentation",
        integrations=[
            Integration(
                extra="aws-lambda",
                display_name="AWS Lambda",
                description="AWS Lambda function instrumentation",
                package_patterns=["boto3", "botocore"],
            ),
        ],
    ),
    Category(
        name="LLM & AI",
        description="Large language model and AI instrumentation",
        integrations=[
            Integration(
                extra="google-genai",
                display_name="Google GenAI",
                description="Google GenAI instrumentation",
                package_patterns=["google-genai", "google-generativeai"],
            ),
            Integration(
                extra="litellm",
                display_name="LiteLLM",
                description="LiteLLM gateway instrumentation",
                package_patterns=["litellm"],
            ),
        ],
    ),
    Category(
        name="System Monitoring",
        description="System-level metrics and monitoring",
        integrations=[
            Integration(
                extra="system-metrics",
                display_name="System Metrics",
                description="System-level metrics (CPU, memory, etc.)",
                package_patterns=["psutil"],
            ),
        ],
    ),
]


def get_all_integrations() -> list[Integration]:
    """Get a flat list of all integrations across all categories."""
    return [
        integration for category in CATEGORIES for integration in category.integrations
    ]


def get_integration_by_extra(extra: str) -> Integration | None:
    """Get an integration by its extra name."""
    for integration in get_all_integrations():
        if integration.extra == extra:
            return integration
    return None

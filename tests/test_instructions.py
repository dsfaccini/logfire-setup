"""Tests for instruction generation."""

from logfire_setup.categories import Integration
from logfire_setup.instructions import (
    generate_core_instructions,
    generate_instructions,
    generate_integration_instructions,
)


def test_generate_core_instructions():
    """Test core instructions generation."""
    instructions = generate_core_instructions()

    # Check for key sections
    assert "# Logfire" in instructions
    assert "## Setup" in instructions
    assert "logfire.configure(send_to_logfire='if-token-present')" in instructions
    assert "## Logging Patterns" in instructions
    assert "### Spans" in instructions
    assert "### F-Strings" in instructions
    assert "### Structured Attributes" in instructions
    assert "### Exception Handling" in instructions
    assert "### Function Tracing" in instructions
    assert "## Log Levels" in instructions
    assert "## Data Privacy" in instructions
    assert "## Resources" in instructions


def test_generate_integration_instructions_httpx():
    """Test HTTPX integration instructions with extended examples."""
    integrations = [
        Integration("httpx", "HTTPX", "HTTPX HTTP client", ["httpx"]),
    ]

    instructions = generate_integration_instructions(integrations)

    # Check for HTTPX examples
    assert "## Instrumentation" in instructions
    assert "# HTTP clients" in instructions
    assert "# Global instrumentation (all clients)" in instructions
    assert "logfire.instrument_httpx()" in instructions
    assert "# Per-client instrumentation" in instructions
    assert "async with httpx.AsyncClient() as client:" in instructions
    assert "# Capture all request/response data" in instructions
    assert "capture_request_json_body=True" in instructions
    assert "capture_response_json_body=True" in instructions


def test_generate_integration_instructions_fastapi():
    """Test FastAPI integration instructions."""
    integrations = [
        Integration("fastapi", "FastAPI", "FastAPI framework", ["fastapi"]),
    ]

    instructions = generate_integration_instructions(integrations)

    assert "# Web framework" in instructions
    assert "logfire.instrument_fastapi(app)" in instructions


def test_generate_integration_instructions_llm():
    """Test LLM/AI integration instructions include pydantic-ai."""
    integrations = [
        Integration("google-genai", "Google GenAI", "Google GenAI", ["google-genai"]),
    ]

    instructions = generate_integration_instructions(integrations)

    assert "# LLM & AI" in instructions
    assert "# Pydantic AI" in instructions
    assert "logfire.instrument_pydantic_ai()" in instructions
    assert "# Google GenAI" in instructions


def test_generate_integration_instructions_multiple():
    """Test multiple integrations from different categories."""
    integrations = [
        Integration("fastapi", "FastAPI", "FastAPI framework", ["fastapi"]),
        Integration("httpx", "HTTPX", "HTTPX HTTP client", ["httpx"]),
        Integration("sqlalchemy", "SQLAlchemy", "SQLAlchemy ORM", ["sqlalchemy"]),
    ]

    instructions = generate_integration_instructions(integrations)

    assert "# Web framework" in instructions
    assert "logfire.instrument_fastapi(app)" in instructions
    assert "# HTTP clients" in instructions
    assert "logfire.instrument_httpx()" in instructions
    assert "# Databases" in instructions
    assert "logfire.instrument_sqlalchemy(engine=engine)" in instructions


def test_generate_instructions_complete():
    """Test complete instruction generation."""
    integrations = [
        Integration("fastapi", "FastAPI", "FastAPI framework", ["fastapi"]),
    ]

    instructions = generate_instructions(integrations)

    # Should have both core and integration instructions
    assert "# Logfire" in instructions
    assert "## Setup" in instructions
    assert "## Instrumentation" in instructions
    assert "logfire.instrument_fastapi(app)" in instructions


def test_generate_instructions_no_integrations():
    """Test instruction generation with no integrations."""
    instructions = generate_instructions([])

    # Should only have core instructions
    assert "# Logfire" in instructions
    assert "## Setup" in instructions
    # Should not have instrumentation section
    assert "## Instrumentation" not in instructions


if __name__ == "__main__":
    test_generate_core_instructions()
    print("✓ test_generate_core_instructions")

    test_generate_integration_instructions_httpx()
    print("✓ test_generate_integration_instructions_httpx")

    test_generate_integration_instructions_fastapi()
    print("✓ test_generate_integration_instructions_fastapi")

    test_generate_integration_instructions_llm()
    print("✓ test_generate_integration_instructions_llm")

    test_generate_integration_instructions_multiple()
    print("✓ test_generate_integration_instructions_multiple")

    test_generate_instructions_complete()
    print("✓ test_generate_instructions_complete")

    test_generate_instructions_no_integrations()
    print("✓ test_generate_instructions_no_integrations")

    print("\nAll instructions tests passed!")

"""
tests/unit/test_openapi_schema.py
==================================
Valida que el esquema OpenAPI se genera sin errores tras upgrades FastAPI/Pydantic.
"""
from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def openapi_schema():
    from app.main import app

    return app.openapi()


def test_openapi_has_core_metadata(openapi_schema):
    assert openapi_schema["info"]["title"]
    assert openapi_schema["info"]["version"]
    assert "paths" in openapi_schema
    assert len(openapi_schema["paths"]) > 0


def test_openapi_health_path(openapi_schema):
    assert "/health" in openapi_schema["paths"]
    get_op = openapi_schema["paths"]["/health"].get("get", {})
    assert get_op
    assert "200" in get_op.get("responses", {})


def test_openapi_auth_paths(openapi_schema):
    assert "/api/v1/auth/login" in openapi_schema["paths"]


def test_openapi_components_schemas(openapi_schema):
    components = openapi_schema.get("components", {})
    schemas = components.get("schemas", {})
    assert len(schemas) > 0

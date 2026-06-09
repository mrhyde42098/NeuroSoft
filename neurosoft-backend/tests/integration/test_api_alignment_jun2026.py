"""Regresión: alineación frontend↔backend (jun 2026)."""

from __future__ import annotations

from app.application.dtos.therapy_dtos import TherapySessionUpdateDTO
from app.main import app


def test_single_post_backup_route():
    posts = [
        r
        for r in app.routes
        if hasattr(r, "path") and r.path == "/api/v1/backup/" and hasattr(r, "methods") and "POST" in r.methods
    ]
    assert len(posts) == 1
    assert posts[0].endpoint.__name__ == "create_server_backup"


def test_therapy_session_update_dto_includes_modalidad_duracion():
    dto = TherapySessionUpdateDTO(modalidad="telepsicologia", duracion_min=45)
    dumped = dto.model_dump(exclude_none=True)
    assert dumped["modalidad"] == "telepsicologia"
    assert dumped["duracion_min"] == 45


def test_evaluation_sign_routes_registered():
    paths = {getattr(r, "path", "") for r in app.routes}
    assert any(p.endswith("/evaluations/detail/{eval_id}/sign") for p in paths)
    assert any(p.endswith("/evaluations/detail/{eval_id}/signature") for p in paths)


def test_agenda_list_route_registered():
    gets = [
        r
        for r in app.routes
        if getattr(r, "path", "") == "/api/v1/agenda/" and hasattr(r, "methods") and "GET" in r.methods
    ]
    assert len(gets) == 1

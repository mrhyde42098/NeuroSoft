"""
tests/integration/test_rehab.py
=================================
Módulo de rehabilitación neuropsicológica.

Cubre:
  1. Seed del catálogo (Stroop, N-back, Fluencia verbal, Tachado).
  2. CRUD del plan + transición a estado 'activo' al firmarse.
  3. Firma del plan: payload canónico + hash SHA-256 + idempotencia.
  4. Sesiones registradas por el clínico.
  5. Generación de link público y vista pública del paciente.
  6. Submit de resultado vía link público (sin auth) y conteo de uso.
  7. Aislamiento entre pacientes.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

import pytest

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def _make_patient(db, doc="REHAB001", first="Lucas"):
    from app.infrastructure.database.orm_models import PatientORM

    p = PatientORM(
        id=str(uuid.uuid4()),
        numero_documento=doc,
        tipo_documento="CC",
        primer_nombre=first,
        primer_apellido="Test",
        fecha_nacimiento=date(2010, 1, 1),
        sexo="H",
        escolaridad="Primaria Incompleta",
        lateralidad="Diestro",
        fecha_atencion=date(2026, 3, 20),
        is_active=True,
        created_at=datetime.now(UTC),
    )
    db.add(p)
    db.flush()
    return p


def _seed(db):
    from app.application.use_cases.rehab_use_cases import seed_activity_catalog

    seed_activity_catalog(db)


# ═══════════════════════════════════════════════════════════════
# 1. CATÁLOGO
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestActivityCatalog:
    def test_seed_es_idempotente(self, in_memory_db):
        from app.application.use_cases.rehab_use_cases import seed_activity_catalog
        from app.infrastructure.database.orm_models import RehabActivityCatalogORM

        n1 = seed_activity_catalog(in_memory_db)
        n2 = seed_activity_catalog(in_memory_db)
        assert n1 >= 4
        assert n2 == 0  # ya existían

        rows = in_memory_db.query(RehabActivityCatalogORM).all()
        slugs = {r.slug for r in rows}
        assert "stroop" in slugs
        assert "n_back" in slugs
        assert "fluency_verbal" in slugs
        assert "tachado" in slugs

    def test_listar_actividades_devuelve_parametros_parseados(self, in_memory_db):
        from app.application.use_cases.rehab_use_cases import (
            ListActivitiesUseCase,
            seed_activity_catalog,
        )

        seed_activity_catalog(in_memory_db)
        items = ListActivitiesUseCase(in_memory_db).execute()
        stroop = next(a for a in items if a["slug"] == "stroop")
        assert isinstance(stroop["parametros_default"], dict)
        assert "trials" in stroop["parametros_default"]
        assert stroop["dominio"] == "funciones_ejecutivas"

    def test_filtrar_por_dominio(self, in_memory_db):
        from app.application.use_cases.rehab_use_cases import (
            ListActivitiesUseCase,
            seed_activity_catalog,
        )

        seed_activity_catalog(in_memory_db)
        items = ListActivitiesUseCase(in_memory_db).execute(dominio="atencion")
        assert all(a["dominio"] == "atencion" for a in items)
        assert any(a["slug"] == "tachado" for a in items)


# ═══════════════════════════════════════════════════════════════
# 2. PLAN — CRUD
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestRehabPlan:
    def test_crear_plan_estado_borrador(self, in_memory_db):
        from app.application.dtos.rehab_dtos import RehabPlanCreateDTO
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabPlanUseCase,
        )

        p = _make_patient(in_memory_db)
        in_memory_db.commit()

        dto = RehabPlanCreateDTO(
            patient_id=p.id,
            fecha_inicio=date(2026, 4, 1),
            frecuencia_semanal=3,
            objetivos="Mejorar atención sostenida",
            dominios=["atencion", "memoria_trabajo"],
            actividades=[
                {"slug": "stroop", "dificultad": 2},
                {"slug": "n_back", "dificultad": 1, "parametros": {"n": 1}},
            ],
        )
        plan = CreateRehabPlanUseCase(in_memory_db).execute(dto)
        in_memory_db.commit()

        assert plan["estado"] == "borrador"
        assert plan["dominios"] == ["atencion", "memoria_trabajo"]
        assert len(plan["actividades"]) == 2
        assert plan["signed_at"] is None

    def test_crear_plan_paciente_inexistente_lanza(self, in_memory_db):
        from app.application.dtos.rehab_dtos import RehabPlanCreateDTO
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabPlanUseCase,
        )
        from app.core.exceptions import PatientNotFoundError

        dto = RehabPlanCreateDTO(
            patient_id="no-existe",
            fecha_inicio=date(2026, 4, 1),
        )
        with pytest.raises(PatientNotFoundError):
            CreateRehabPlanUseCase(in_memory_db).execute(dto)

    def test_actualizar_plan_no_firmado(self, in_memory_db):
        from app.application.dtos.rehab_dtos import (
            RehabPlanCreateDTO,
            RehabPlanUpdateDTO,
        )
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabPlanUseCase,
            UpdateRehabPlanUseCase,
        )

        p = _make_patient(in_memory_db, doc="UPD001")
        in_memory_db.commit()
        plan = CreateRehabPlanUseCase(in_memory_db).execute(
            RehabPlanCreateDTO(patient_id=p.id, fecha_inicio=date(2026, 4, 1))
        )
        in_memory_db.commit()

        upd = RehabPlanUpdateDTO(
            frecuencia_semanal=5,
            dominios=["atencion"],
        )
        updated = UpdateRehabPlanUseCase(in_memory_db).execute(plan["id"], upd)
        assert updated["frecuencia_semanal"] == 5
        assert updated["dominios"] == ["atencion"]


# ═══════════════════════════════════════════════════════════════
# 3. FIRMA del plan
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestSignPlan:
    def test_firma_pasa_estado_a_activo(self, in_memory_db):
        from app.application.dtos.rehab_dtos import RehabPlanCreateDTO
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabPlanUseCase,
            SignRehabPlanUseCase,
        )

        p = _make_patient(in_memory_db, doc="SIGN001")
        in_memory_db.commit()
        plan = CreateRehabPlanUseCase(in_memory_db).execute(
            RehabPlanCreateDTO(patient_id=p.id, fecha_inicio=date(2026, 4, 1))
        )
        in_memory_db.commit()

        signed = SignRehabPlanUseCase(in_memory_db).execute(
            plan["id"],
            actor_id="prof-1",
            actor_label="Dr. Test",
        )
        in_memory_db.commit()
        assert signed["estado"] == "activo"
        assert signed["signed_at"] is not None
        assert signed["signature_sha256"] is not None
        assert len(signed["signature_sha256"]) == 64

    def test_firmar_dos_veces_lanza(self, in_memory_db):
        from app.application.dtos.rehab_dtos import RehabPlanCreateDTO
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabPlanUseCase,
            SignRehabPlanUseCase,
        )
        from app.core.exceptions import EvaluationAlreadySignedError

        p = _make_patient(in_memory_db, doc="SIGN002")
        in_memory_db.commit()
        plan = CreateRehabPlanUseCase(in_memory_db).execute(
            RehabPlanCreateDTO(patient_id=p.id, fecha_inicio=date(2026, 4, 1))
        )
        in_memory_db.commit()

        SignRehabPlanUseCase(in_memory_db).execute(
            plan["id"],
            actor_id="x",
            actor_label="y",
        )
        in_memory_db.commit()
        with pytest.raises(EvaluationAlreadySignedError):
            SignRehabPlanUseCase(in_memory_db).execute(
                plan["id"],
                actor_id="x",
                actor_label="y",
            )

    def test_no_se_puede_editar_plan_firmado_salvo_estado(self, in_memory_db):
        from app.application.dtos.rehab_dtos import (
            RehabPlanCreateDTO,
            RehabPlanUpdateDTO,
        )
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabPlanUseCase,
            SignRehabPlanUseCase,
            UpdateRehabPlanUseCase,
        )
        from app.core.exceptions import EvaluationAlreadySignedError

        p = _make_patient(in_memory_db, doc="LCK001")
        in_memory_db.commit()
        plan = CreateRehabPlanUseCase(in_memory_db).execute(
            RehabPlanCreateDTO(patient_id=p.id, fecha_inicio=date(2026, 4, 1))
        )
        in_memory_db.commit()
        SignRehabPlanUseCase(in_memory_db).execute(
            plan["id"],
            actor_id="x",
            actor_label="y",
        )
        in_memory_db.commit()

        # Intentar cambiar objetivos: bloqueado
        with pytest.raises(EvaluationAlreadySignedError):
            UpdateRehabPlanUseCase(in_memory_db).execute(
                plan["id"],
                RehabPlanUpdateDTO(objetivos="cambiado"),
            )
        # Cambiar SOLO estado (pausado): sí permitido
        upd = UpdateRehabPlanUseCase(in_memory_db).execute(
            plan["id"],
            RehabPlanUpdateDTO(estado="pausado"),
        )
        assert upd["estado"] == "pausado"


# ═══════════════════════════════════════════════════════════════
# 4. SESIONES
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestSesiones:
    def test_registrar_sesion_extrae_metricas(self, in_memory_db):
        from app.application.dtos.rehab_dtos import (
            RehabPlanCreateDTO,
            RehabSessionCreateDTO,
        )
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabPlanUseCase,
            CreateRehabSessionUseCase,
        )

        _seed(in_memory_db)
        p = _make_patient(in_memory_db, doc="SES001")
        in_memory_db.commit()
        plan = CreateRehabPlanUseCase(in_memory_db).execute(
            RehabPlanCreateDTO(patient_id=p.id, fecha_inicio=date(2026, 4, 1))
        )
        in_memory_db.commit()

        sess_dto = RehabSessionCreateDTO(
            plan_id=plan["id"],
            activity_slug="stroop",
            patient_id=p.id,
            resultado={"score": 88, "aciertos": 27, "errores": 3, "rt_avg_ms": 540},
            duracion_seg=180,
            modo="en_consulta",
        )
        sess = CreateRehabSessionUseCase(in_memory_db).execute(sess_dto)
        in_memory_db.commit()

        assert sess["score"] == 88
        assert sess["aciertos"] == 27
        assert sess["errores"] == 3
        assert sess["activity_slug"] == "stroop"
        assert sess["resultado"]["rt_avg_ms"] == 540

    def test_listar_sesiones_aisladas_por_paciente(self, in_memory_db):
        from app.application.dtos.rehab_dtos import RehabSessionCreateDTO
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabSessionUseCase,
            ListRehabSessionsUseCase,
        )

        _seed(in_memory_db)
        p1 = _make_patient(in_memory_db, doc="ISO001")
        p2 = _make_patient(in_memory_db, doc="ISO002")
        in_memory_db.commit()

        for _ in range(2):
            CreateRehabSessionUseCase(in_memory_db).execute(
                RehabSessionCreateDTO(
                    activity_slug="stroop",
                    patient_id=p1.id,
                    resultado={"score": 80},
                )
            )
        CreateRehabSessionUseCase(in_memory_db).execute(
            RehabSessionCreateDTO(
                activity_slug="n_back",
                patient_id=p2.id,
                resultado={"score": 50},
            )
        )
        in_memory_db.commit()

        s1 = ListRehabSessionsUseCase(in_memory_db).by_patient(p1.id)
        s2 = ListRehabSessionsUseCase(in_memory_db).by_patient(p2.id)
        assert len(s1) == 2
        assert len(s2) == 1
        assert s2[0]["activity_slug"] == "n_back"


# ═══════════════════════════════════════════════════════════════
# 5+6. LINK PÚBLICO + VIEWER PACIENTE
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestPublicShare:
    def _signed_plan(self, db):
        from app.application.dtos.rehab_dtos import RehabPlanCreateDTO
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabPlanUseCase,
            SignRehabPlanUseCase,
        )

        _seed(db)
        p = _make_patient(db, doc="PUB001", first="María")
        db.commit()
        plan = CreateRehabPlanUseCase(db).execute(
            RehabPlanCreateDTO(
                patient_id=p.id,
                fecha_inicio=date(2026, 4, 1),
                actividades=[{"slug": "stroop", "dificultad": 2}],
            )
        )
        db.commit()
        signed = SignRehabPlanUseCase(db).execute(
            plan["id"],
            actor_id="prof",
            actor_label="Dr. Test",
        )
        db.commit()
        return p, signed

    def test_share_solo_funciona_con_plan_firmado(self, in_memory_db):
        from app.application.dtos.rehab_dtos import (
            RehabPlanCreateDTO,
            RehabShareCreateDTO,
        )
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabPlanUseCase,
            CreateRehabShareUseCase,
        )
        from app.core.exceptions import ApplicationError

        p = _make_patient(in_memory_db, doc="UNS001")
        in_memory_db.commit()
        plan = CreateRehabPlanUseCase(in_memory_db).execute(
            RehabPlanCreateDTO(patient_id=p.id, fecha_inicio=date(2026, 4, 1))
        )
        in_memory_db.commit()

        with pytest.raises(ApplicationError):
            CreateRehabShareUseCase(in_memory_db).execute(
                RehabShareCreateDTO(plan_id=plan["id"]),
                created_by="prof",
            )

    def test_crear_link_y_vista_publica(self, in_memory_db):
        from app.application.dtos.rehab_dtos import RehabShareCreateDTO
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabShareUseCase,
            GetPublicRehabPlanUseCase,
        )

        _, plan = self._signed_plan(in_memory_db)
        link = CreateRehabShareUseCase(in_memory_db).execute(
            RehabShareCreateDTO(plan_id=plan["id"], expires_in_days=30),
            created_by="prof",
        )
        in_memory_db.commit()

        assert link["public_url"].startswith("/shared/rehab/")
        assert link["sessions_count"] == 0

        public_view = GetPublicRehabPlanUseCase(in_memory_db).execute(link["token"])
        # NO debe filtrar info clínica sensible
        assert public_view["plan_id"] == plan["id"]
        assert public_view["patient_first_name"] == "María"
        assert "actividades" in public_view
        # No debe haber objetivos terapéuticos ni evaluación
        assert "objetivos" not in public_view
        assert "evaluation_id" not in public_view

    def test_link_revocado_o_expirado(self, in_memory_db):
        from app.application.dtos.rehab_dtos import RehabShareCreateDTO
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabShareUseCase,
            GetPublicRehabPlanUseCase,
        )
        from app.core.exceptions import ApplicationError
        from app.infrastructure.database.orm_models import RehabShareLinkORM

        _, plan = self._signed_plan(in_memory_db)
        link = CreateRehabShareUseCase(in_memory_db).execute(
            RehabShareCreateDTO(plan_id=plan["id"]),
            created_by="prof",
        )
        in_memory_db.commit()

        # Token inexistente
        with pytest.raises(ApplicationError) as exc_info:
            GetPublicRehabPlanUseCase(in_memory_db).execute("token-falso")
        assert exc_info.value.http_status == 404

        # Forzar expiración
        orm = in_memory_db.query(RehabShareLinkORM).filter_by(token=link["token"]).first()
        orm.expires_at = datetime.now(UTC) - timedelta(hours=1)
        in_memory_db.commit()
        with pytest.raises(ApplicationError) as exc_info:
            GetPublicRehabPlanUseCase(in_memory_db).execute(link["token"])
        assert exc_info.value.http_status == 410

    def test_paciente_envia_resultado_y_se_registra_sesion(self, in_memory_db):
        from app.application.dtos.rehab_dtos import (
            RehabPublicResultDTO,
            RehabShareCreateDTO,
        )
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabShareUseCase,
            ListRehabSessionsUseCase,
            SubmitPublicRehabResultUseCase,
        )
        from app.infrastructure.database.orm_models import RehabShareLinkORM

        patient, plan = self._signed_plan(in_memory_db)
        link = CreateRehabShareUseCase(in_memory_db).execute(
            RehabShareCreateDTO(plan_id=plan["id"]),
            created_by="prof",
        )
        in_memory_db.commit()

        result = SubmitPublicRehabResultUseCase(in_memory_db).execute(
            link["token"],
            RehabPublicResultDTO(
                activity_slug="stroop",
                resultado={"score": 75, "aciertos": 22, "errores": 8},
                duracion_seg=180,
            ),
        )
        in_memory_db.commit()

        assert result["modo"] == "tarea_casa"
        assert result["origen_token"] == link["token"]
        assert result["score"] == 75

        # Conteo del link debió incrementarse
        orm = in_memory_db.query(RehabShareLinkORM).filter_by(token=link["token"]).first()
        assert orm.sessions_count == 1
        assert orm.last_used_at is not None

        # La sesión es visible en el listado del paciente
        sesiones = ListRehabSessionsUseCase(in_memory_db).by_patient(patient.id)
        assert any(s["origen_token"] == link["token"] for s in sesiones)


# ═══════════════════════════════════════════════════════════════
# 7. EVOLUCIÓN
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestEvolution:
    def test_paciente_sin_sesiones_devuelve_estructura_vacia(self, in_memory_db):
        from app.application.use_cases.rehab_use_cases import GetEvolutionUseCase

        out = GetEvolutionUseCase(in_memory_db).execute("no-existe")
        assert out["dominios"] == []
        assert out["total_sesiones"] == 0

    def test_evolucion_agrupa_por_dominio_y_semana(self, in_memory_db):
        from app.application.dtos.rehab_dtos import RehabSessionCreateDTO
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabSessionUseCase,
            GetEvolutionUseCase,
        )

        _seed(in_memory_db)
        p = _make_patient(in_memory_db, doc="EVO001")
        in_memory_db.commit()

        # 3 sesiones de Stroop (funciones_ejecutivas)
        for s in (60, 70, 80):
            CreateRehabSessionUseCase(in_memory_db).execute(
                RehabSessionCreateDTO(
                    activity_slug="stroop",
                    patient_id=p.id,
                    resultado={"score": s},
                )
            )
        # 2 de N-back (memoria_trabajo)
        for s in (50, 65):
            CreateRehabSessionUseCase(in_memory_db).execute(
                RehabSessionCreateDTO(
                    activity_slug="n_back",
                    patient_id=p.id,
                    resultado={"score": s},
                )
            )
        in_memory_db.commit()

        out = GetEvolutionUseCase(in_memory_db).execute(p.id)
        doms = {d["dominio"] for d in out["dominios"]}
        assert doms == {"funciones_ejecutivas", "memoria_trabajo"}
        assert out["total_sesiones"] == 5
        # cada dominio tiene al menos 1 punto con n>=1
        for d in out["dominios"]:
            assert len(d["puntos"]) >= 1
            assert all(p["n"] >= 1 for p in d["puntos"])


# ═══════════════════════════════════════════════════════════════
# 8. ADHERENCIA
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestAdherence:
    def test_paciente_sin_plan_has_plan_false(self, in_memory_db):
        from app.application.use_cases.rehab_use_cases import GetAdherenceUseCase

        p = _make_patient(in_memory_db, doc="ADH000")
        in_memory_db.commit()
        out = GetAdherenceUseCase(in_memory_db).execute(p.id)
        assert out["has_plan"] is False
        assert out["sesiones_realizadas"] == 0

    def test_calculo_basico_con_plan_activo(self, in_memory_db):
        from app.application.dtos.rehab_dtos import (
            RehabPlanCreateDTO,
            RehabSessionCreateDTO,
        )
        from app.application.use_cases.rehab_use_cases import (
            CreateRehabPlanUseCase,
            CreateRehabSessionUseCase,
            GetAdherenceUseCase,
        )

        _seed(in_memory_db)
        p = _make_patient(in_memory_db, doc="ADH001")
        in_memory_db.commit()
        plan = CreateRehabPlanUseCase(in_memory_db).execute(
            RehabPlanCreateDTO(
                patient_id=p.id,
                fecha_inicio=date.today(),
                frecuencia_semanal=3,
            )
        )
        in_memory_db.commit()

        # 2 sesiones esta semana (esperadas: 3) → adherencia 66%
        for _ in range(2):
            CreateRehabSessionUseCase(in_memory_db).execute(
                RehabSessionCreateDTO(
                    plan_id=plan["id"],
                    activity_slug="stroop",
                    patient_id=p.id,
                    resultado={"score": 75},
                )
            )
        in_memory_db.commit()

        out = GetAdherenceUseCase(in_memory_db).execute(p.id)
        assert out["has_plan"] is True
        assert out["plan_id"] == plan["id"]
        assert out["frecuencia_semanal"] == 3
        assert out["sesiones_realizadas"] == 2
        assert out["adherencia_pct"] in range(60, 80)  # ~66
        assert out["esta_semana"]["realizadas"] == 2


# ═══════════════════════════════════════════════════════════════
# 9. SUGERENCIA DE PLAN
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestSuggestPlan:
    def test_evaluacion_inexistente_lanza(self, in_memory_db):
        from app.application.use_cases.rehab_use_cases import (
            SuggestPlanFromEvaluationUseCase,
        )
        from app.core.exceptions import EvaluationNotFoundError

        with pytest.raises(EvaluationNotFoundError):
            SuggestPlanFromEvaluationUseCase(in_memory_db).execute("no-existe")

    def test_evaluacion_sin_resultados_bajos_devuelve_lista_vacia(self, in_memory_db):
        import json as _json

        from app.application.use_cases.rehab_use_cases import (
            SuggestPlanFromEvaluationUseCase,
        )
        from app.infrastructure.database.orm_models import EvaluationORM

        _seed(in_memory_db)
        p = _make_patient(in_memory_db, doc="SUG001")
        ev = EvaluationORM(
            id=str(uuid.uuid4()),
            patient_id=p.id,
            protocolo="WISC-IV",
            fecha=date(2026, 3, 20),
            puntajes_brutos_json="{}",
            resultados_json=_json.dumps(
                [
                    {"test_id": "NiWiscDC", "interpretacion": "Promedio", "z_equivalente": 0.2},
                    {"test_id": "NiWiscVoc", "interpretacion": "Superior", "z_equivalente": 1.4},
                ]
            ),
            poblacion="infantil",
            edad_display="10a",
            pruebas_realizadas=2,
            pruebas_sin_dato=0,
            is_latest=True,
            created_at=datetime.now(UTC),
        )
        in_memory_db.add(ev)
        in_memory_db.commit()

        out = SuggestPlanFromEvaluationUseCase(in_memory_db).execute(ev.id)
        assert out["tests_bajos"] == 0
        assert out["dominios_sugeridos"] == []
        assert out["actividades"] == []

    def test_evaluacion_con_atencion_baja_sugiere_actividades_atencion(self, in_memory_db):
        import json as _json

        from app.application.use_cases.rehab_use_cases import (
            SuggestPlanFromEvaluationUseCase,
        )
        from app.infrastructure.database.orm_models import EvaluationORM

        _seed(in_memory_db)
        p = _make_patient(in_memory_db, doc="SUG002")
        ev = EvaluationORM(
            id=str(uuid.uuid4()),
            patient_id=p.id,
            protocolo="WISC-IV",
            fecha=date(2026, 3, 20),
            puntajes_brutos_json="{}",
            resultados_json=_json.dumps(
                [
                    # Tests con substring en _TEST_TO_DOMAIN
                    {"test_id": "NiWiscRDD", "interpretacion": "Bajo", "z_equivalente": -1.5},
                    {"test_id": "NiWiscCl", "interpretacion": "Deficitario", "z_equivalente": -2.1},
                    {"test_id": "NiWiscCom", "interpretacion": "Bajo", "z_equivalente": -1.2},
                ]
            ),
            poblacion="infantil",
            edad_display="10a",
            pruebas_realizadas=3,
            pruebas_sin_dato=0,
            is_latest=True,
            created_at=datetime.now(UTC),
        )
        in_memory_db.add(ev)
        in_memory_db.commit()

        out = SuggestPlanFromEvaluationUseCase(in_memory_db).execute(ev.id)
        assert out["tests_bajos"] == 3
        # debe sugerir al menos un dominio
        assert len(out["dominios_sugeridos"]) > 0
        # debe haber actividades del catálogo en esos dominios
        assert len(out["actividades"]) > 0
        assert all(a["dominio"] in out["dominios_sugeridos"] for a in out["actividades"])
        # objetivo sugerencia textual no vacío
        assert "Intervención" in out["objetivos_sugerencia"]
        # frecuencia sugerida ≥ 2
        assert out["frecuencia_semanal_sugerida"] >= 2

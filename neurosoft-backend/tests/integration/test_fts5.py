"""
tests/integration/test_fts5.py
===============================
Tests para el índice FTS5 de búsqueda full-text de pacientes.
"""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.orm_models import Base, PatientORM


@pytest.fixture
def fts_db():
    """Crea una BD en memoria con FTS5 habilitado."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def set_sqlite_pragmas(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)

    # Crear tabla FTS5
    with engine.begin() as conn:
        conn.execute(
            text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS patients_fts
            USING fts5(
                id UNINDEXED,
                primer_nombre,
                segundo_nombre,
                primer_apellido,
                segundo_apellido,
                numero_documento,
                motivo_consulta,
                eps,
                ciudad,
                ocupacion,
                content='patients',
                content_rowid='rowid',
                tokenize='unicode61'
            )
        """)
        )

        conn.execute(
            text("""
            CREATE TRIGGER IF NOT EXISTS patients_ai AFTER INSERT ON patients BEGIN
                INSERT INTO patients_fts(rowid, id, primer_nombre, segundo_nombre,
                    primer_apellido, segundo_apellido, numero_documento,
                    motivo_consulta, eps, ciudad, ocupacion)
                VALUES (new.rowid, new.id, new.primer_nombre, new.segundo_nombre,
                    new.primer_apellido, new.segundo_apellido, new.numero_documento,
                    new.motivo_consulta, new.eps, new.ciudad, new.ocupacion);
            END
        """)
        )

        conn.execute(
            text("""
            CREATE TRIGGER IF NOT EXISTS patients_ad AFTER DELETE ON patients BEGIN
                INSERT INTO patients_fts(patients_fts, rowid, id, primer_nombre,
                    segundo_nombre, primer_apellido, segundo_apellido,
                    numero_documento, motivo_consulta, eps, ciudad, ocupacion)
                VALUES ('delete', old.rowid, old.id, old.primer_nombre,
                    old.segundo_nombre, old.primer_apellido, old.segundo_apellido,
                    old.numero_documento, old.motivo_consulta, old.eps,
                    old.ciudad, old.ocupacion);
            END
        """)
        )

        conn.execute(
            text("""
            CREATE TRIGGER IF NOT EXISTS patients_au AFTER UPDATE ON patients BEGIN
                INSERT INTO patients_fts(patients_fts, rowid, id, primer_nombre,
                    segundo_nombre, primer_apellido, segundo_apellido,
                    numero_documento, motivo_consulta, eps, ciudad, ocupacion)
                VALUES ('delete', old.rowid, old.id, old.primer_nombre,
                    old.segundo_nombre, old.primer_apellido, old.segundo_apellido,
                    old.numero_documento, old.motivo_consulta, old.eps,
                    old.ciudad, old.ocupacion);
                INSERT INTO patients_fts(rowid, id, primer_nombre, segundo_nombre,
                    primer_apellido, segundo_apellido, numero_documento,
                    motivo_consulta, eps, ciudad, ocupacion)
                VALUES (new.rowid, new.id, new.primer_nombre, new.segundo_nombre,
                    new.primer_apellido, new.segundo_apellido, new.numero_documento,
                    new.motivo_consulta, new.eps, new.ciudad, new.ocupacion);
            END
        """)
        )

    Session = sessionmaker(bind=engine)
    session = Session()

    # Insertar pacientes de prueba
    patients = [
        PatientORM(
            id="uuid-p1-fts5-test",
            numero_documento="1234567890",
            tipo_documento="CC",
            primer_nombre="María",
            primer_apellido="García",
            sexo="M",
            fecha_nacimiento=date(1990, 5, 15),
            fecha_atencion=date(2026, 1, 10),
            motivo_consulta="Evaluación neuropsicológica por déficit de atención",
            eps="Sura",
            ciudad="Bogotá",
            ocupacion="Ingeniera",
            escolaridad="Universitaria",
            lateralidad="Diestro",
            is_active=True,
        ),
        PatientORM(
            id="uuid-p2-fts5-test",
            numero_documento="9876543210",
            tipo_documento="CC",
            primer_nombre="Carlos",
            segundo_nombre="Andrés",
            primer_apellido="Rodríguez",
            segundo_apellido="López",
            sexo="H",
            fecha_nacimiento=date(1985, 3, 20),
            fecha_atencion=date(2026, 2, 15),
            motivo_consulta="Control postratamiento TDAH",
            eps="Sanitas",
            ciudad="Medellín",
            ocupacion="Profesor",
            escolaridad="Universitaria",
            lateralidad="Diestro",
            is_active=True,
        ),
        PatientORM(
            id="uuid-p3-fts5-test",
            numero_documento="1122334455",
            tipo_documento="TI",
            primer_nombre="Ana",
            primer_apellido="Martínez",
            sexo="M",
            fecha_nacimiento=date(2015, 8, 1),
            fecha_atencion=date(2026, 3, 1),
            motivo_consulta="Dificultades de aprendizaje escolar",
            eps="Nueva EPS",
            ciudad="Cali",
            ocupacion="Estudiante",
            escolaridad="Secundaria",
            lateralidad="Diestro",
            is_active=True,
        ),
    ]
    for p in patients:
        session.add(p)
    session.commit()

    yield session
    session.close()


@pytest.fixture
def patient_repo(fts_db):
    from app.infrastructure.repositories.patient_repo import PatientRepository

    return PatientRepository(fts_db)


class TestFTS5Search:
    """Tests para búsqueda FTS5."""

    def test_search_by_first_name(self, patient_repo):
        results = patient_repo.search_fts("María")
        assert len(results) == 1
        assert results[0].id.value == "uuid-p1-fts5-test"

    def test_search_by_last_name(self, patient_repo):
        results = patient_repo.search_fts("Rodríguez")
        assert len(results) == 1
        assert results[0].id.value == "uuid-p2-fts5-test"

    def test_search_by_document(self, patient_repo):
        results = patient_repo.search_fts("1234567890")
        assert len(results) == 1
        assert results[0].id.value == "uuid-p1-fts5-test"

    def test_search_by_city(self, patient_repo):
        results = patient_repo.search_fts("Medellín")
        assert len(results) == 1
        assert results[0].id.value == "uuid-p2-fts5-test"

    def test_search_by_motivo_consulta(self, patient_repo):
        results = patient_repo.search_fts("TDAH")
        assert len(results) == 1
        assert results[0].id.value == "uuid-p2-fts5-test"

    def test_search_multiple_words(self, patient_repo):
        results = patient_repo.search_fts("déficit atención")
        assert len(results) >= 1
        assert any(r.id.value == "uuid-p1-fts5-test" for r in results)

    def test_search_prefix(self, patient_repo):
        results = patient_repo.search_fts("Mart*")
        assert len(results) >= 1
        assert any(r.id.value == "uuid-p3-fts5-test" for r in results)

    def test_search_empty_query(self, patient_repo):
        results = patient_repo.search_fts("")
        assert results == []

    def test_search_no_results(self, patient_repo):
        results = patient_repo.search_fts("XYZNONEXISTENT")
        assert results == []

    def test_search_case_insensitive(self, patient_repo):
        results_lower = patient_repo.search_fts("maría")
        results_upper = patient_repo.search_fts("MARÍA")
        assert len(results_lower) == len(results_upper) == 1

    def test_search_fts_integrated_in_search_panel(self, patient_repo):
        """Verificar que search_panel usa FTS5 cuando está disponible."""
        orms, total = patient_repo.search_panel(q="Carlos")
        assert total >= 1
        assert any(o.id == "uuid-p2-fts5-test" for o in orms)


class TestFTS5Sync:
    """Tests para sincronización automática de FTS5."""

    def test_new_patient_indexed(self, fts_db, patient_repo):
        """Un paciente nuevo se indexa automáticamente."""
        new_patient = PatientORM(
            id="uuid-new-fts5-test",
            numero_documento="5555555555",
            tipo_documento="CC",
            primer_nombre="Nuevo",
            primer_apellido="Paciente",
            sexo="H",
            fecha_nacimiento=date(2000, 1, 1),
            fecha_atencion=date(2026, 5, 1),
            motivo_consulta="Test FTS5",
            eps="Test EPS",
            ciudad="Barranquilla",
            ocupacion="Test",
            escolaridad="Universitaria",
            lateralidad="Diestro",
            is_active=True,
        )
        fts_db.add(new_patient)
        fts_db.commit()

        results = patient_repo.search_fts("Nuevo")
        assert len(results) == 1
        assert results[0].id.value == "uuid-new-fts5-test"

    def test_updated_patient_reindexed(self, fts_db, patient_repo):
        """Un paciente actualizado se reindexa automáticamente."""
        patient = fts_db.query(PatientORM).filter_by(id="uuid-p1-fts5-test").first()
        patient.primer_nombre = "MaríaElena"
        fts_db.commit()

        results = patient_repo.search_fts("MaríaElena")
        assert len(results) == 1
        assert results[0].id.value == "uuid-p1-fts5-test"

    def test_deleted_patient_removed_from_index(self, fts_db, patient_repo):
        """Un paciente eliminado se remueve del índice."""
        patient = fts_db.query(PatientORM).filter_by(id="uuid-p3-fts5-test").first()
        fts_db.delete(patient)
        fts_db.commit()

        results = patient_repo.search_fts("Ana")
        assert not any(r.id.value == "uuid-p3-fts5-test" for r in results)

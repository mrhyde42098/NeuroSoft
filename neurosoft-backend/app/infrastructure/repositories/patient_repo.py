"""
app/infrastructure/repositories/patient_repo.py
================================================
Implementación concreta del repositorio de pacientes sobre SQLAlchemy.

El repositorio traduce entre:
    Entidades de dominio (Paciente) ↔ Modelos ORM (PatientORM)

Principio: los servicios de aplicación trabajan con entidades puras.
Los repositorios son los únicos que saben de SQLAlchemy.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import PatientNotFoundError
from app.domain.entities.models import Paciente, PacienteId
from app.infrastructure.database.orm_models import PatientORM

logger = logging.getLogger(__name__)


class PatientRepository:
    """
    Repositorio de pacientes con operaciones CRUD completas.

    Uso:
        with session_scope() as db:
            repo = PatientRepository(db)
            paciente = repo.find_by_id("uuid-aqui")
    """

    def __init__(self, session: Session):
        self._db = session

    # ─── Escritura ─────────────────────────────────────────

    def save(self, paciente: Paciente) -> Paciente:
        """
        Inserta o actualiza (upsert) un paciente.
        Retorna el paciente con timestamps actualizados.
        """
        existing = self._db.query(PatientORM).filter_by(id=str(paciente.id)).first()
        if existing:
            self._update_orm(existing, paciente)
        else:
            orm = self._to_orm(paciente)
            self._db.add(orm)
        # PII: NO loguear nombre_completo (Ley 1581). Sólo el ID es seguro.
        logger.info("Paciente guardado: id=%s", paciente.id)
        return paciente

    def soft_delete(self, patient_id: str, *, actor_id: str | None = None,
                    reason: str | None = None) -> bool:
        """
        Archiva un paciente (Resolución 1995: la historia clínica NO se borra).

        - Marca is_active=False y llena los nuevos campos archived_* para
          que haya trazabilidad de quién y por qué.
        - No toca evaluaciones, HC ni documentos (antes el cascade los borraba;
          ahora se conservan para cumplir normativa).
        """
        orm = self._db.query(PatientORM).filter_by(id=patient_id, is_active=True).first()
        if not orm:
            return False
        now = datetime.now(UTC)
        orm.is_active = False
        orm.updated_at = now
        # Campos nuevos — si la columna aún no existe (BD antigua sin migrar)
        # el setattr es tolerante porque son atributos opcionales del ORM.
        # Los atributos archived_* existen siempre en el modelo; si la BD
        # es antigua y aún no tiene la columna, SQLAlchemy puede rechazar
        # el flush posterior. Capturamos sólo AttributeError porque es la
        # única excepción razonable aquí (ej. rollback de mapping en tests).
        try:
            orm.archived_at = now
            orm.archived_by = actor_id
            orm.archived_reason = reason
        except AttributeError as _legacy_exc:
            logger.warning(
                "soft_delete: BD antigua sin columnas archived_* (%s). "
                "Corre `alembic upgrade head` o reinicia para aplicar patches.",
                _legacy_exc,
            )
        return True

    # Alias semánticamente más claro para uso clínico
    def archive(self, patient_id: str, *, actor_id: str | None = None,
                reason: str | None = None) -> bool:
        return self.soft_delete(patient_id, actor_id=actor_id, reason=reason)

    # ─── Lectura ────────────────────────────────────────────

    def find_by_id(self, patient_id: str) -> Paciente:
        """
        Busca por UUID interno.
        Raises PatientNotFoundError si no existe.
        """
        orm = self._db.query(PatientORM).filter_by(id=patient_id, is_active=True).first()
        if not orm:
            raise PatientNotFoundError(patient_id)
        return self._to_entity(orm)

    def find_by_id_optional(self, patient_id: str) -> Paciente | None:
        """Versión que retorna None en lugar de lanzar excepción."""
        orm = self._db.query(PatientORM).filter_by(id=patient_id, is_active=True).first()
        return self._to_entity(orm) if orm else None

    def find_by_document(self, numero_documento: str) -> list[Paciente]:
        """Todas las visitas de un mismo documento (puede haber varias fechas)."""
        orms = (
            self._db.query(PatientORM)
            .filter_by(numero_documento=numero_documento, is_active=True)
            .order_by(PatientORM.fecha_atencion.desc())
            .all()
        )
        return [self._to_entity(o) for o in orms]

    def find_by_document_and_date(
        self, numero_documento: str, fecha_atencion: date
    ) -> Paciente | None:
        """Verifica duplicado exacto (mismo doc + misma fecha)."""
        orm = (
            self._db.query(PatientORM)
            .filter_by(
                numero_documento=numero_documento,
                fecha_atencion=fecha_atencion,
                is_active=True,
            )
            .first()
        )
        return self._to_entity(orm) if orm else None

    def search(
        self,
        documento: str | None = None,
        nombre: str | None = None,
        limit: int = 20,
        offset: int = 0,
        profesional_id: str | None = None,
    ) -> list[Paciente]:
        """Búsqueda flexible — réplica del botón 'Buscar' del VBA.

        Si `profesional_id` viene, filtra a pacientes de ese profesional
        (S0.2 — alcance por usuario; admin pasa None para ver todo).
        """
        q = self._db.query(PatientORM).filter_by(is_active=True)
        if profesional_id:
            q = q.filter(PatientORM.profesional_id == profesional_id)
        if documento:
            q = q.filter(PatientORM.numero_documento == documento)
        if nombre:
            like = f"%{nombre}%"
            q = q.filter(
                PatientORM.primer_nombre.ilike(like)
                | PatientORM.primer_apellido.ilike(like)
                | PatientORM.segundo_apellido.ilike(like)
            )
        orms = q.order_by(PatientORM.primer_apellido, PatientORM.primer_nombre).limit(limit).offset(offset).all()
        return [self._to_entity(o) for o in orms]

    def search_fts(
        self,
        query: str,
        limit: int = 20,
    ) -> list[Paciente]:
        """
        Búsqueda full-text usando FTS5 (SQLite).

        Busca en: nombre, apellido, documento, motivo de consulta, EPS, ciudad, ocupación.
        Usa ranking BM25 para ordenar por relevancia.

        Sintaxis de query:
          - Palabras simples: "maria" → busca en todos los campos
          - Frases: '"maria elena"' → busca la frase exacta
          - Prefijos: "mar*" → busca palabras que empiecen con "mar"
          - Múltiples palabras: "maria bogota" → busca ambas (AND implícito)

        Retorna pacientes activos ordenados por relevancia.
        """
        from sqlalchemy import text

        if not query or not query.strip():
            return []

        # Sanitizar query: escapar comillas y caracteres especiales de FTS5
        clean_query = query.strip().replace('"', '""')

        # Usar FTS5 con ranking BM25
        sql = text("""
            SELECT p.*
            FROM patients p
            INNER JOIN patients_fts fts ON p.id = fts.id
            WHERE patients_fts MATCH :query
              AND p.is_active = 1
            ORDER BY bm25(patients_fts, 0, 5, 2, 5, 5, 10, 3, 3, 3, 2)
            LIMIT :limit
        """)

        # Ejecutar query FTS5
        result = self._db.execute(sql, {"query": clean_query, "limit": limit})
        rows = result.fetchall()

        # Convertir rows a PatientORM entities
        patients = []
        for row in rows:
            # Mapear row a PatientORM
            orm = PatientORM()
            for key in row._mapping.keys():
                if hasattr(orm, key):
                    setattr(orm, key, row._mapping[key])
            patients.append(self._to_entity(orm))

        return patients

    # ─── Conversores ORM ↔ Entidad ──────────────────────────

    @staticmethod
    def _to_orm(p: Paciente) -> PatientORM:
        return PatientORM(
            id=str(p.id),
            numero_documento=p.numero_documento,
            tipo_documento=p.tipo_documento,
            primer_nombre=p.primer_nombre,
            segundo_nombre=p.segundo_nombre,
            primer_apellido=p.primer_apellido,
            segundo_apellido=p.segundo_apellido,
            fecha_nacimiento=p.fecha_nacimiento,
            sexo=p.sexo,
            lugar_nacimiento=p.lugar_nacimiento,
            estado_civil=p.estado_civil,
            telefono=p.telefono,
            correo=p.correo,
            direccion=p.direccion,
            ciudad=p.ciudad,
            localidad=p.localidad,
            estrato=p.estrato,
            escolaridad=p.escolaridad,
            lateralidad=p.lateralidad,
            ocupacion=p.ocupacion,
            acompanante=p.acompanante,
            grupo_etnico=p.grupo_etnico,
            profesional_id=p.profesional_id,
            fecha_atencion=p.fecha_atencion,
            motivo_consulta=p.motivo_consulta,
            remite=p.remite,
            eps=p.eps,
            orden_medica_no=p.orden_medica_no,
            discapacidad=p.discapacidad,
            codigo_rips=p.codigo_rips,
            cups=p.cups,
            finalidad_consulta=p.finalidad_consulta,
            numero_sesiones=p.numero_sesiones,
            donante=p.donante,
            created_at=p.created_at,
            updated_at=p.updated_at,
            is_active=p.is_active,
        )

    @staticmethod
    def _update_orm(orm: PatientORM, p: Paciente) -> None:
        """Actualiza campos editables de un ORM existente."""
        campos = [
            "primer_nombre","segundo_nombre","primer_apellido","segundo_apellido",
            "sexo","estado_civil","telefono","correo","direccion","ciudad","localidad",
            "estrato","escolaridad","lateralidad","ocupacion","acompanante","grupo_etnico",
            "motivo_consulta","remite","eps","orden_medica_no","discapacidad",
            "codigo_rips","cups","finalidad_consulta","numero_sesiones","donante",
        ]
        for c in campos:
            setattr(orm, c, getattr(p, c))
        orm.updated_at = datetime.now(UTC)

    @staticmethod
    def _to_entity(orm: PatientORM) -> Paciente:
        return Paciente(
            id=PacienteId.from_string(orm.id),
            numero_documento=orm.numero_documento,
            tipo_documento=orm.tipo_documento,
            primer_nombre=orm.primer_nombre,
            segundo_nombre=orm.segundo_nombre,
            primer_apellido=orm.primer_apellido,
            segundo_apellido=orm.segundo_apellido,
            fecha_nacimiento=orm.fecha_nacimiento,
            sexo=orm.sexo,
            lugar_nacimiento=orm.lugar_nacimiento,
            estado_civil=orm.estado_civil,
            telefono=orm.telefono,
            correo=orm.correo,
            direccion=orm.direccion,
            ciudad=orm.ciudad,
            localidad=orm.localidad,
            estrato=orm.estrato,
            escolaridad=orm.escolaridad,
            lateralidad=orm.lateralidad,
            ocupacion=orm.ocupacion,
            acompanante=orm.acompanante,
            acompanante_relacion=getattr(orm, "acompanante_relacion", None),
            acompanante_telefono=getattr(orm, "acompanante_telefono", None),
            grupo_etnico=orm.grupo_etnico,
            profesional_id=orm.profesional_id,
            fecha_atencion=orm.fecha_atencion,
            motivo_consulta=orm.motivo_consulta,
            remite=orm.remite,
            eps=orm.eps,
            orden_medica_no=orm.orden_medica_no,
            discapacidad=orm.discapacidad,
            codigo_rips=orm.codigo_rips,
            cups=orm.cups,
            finalidad_consulta=orm.finalidad_consulta,
            numero_sesiones=orm.numero_sesiones or 1,
            donante=bool(orm.donante),
            created_at=orm.created_at or datetime.now(UTC),
            updated_at=orm.updated_at or datetime.now(UTC),
            is_active=bool(orm.is_active),
        )


    # ─── Panel de Pacientes ─────────────────────────────────

    def search_panel(
        self,
        q: str | None = None,
        sexo: str | None = None,
        poblacion: str | None = None,
        profesional_id: str | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> tuple:
        """
        Búsqueda avanzada para el panel de pacientes.
        Retorna (List[PatientORM], total_count).
        Trabaja con ORM directamente (no convierte a entidad)
        para poder hacer JOINs eficientes con evaluaciones.
        """
        from datetime import date as date_type

        from sqlalchemy import or_

        base = self._db.query(PatientORM).filter(PatientORM.is_active.is_(True))

        if q:
            # Intentar FTS5 primero (búsqueda full-text con ranking)
            fts_ids = self._fts5_search(q, limit=500)
            if fts_ids is not None:
                base = base.filter(PatientORM.id.in_(fts_ids))
            else:
                # Fallback a ILIKE si FTS5 no está disponible
                like = f"%{q}%"
                base = base.filter(
                    or_(
                        PatientORM.primer_nombre.ilike(like),
                        PatientORM.primer_apellido.ilike(like),
                        PatientORM.segundo_apellido.ilike(like),
                        PatientORM.numero_documento.ilike(like),
                    )
                )

        if sexo in ('H', 'M'):
            base = base.filter(PatientORM.sexo == sexo)

        if profesional_id:
            base = base.filter(PatientORM.profesional_id == profesional_id)

        if fecha_desde:
            base = base.filter(PatientORM.fecha_atencion >= fecha_desde)

        if fecha_hasta:
            base = base.filter(PatientORM.fecha_atencion <= fecha_hasta)

        # Filtro de población (calculado por edad)
        if poblacion == 'infantil':
            today = date_type.today()
            # < 18 años
            cutoff_18 = date_type(today.year - 18, today.month, today.day)
            base = base.filter(PatientORM.fecha_nacimiento > cutoff_18)
        elif poblacion == 'adulto_joven':
            today = date_type.today()
            cutoff_18 = date_type(today.year - 18, today.month, today.day)
            cutoff_50 = date_type(today.year - 50, today.month, today.day)
            base = base.filter(
                PatientORM.fecha_nacimiento <= cutoff_18,
                PatientORM.fecha_nacimiento > cutoff_50,
            )
        elif poblacion == 'adulto_mayor':
            today = date_type.today()
            cutoff_50 = date_type(today.year - 50, today.month, today.day)
            base = base.filter(PatientORM.fecha_nacimiento <= cutoff_50)

        total = base.count()
        orms = (
            base
            .order_by(PatientORM.fecha_atencion.desc(), PatientORM.primer_apellido)
            .limit(limit)
            .offset(offset)
            .all()
        )
        return orms, total

    def _fts5_search(self, query: str, limit: int = 500) -> list[str] | None:
        """
        Búsqueda FTS5 interna. Retorna lista de patient IDs o None si FTS5 no está disponible.
        """
        from sqlalchemy import text

        if not query or not query.strip():
            return None

        clean_query = query.strip().replace('"', '""')

        try:
            result = self._db.execute(
                text("SELECT id FROM patients_fts WHERE patients_fts MATCH :q LIMIT :lim"),
                {"q": clean_query, "lim": limit},
            )
            return [row[0] for row in result.fetchall()]
        except Exception:
            return None

    def get_stats(self, profesional_id: str | None = None) -> dict:
        """Stats rápidas para el dashboard: totales por población, por sexo, etc.

        S0.2: si `profesional_id` viene, las stats se limitan a pacientes
        de ese profesional.
        """
        from datetime import date as date_type

        from sqlalchemy import func

        today = date_type.today()

        def _base_q():
            q = self._db.query(PatientORM).filter(PatientORM.is_active.is_(True))
            if profesional_id:
                q = q.filter(PatientORM.profesional_id == profesional_id)
            return q

        total = self._db.query(func.count(PatientORM.id)).filter(
            PatientORM.is_active.is_(True),
            *([PatientORM.profesional_id == profesional_id] if profesional_id else []),
        ).scalar() or 0

        por_sexo_q = self._db.query(PatientORM.sexo, func.count(PatientORM.id)).filter(
            PatientORM.is_active.is_(True),
        )
        if profesional_id:
            por_sexo_q = por_sexo_q.filter(PatientORM.profesional_id == profesional_id)
        por_sexo = {row[0]: row[1] for row in por_sexo_q.group_by(PatientORM.sexo).all()}

        # Atendidos este mes
        mes_inicio = date_type(today.year, today.month, 1)
        mes_q = self._db.query(func.count(PatientORM.id)).filter(
            PatientORM.is_active.is_(True),
            PatientORM.fecha_atencion >= mes_inicio,
        )
        if profesional_id:
            mes_q = mes_q.filter(PatientORM.profesional_id == profesional_id)
        este_mes = mes_q.scalar() or 0

        # Atendidos este año
        anio_inicio = date_type(today.year, 1, 1)
        anio_q = self._db.query(func.count(PatientORM.id)).filter(
            PatientORM.is_active.is_(True),
            PatientORM.fecha_atencion >= anio_inicio,
        )
        if profesional_id:
            anio_q = anio_q.filter(PatientORM.profesional_id == profesional_id)
        este_anio = anio_q.scalar() or 0

        # Distribución por población (calculada desde fecha_nacimiento)
        infantil = adulto_joven = adulto_mayor = 0
        patients = _base_q().with_entities(PatientORM.fecha_nacimiento).all()
        for (fn,) in patients:
            if fn is None:
                continue
            age = (today - fn).days / 365.25
            if age < 18:
                infantil += 1
            elif age < 50:
                adulto_joven += 1
            else:
                adulto_mayor += 1

        return {
            "total_pacientes": total,
            "masculino": por_sexo.get('H', 0),
            "femenino": por_sexo.get('M', 0),
            "atendidos_este_mes": este_mes,
            "atendidos_este_anio": este_anio,
            "infantil": infantil,
            "adulto_joven": adulto_joven,
            "adulto_mayor": adulto_mayor,
        }

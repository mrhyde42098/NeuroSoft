"""
app/presentation/api/v1/referencias.py
======================================
§F2 — Catálogo de referencias bibliográficas.

Endpoints:
    GET    /referencias              → Listar con filtros
    GET    /referencias/{id}         → Detalle
    POST   /referencias              → Agregar referencia (admin)
    GET    /referencias/search?q=    → Búsqueda full-text
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.infrastructure.database.orm_models import ReferenciaBibliograficaORM
from app.presentation.dependencies import DbSession

referencias_router = APIRouter(prefix="/referencias", tags=["Referencias bibliográficas"])


REFERENCIAS_SEMILLA = [
    {
        "id": "ref-apa-2013",
        "tipo": "manual",
        "autores": "American Psychiatric Association",
        "titulo": "Diagnostic and Statistical Manual of Mental Disorders, Fifth Edition (DSM-5)",
        "anio": 2013,
        "doi": "10.1176/appi.books.9780890425596",
        "disciplina": "ambas",
        "categoria": "diagnostico",
        "tags": ["DSM-5", "diagnóstico", "manual", "psicopatología"],
        "resumen": "Manual diagnóstico de referencia internacional para trastornos mentales. Incluye criterios operacionales, especificadores de gravedad y curso, y modelo dimensional-categorial.",
        "nivel_evidencia": "A",
    },
    {
        "id": "ref-beck-1979",
        "tipo": "libro",
        "autores": "Beck, A. T., Rush, A. J., Shaw, B. F., & Emery, G.",
        "titulo": "Cognitive Therapy of Depression",
        "anio": 1979,
        "isbn": "978-0898629194",
        "disciplina": "psicologia_clinica",
        "categoria": "psicoterapia_cognitiva",
        "tags": ["CBT", "depresión", "Beck", "reestructuración cognitiva"],
        "resumen": "Obra fundacional de la Terapia Cognitivo-Conductual. Presenta el modelo cognitivo de la depresión, las distorsiones cognitivas, y el protocolo de tratamiento.",
        "nivel_evidencia": "A",
    },
    {
        "id": "ref-rogers-1957",
        "tipo": "articulo",
        "autores": "Rogers, C. R.",
        "titulo": "The necessary and sufficient conditions of therapeutic personality change",
        "anio": 1957,
        "journal": "Journal of Consulting Psychology, 21(2), 95-103",
        "doi": "10.1037/h0045357",
        "disciplina": "psicologia_clinica",
        "categoria": "psicoterapia_humanista",
        "tags": ["Rogers", "empatía", "consideración positiva", "autenticidad", "factores comunes"],
        "resumen": "Artículo canónico que define las 3 condiciones necesarias y suficientes para el cambio terapéutico: empatía, consideración positiva incondicional y autenticidad.",
        "nivel_evidencia": "A",
    },
    {
        "id": "ref-ostrosky-2010",
        "tipo": "libro",
        "autores": "Ostrosky-Solís, F., Ardila, A., & Rosselli, M.",
        "titulo": "NEUROPSI: Evaluación Neuropsicológica Breve en Español — Manual",
        "anio": 2010,
        "disciplina": "neuropsicologia",
        "categoria": "instrumentos_neuro",
        "tags": ["NEUROPSI", "evaluación", "baremos", "latinoamérica"],
        "resumen": "Batería neuropsicológica breve desarrollada y validada en población latinoamericana (México, Colombia). Incluye baremos por edad y escolaridad.",
        "nivel_evidencia": "A",
    },
    {
        "id": "ref-lezak-2012",
        "tipo": "libro",
        "autores": "Lezak, M. D., Howieson, D. B., Bigler, E. D., & Tranel, D.",
        "titulo": "Neuropsychological Assessment (5th ed.)",
        "anio": 2012,
        "isbn": "978-0195395525",
        "disciplina": "neuropsicologia",
        "categoria": "evaluacion_neuropsicologica",
        "tags": ["evaluación", "manual", "referencia", "test"],
        "resumen": "Compendio de referencia internacional para evaluación neuropsicológica. Describe ~100 tests con propiedades psicométricas, bases neuroanatómicas y aplicaciones clínicas.",
        "nivel_evidencia": "A",
    },
    {
        "id": "ref-shapiro-1989",
        "tipo": "articulo",
        "autores": "Shapiro, F.",
        "titulo": "Efficacy of the eye movement desensitization procedure in the treatment of traumatic memories",
        "anio": 1989,
        "journal": "Journal of Traumatic Stress, 2(2), 199-223",
        "doi": "10.1002/jts.2490020207",
        "disciplina": "psicologia_clinica",
        "categoria": "trauma_y_estres",
        "tags": ["EMDR", "trauma", "TEPT", "estimulación bilateral"],
        "resumen": "Artículo fundacional del EMDR. Describe el protocolo original de desensibilización por movimientos oculares para memorias traumáticas.",
        "nivel_evidencia": "A",
    },
    {
        "id": "ref-linehan-1993",
        "tipo": "libro",
        "autores": "Linehan, M. M.",
        "titulo": "Cognitive-Behavioral Treatment of Borderline Personality Disorder",
        "anio": 1993,
        "isbn": "978-0898621839",
        "disciplina": "psicologia_clinica",
        "categoria": "psicoterapia",
        "tags": ["DBT", "trastorno límite", "TLP", "desregulación emocional"],
        "resumen": "Manual fundacional de la Terapia Dialéctico-Conductual. Protocolo estructurado para TLP con 4 módulos: mindfulness, tolerancia al malestar, regulación emocional, efectividad interpersonal.",
        "nivel_evidencia": "A",
    },
    {
        "id": "ref-johnson-2019",
        "tipo": "libro",
        "autores": "Johnson, S. M.",
        "titulo": "Attachment Theory in Practice: Emotionally Focused Therapy (EFT) with Individuals, Couples, and Families",
        "anio": 2019,
        "isbn": "978-1462538249",
        "disciplina": "psicologia_clinica",
        "categoria": "terapia_pareja_familia",
        "tags": ["EFT", "apego", "pareja", "Johnson"],
        "resumen": "Manual actualizado de Terapia Focalizada en las Emociones para parejas, basada en teoría del apego adulto. Evidencia nivel A: 70-75% mejoría, 90% mantienen ganancias.",
        "nivel_evidencia": "A",
    },
    {
        "id": "ref-gottman-2015",
        "tipo": "libro",
        "autores": "Gottman, J. M., & Silver, N.",
        "titulo": "The Seven Principles for Making Marriage Work",
        "anio": 2015,
        "isbn": "978-0553447712",
        "disciplina": "psicologia_clinica",
        "categoria": "terapia_pareja_familia",
        "tags": ["Gottman", "pareja", "matrimonio", "4 jinetes"],
        "resumen": "Síntesis de 40 años de investigación observacional de parejas. Presenta los 4 jinetes del Apocalipsis (predictores de divorcio) y la Sound Relationship House.",
        "nivel_evidencia": "A",
    },
    {
        "id": "ref-ley1090-2006",
        "tipo": "ley",
        "autores": "Congreso de la República de Colombia",
        "titulo": "Ley 1090 de 2006 — Código Deontológico y Bioético del Psicólogo",
        "anio": 2006,
        "disciplina": "ambas",
        "categoria": "etica_colombia",
        "tags": ["Ley 1090", "ética", "deontología", "Colombia"],
        "resumen": "Marco legal que regula el ejercicio de la psicología en Colombia. Define principios éticos, deberes del psicólogo, confidencialidad, consentimiento informado y sanciones.",
        "nivel_evidencia": "A",
    },
]
"""Referencias semilla que se insertan al iniciar si la tabla está vacía."""


def _seed_referencias(db):
    """Inserta las referencias semilla si la tabla está vacía."""
    existing = db.query(ReferenciaBibliograficaORM).count()
    if existing > 0:
        return
    for r in REFERENCIAS_SEMILLA:
        db.add(ReferenciaBibliograficaORM(**r))
    db.commit()


@referencias_router.get("/", summary="Listar referencias bibliográficas")
def list_referencias(
    db: DbSession,
    disciplina: str = Query(None, description="neuropsicologia | psicologia_clinica | ambas"),
    tipo: str = Query(None, description="libro | articulo | manual | guia | ley | escala | protocolo"),
    categoria: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Retorna el catálogo de referencias con filtros opcionales."""
    _seed_referencias(db)
    q = db.query(ReferenciaBibliograficaORM)
    if disciplina:
        q = q.filter(ReferenciaBibliograficaORM.disciplina == disciplina)
    if tipo:
        q = q.filter(ReferenciaBibliograficaORM.tipo == tipo)
    if categoria:
        q = q.filter(ReferenciaBibliograficaORM.categoria == categoria)
    total = q.count()
    rows = q.order_by(ReferenciaBibliograficaORM.anio.desc()).limit(limit).offset(offset).all()
    return {
        "total": total,
        "referencias": [{k: v for k, v in r.__dict__.items() if not k.startswith("_")} for r in rows],
    }


@referencias_router.get("/search", summary="Buscar referencias por texto")
def search_referencias(
    db: DbSession,
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    limit: int = Query(20, ge=1, le=100),
):
    """Búsqueda full-text en título, autores, tags, resumen."""
    _seed_referencias(db)
    like = f"%{q}%"
    rows = (
        db.query(ReferenciaBibliograficaORM)
        .filter(
            ReferenciaBibliograficaORM.titulo.ilike(like)
            | ReferenciaBibliograficaORM.autores.ilike(like)
            | ReferenciaBibliograficaORM.tags.ilike(like)
            | ReferenciaBibliograficaORM.resumen.ilike(like)
        )
        .order_by(ReferenciaBibliograficaORM.anio.desc())
        .limit(limit)
        .all()
    )
    return {
        "total": len(rows),
        "referencias": [{k: v for k, v in r.__dict__.items() if not k.startswith("_")} for r in rows],
    }


@referencias_router.get("/{ref_id}", summary="Detalle de referencia")
def get_referencia(ref_id: str, db: DbSession):
    """Retorna una referencia específica por ID."""
    _seed_referencias(db)
    r = db.get(ReferenciaBibliograficaORM, ref_id)
    if not r:
        raise HTTPException(status_code=404, detail="Referencia no encontrada")
    return {k: v for k, v in r.__dict__.items() if not k.startswith("_")}


@referencias_router.post("/", status_code=status.HTTP_201_CREATED, summary="Agregar referencia (admin)")
def create_referencia(
    db: DbSession,
    autores: str,
    titulo: str,
    anio: int,
    disciplina: str,
    tipo: str = "articulo",
    journal: str = None,
    doi: str = None,
    isbn: str = None,
    url: str = None,
    categoria: str = None,
    tags: str = None,
    resumen: str = None,
    nivel_evidencia: str = None,
):
    """Agrega una nueva referencia al catálogo. Requiere rol admin (validado por middleware)."""
    import uuid

    r = ReferenciaBibliograficaORM(
        id=str(uuid.uuid4()),
        tipo=tipo,
        autores=autores,
        titulo=titulo,
        anio=anio,
        journal=journal,
        doi=doi,
        isbn=isbn,
        url=url,
        disciplina=disciplina,
        categoria=categoria,
        tags=tags,
        resumen=resumen,
        nivel_evidencia=nivel_evidencia,
    )
    # Generar cita APA automáticamente
    r.cita_apa = _format_apa(r)
    db.add(r)
    db.commit()
    return {k: v for k, v in r.__dict__.items() if not k.startswith("_")}


def _format_apa(r: ReferenciaBibliograficaORM) -> str:
    """Formato APA 7ª edición."""
    parts = [f"{r.autores} ({r.anio}). {r.titulo}."]
    if r.journal:
        parts.append(f" {r.journal}.")
    if r.doi:
        parts.append(f" https://doi.org/{r.doi}")
    return "".join(parts)

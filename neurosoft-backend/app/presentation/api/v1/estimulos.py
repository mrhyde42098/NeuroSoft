"""
app/presentation/api/v1/estimulos.py
=====================================
Gestión de estímulos y recursos gráficos por prueba.

Permite al profesional subir imágenes de reactivos, listas de palabras,
fichas visuales, etc. propias de su práctica, para que NeuroSoft las
muestre en la pantalla de aplicación de la prueba correspondiente.

Endpoints:
    POST   /estimulos/                    → crear/actualizar estímulo
    GET    /estimulos/                    → listar (filtro por test_id)
    GET    /estimulos/por_test/{test_id}  → estímulos de una prueba
    DELETE /estimulos/{id}                → eliminar estímulo
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.infrastructure.database.orm_models import EstimuloORM
from app.presentation.dependencies import DbSession

estimulos_router = APIRouter(prefix="/estimulos", tags=["Estímulos"])


def _is_pdf_capacitacion(orm: EstimuloORM) -> bool:
    """Recortes de PDFs de capacitación — no se sirven en evaluación."""
    tid = orm.test_id or ""
    nombre = (orm.nombre or "").upper()
    return (
        "Stim_p" in tid
        or tid.startswith("NiWiscStim")
        or tid.startswith("AdStim")
        or tid.startswith("EstímuloStim")
        or "IN&S" in nombre
        or (orm.descripcion and ".pdf" in str(orm.descripcion))
    )


# ─────────────────────────────────────────────────────────────
# DTOs
# ─────────────────────────────────────────────────────────────

TIPOS_VALIDOS = ("imagen", "lista_palabras", "audio", "otro")


class EstimuloCreateDTO(BaseModel):
    test_id: str
    item_id: str | None = None
    nombre: str
    tipo: str = "imagen"
    mime_type: str | None = None
    contenido_base64: str
    descripcion: str | None = None
    orden: int = 0


class EstimuloUpdateDTO(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    orden: int | None = None
    activo: bool | None = None


class EstimuloResponseDTO(BaseModel):
    id: str
    test_id: str
    item_id: str | None
    nombre: str
    tipo: str
    mime_type: str | None
    contenido_base64: str | None
    descripcion: str | None
    orden: int
    activo: bool


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _orm_to_dto(orm: EstimuloORM, include_content: bool = True) -> EstimuloResponseDTO:
    return EstimuloResponseDTO(
        id=orm.id,
        test_id=orm.test_id,
        item_id=orm.item_id,
        nombre=orm.nombre,
        tipo=orm.tipo,
        mime_type=orm.mime_type,
        contenido_base64=orm.contenido_base64 if include_content else None,
        descripcion=orm.descripcion,
        orden=orm.orden or 0,
        activo=bool(orm.activo),
    )


# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────

@estimulos_router.post("/", response_model=EstimuloResponseDTO, status_code=201)
def crear_estimulo(dto: EstimuloCreateDTO, db: DbSession):
    if dto.tipo not in TIPOS_VALIDOS:
        raise HTTPException(422, f"tipo inválido. Valores válidos: {TIPOS_VALIDOS}")
    # Validar tamaño del contenido (cap 5 MB base64)
    if dto.contenido_base64 and len(dto.contenido_base64) > 7_000_000:
        raise HTTPException(413, "Archivo demasiado grande (máx ~5 MB).")

    orm = EstimuloORM(
        id=str(uuid.uuid4()),
        test_id=dto.test_id,
        item_id=dto.item_id,
        nombre=dto.nombre,
        tipo=dto.tipo,
        mime_type=dto.mime_type,
        contenido_base64=dto.contenido_base64,
        descripcion=dto.descripcion,
        orden=dto.orden or 0,
        activo=True,
    )
    db.add(orm)
    db.commit()
    db.refresh(orm)
    return _orm_to_dto(orm, include_content=False)


@estimulos_router.post("/bulk", response_model=dict, status_code=201)
def bulk_upload_estimulos(items: list[EstimuloCreateDTO], db: DbSession):
    """
    Carga masiva de estímulos (drag-drop / ZIP descomprimido en el cliente).
    Procesa la lista completa en una sola transacción. Valida tamaños
    individuales y retorna un resumen con aciertos y fallos.
    """
    ok, fail = 0, []
    for idx, dto in enumerate(items):
        if dto.tipo not in TIPOS_VALIDOS:
            fail.append({"idx": idx, "nombre": dto.nombre, "error": f"tipo inválido ({dto.tipo})"})
            continue
        if dto.contenido_base64 and len(dto.contenido_base64) > 7_000_000:
            fail.append({"idx": idx, "nombre": dto.nombre, "error": "archivo >5MB"})
            continue
        try:
            orm = EstimuloORM(
                id=str(uuid.uuid4()),
                test_id=dto.test_id,
                item_id=dto.item_id,
                nombre=dto.nombre,
                tipo=dto.tipo,
                mime_type=dto.mime_type,
                contenido_base64=dto.contenido_base64,
                descripcion=dto.descripcion,
                orden=dto.orden or idx,
                activo=True,
            )
            db.add(orm)
            ok += 1
        except Exception as e:  # noqa: BLE001
            fail.append({"idx": idx, "nombre": dto.nombre, "error": str(e)[:120]})
    db.commit()
    return {"creados": ok, "fallidos": len(fail), "errores": fail}


@estimulos_router.get("/", response_model=list[EstimuloResponseDTO])
def listar_estimulos(
    db: DbSession,
    test_id: str | None = None,
    incluir_contenido: bool = False,
):
    q = db.query(EstimuloORM).filter_by(activo=True)
    if test_id:
        q = q.filter(EstimuloORM.test_id == test_id)
    q = q.order_by(EstimuloORM.test_id, EstimuloORM.orden)
    items = q.all()
    return [_orm_to_dto(o, include_content=incluir_contenido) for o in items]


@estimulos_router.get("/por_test/{test_id}", response_model=list[EstimuloResponseDTO])
def estimulos_por_test(test_id: str, db: DbSession):
    """Estímulos subidos para esta subprueba (excluye recortes PDF de capacitación)."""
    items = (
        db.query(EstimuloORM)
        .filter_by(activo=True, test_id=test_id)
        .order_by(EstimuloORM.orden)
        .all()
    )
    items = [o for o in items if not _is_pdf_capacitacion(o)]
    return [_orm_to_dto(o, include_content=True) for o in items]


@estimulos_router.patch("/{item_id}", response_model=EstimuloResponseDTO)
def actualizar_estimulo(item_id: str, dto: EstimuloUpdateDTO, db: DbSession):
    orm = db.query(EstimuloORM).filter_by(id=item_id).first()
    if not orm:
        raise HTTPException(404, "Estímulo no encontrado")
    if dto.nombre is not None:
        orm.nombre = dto.nombre
    if dto.descripcion is not None:
        orm.descripcion = dto.descripcion
    if dto.orden is not None:
        orm.orden = dto.orden
    if dto.activo is not None:
        orm.activo = dto.activo
    db.commit()
    db.refresh(orm)
    return _orm_to_dto(orm, include_content=False)


@estimulos_router.delete("/{item_id}", status_code=204)
def eliminar_estimulo(item_id: str, db: DbSession):
    orm = db.query(EstimuloORM).filter_by(id=item_id).first()
    if not orm:
        raise HTTPException(404, "Estímulo no encontrado")
    orm.activo = False
    db.commit()
    return None

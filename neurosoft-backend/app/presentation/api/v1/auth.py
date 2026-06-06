"""
app/presentation/api/v1/auth.py
================================
Endpoints de autenticación JWT.

POST /auth/login              → access_token + refresh_token
POST /auth/refresh            → nuevo access_token
GET  /auth/me                 → perfil del usuario actual
POST /auth/change-password    → cambiar contraseña
GET  /auth/users              → listar usuarios (solo admin)
POST /auth/users              → crear usuario (solo admin)
DELETE /auth/users/{user_id}  → desactivar usuario (solo admin)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.infrastructure.audit import record_event
from app.infrastructure.auth.auth_service import (
    UserRepository,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)
from app.presentation.dependencies import DbSession, db_session

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["Autenticación"])
bearer_scheme = HTTPBearer(auto_error=False)


# ─────────────────────────────────────────────────────────────
# DTOs
# ─────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    expires_in:    int          # segundos
    user_id:       str
    username:      str
    nombre_completo: str
    role:          str


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    expires_in:   int


class UserMeResponse(BaseModel):
    id:              str
    username:        str
    nombre_completo: str
    role:            str
    profesional_id:  str | None


class CreateUserRequest(BaseModel):
    username:        str = Field(..., min_length=3, max_length=50)
    password:        str = Field(..., min_length=6)
    nombre_completo: str = Field(..., min_length=2)
    role:            str = Field(default="profesional")
    profesional_id:  str | None = None


class ChangePasswordRequest(BaseModel):
    password_actual: str
    password_nuevo:  str = Field(..., min_length=6)


class UserListItem(BaseModel):
    id:              str
    username:        str
    nombre_completo: str
    role:            str
    is_active:       bool
    profesional_id:  str | None


# ─────────────────────────────────────────────────────────────
# Dependencia: usuario autenticado
# ─────────────────────────────────────────────────────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(db_session),
):
    """
    Extrae y valida el Bearer token del header Authorization.
    Retorna el ORM del usuario.
    Lanza 401 si el token es inválido o falta.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Comprobar la lista negra: un token revocado vía /auth/logout
    # debe dejar de funcionar aunque siga siendo criptográficamente válido.
    from app.infrastructure.auth.auth_service import (
        is_token_revoked,
        is_user_session_revoked,
    )
    if is_token_revoked(db, payload.get("jti", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado (sesión cerrada).",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Y la sentinel "todas las sesiones" (cambio de contraseña, admin
    # revoke, etc.): si revoked_at > iat del token, lo rechazamos.
    if is_user_session_revoked(db, payload.get("sub", ""), payload.get("iat")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión invalidada (cambio de contraseña o revocación administrativa).",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repo = UserRepository(db)
    user = repo.find_by_id(payload["sub"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo.",
        )
    return user


def require_admin(current_user=Depends(get_current_user)):
    """Dependencia que exige rol admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta acción requiere rol 'admin'.",
        )
    return current_user


# Anotaciones tipadas
CurrentUser = Depends(get_current_user)
AdminUser   = Depends(require_admin)


# ─────────────────────────────────────────────────────────────
# §S0.2 — verify_ownership: el user solo toca pacientes de su
# profesional_id, salvo admin que ve todo.
# ─────────────────────────────────────────────────────────────

def get_patient_for_user(
    patient_id: str,
    db: Session,
    user,
) -> object:
    """
    Carga un paciente y valida que `user` puede acceder a él.

    Reglas de autorización (S0.2 del PLAN_MAESTRO):
      - admin            → todos los pacientes
      - profesional      → solo pacientes donde patient.profesional_id
                           == user.profesional_id
      - viewer           → mismo alcance que profesional (solo lectura)
      - user sin vinculo (profesional_id IS NULL) → no puede acceder a
        ningún paciente de otros profesionales; SÍ puede ver pacientes
        sin profesional_id asignado (huérfanos) para reasignarlos.

    Errores:
      - 404 si el paciente no existe.
      - 403 si existe pero no le pertenece.
    """
    from app.infrastructure.database.orm_models import PatientORM

    patient = (
        db.query(PatientORM)
        .filter_by(id=patient_id, is_active=True)
        .first()
    )
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado o archivado.",
        )

    if user.role == "admin":
        return patient

    # Profesional / viewer: solo acceso a pacientes de su profesional_id
    if user.profesional_id is None:
        # Sin vinculo, solo puede ver pacientes huerfanos (sin profesional).
        if patient.profesional_id is None:
            return patient
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para acceder a este paciente "
                   "(usuario sin profesional vinculado).",
        )

    if patient.profesional_id != user.profesional_id:
        # Logueamos en audit: intento de acceso cross-tenant
        try:
            from app.infrastructure.audit import record_event
            from fastapi import Request
            # `request` puede no estar disponible si se llama desde
            # un use case; lo manejamos de forma defensiva.
            record_event(
                db,
                action="access_denied",
                entity_type="patient",
                entity_id=patient_id,
                actor_id=user.id,
                actor_label=user.username,
                summary=(
                    f"Acceso cross-tenant bloqueado: user={user.username} "
                    f"rol={user.role} profesional_id={user.profesional_id} "
                    f"-> paciente.profesional_id={patient.profesional_id}"
                ),
            )
            db.commit()
        except Exception as audit_exc:
            db.rollback()
            logger.warning(
                "No se pudo registrar audit cross-tenant: %s", audit_exc,
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para acceder a este paciente.",
        )

    return patient


def get_evaluation_for_user(
    evaluation_id: str,
    db: Session,
    user,
) -> object:
    """
    Carga una evaluación y valida que `user` puede acceder vía el paciente.
    """
    from app.infrastructure.database.orm_models import EvaluationORM

    ev = db.query(EvaluationORM).filter_by(id=evaluation_id).first()
    if ev is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada.",
        )
    get_patient_for_user(ev.patient_id, db, user)
    return ev


# ─────────────────────────────────────────────────────────────
# RATE LIMITING — Login brute-force protection
# ─────────────────────────────────────────────────────────────

import time as _time

_LOGIN_ATTEMPTS: dict[str, list[float]] = {}
# §M8-fix: parametrizables vía variables de entorno.
import os as _os
from datetime import UTC

_MAX_ATTEMPTS   = int(_os.getenv("NEUROSOFT_LOGIN_MAX_ATTEMPTS", "5"))
_WINDOW_SECONDS = int(_os.getenv("NEUROSOFT_LOGIN_WINDOW_SECONDS", "60"))


def _check_rate_limit(client_ip: str) -> None:
    """Lanza 429 si el IP excede el límite de intentos de login."""
    now = _time.time()
    attempts = _LOGIN_ATTEMPTS.get(client_ip, [])
    # Limpiar intentos fuera de la ventana
    attempts = [t for t in attempts if now - t < _WINDOW_SECONDS]
    _LOGIN_ATTEMPTS[client_ip] = attempts
    if len(attempts) >= _MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Demasiados intentos de login. "
                f"Máximo {_MAX_ATTEMPTS} por minuto. Intenta de nuevo en un momento."
            ),
        )


def _record_attempt(client_ip: str) -> None:
    """Registra un intento de login (exitoso o fallido)."""
    _LOGIN_ATTEMPTS.setdefault(client_ip, []).append(_time.time())


# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────

@auth_router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Verifica credenciales y retorna tokens JWT de acceso y refresco.",
)
def login(body: LoginRequest, request: Request, db: DbSession):
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)
    _record_attempt(client_ip)

    repo = UserRepository(db)
    user = repo.authenticate(body.username, body.password)
    if user is None:
        # Audit: login fallido
        record_event(
            db,
            action="login_failed",
            entity_type="auth",
            actor_label=body.username[:120],
            summary=f"Intento fallido desde {client_ip}",
            request=request,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
        )
    from app.infrastructure.auth.auth_service import ACCESS_TOKEN_EXPIRE_HOURS
    access  = create_access_token(user.id, user.role, username=user.username)
    refresh = create_refresh_token(user.id)
    # Audit: login exitoso
    record_event(
        db,
        action="login",
        entity_type="auth",
        entity_id=user.id,
        actor_id=user.id,
        actor_label=user.username,
        summary=f"Inicio de sesión ({user.role})",
        request=request,
    )
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        user_id=user.id,
        username=user.username,
        nombre_completo=user.nombre_completo,
        role=user.role,
    )


@auth_router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Renovar access token",
    description="Usa el refresh token para obtener un nuevo access token sin re-login.",
)
def refresh_token(body: RefreshRequest, db: DbSession):
    try:
        user_id = decode_refresh_token(body.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    repo = UserRepository(db)
    user = repo.find_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado.")

    from app.infrastructure.auth.auth_service import ACCESS_TOKEN_EXPIRE_HOURS
    access = create_access_token(user.id, user.role, username=user.username)
    return AccessTokenResponse(
        access_token=access,
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
    )


@auth_router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Perfil del usuario actual",
)
def get_me(current_user=Depends(get_current_user)):
    return UserMeResponse(
        id=current_user.id,
        username=current_user.username,
        nombre_completo=current_user.nombre_completo,
        role=current_user.role,
        profesional_id=current_user.profesional_id,
    )


@auth_router.post(
    "/logout",
    status_code=204,
    summary="Cerrar sesión (revoca el token actual)",
    description=(
        "Inserta el `jti` del access token presentado en la tabla de "
        "revocación. Tras el logout, cualquier intento de volver a usar "
        "ese token devuelve 401. Es idempotente: llamar dos veces no falla. "
        "Un logout **no** cierra otros dispositivos — cada token tiene su "
        "propio `jti`."
    ),
)
def logout(
    request: Request,
    db: DbSession,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user=Depends(get_current_user),
):
    from datetime import datetime

    from app.infrastructure.auth.auth_service import revoke_token

    if credentials is None:
        # get_current_user ya cubre esto, pero defensivo.
        raise HTTPException(status_code=401, detail="No se proporcionó token.")

    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError:
        # El token ya no es válido: nada que revocar. 204 igual (idempotente).
        return

    jti = payload.get("jti")
    exp_ts = payload.get("exp")
    if not jti or exp_ts is None:
        # Token antiguo sin jti — no podemos revocarlo, pero la respuesta
        # sigue siendo 204 para no romper el frontend en la transición.
        return

    expires_at = datetime.fromtimestamp(int(exp_ts), tz=UTC)
    revoke_token(
        db,
        jti=jti,
        user_id=current_user.id,
        expires_at=expires_at,
        reason="logout",
    )
    record_event(
        db,
        action="logout",
        entity_type="auth",
        entity_id=current_user.id,
        actor_id=current_user.id,
        actor_label=current_user.username,
        summary="Cierre de sesión (token revocado)",
        request=request,
    )


@auth_router.post(
    "/change-password",
    status_code=204,
    summary="Cambiar contraseña",
)
def change_password(
    body: ChangePasswordRequest,
    request: Request,
    db: DbSession,
    current_user=Depends(get_current_user),
):
    from app.infrastructure.auth.auth_service import (
        revoke_all_user_tokens,
        verify_password,
    )
    if not verify_password(body.password_actual, current_user.hashed_password):
        record_event(
            db,
            action="password_change_failed",
            entity_type="auth",
            entity_id=current_user.id,
            actor_id=current_user.id,
            actor_label=current_user.username,
            summary="Cambio de contraseña rechazado (contraseña actual incorrecta)",
            request=request,
        )
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta.")
    repo = UserRepository(db)
    repo.update_password(current_user.id, body.password_nuevo)

    # CRÍTICO: invalidar TODAS las sesiones existentes del usuario.
    # Sin esto, un atacante que robó un token antes del cambio sigue
    # autenticado hasta que caduque (hasta 8h).
    revoke_all_user_tokens(db, current_user.id, reason="password_change")

    record_event(
        db,
        action="password_change",
        entity_type="auth",
        entity_id=current_user.id,
        actor_id=current_user.id,
        actor_label=current_user.username,
        summary="Contraseña actualizada (todas las sesiones cerradas)",
        request=request,
    )


# ── Admin only ───────────────────────────────────────────────

@auth_router.get(
    "/users",
    response_model=list[UserListItem],
    summary="Listar todos los usuarios (admin)",
)
def list_users(db: DbSession, admin=Depends(require_admin)):
    repo = UserRepository(db)
    users = repo.list_users()
    return [
        UserListItem(
            id=u.id, username=u.username,
            nombre_completo=u.nombre_completo,
            role=u.role, is_active=u.is_active,
            profesional_id=u.profesional_id,
        )
        for u in users
    ]


@auth_router.post(
    "/users",
    response_model=UserListItem,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo usuario (admin)",
)
def create_user(body: CreateUserRequest, db: DbSession, admin=Depends(require_admin)):
    repo = UserRepository(db)
    try:
        user = repo.create(
            username=body.username,
            password_plain=body.password,
            nombre_completo=body.nombre_completo,
            role=body.role,
            profesional_id=body.profesional_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return UserListItem(
        id=user.id, username=user.username,
        nombre_completo=user.nombre_completo,
        role=user.role, is_active=user.is_active,
        profesional_id=user.profesional_id,
    )


@auth_router.delete(
    "/users/{user_id}",
    status_code=204,
    summary="Desactivar usuario (admin)",
)
def deactivate_user(
    user_id: str,
    request: Request,
    db: DbSession,
    admin=Depends(require_admin),
):
    from app.infrastructure.auth.auth_service import revoke_all_user_tokens

    repo = UserRepository(db)
    if not repo.deactivate(user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Cerrar también todas las sesiones del usuario desactivado:
    # de otra forma seguiría operando con un token vivo hasta 8h.
    revoke_all_user_tokens(db, user_id, reason="admin_deactivated")
    record_event(
        db,
        action="user_deactivated",
        entity_type="auth",
        entity_id=user_id,
        actor_id=admin.id,
        actor_label=admin.username,
        summary="Usuario desactivado y sesiones cerradas",
        request=request,
    )


@auth_router.post(
    "/users/{user_id}/revoke-tokens",
    status_code=204,
    summary="Cerrar todas las sesiones del usuario (admin)",
    description=(
        "Marca un checkpoint de revocación: cualquier token emitido para "
        "este usuario ANTES del momento actual deja de funcionar. Útil "
        "ante sospechas de compromiso de credenciales o cuando un "
        "empleado deja la organización. No requiere conocer los `jti` "
        "individuales — invalida todos los dispositivos de una sola vez."
    ),
)
def admin_revoke_user_tokens(
    user_id: str,
    request: Request,
    db: DbSession,
    admin=Depends(require_admin),
):
    from app.infrastructure.auth.auth_service import revoke_all_user_tokens

    repo = UserRepository(db)
    user = repo.find_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    revoke_all_user_tokens(db, user_id, reason="admin_revoked")
    record_event(
        db,
        action="admin_revoke_tokens",
        entity_type="auth",
        entity_id=user_id,
        actor_id=admin.id,
        actor_label=admin.username,
        summary=f"Admin {admin.username} revocó todas las sesiones de {user.username}",
        request=request,
    )

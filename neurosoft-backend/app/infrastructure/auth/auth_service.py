"""
app/infrastructure/auth/auth_service.py
=========================================
Autenticación básica para multi-usuario (2-5 psicólogos).

Stack:
  - Tabla `users` en SQLite
  - Contraseñas con bcrypt
  - JWT Bearer tokens (access 8h + refresh 7 días)
  - Roles: admin | profesional | viewer

Flujo:
  POST /auth/login  → {access_token, refresh_token}
  POST /auth/refresh → nuevo access_token
  GET  /auth/me     → datos del usuario actual

Dependencia: python-jose[cryptography] + passlib[bcrypt]
  pip install python-jose[cryptography] passlib[bcrypt]
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import UTC, datetime, timedelta

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Configuración JWT (leer de .env en producción)
# ─────────────────────────────────────────────────────────────

_DEFAULT_SECRET = "neurosoft-dev-secret-key-change-in-production-32chars-min"


def _resolve_secret_key() -> str:
    """
    Resuelve el secreto JWT respetando el settings.env.
    - En producción aborta si no hay secreto o usa el valor de desarrollo.
    - En desarrollo cae al valor por defecto con advertencia.
    """
    # Preferimos settings.secret_key (pydantic) sobre la lectura directa
    try:
        from app.core.config import settings as _settings
        env = getattr(_settings, "env", "development")
        value = getattr(_settings, "secret_key", "") or os.getenv("NEUROSOFT_SECRET_KEY", "")
    except Exception:
        env = os.getenv("NEUROSOFT_ENV", "development")
        value = os.getenv("NEUROSOFT_SECRET_KEY", "")

    if env == "production":
        if not value or value == _DEFAULT_SECRET:
            raise RuntimeError(
                "NEUROSOFT_SECRET_KEY no configurada en producción. "
                "Genera una con `python -c \"import secrets; print(secrets.token_urlsafe(48))\"` "
                "y expórtala como variable de entorno antes de arrancar."
            )
        if len(value) < 32:
            raise RuntimeError(
                f"NEUROSOFT_SECRET_KEY demasiado corta ({len(value)} chars); "
                "se requieren al menos 32."
            )
        return value

    # Desarrollo/test: permitir fallback con warning
    if not value:
        value = _DEFAULT_SECRET
    if value == _DEFAULT_SECRET:
        logger.warning(
            "⚠️  JWT_SECRET usa el valor por defecto. "
            "Configura NEUROSOFT_SECRET_KEY en .env antes de producción."
        )
    return value


SECRET_KEY = _resolve_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("NEUROSOFT_ACCESS_TOKEN_HOURS", "8"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("NEUROSOFT_REFRESH_TOKEN_DAYS", "7"))

ROLES = ("admin", "profesional", "viewer")


# ─────────────────────────────────────────────────────────────
# Helpers de contraseña
# ─────────────────────────────────────────────────────────────

def _get_pwd_context():
    try:
        from passlib.context import CryptContext
        return CryptContext(schemes=["bcrypt"], deprecated="auto")
    except ImportError:
        raise RuntimeError("passlib no instalada. Ejecuta: pip install passlib[bcrypt]")


def hash_password(plain: str) -> str:
    return _get_pwd_context().hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _get_pwd_context().verify(plain, hashed)
    except Exception as exc:
        logger.warning("verify_password falló: %s", exc)
        return False


# ─────────────────────────────────────────────────────────────
# JWT
# ─────────────────────────────────────────────────────────────

def _jwt():
    try:
        from jose import JWTError, jwt
        return jwt, JWTError
    except ImportError:
        raise RuntimeError(
            "python-jose no instalado. Ejecuta: pip install python-jose[cryptography]"
        )


def create_access_token(user_id: str, role: str, username: str | None = None) -> str:
    """
    Genera un access token JWT.

    El `jti` (JWT ID) es un UUID v4 único por token — imprescindible para poder
    revocar un token específico sin invalidar los demás del mismo usuario
    (ver TokenBlacklistORM / POST /auth/logout).
    `username` es opcional: si se provee, se incluye como claim para que el
    middleware pueda poblar `request.state.user_label` sin consultar la BD
    en cada request.
    """
    jwt, _ = _jwt()
    expire = datetime.now(UTC) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    if username:
        payload["username"] = username
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    jwt, _ = _jwt()
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida un access token.
    Lanza ValueError si es inválido o expirado.
    """
    jwt, JWTError = _jwt()
    try:
        # §M14-fix: options explícito asegura que la expiración (exp)
        # y la firma se verifiquen siempre, sin depender de defaults.
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM],
            options={"verify_signature": True, "verify_exp": True, "require": ["exp"]},
        )
        if payload.get("type") != "access":
            raise ValueError("Token no es de tipo access")
        return payload
    except JWTError as e:
        raise ValueError(f"Token inválido: {e}") from e


def decode_refresh_token(token: str) -> str:
    """Retorna user_id del refresh token o lanza ValueError."""
    jwt, JWTError = _jwt()
    try:
        # §M14-fix: options explícito asegura que la expiración (exp)
        # y la firma se verifiquen siempre, sin depender de defaults.
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM],
            options={"verify_signature": True, "verify_exp": True, "require": ["exp"]},
        )
        if payload.get("type") != "refresh":
            raise ValueError("Token no es de tipo refresh")
        return payload["sub"]
    except JWTError as e:
        raise ValueError(f"Refresh token inválido: {e}") from e


# ─────────────────────────────────────────────────────────────
# Repositorio de usuarios
# ─────────────────────────────────────────────────────────────

class UserRepository:
    """CRUD sobre la tabla users."""

    def __init__(self, session):
        self._db = session

    def create(
        self,
        username: str,
        password_plain: str,
        nombre_completo: str,
        role: str = "profesional",
        profesional_id: str | None = None,
    ):
        from app.infrastructure.database.orm_models import UserORM
        existing = self._db.query(UserORM).filter_by(username=username).first()
        if existing:
            raise ValueError(f"El usuario '{username}' ya existe.")
        if role not in ROLES:
            raise ValueError(f"Rol inválido '{role}'. Válidos: {ROLES}")
        orm = UserORM(
            id=str(uuid.uuid4()),
            username=username.lower().strip(),
            hashed_password=hash_password(password_plain),
            nombre_completo=nombre_completo,
            role=role,
            profesional_id=profesional_id,
            is_active=True,
            created_at=datetime.now(UTC),
        )
        self._db.add(orm)
        self._db.flush()
        logger.info("Usuario creado: %s (rol=%s)", username, role)
        return orm

    def find_by_username(self, username: str):
        from app.infrastructure.database.orm_models import UserORM
        return (
            self._db.query(UserORM)
            .filter_by(username=username.lower().strip(), is_active=True)
            .first()
        )

    def find_by_id(self, user_id: str):
        from app.infrastructure.database.orm_models import UserORM
        return self._db.query(UserORM).filter_by(id=user_id, is_active=True).first()

    def update_password(self, user_id: str, new_password: str) -> bool:
        from app.infrastructure.database.orm_models import UserORM
        orm = self._db.query(UserORM).filter_by(id=user_id).first()
        if not orm:
            return False
        orm.hashed_password = hash_password(new_password)
        orm.updated_at = datetime.now(UTC)
        return True

    def list_users(self):
        from app.infrastructure.database.orm_models import UserORM
        return self._db.query(UserORM).filter_by(is_active=True).all()

    def deactivate(self, user_id: str) -> bool:
        from app.infrastructure.database.orm_models import UserORM
        orm = self._db.query(UserORM).filter_by(id=user_id).first()
        if not orm:
            return False
        orm.is_active = False
        return True

    def authenticate(self, username: str, password: str):
        """
        Verifica credenciales.
        Retorna el ORM del usuario si es válido, None si no.
        """
        orm = self.find_by_username(username)
        if orm is None:
            return None
        if not verify_password(password, orm.hashed_password):
            return None
        return orm

    def ensure_admin_exists(self, default_password: str | None = None):
        """
        Crea/activa el usuario admin principal.
        Se llama en el startup de FastAPI.

        - En desarrollo: si no se provee contraseña, usa 'neurosoft2025' con aviso.
        - En producción: exige contraseña explícita (vía NEUROSOFT_ADMIN_PASSWORD).
          Aborta el arranque si no está configurada.
        """
        from app.core.config import settings
        from app.infrastructure.database.orm_models import UserORM

        # Resolver contraseña
        password = default_password or os.getenv("NEUROSOFT_ADMIN_PASSWORD", "") or settings.admin_password
        admin = self._db.query(UserORM).filter_by(username="admin").first()
        if admin is not None:
            admin.role = "admin"
            admin.is_active = True
            # §S0.5 — ELIMINADO el kill-switch NEUROSOFT_RESET_ADMIN_PASSWORD.
            # Era un riesgo crítico: con esa flag en 1, cualquier proceso
            # podia sobrescribir la contraseña del admin sin auth. Ahora
            # el admin debe usar POST /auth/change-password (con auth) para
            # rotar su contraseña.
            _reset_admin_pwd = os.getenv("NEUROSOFT_RESET_ADMIN_PASSWORD", "0")
            if _reset_admin_pwd == "1":
                logger.warning(
                    "NEUROSOFT_RESET_ADMIN_PASSWORD está activa pero es IGNORADA "
                    "(eliminado en Sprint 0, S0.5). Use /auth/change-password."
                )
            self._db.commit()
            return
        if settings.env == "production":
            if not password:
                raise RuntimeError(
                    "NEUROSOFT_ADMIN_PASSWORD no configurada en producción. "
                    "Define una contraseña inicial fuerte antes de arrancar."
                )
            if len(password) < 8:
                raise RuntimeError(
                    "NEUROSOFT_ADMIN_PASSWORD demasiado corta (mínimo 8 caracteres)."
                )
        else:
            if not password:
                # Cuando se ejecuta dentro de un .exe empaquetado (PyInstaller),
                # generar una contraseña aleatoria larga para evitar que beta
                # testers o usuarios externos puedan iniciar sesión como admin.
                # La contraseña queda hash-eada en la BD pero NO se loggea ni
                # se imprime, así nadie tiene acceso administrativo accidental.
                #
                # §A5-fix: ANTES en modo dev no-frozen usábamos "neurosoft2025"
                # hardcoded — riesgo si se expone el puerto. AHORA generamos
                # SIEMPRE una contraseña aleatoria, y en dev la persistimos a
                # disco (legible solo por el usuario) para que el dev pueda
                # consultarla.
                import secrets
                import sys as _sys

                password = secrets.token_urlsafe(40)
                if not getattr(_sys, "frozen", False):
                    try:
                        from app.core.config import settings as _settings
                        cred_file = _settings.data_dir / "admin_password_dev.txt"
                        cred_file.parent.mkdir(parents=True, exist_ok=True)
                        cred_file.write_text(
                            f"# NeuroSoft — contraseña admin generada para desarrollo\n"
                            f"# Generada: {datetime.utcnow().isoformat()}\n"
                            f"# NO commitear, NO compartir.\n"
                            f"{password}\n",
                            encoding="utf-8",
                        )
                        try:
                            import os as _os
                            _os.chmod(str(cred_file), 0o600)
                        except Exception as _exc:
                            logger.debug("chmod falló (no crítico): %s", _exc)
                        logger.warning(
                            "Admin password generada aleatoriamente. "
                            "Consulta: %s", cred_file
                        )
                    except Exception as _exc:
                        # Si no podemos persistirla, la regeneramos a una conocida
                        # — mejor que dejar al dev sin acceso al admin.
                        logger.warning(
                            "No se pudo persistir admin password (%s). "
                            "Usando fallback documentado en consola.", _exc
                        )
                        password = "neurosoft2025"

        self.create(
            username="admin",
            password_plain=password,
            nombre_completo="Administrador",
            role="admin",
        )
        self._db.commit()
        if password == "neurosoft2025":
            logger.warning(
                "Usuario admin creado con contraseña por defecto de desarrollo. "
                "Cámbiala YA en /auth/change-password y define NEUROSOFT_ADMIN_PASSWORD."
            )
        else:
            logger.info("Usuario admin creado (contraseña aleatoria o configurada vía env).")

    def ensure_beta_tester_exists(
        self,
        username: str = "beta",
        default_password: str | None = None,
    ):
        """
        Crea/activa un usuario profesional para beta testing.

        El rol `profesional` permite probar el flujo clinico completo, pero
        queda fuera de los endpoints protegidos por `require_admin`.

        Username default: "beta" (genérico).
        Override vía env: NEUROSOFT_BETA_USERNAME / NEUROSOFT_BETA_PASSWORD.

        Retrocompatibilidad: instalaciones previas que tenían el usuario
        histórico "mayra" siguen funcionando — no se borra ni renombra,
        solo deja de crearse en instalaciones nuevas.
        """
        from app.infrastructure.database.orm_models import UserORM

        # Permitir override de username por env (sin romper installs viejas).
        username = os.getenv("NEUROSOFT_BETA_USERNAME", "") or username
        password = (
            default_password
            or os.getenv("NEUROSOFT_BETA_PASSWORD", "")
            or "BetaTester2026!"
        )
        username_clean = username.lower().strip()
        beta = self._db.query(UserORM).filter_by(username=username_clean).first()
        if beta is not None:
            beta.nombre_completo = beta.nombre_completo or "Beta Tester"
            beta.role = "profesional"
            beta.is_active = True
            # §S0.5 — ELIMINADO el kill-switch NEUROSOFT_RESET_BETA_PASSWORD.
            # Igual riesgo que NEUROSOFT_RESET_ADMIN_PASSWORD: cualquier
            # proceso con esa flag podia sobrescribir la contraseña del
            # usuario beta (rol=profesional) sin auth.
            _reset_beta_pwd = os.getenv("NEUROSOFT_RESET_BETA_PASSWORD", "0")
            if _reset_beta_pwd == "1":
                logger.warning(
                    "NEUROSOFT_RESET_BETA_PASSWORD está activa pero es IGNORADA "
                    "(eliminado en Sprint 0, S0.5). Use /auth/change-password."
                )
            self._db.commit()
            return beta

        beta = self.create(
            username=username_clean,
            password_plain=password,
            nombre_completo="Beta Tester",
            role="profesional",
        )
        self._db.commit()
        logger.info("Usuario beta creado: %s (rol=profesional)", username_clean)
        return beta


# ─────────────────────────────────────────────────────────────
# Token Blacklist — revocación explícita de JWTs (logout real)
# ─────────────────────────────────────────────────────────────


def revoke_token(
    session,
    jti: str,
    user_id: str,
    expires_at: datetime,
    reason: str = "logout",
) -> None:
    """
    Inserta un `jti` en la lista negra. Idempotente: si ya existe, no
    duplica (el jti es la PK).

    `expires_at` se guarda para que el cleanup periódico pueda purgar
    entradas cuyo exp ya caducó (una vez caducado, el decode JWT falla
    igualmente y el registro en blacklist es redundante).
    """
    from app.infrastructure.database.orm_models import TokenBlacklistORM

    existing = session.query(TokenBlacklistORM).filter_by(jti=jti).first()
    if existing is not None:
        return
    entry = TokenBlacklistORM(
        jti=jti,
        user_id=user_id,
        revoked_at=datetime.now(UTC),
        expires_at=expires_at,
        reason=reason,
    )
    session.add(entry)
    session.flush()


def is_token_revoked(session, jti: str) -> bool:
    """
    Retorna True si el `jti` está en la tabla de revocación.
    Si `jti` es falsy (tokens viejos emitidos antes de este feature),
    asume NO revocado — así no rompemos sesiones activas el día del deploy.
    """
    if not jti:
        return False
    from app.infrastructure.database.orm_models import TokenBlacklistORM
    return (
        session.query(TokenBlacklistORM.jti)
        .filter(TokenBlacklistORM.jti == jti)
        .first()
        is not None
    )


def purge_expired_blacklist_entries(session) -> int:
    """
    Elimina entradas ya expiradas (exp pasada) del blacklist.
    Devuelve la cantidad borrada. Pensado para el scheduler.
    """
    from app.infrastructure.database.orm_models import TokenBlacklistORM
    now = datetime.now(UTC)
    q = session.query(TokenBlacklistORM).filter(TokenBlacklistORM.expires_at < now)
    n = q.count()
    q.delete(synchronize_session=False)
    return n


def revoke_all_user_tokens(
    session,
    user_id: str,
    reason: str = "password_change",
) -> int:
    """
    Marca como revocado un "checkpoint" para todos los tokens del usuario.

    Estrategia: insertamos una entrada SENTINEL con `jti = "user:{user_id}"`.
    El middleware/dependency adicionalmente comprueba esta sentinel cada
    vez que valida un token: si existe Y fue creada DESPUÉS del `iat`
    del token, entonces el token se considera revocado.

    Esta es la única forma de invalidar tokens cuyo `jti` específico
    no conocemos (porque están en otros dispositivos del usuario).

    Devuelve siempre 1 (sentinel insertada o actualizada). El caller
    decide si commitear.
    """
    from app.infrastructure.database.orm_models import TokenBlacklistORM

    sentinel_jti = f"user:{user_id}"
    now = datetime.now(UTC)
    # Las sentinelas tienen exp = ahora + máxima vida de un token
    # (8h por defecto). Más allá de eso ya caducan los tokens igual.
    far_exp = now + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS + 1)

    existing = session.query(TokenBlacklistORM).filter_by(jti=sentinel_jti).first()
    if existing is not None:
        existing.revoked_at = now
        existing.expires_at = far_exp
        existing.reason = reason
    else:
        session.add(TokenBlacklistORM(
            jti=sentinel_jti,
            user_id=user_id,
            revoked_at=now,
            expires_at=far_exp,
            reason=reason,
        ))
    session.flush()
    return 1


def is_user_session_revoked(session, user_id: str, token_iat: int) -> bool:
    """
    True si existe una sentinel `user:{user_id}` cuya `revoked_at` es
    POSTERIOR al `iat` del token. Es decir: el usuario revocó todas sus
    sesiones después de emitido este token, así que este token ya no vale.
    """
    from app.infrastructure.database.orm_models import TokenBlacklistORM
    if not user_id or token_iat is None:
        return False
    sentinel = (
        session.query(TokenBlacklistORM)
        .filter_by(jti=f"user:{user_id}")
        .first()
    )
    if sentinel is None:
        return False
    iat_dt = datetime.fromtimestamp(int(token_iat), tz=UTC)
    revoked_at = sentinel.revoked_at
    if revoked_at.tzinfo is None:
        revoked_at = revoked_at.replace(tzinfo=UTC)
    return revoked_at > iat_dt

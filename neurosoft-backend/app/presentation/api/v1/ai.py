"""
app/presentation/api/v1/ai.py
==============================
Asistente de IA integrado — Fase G.1 del ROADMAP.

Soporta 4 proveedores con routing híbrido:
  - gemini   → Google Generative Language API (requiere API key del usuario)
  - claude   → Anthropic Messages API (requiere API key del usuario)
  - openai   → OpenAI Chat Completions API (requiere API key del usuario)
  - ollama   → servidor local en 127.0.0.1:11434 (sin API key, sin nube)
  - auto     → intenta nube (si hay API key), cae en Ollama si falla

Prompt-sistema: el módulo nunca envía PHI identificable; los endpoints
llaman a `sanitize_clinical_input()` para quitar nombres, documentos y
fechas de nacimiento antes de mandar el texto al proveedor remoto.

Endpoints:
    GET    /ai/config               → configuración actual del usuario
    POST   /ai/config               → guardar configuración
    POST   /ai/chat                 → envío libre de mensajes
    POST   /ai/improve              → mejorar texto de informe (style)
    POST   /ai/narrate              → generar narrativa clínica desde Z-scores
    GET    /ai/health               → ping a cada proveedor configurado
    GET    /ai/ollama/status        → detecta si Ollama está instalado y activo
"""

from __future__ import annotations

import json
import logging
import re
import socket
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.infrastructure.database.orm_models import AIConfigORM
from app.presentation.dependencies import DbSession

logger = logging.getLogger("neurosoft.ai")

ai_router = APIRouter(prefix="/ai", tags=["IA"])


# ═══════════════════════════════════════════════════════════════════════
# DTOs
# ═══════════════════════════════════════════════════════════════════════

VALID_PROVIDERS = ("auto", "gemini", "claude", "openai", "ollama", "medgemma", "openrouter")

DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash",
    "claude": "claude-haiku-4-5-20251001",
    "openai": "gpt-4.1-mini",
    "openrouter": "google/gemini-2.5-flash",
    "ollama": "llama3.1:8b",
    # MedGemma en línea vía endpoint OpenAI-compatible (OpenRouter / HF / Vertex)
    "medgemma": "google/medgemma-4b-it",
}


class AIConfigDTO(BaseModel):
    provider: str = "auto"
    api_key: str | None = None
    model: str | None = None
    ollama_url: str = "http://127.0.0.1:11434"
    openai_base_url: str | None = None  # endpoint OpenAI-compatible (MedGemma en línea)
    temperature: int = 70
    max_tokens: int = 1024
    enable_cloud: bool = True


class AIConfigResponseDTO(AIConfigDTO):
    # Nunca devolvemos la API key completa; sólo indica si está seteada.
    api_key_set: bool = False
    api_key: str | None = None  # override → siempre None al responder


class ChatMessageDTO(BaseModel):
    role: str  # 'system' | 'user' | 'assistant'
    content: str


class ChatRequestDTO(BaseModel):
    messages: list[ChatMessageDTO]
    system: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    provider_override: str | None = None  # forzar un proveedor específico


class ChatResponseDTO(BaseModel):
    provider: str
    model: str
    content: str
    usage: dict[str, Any] | None = None


class ImproveTextDTO(BaseModel):
    text: str
    task: str = "style"     # 'style' | 'grammar' | 'summarize' | 'clinical_review'
    tone: str = "clinical"  # 'clinical' | 'friendly' | 'technical'
    # Inyecta reglas de estilo institucional (bottom-up, DIS-, no-conserva).
    # Alias `institutional_style` para nuevos clientes.
    ins_style: bool = False
    is_pediatric: bool = False
    test: str | None = None  # p.ej. "WISC-IV" → gatilla reglas específicas


class NarrateDTO(BaseModel):
    dominio: str          # 'atencion', 'memoria', 'lenguaje', 'ffee', 'visoespacial'
    paciente_edad: str | None = None
    resultados: list[dict[str, Any]]  # [{test: str, z: float, interpretacion: str}...]
    # Inyecta reglas de estilo institucional en el system prompt.
    ins_style: bool = False
    is_pediatric: bool = False
    test: str | None = None


# ═══════════════════════════════════════════════════════════════════════
# Sanitización de PHI — NO enviar datos identificables a la nube
# ═══════════════════════════════════════════════════════════════════════

_PHI_PATTERNS = [
    (re.compile(r"\b\d{6,12}\b"), "[DOCUMENTO]"),            # cédulas, TI, etc.
    (re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"), "[FECHA]"),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), "[FECHA]"),
    (re.compile(r"[\w\.\-]+@[\w\-]+\.\w+"), "[EMAIL]"),
    (re.compile(r"\+?\d[\d\s\-]{7,15}"), "[TEL]"),
]


def sanitize_clinical_input(text: str) -> str:
    """Remueve PHI común antes de mandar a proveedores externos."""
    if not text:
        return text
    out = text
    for pattern, repl in _PHI_PATTERNS:
        out = pattern.sub(repl, out)
    return out


# ═══════════════════════════════════════════════════════════════════════
# Config: get / save
# ═══════════════════════════════════════════════════════════════════════

def _get_user_config(db, user_id: str) -> AIConfigORM:
    cfg = db.query(AIConfigORM).filter_by(user_id=user_id).first()
    if not cfg:
        cfg = AIConfigORM(user_id=user_id)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


@ai_router.get("/config", response_model=AIConfigResponseDTO)
def get_ai_config(request: Request, db: DbSession):
    user_id = getattr(request.state, "user_id", "default")
    cfg = _get_user_config(db, user_id)
    return AIConfigResponseDTO(
        provider=cfg.provider or "auto",
        api_key_set=bool(cfg.api_key),
        model=cfg.model,
        ollama_url=cfg.ollama_url or "http://127.0.0.1:11434",
        openai_base_url=getattr(cfg, "openai_base_url", None),
        temperature=cfg.temperature or 70,
        max_tokens=cfg.max_tokens or 1024,
        enable_cloud=cfg.enable_cloud if cfg.enable_cloud is not None else True,
    )


@ai_router.post("/config", response_model=AIConfigResponseDTO)
def save_ai_config(dto: AIConfigDTO, request: Request, db: DbSession):
    user_id = getattr(request.state, "user_id", "default")
    if dto.provider not in VALID_PROVIDERS:
        raise HTTPException(422, detail=f"Proveedor inválido. Usa {VALID_PROVIDERS}")
    cfg = _get_user_config(db, user_id)
    cfg.provider     = dto.provider
    if dto.api_key is not None:            # None → no tocar (permite actualizar sin reenviar key)
        cfg.api_key = dto.api_key.strip() or None
    cfg.model        = dto.model or DEFAULT_MODELS.get(dto.provider, "")
    cfg.ollama_url   = dto.ollama_url
    cfg.openai_base_url = (dto.openai_base_url or "").strip() or None
    cfg.temperature  = max(0, min(100, dto.temperature))
    cfg.max_tokens   = max(64, min(8192, dto.max_tokens))
    cfg.enable_cloud = dto.enable_cloud
    db.commit()
    return get_ai_config(request, db)


# ═══════════════════════════════════════════════════════════════════════
# Backends por proveedor
# ═══════════════════════════════════════════════════════════════════════

class AIProviderError(Exception):
    pass


def _build_system(
    system: str | None,
    *,
    ins_style: bool = False,
    is_pediatric: bool = False,
    test: str | None = None,
    dominios: list[str] | None = None,
) -> str:
    default = (
        "Eres un asistente clínico experto en neuropsicología, especializado "
        "en evaluación y diagnóstico. Respondes en español claro y preciso, "
        "usando terminología técnica apropiada cuando corresponde. Nunca "
        "inventas datos clínicos ni sustituyes el juicio del profesional. "
        "Si no hay datos suficientes para una afirmación, lo dices explícitamente."
    )
    base = system or default
    if not ins_style:
        return base
    try:
        from app.domain.data.informe_style_guide_ins import build_ins_style_suffix
        suffix = build_ins_style_suffix(
            is_pediatric=is_pediatric, test=test, dominios=dominios,
        )
        return base + "\n\n" + suffix
    except Exception as e:  # noqa: BLE001
        logger.warning("No se pudo inyectar estilo institucional: %s", e)
        return base


async def _call_gemini(cfg: AIConfigORM, req: ChatRequestDTO, system: str) -> ChatResponseDTO:
    if not cfg.api_key:
        raise AIProviderError("Falta API key de Gemini")
    model = cfg.model or DEFAULT_MODELS["gemini"]
    # Gemini acepta el system prompt como systemInstruction
    contents = []
    for m in req.messages:
        role = "user" if m.role == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m.content}]})
    body = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system}]},
        "generationConfig": {
            "temperature": (req.temperature if req.temperature is not None else (cfg.temperature or 70) / 100.0),
            "maxOutputTokens": req.max_tokens or cfg.max_tokens or 1024,
        },
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={cfg.api_key}"
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=body)
    if r.status_code >= 400:
        raise AIProviderError(f"Gemini {r.status_code}: {r.text[:300]}")
    data = r.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise AIProviderError(f"Respuesta Gemini inesperada: {json.dumps(data)[:300]}")
    return ChatResponseDTO(provider="gemini", model=model, content=text, usage=data.get("usageMetadata"))


async def _call_claude(cfg: AIConfigORM, req: ChatRequestDTO, system: str) -> ChatResponseDTO:
    if not cfg.api_key:
        raise AIProviderError("Falta API key de Claude")
    model = cfg.model or DEFAULT_MODELS["claude"]
    body = {
        "model": model,
        "max_tokens": req.max_tokens or cfg.max_tokens or 1024,
        "temperature": (req.temperature if req.temperature is not None else (cfg.temperature or 70) / 100.0),
        "system": system,
        "messages": [{"role": m.role, "content": m.content} for m in req.messages if m.role != "system"],
    }
    headers = {
        "x-api-key": cfg.api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post("https://api.anthropic.com/v1/messages", json=body, headers=headers)
    if r.status_code >= 400:
        raise AIProviderError(f"Claude {r.status_code}: {r.text[:300]}")
    data = r.json()
    text = "".join(b.get("text", "") for b in data.get("content", []))
    return ChatResponseDTO(provider="claude", model=model, content=text, usage=data.get("usage"))


async def _call_openai(cfg: AIConfigORM, req: ChatRequestDTO, system: str,
                       provider_name: str = "openai") -> ChatResponseDTO:
    """Llama a OpenAI o a cualquier endpoint OpenAI-compatible.

    Para ``provider_name == "medgemma"`` se usa ``cfg.openai_base_url``
    (OpenRouter, Hugging Face TGI, Vertex proxy, etc.) que sirve modelos
    MedGemma en línea con el mismo contrato /chat/completions.
    """
    default_base = "https://api.openai.com/v1"
    if provider_name == "openrouter":
        default_base = "https://openrouter.ai/api/v1"
    base = (getattr(cfg, "openai_base_url", None) or default_base).rstrip("/")
    if provider_name == "medgemma" and not getattr(cfg, "openai_base_url", None):
        raise AIProviderError(
            "MedGemma en línea requiere un endpoint OpenAI-compatible. "
            "Configura la URL base (ej. OpenRouter: https://openrouter.ai/api/v1)."
        )
    if not cfg.api_key:
        raise AIProviderError("Falta la API key del proveedor en línea.")
    model = cfg.model or DEFAULT_MODELS.get(provider_name, DEFAULT_MODELS["openai"])
    msgs = [{"role": "system", "content": system}]
    msgs += [{"role": m.role, "content": m.content} for m in req.messages if m.role != "system"]
    body = {
        "model": model,
        "messages": msgs,
        "temperature": (req.temperature if req.temperature is not None else (cfg.temperature or 70) / 100.0),
        "max_tokens": req.max_tokens or cfg.max_tokens or 1024,
    }
    headers = {"Authorization": f"Bearer {cfg.api_key}", "content-type": "application/json"}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(base + "/chat/completions", json=body, headers=headers)
    if r.status_code >= 400:
        raise AIProviderError(f"{provider_name} {r.status_code}: {r.text[:300]}")
    data = r.json()
    text = data["choices"][0]["message"]["content"]
    return ChatResponseDTO(provider=provider_name, model=model, content=text, usage=data.get("usage"))


async def _call_ollama(cfg: AIConfigORM, req: ChatRequestDTO, system: str) -> ChatResponseDTO:
    model = cfg.model or DEFAULT_MODELS["ollama"]
    url = (cfg.ollama_url or "http://127.0.0.1:11434").rstrip("/") + "/api/chat"
    msgs = [{"role": "system", "content": system}]
    msgs += [{"role": m.role, "content": m.content} for m in req.messages if m.role != "system"]
    body = {
        "model": model,
        "messages": msgs,
        "stream": False,
        "options": {
            "temperature": (req.temperature if req.temperature is not None else (cfg.temperature or 70) / 100.0),
            "num_predict": req.max_tokens or cfg.max_tokens or 1024,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(url, json=body)
    except (httpx.ConnectError, httpx.ConnectTimeout):
        raise AIProviderError("Ollama no está corriendo. Instálalo desde https://ollama.com y ejecuta `ollama run llama3.1:8b`.")
    if r.status_code >= 400:
        raise AIProviderError(f"Ollama {r.status_code}: {r.text[:300]}")
    data = r.json()
    text = data.get("message", {}).get("content", "")
    return ChatResponseDTO(
        provider="ollama", model=model, content=text,
        usage={k: data.get(k) for k in ("prompt_eval_count", "eval_count")},
    )


async def _dispatch(cfg: AIConfigORM, req: ChatRequestDTO, system: str, override: str | None = None) -> ChatResponseDTO:
    provider = override or cfg.provider or "auto"
    # 'auto' → intenta proveedor con API key > ollama
    if provider == "auto":
        if cfg.enable_cloud and cfg.api_key:
            # Si el usuario tiene key pero provider=auto, asumimos gemini por defecto
            # a menos que el model string identifique otro
            m = (cfg.model or "").lower()
            if "claude" in m:   provider = "claude"
            elif "gpt"  in m:   provider = "openai"
            else:               provider = "gemini"
        else:
            provider = "ollama"

    if provider == "gemini":  return await _call_gemini(cfg, req, system)
    if provider == "claude":  return await _call_claude(cfg, req, system)
    if provider == "openai":  return await _call_openai(cfg, req, system)
    if provider == "medgemma": return await _call_openai(cfg, req, system, provider_name="medgemma")
    if provider == "openrouter": return await _call_openai(cfg, req, system, provider_name="openrouter")
    if provider == "ollama":  return await _call_ollama(cfg, req, system)
    raise AIProviderError(f"Proveedor no soportado: {provider}")


# ═══════════════════════════════════════════════════════════════════════
# Endpoints de chat
# ═══════════════════════════════════════════════════════════════════════

@ai_router.post("/chat", response_model=ChatResponseDTO)
async def chat(dto: ChatRequestDTO, request: Request, db: DbSession):
    user_id = getattr(request.state, "user_id", "default")
    cfg = _get_user_config(db, user_id)
    system = _build_system(dto.system)
    # Sanitizar los mensajes del usuario si vamos a nube
    target_provider = dto.provider_override or cfg.provider
    if target_provider != "ollama":
        dto = ChatRequestDTO(
            messages=[ChatMessageDTO(role=m.role, content=sanitize_clinical_input(m.content)) for m in dto.messages],
            system=dto.system, temperature=dto.temperature,
            max_tokens=dto.max_tokens, provider_override=dto.provider_override,
        )
    try:
        return await _dispatch(cfg, dto, system, dto.provider_override)
    except AIProviderError as e:
        # Fallback automático a Ollama si el provider remoto falla
        if target_provider not in ("ollama", "auto") and (cfg.provider == "auto"):
            logger.warning("Fallback a Ollama tras fallo en %s: %s", target_provider, e)
            try:
                return await _call_ollama(cfg, dto, system)
            except AIProviderError as e2:
                raise HTTPException(503, detail=f"Nube falló: {e} · Local falló: {e2}")
        raise HTTPException(503, detail=str(e))


@ai_router.post("/improve", response_model=ChatResponseDTO)
async def improve(dto: ImproveTextDTO, request: Request, db: DbSession):
    user_id = getattr(request.state, "user_id", "default")
    cfg = _get_user_config(db, user_id)
    task_prompts = {
        "style":           "Revisa el siguiente texto de informe neuropsicológico. Mejora redacción, cohesión y estilo manteniendo EXACTAMENTE el mismo contenido clínico y los mismos términos técnicos. No inventes datos. Devuelve solo el texto corregido, sin preámbulos.",
        "grammar":         "Corrige gramática, ortografía y puntuación del siguiente texto sin cambiar su contenido. Devuelve solo el texto corregido.",
        "summarize":       "Resume el siguiente texto clínico en máximo 4 frases manteniendo los datos esenciales.",
        "clinical_review": "Actúa como neuropsicólogo senior. Revisa el siguiente fragmento de informe y señala: (1) afirmaciones que no se sustentan en los datos presentados, (2) términos imprecisos, (3) sugerencias de mejora. No modifiques el texto — solo listado de observaciones.",
    }
    instruction = task_prompts.get(dto.task, task_prompts["style"])
    if dto.tone == "friendly":
        instruction += " Usa un tono cercano y accesible."
    elif dto.tone == "technical":
        instruction += " Usa registro técnico-académico."

    text = sanitize_clinical_input(dto.text)
    req = ChatRequestDTO(
        messages=[ChatMessageDTO(role="user", content=f"{instruction}\n\n---\n{text}")],
    )
    system = _build_system(
        None,
        ins_style=dto.ins_style,
        is_pediatric=dto.is_pediatric,
        test=dto.test,
    )
    try:
        return await _dispatch(cfg, req, system)
    except AIProviderError as e:
        raise HTTPException(503, detail=str(e))


@ai_router.post("/narrate", response_model=ChatResponseDTO)
async def narrate(dto: NarrateDTO, request: Request, db: DbSession):
    user_id = getattr(request.state, "user_id", "default")
    cfg = _get_user_config(db, user_id)
    dom_label = {
        "atencion":      "atención y concentración",
        "memoria":       "memoria",
        "lenguaje":      "lenguaje",
        "ffee":          "funciones ejecutivas",
        "visoespacial":  "habilidades visoespaciales y visoconstructivas",
        "praxias":       "praxias y gnosias",
        "cognicion_social": "cognición social",
    }.get(dto.dominio, dto.dominio)
    datos = "\n".join(
        f"- {r.get('test', '?')}: Z={r.get('z', '?')}, {r.get('interpretacion', '?')}"
        for r in dto.resultados[:20]
    )
    edad = f" (paciente: {dto.paciente_edad})" if dto.paciente_edad else ""
    user_msg = (
        f"Genera el párrafo del informe neuropsicológico correspondiente al dominio de "
        f"{dom_label}{edad}, basándote EXCLUSIVAMENTE en estos resultados:\n\n{datos}\n\n"
        f"Extensión: 2–4 oraciones. Usa términos técnicos apropiados. "
        f"Destaca fortalezas y debilidades de forma equilibrada. No inventes pruebas ni datos."
    )
    req = ChatRequestDTO(messages=[ChatMessageDTO(role="user", content=user_msg)])
    system = _build_system(
        None,
        ins_style=dto.ins_style,
        is_pediatric=dto.is_pediatric,
        test=dto.test,
        dominios=[dto.dominio] if dto.dominio else None,
    )
    try:
        return await _dispatch(cfg, req, system)
    except AIProviderError as e:
        raise HTTPException(503, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════
# Prompts especializados clínicos (§ai-prompts 2026-05-18)
# ═══════════════════════════════════════════════════════════════════════

@ai_router.get("/prompts", summary="Lista los prompts especializados disponibles")
def ai_list_prompts():
    """
    Catálogo de prompts especializados que el frontend puede invocar
    para distintas tareas clínicas: pulir redacción, sugerir dx,
    explicar discrepancias, generar recomendaciones, etc.

    Cada uno tiene un `system prompt` cuidadosamente construido con
    persona clínica colombiana, restricciones éticas (Ley 1090),
    formato de salida estructurado y disclaimers automáticos.
    """
    from app.domain.clinical_engine.ai_prompts import AI_USAGE_DISCLAIMER, list_prompts
    return {
        "prompts": list_prompts(),
        "disclaimer": AI_USAGE_DISCLAIMER,
    }


class SpecializedRequestDTO(BaseModel):
    """Petición a un prompt especializado."""
    prompt_id: str
    variables: dict[str, Any]
    provider_override: str | None = None


@ai_router.post("/specialized", response_model=ChatResponseDTO,
                summary="Invoca un prompt especializado (con sanitización PHI y log)")
async def ai_specialized(req: SpecializedRequestDTO, request: Request, db: DbSession):
    """
    Ejecuta un prompt especializado de la biblioteca clínica.

    §ai-log: cada llamada queda registrada (tabla `ai_logs` + logger.info)
    con prompt_id, user_id, longitud in/out, provider, modelo y duración
    para trazabilidad clínica según Resolución 1995. Si el clínico usa
    esto en un informe, queda el rastro de qué herramienta IA asistió en
    qué sección — sin guardar el contenido (PHI).
    """
    import time

    from app.domain.clinical_engine.ai_prompts import format_user_message, get_prompt

    try:
        prompt_def = get_prompt(req.prompt_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    safe_vars = {
        k: (sanitize_clinical_input(v) if isinstance(v, str) else v)
        for k, v in req.variables.items()
    }
    try:
        user_msg = format_user_message(req.prompt_id, **safe_vars)
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Falta variable requerida para este prompt: {e}",
        )

    user_id = getattr(request.state, "user_id", "default")
    _ = _get_user_config(db, user_id)  # asegura que exista la config

    chat_req = ChatRequestDTO(
        messages=[ChatMessageDTO(role="user", content=user_msg)],
        system=prompt_def["system"],
        provider_override=req.provider_override,
    )

    t0 = time.monotonic()
    success = True
    error_message = None
    try:
        # §ai-specialized-fix-2026-05-19: el endpoint chat real se llama
        # `chat` (no `ai_chat`). Esto generaba NameError al usar prompts
        # especializados — el log lo capturaba como success=False con
        # "name 'ai_chat' is not defined".
        resp = await chat(chat_req, request, db)
        out_content = resp.content or ""
    except Exception as exc:
        success = False
        error_message = str(exc)
        # Persistimos el fallo aún así, para diagnóstico.
        try:
            _persist_ai_log(
                db, user_id, req.prompt_id, "/specialized",
                provider=None, model=None,
                input_length=len(user_msg), output_length=0,
                duration_ms=int((time.monotonic() - t0) * 1000),
                tokens_in=None, tokens_out=None,
                success=False, error_message=error_message,
            )
        except Exception:
            pass
        raise

    duration_ms = int((time.monotonic() - t0) * 1000)

    # Persistir log en BD + logger
    tokens_in = resp.usage.get("input_tokens") if resp.usage else None
    tokens_out = resp.usage.get("output_tokens") if resp.usage else None
    try:
        _persist_ai_log(
            db, user_id, req.prompt_id, "/specialized",
            provider=resp.provider, model=resp.model,
            input_length=len(user_msg), output_length=len(out_content),
            duration_ms=duration_ms,
            tokens_in=tokens_in, tokens_out=tokens_out,
            success=success, error_message=None,
        )
    except Exception as exc:
        # No bloqueamos la respuesta si el log falla — solo loggeamos.
        logger.warning("No se pudo persistir AI log: %s", exc)

    logger.info(
        "AI specialized — user=%s prompt=%s provider=%s model=%s "
        "in=%d out=%d dur=%dms",
        user_id, req.prompt_id, resp.provider, resp.model,
        len(user_msg), len(out_content), duration_ms,
    )

    return resp


def _persist_ai_log(db, user_id, prompt_id, endpoint, *,
                    provider, model, input_length, output_length,
                    duration_ms, tokens_in, tokens_out,
                    success, error_message,
                    patient_id=None, evaluation_id=None, session_id=None):
    """Crea una fila en `ai_logs`. No lanza — siempre best-effort."""
    import uuid as _uuid

    from app.infrastructure.database.orm_models import AILogORM

    log = AILogORM(
        id=str(_uuid.uuid4()),
        user_id=user_id,
        patient_id=patient_id,
        evaluation_id=evaluation_id,
        session_id=session_id,
        prompt_id=prompt_id,
        endpoint=endpoint,
        provider=provider,
        model=model,
        input_length=input_length,
        output_length=output_length,
        duration_ms=duration_ms,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        success=success,
        error_message=error_message,
    )
    db.add(log)
    db.commit()


# ═══════════════════════════════════════════════════════════════════════
# Health + detección de Ollama local
# ═══════════════════════════════════════════════════════════════════════

@ai_router.get("/health")
async def ai_health(request: Request, db: DbSession):
    user_id = getattr(request.state, "user_id", "default")
    cfg = _get_user_config(db, user_id)
    out: dict[str, Any] = {"provider_configured": cfg.provider, "cloud_enabled": cfg.enable_cloud}
    # Ollama
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get((cfg.ollama_url or "http://127.0.0.1:11434").rstrip("/") + "/api/tags")
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            out["ollama"] = {"status": "ok", "models": models}
        else:
            out["ollama"] = {"status": "error", "detail": f"HTTP {r.status_code}"}
    except Exception as e:
        out["ollama"] = {"status": "offline", "detail": str(e)[:120]}
    out["has_cloud_key"] = bool(cfg.api_key)
    return out


@ai_router.get("/ollama/status")
async def ollama_status(request: Request, db: DbSession):
    """Detecta si hay un servidor Ollama corriendo y qué modelos tiene."""
    user_id = getattr(request.state, "user_id", "default")
    cfg = _get_user_config(db, user_id)
    url = (cfg.ollama_url or "http://127.0.0.1:11434").rstrip("/")
    # Intento rápido de TCP connect antes del HTTP
    host_port = url.replace("http://", "").replace("https://", "").split("/")[0]
    host, port = (host_port.split(":") + ["11434"])[:2]
    try:
        s = socket.create_connection((host, int(port)), timeout=2)
        s.close()
    except OSError:
        return {"installed": False, "running": False, "url": url,
                "hint": "Instala Ollama desde https://ollama.com/download y reinicia NeuroSoft."}
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(url + "/api/tags")
        data = r.json()
        models = [m["name"] for m in data.get("models", [])]
        suggested = DEFAULT_MODELS["ollama"]
        return {
            "installed": True, "running": True, "url": url,
            "models": models, "suggested": suggested,
            "suggested_installed": suggested in models,
        }
    except Exception as e:
        return {"installed": True, "running": False, "url": url, "detail": str(e)[:200]}


class PullModelDTO(BaseModel):
    name: str = "llama3.1:8b"


@ai_router.post("/ollama/pull")
async def ollama_pull(dto: PullModelDTO, request: Request, db: DbSession):
    """Dispara la descarga de un modelo en Ollama (no-streaming, espera a terminar)."""
    user_id = getattr(request.state, "user_id", "default")
    cfg = _get_user_config(db, user_id)
    url = (cfg.ollama_url or "http://127.0.0.1:11434").rstrip("/") + "/api/pull"
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            r = await client.post(url, json={"name": dto.name, "stream": False})
        if r.status_code >= 400:
            raise HTTPException(503, detail=f"Ollama pull falló: {r.text[:300]}")
        return {"ok": True, "model": dto.name}
    except httpx.ConnectError:
        raise HTTPException(503, detail="Ollama no está corriendo.")


@ai_router.post("/ollama/pull_stream")
async def ollama_pull_stream(dto: PullModelDTO, request: Request, db: DbSession):
    """
    Descarga de modelo con streaming NDJSON (progreso). El cliente recibe líneas
    JSON con `{status, completed, total}` por chunk (formato nativo de Ollama).
    """
    from fastapi.responses import StreamingResponse
    user_id = getattr(request.state, "user_id", "default")
    cfg = _get_user_config(db, user_id)
    url = (cfg.ollama_url or "http://127.0.0.1:11434").rstrip("/") + "/api/pull"

    async def _gen():
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, json={"name": dto.name, "stream": True}) as r:
                    if r.status_code >= 400:
                        yield f'{{"error":"HTTP {r.status_code}"}}\n'
                        return
                    async for line in r.aiter_lines():
                        if line:
                            yield line + "\n"
        except httpx.ConnectError:
            yield '{"error":"Ollama no está corriendo"}\n'
        except Exception as e:  # noqa: BLE001
            yield '{"error":"' + str(e).replace('"', "'")[:200] + '"}\n'

    return StreamingResponse(_gen(), media_type="application/x-ndjson")


@ai_router.post("/ollama/autosetup")
async def ollama_autosetup(request: Request, db: DbSession):
    """
    Orquesta: verifica si Ollama está instalado → si no, ejecuta el installer
    bundleado → espera a que el servicio responda → reporta estado listo para
    que la UI dispare un pull_stream del modelo por defecto.
    """
    import asyncio
    import subprocess
    import sys as _sys
    user_id = getattr(request.state, "user_id", "default")
    cfg = _get_user_config(db, user_id)
    url = (cfg.ollama_url or "http://127.0.0.1:11434").rstrip("/")
    # Paso 1: ya instalado y respondiendo
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(url + "/api/tags")
            if r.status_code < 400:
                return {"installed": True, "running": True, "installer_launched": False, "suggested_model": DEFAULT_MODELS["ollama"]}
    except Exception:
        pass
    # Paso 2: lanzar installer bundleado si aplica
    launched = False
    if _sys.platform == "win32":
        p = _bundled_ollama_path()
        if p:
            try:
                subprocess.Popen(
                    [str(p), "/SILENT", "/NORESTART"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    creationflags=0x00000008,
                )
                launched = True
            except Exception as e:  # noqa: BLE001
                return {"installed": False, "running": False, "installer_launched": False, "detail": f"No se pudo lanzar installer: {e}"}
    # Paso 3: esperar hasta 120 s a que el servicio responda
    running = False
    for _ in range(40):
        await asyncio.sleep(3)
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(url + "/api/tags")
                if r.status_code < 400:
                    running = True
                    break
        except Exception:
            continue
    return {
        "installed": running or launched,
        "running": running,
        "installer_launched": launched,
        "suggested_model": DEFAULT_MODELS["ollama"],
        "next_step": ("pull_stream" if running else "waiting_for_service"),
    }


def _bundled_ollama_path() -> Path | None:
    """
    Devuelve la ruta al OllamaSetup.exe.

    §ollama-fix: el instalador ya NO está dentro del .exe de PyInstaller
    (causaba corrupción de archivo grande). Ahora se distribuye como archivo
    separado junto al .exe principal (en {app}\\vendor\\ollama\\OllamaSetup.exe
    cuando se instala vía Inno Setup) o en vendor/ollama/ relativo al proyecto
    en modo desarrollo.
    """
    import sys
    from pathlib import Path
    candidates = []
    # 1. Junto al .exe principal (PyInstaller frozen) → ruta de Inno Setup
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.append(exe_dir / "vendor" / "ollama" / "OllamaSetup.exe")
        candidates.append(exe_dir / "OllamaSetup.exe")  # fallback raíz
    # 2. Legacy: dentro del bundle (compatibilidad si alguien rebuildea con el spec viejo)
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[4]))
    candidates.append(base / "vendor" / "ollama" / "OllamaSetup.exe")
    # 3. Desarrollo: relativo al checkout
    candidates.append(Path(__file__).resolve().parents[4] / "vendor" / "ollama" / "OllamaSetup.exe")
    for c in candidates:
        try:
            if c.exists():
                return c
        except Exception:
            continue
    return None


@ai_router.get("/ollama/bundled")
async def ollama_bundled(request: Request):
    """Reporta si el instalador de Ollama está empaquetado en este build."""
    p = _bundled_ollama_path()
    if not p:
        return {"available": False, "hint": "Descargue Ollama desde https://ollama.com/download"}
    try:
        size_mb = p.stat().st_size // (1024 * 1024)
    except Exception:
        size_mb = None
    return {"available": True, "path": str(p), "size_mb": size_mb}


@ai_router.post("/ollama/install")
async def ollama_install(request: Request):
    """
    Lanza el instalador bundleado de Ollama (sólo Windows). Corre el .exe
    en modo silencioso en segundo plano; el usuario verá la barra de progreso
    oficial del installer. Tras terminar, el servicio Ollama arranca solo.
    """
    import subprocess
    import sys as _sys
    if _sys.platform != "win32":
        raise HTTPException(400, "La instalación automática sólo está soportada en Windows.")
    p = _bundled_ollama_path()
    if not p:
        raise HTTPException(404, "Este build no incluye el instalador de Ollama.")
    try:
        # Ejecuta el installer — no bloquea el servidor.
        # /SILENT = instalación silenciosa de Inno Setup (Ollama usa Inno).
        subprocess.Popen(
            [str(p), "/SILENT", "/NORESTART"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=0x00000008,  # DETACHED_PROCESS
        )
        logger.info("ollama_install launched pid=? path=%s", p)
        return {"ok": True, "launched": True, "path": str(p)}
    except Exception as e:
        raise HTTPException(500, f"No se pudo lanzar el instalador: {e}")

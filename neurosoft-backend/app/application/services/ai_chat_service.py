"""Lógica de proveedores IA — extraída de ai.py para testabilidad."""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING

import httpx

from app.infrastructure.database.orm_models import AIConfigORM

if TYPE_CHECKING:
    from app.presentation.api.v1.ai import ChatRequestDTO, ChatResponseDTO

logger = logging.getLogger("neurosoft.ai")

VALID_PROVIDERS = ("auto", "gemini", "claude", "openai", "ollama", "medgemma", "openrouter")

DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash",
    "claude": "claude-haiku-4-5-20251001",
    "openai": "gpt-4.1-mini",
    "openrouter": "google/gemini-2.5-flash",
    "ollama": "llama3.1:8b",
    "medgemma": "google/medgemma-4b-it",
}

_PHI_PATTERNS = [
    (re.compile(r"\b\d{6,12}\b"), "[DOCUMENTO]"),
    (re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"), "[FECHA]"),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), "[FECHA]"),
    (re.compile(r"[\w\.\-]+@[\w\-]+\.\w+"), "[EMAIL]"),
    (re.compile(r"\+?\d[\d\s\-]{7,15}"), "[TEL]"),
]


class AIProviderError(Exception):
    pass


def sanitize_clinical_input(text: str) -> str:
    if not text:
        return text
    out = text
    for pattern, repl in _PHI_PATTERNS:
        out = pattern.sub(repl, out)
    return out


def build_system_prompt(
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

        suffix = build_ins_style_suffix(is_pediatric=is_pediatric, test=test, dominios=dominios)
        return base + "\n\n" + suffix
    except Exception as e:
        logger.warning("No se pudo inyectar estilo institucional: %s", e)
        return base


async def dispatch_chat(
    cfg: AIConfigORM,
    req: ChatRequestDTO,
    system: str,
    override: str | None = None,
) -> ChatResponseDTO:

    provider = override or cfg.provider or "auto"
    if provider == "auto":
        if cfg.enable_cloud and cfg.api_key:
            m = (cfg.model or "").lower()
            if "claude" in m:
                provider = "claude"
            elif "gpt" in m:
                provider = "openai"
            else:
                provider = "gemini"
        else:
            provider = "ollama"

    if provider == "gemini":
        return await _call_gemini(cfg, req, system)
    if provider == "claude":
        return await _call_claude(cfg, req, system)
    if provider == "openai":
        return await _call_openai(cfg, req, system)
    if provider == "medgemma":
        return await _call_openai(cfg, req, system, provider_name="medgemma")
    if provider == "openrouter":
        return await _call_openai(cfg, req, system, provider_name="openrouter")
    if provider == "ollama":
        return await _call_ollama(cfg, req, system)
    raise AIProviderError(f"Proveedor no soportado: {provider}")


async def _call_gemini(cfg: AIConfigORM, req: ChatRequestDTO, system: str) -> ChatResponseDTO:
    from app.presentation.api.v1.ai import ChatResponseDTO

    if not cfg.api_key:
        raise AIProviderError("Falta API key de Gemini")
    model = cfg.model or DEFAULT_MODELS["gemini"]
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
    from app.presentation.api.v1.ai import ChatResponseDTO

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


async def _call_openai(
    cfg: AIConfigORM, req: ChatRequestDTO, system: str, provider_name: str = "openai"
) -> ChatResponseDTO:
    from app.presentation.api.v1.ai import ChatResponseDTO

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
    from app.presentation.api.v1.ai import ChatResponseDTO

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
        raise AIProviderError(
            "Ollama no está corriendo. Instálalo desde https://ollama.com y ejecuta `ollama run llama3.1:8b`."
        )
    if r.status_code >= 400:
        raise AIProviderError(f"Ollama {r.status_code}: {r.text[:300]}")
    data = r.json()
    text = data.get("message", {}).get("content", "")
    return ChatResponseDTO(
        provider="ollama",
        model=model,
        content=text,
        usage={k: data.get(k) for k in ("prompt_eval_count", "eval_count")},
    )


def persist_ai_log(db, user_id, prompt_id, endpoint, **kwargs) -> None:
    import uuid as _uuid

    from app.infrastructure.database.orm_models import AILogORM

    log = AILogORM(
        id=str(_uuid.uuid4()),
        user_id=user_id,
        patient_id=kwargs.get("patient_id"),
        evaluation_id=kwargs.get("evaluation_id"),
        session_id=kwargs.get("session_id"),
        prompt_id=prompt_id,
        endpoint=endpoint,
        provider=kwargs.get("provider"),
        model=kwargs.get("model"),
        input_length=kwargs.get("input_length"),
        output_length=kwargs.get("output_length"),
        duration_ms=kwargs.get("duration_ms"),
        tokens_in=kwargs.get("tokens_in"),
        tokens_out=kwargs.get("tokens_out"),
        success=kwargs.get("success"),
        error_message=kwargs.get("error_message"),
    )
    db.add(log)
    db.commit()

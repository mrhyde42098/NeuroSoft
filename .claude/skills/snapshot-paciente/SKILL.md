---
name: snapshot-paciente
description: Toma un paciente de la BD de NeuroSoft (o lo construye desde un caso documentado) y genera un fixture JSON para tests de regresión clínica. Cada bug clínico corregido debe poder reproducirse con un fixture así. Usar cuando se quiera congelar un caso clínico (real anonimizado o sintético) como caso de prueba permanente.
---

# Snapshot de caso clínico para tests

Genera fixtures de tests de regresión basados en casos clínicos reales (anonimizados) o sintéticos. Estos fixtures protegen contra regresiones futuras del motor de baremos.

## Cuándo activarte

Usuario escribió:
- `/snapshot-paciente <patient_id>` — toma uno de la BD local
- `/snapshot-paciente sintetico <descripción>` — construye uno sintético
- `/snapshot-paciente caso-jesus-viloria` — los casos canónicos del CLAUDE.md backend

## Protocolo

### Paso 1: Localizar el caso

**Si patient_id**: consultar la BD local de SQLite:
```bash
cd D:\NeuroSoftApp\neurosoft-backend
sqlite3 "%APPDATA%/NeuroSoft/neurosoft.db" "SELECT id, primer_nombre, primer_apellido, fecha_nacimiento, sexo, escolaridad FROM patients WHERE id='<id>'"
```

**Si caso canónico**: leer de `neurosoft-backend/CLAUDE.md` (sección "Casos clínicos verificados"). Hay 2 documentados:
- Caso 1: Andrés Felipe Romero Castaño (16a 11m, M, Sec. Inc.) — WISC-IV
- Caso 2: María Elena Cardona Restrepo (80a 5m, F, Prim. Inc.) — Neuronorma AM
- Casos 3-17: ver `docs/casos-clinicos/CASOS_GROUND_TRUTH.md` (15 casos
  inventados con contexto colombiano, validables vía MCP baremos).

**Si sintético**: construir basado en la descripción del usuario.

### Paso 2: ANONIMIZAR (obligatorio para casos reales)

NUNCA guardar en el fixture:
- Nombre real completo
- Documento de identidad real
- Fecha de nacimiento exacta (usar solo edad y meses)
- Dirección, teléfono, email

Sustituir por:
- `patient_id`: hash SHA-256[:8] del ID original (no reversible)
- `nombre_completo`: `"Paciente Caso N"` o similar
- `fecha_nacimiento`: calcular desde edad actual + fecha sintética
- Documento: `"00000000"` (placeholder)

### Paso 3: Estructurar el fixture

Formato JSON estándar:

```json
{
  "$schema": "fixture-paciente-v1",
  "_meta": {
    "fuente": "anonimizado_de_<patient_hash> | sintetico | caso_canonico_CLAUDE_md",
    "creado_en": "2026-05-15",
    "descripcion": "Adolescente con perfil WISC-IV completo — verifica cálculo ICV/IRP/IMT/IVP/CIT",
    "tests_que_protege": ["tests/unit/clinical_engine/test_wisc_iv_caso_1.py"]
  },
  "demograficos": {
    "edad_anos": 16,
    "edad_meses": 11,
    "sexo": "M",
    "escolaridad": "Secundaria Incompleta",
    "lateralidad": "Diestro",
    "poblacion_esperada": "adulto_joven"
  },
  "puntajes": {
    "NiWiscDC": 53,
    "NiWiscSem": 32,
    "NiWiscVoc": 37,
    "NiWiscLN": 25,
    "NiWiscCl": 46,
    "NiWiscAri": 21
  },
  "indices_compuestos": {
    "NiWISCIndComVer": {"suma_escalares": 26},
    "NiWISCIndRazPer": {"suma_escalares": 29},
    "NiWISCIndMemTra": {"suma_escalares": 15},
    "NiWISCIndVelPro": {"suma_escalares": 13},
    "NiWISCTot": {"suma_total": 83}
  },
  "resultados_esperados": {
    "NiWiscDC": {"escalar": 11, "interpretacion": "Bajo"},
    "NiWiscSem": {"escalar": 11, "interpretacion": "Bajo"},
    "NiWiscVoc": {"escalar": 6, "interpretacion": "Bajo"},
    "NiWiscLN": {"escalar": 16, "interpretacion": "Bajo"},
    "NiWiscCl": {"escalar": 4, "interpretacion": "Bajo"},
    "NiWiscAri": {"escalar": 6, "interpretacion": "Bajo"},
    "NiWISCIndComVer": {"ci": 93, "interpretacion": "Promedio"},
    "NiWISCIndRazPer": {"ci": 98, "interpretacion": "Promedio"},
    "NiWISCIndMemTra": {"ci": 86, "interpretacion": "Promedio"},
    "NiWISCIndVelPro": {"ci": 80, "interpretacion": "Promedio"},
    "NiWISCTot": {"ci": 87, "interpretacion": "Promedio"}
  }
}
```

### Paso 4: Guardar y registrar

Guardar en `D:\NeuroSoftApp\neurosoft-backend\tests\fixtures\<slug-descripcion>.json`.

Si no existe ya un test que use este fixture, ofrecer al usuario:
> "¿Genero también `tests/unit/clinical_engine/test_<slug>.py` que cargue este fixture y verifique los `resultados_esperados`?"

### Paso 5: Estructura del test sugerida

```python
"""tests/unit/clinical_engine/test_<slug>.py — regression test caso <descripción>"""
import json
import pytest
from pathlib import Path
from app.domain.clinical_engine.engine import ClinicalEngine
from app.domain.clinical_engine.baremos_loader import BaremosLoader

FIXTURE = Path(__file__).parent.parent.parent / 'fixtures' / '<slug>.json'

@pytest.mark.unit
def test_caso_<slug>():
    with open(FIXTURE, encoding='utf-8') as f:
        case = json.load(f)
    engine = ClinicalEngine(BaremosLoader.instance())
    result = engine.score(
        puntajes=case['puntajes'],
        ctx=...  # construir PatientContext desde case['demograficos']
    )
    for test_id, expected in case['resultados_esperados'].items():
        actual = next((r for r in result.resultados if r.test_id == test_id), None)
        assert actual is not None, f"Resultado faltante: {test_id}"
        if 'escalar' in expected:
            assert actual.puntaje_escalar == expected['escalar']
        if 'ci' in expected:
            assert actual.puntaje_escalar == expected['ci']
        if 'interpretacion' in expected:
            assert expected['interpretacion'].lower() in actual.interpretacion.lower()
```

## Reglas

1. **NUNCA datos PII** — siempre anonimizar antes de guardar fixture
2. **Resultados esperados verificados manualmente** — si no estás 100% seguro de un escalar, marcar como `"escalar": null` y dejar TODO en el _meta
3. **Un fixture = un caso clínico canónico** — no mezclar pruebas de diferentes pacientes
4. **Naming convention**: `<bateria>_caso_<descripcion-corta>.json` (ej. `wisc_iv_caso_1.json`, `neuronorma_am_caso_2.json`)

## Outputs

Al terminar reporta:
- Ruta del fixture creado
- Si se generó test asociado o no
- Comando para correr el test: `pytest tests/unit/clinical_engine/test_<slug>.py -v`

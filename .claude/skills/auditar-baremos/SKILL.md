---
name: auditar-baremos
description: Audita los baremos de NeuroSoft (BD_NEURO_MAESTRA.json) comparando con literatura reciente. Verifica que las normas usadas para una prueba específica coincidan con las publicadas para población colombiana o latinoamericana. Usar cuando el usuario dude de la corrección de un baremo, o quiera revisar sistemáticamente una prueba antes de validarla con un paciente real.
---

# Auditor de baremos clínicos

Eres el auditor de los datos normativos de NeuroSoft. Tu trabajo es verificar que los baremos sean correctos comparándolos con la literatura publicada.

## Cuándo activarte

Usuario escribió `/auditar-baremos <test_id>` o equivalente:
- `/auditar-baremos NiWiscDC` (Diseño con Cubos WISC-IV)
- `/auditar-baremos ViTMTA` (TMT-A Adulto Mayor)
- `/auditar-baremos BNT` (Boston Naming)

O en lenguaje natural: "audita el baremo de Stroop", "revisa si el TMT está bien para adulto mayor 80 años"

## Protocolo

### Paso 1: Identificar el test

Si el usuario dio un ID directo (`NiWiscDC`), úsalo. Si dio una descripción, mapéalo:
- "Diseño con Cubos infantil" → `NiWiscDC`
- "TMT adulto mayor" → `ViTMTA` (o `AdTMTA` si es adulto joven)
- "Stroop palabras" → buscar en `data/clinical.js` el test_id correcto

Si no encuentras el ID, lista las pruebas disponibles para que el usuario elija.

### Paso 2: Leer el baremo actual

Abre `D:\NeuroSoftApp\neurosoft-backend\data\BD_NEURO_MAESTRA.json` y busca el test. Reporta:
- `tipo_calculo` (rango_puntaje / wais_range / desconocido / z_score / etc.)
- Estratos disponibles (edades, escolaridades)
- Rango de PD válidos
- 3-5 valores muestra del baremo

### Paso 3: Buscar literatura comparativa

Usa la skill `/investigar-clinica` mentalmente (NO la invoques recursivamente, hazla directo): 1-2 búsquedas web orientadas a la prueba específica + Colombia.

### Paso 4: Casos clínicos verificados

Si el test está en `neurosoft-backend/CLAUDE.md` (Casos clínicos verificados — Caso 1 Andrés Romero, Caso 2 María Elena Cardona) o en `docs/casos-clinicos/CASOS_GROUND_TRUTH.md` (15 casos inventados colombianos), verifica que el código aún produzca esos escalares con los PD listados. Estos son la fuente de verdad.

### Paso 5: Reporte

```markdown
# 🔍 Auditoría de baremo: <nombre_prueba> (<test_id>)

## ⚙ Configuración actual
- Tipo de cálculo: ___
- Estratos: ___
- Población objetivo: ___
- Fuente original (si está documentada): ___

## 📚 Comparación con literatura

| Aspecto | NeuroSoft | Literatura | ¿Coincide? |
|---|---|---|---|
| Media PD edad 25 esc 12 | XX | YY | ✅ / ⚠ / ❌ |
| ... | ... | ... | ... |

## 🧪 Casos clínicos verificados
- Caso 1 (Andrés Romero): NiWiscDC PD=53 → escalar esperado=11 → resultado actual=___ ✅/❌
- ... (solo si el test está en los casos verificados)

## 💡 Conclusión

✅ **Baremo correcto** — coincide con literatura, mantener como está.

⚠ **Posibles ajustes** — diferencias menores; revisar antes de cambiar.

❌ **Error detectado** — discrepancia clínica significativa; NO usar hasta corregir.

## 🛠 Acciones sugeridas (si aplica)

- [ ] Consultar con Johan antes de modificar `BD_NEURO_MAESTRA.json`
- [ ] Crear test que verifique caso edge: PD=X, edad=Y → escalar=Z
- [ ] Agregar nota clínica en `neuronormaColombia.js` sobre la fuente
```

## Reglas críticas

1. **NUNCA modifiques `BD_NEURO_MAESTRA.json` automáticamente**. Solo reportar.
2. **Si encuentras un error**: marca el reporte con ❌ y notifica visualmente.
3. **Ante ambigüedad**: cita la regla de CLAUDE.md backend: "Para cambios en datos clínicos: NO modificar — consultar primero".
4. **Documenta la fuente** de cada valor literatura comparado.

## Output adicional

Al final del reporte, ofrece:
- "¿Quieres que cree un test `tests/unit/clinical_engine/test_<id>.py` que verifique este baremo?"
- "¿Genero un issue en GitHub para tracking?"

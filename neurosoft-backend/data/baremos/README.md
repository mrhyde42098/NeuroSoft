# `data/baremos/` — Baremos adicionales (Sprint 9)

Esta carpeta contiene archivos JSON con baremos **alternativos** que se
cargan EN ADICIÓN al baremo maestro `data/BD_NEURO_MAESTRA.json`.

## Formato esperado

Cada archivo debe tener la siguiente estructura:

```jsonc
{
  "_meta": {
    "fuente_id": "neuronorma_colombia",      // ID único de la fuente
    "fuente_nombre": "Neuronorma Colombia",   // Nombre legible
    "autores": "Peña-Casanova, Montañés et al.",
    "anio": 2021,
    "edad_min": 50,
    "edad_max": 90,
    "cita_bibliografica": "Peña-Casanova et al. Neurología 2021",
    "version": "1.0",
    "checksum_sha256": "..."  // opcional, autogenerado
  },
  "baterias": {
    "adulto_mayor": {
      "FCSRT": {
        "id": "FCSRT",
        "nombre": "Free and Cued Selective Reminding Task",
        "tipo_calculo": "rango_puntaje",
        "tipo_metrica": "puntaje_t",
        "baremos": {
          "50_56_anos": { ... },   // sub-grupos etarios
          "57_59_anos": { ... }
        }
      }
    }
  }
}
```

## Comportamiento del loader

1. El motor de scoring sigue usando `BD_NEURO_MAESTRA.json` como fuente
   primaria por defecto (compatibilidad clínica preservada).
2. Los archivos de esta carpeta se cargan como **overlays**: el endpoint
   `GET /api/v1/baremos/info` los lista pero **NO** los aplica
   automáticamente al scoring.
3. Para forzar el uso de una fuente alternativa, el clínico debe
   especificarla explícitamente en el payload de scoring (futura
   iteración: `POST /api/v1/scores/ {... "fuente_baremo": "neuronorma_colombia"}`).

## Archivos incluidos por defecto

- (vacío — agregue aquí los archivos JSON de fuentes adicionales)

## Recomendación

NO modifique este README ni el contenido de `BD_NEURO_MAESTRA.json`
directamente para evitar romper la trazabilidad de informes ya emitidos.
Cualquier cambio de baremos debe quedar versionado en el campo
`baremo_version` de la evaluación.

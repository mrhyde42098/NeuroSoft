# MCP Server — NeuroSoft Baremos

Servidor MCP local que expone los **186 baremos clínicos colombianos** de `BD_NEURO_MAESTRA.json` como herramientas invocables desde Claude Code.

## Para qué sirve

Cuando estás iterando con Claude Code y necesitas:
- Verificar manualmente un escalar de WISC-IV / WAIS-III / Neuronorma sin arrancar la SPA.
- Buscar una prueba por nombre o id.
- Reproducir un caso clínico ground-truth (Caso 1 Jesús, Caso 2 Blanca).
- Generar fixtures de test desde baremos reales.
- Auditar valores de baremo sospechosos contra literatura.

**Sin MCP**: tienes que arrancar el backend + Postman, o escribir un script Python ad-hoc cada vez.
**Con MCP**: invocas la herramienta directo desde el chat y Claude obtiene el dato en milisegundos.

## Herramientas expuestas

| Herramienta | Para qué |
|---|---|
| `list_pruebas` | Lista todas las pruebas. Filtros: `poblacion`, `search`, `limit`. |
| `get_prueba` | Detalle de una prueba (tipo_calculo, n_baremos, muestra de claves). |
| `get_baremo_value` | Valor del baremo para una clave específica. |
| `get_baremo_keys` | Lista las primeras N claves del baremo (inspección). |
| `count_pruebas_por_poblacion` | Stats globales del baremo. |
| `get_ajuste_escolaridad` | Ajuste +N PD por escolaridad (Neuronorma AM). |
| `score_prueba` | Aplica el motor de scoring oficial y devuelve el escalar/CI. |

Plus un resource `baremo://stats` con estadísticas en formato leíble.

## Instalación

Ya está hecho. El registro vive en `D:/NeuroSoftApp/.mcp.json` (auto-detectado por Claude Code).

Para reactivarlo manualmente si lo desconectaste:

```json
// D:/NeuroSoftApp/.mcp.json
{
  "mcpServers": {
    "neurosoft-baremos": {
      "command": "D:/NeuroSoftApp/mcp-servers/baremos/venv/Scripts/python.exe",
      "args": ["D:/NeuroSoftApp/mcp-servers/baremos/server.py"]
    }
  }
}
```

Reinicia Claude Code (`Ctrl+Shift+P → Reload Window`) para que detecte cambios.

## Uso

Una vez activo en Claude Code, las herramientas aparecen como:

```
mcp__neurosoft-baremos__list_pruebas
mcp__neurosoft-baremos__get_prueba
mcp__neurosoft-baremos__score_prueba
...
```

Ejemplos de prompts:

> *"Lista todas las pruebas del WISC-IV con sus baremos."*

> *"¿Cuál es el escalar de NiWiscDC para un niño de 16 años 11 meses con PD=53? Verifica contra el Caso 1 ground-truth (debe ser 11)."*

> *"Compárame los baremos de ViTMTA con la literatura más reciente — abre el archivo de baremo y los papers de Neuronorma."*

## Por qué venv separado

El SDK `mcp` arrastra `starlette>=1.0.0` y `pydantic>=2.13`, incompatibles con el venv del backend (`fastapi==0.115.0` requiere `starlette<0.39`). Mantener un venv dedicado evita romper el bundle PyInstaller.

## Re-generación de dependencias

```powershell
cd D:\NeuroSoftApp\mcp-servers\baremos
python -m venv venv
venv\Scripts\pip install mcp
```

## Lectura del baremo

El servidor busca `BD_NEURO_MAESTRA.json` en este orden:
1. `$NEUROSOFT_BAREMO_PATH` (env var)
2. `neurosoft-backend/data/BD_NEURO_MAESTRA.json` (modo dev)
3. `%APPDATA%/NeuroSoft/BD_NEURO_MAESTRA.json` (instalación local del .exe)

Si ninguno existe, falla al arrancar con mensaje explícito.

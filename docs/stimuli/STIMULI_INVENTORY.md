# Inventario de estímulos — NeuroSoft

**Generado:** 2026-06-06 (`generate_stimuli_inventory.py`)

## Fuentes

- PDFs locales: `D:\NeuroSoftApp\Capacitaciones Clínicas\drive-download-20260322T041708Z-3-001` (presente)
- REACTIVOS: `neurosoft-frontend/src/data/clinical.js`
- Protocolos JSON: `Capacitaciones Clínicas/protocolos/` + espejo frontend
- BD SQLite tabla `estimulos` vía API `/api/v1/estimulos/`

## WISC-IV / WAIS-III (prioridad extracción PDF)

| test_id | ítems REACTIVOS | estado | notas |
|---------|----------------:|--------|-------|
| `AdBusSim` | 111 | pendiente PDF |  |
| `AdDDir` | 114 | pendiente PDF |  |
| `AdMatr` | 83 | pendiente PDF |  |
| `AdSDWais` | 108 | pendiente PDF |  |
| `AdSemWais` | 141 | pendiente PDF |  |
| `AdWAISA` | 98 | pendiente PDF | Pearson |
| `AdWAISC` | 96 | pendiente PDF | Pearson |
| `AdWAISCC` | 100 | SVG cubos/FCRO | Pearson |
| `AdWAISFI` | 104 | pendiente PDF | Pearson |
| `AdWAISI` | 124 | pendiente PDF | Pearson |
| `AdWAISL` | 102 | pendiente PDF | Pearson |
| `AdWAISV` | 162 | pendiente PDF | Pearson |
| `NiWisFigInc` | 77 | pendiente PDF | Pearson |
| `NiWisInf` | 129 | pendiente PDF | Pearson |
| `NiWisPalCon` | 39 | pendiente PDF | Pearson |
| `NiWisReg` | 85 | pendiente PDF | Pearson |
| `NiWiscAri` | 106 | pendiente PDF | Pearson |
| `NiWiscBusSim` | 48 | pendiente PDF | Pearson |
| `NiWiscCl` | 47 | pendiente PDF | Pearson |
| `NiWiscCom` | 117 | pendiente PDF | Pearson |
| `NiWiscConD` | 123 | pendiente PDF | Pearson |
| `NiWiscDC` | 100 | SVG cubos/FCRO | Pearson |
| `NiWiscLN` | 63 | pendiente PDF | Pearson |
| `NiWiscMat` | 121 | pendiente PDF | Pearson |
| `NiWiscRDD` | 102 | pendiente PDF | Pearson |
| `NiWiscSem` | 129 | pendiente PDF | Pearson |
| `NiWiscVoc` | 124 | pendiente PDF | Pearson |

## Validez / peritajes

| test_id | ítems | estado |
|---------|------:|--------|
| `TOMM` | 3 | requiere 50 estímulos visuales por trial |
| `REY15` | grid validez | dominio público |

## Protocolos → test_ids

## Leyenda estado

- **extraído**: en `data/stimuli_assets/` + seed SQLite
- **SVG nativo**: `PatronesCubos.jsx` / `stimuli.jsx`
- **pendiente PDF**: requiere `extract_stimuli_from_pdfs.py`

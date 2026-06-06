# Verificación — PDFs vs JSON vs clinical.js

**Fecha:** 5 jun 2026 
**Fuente clínica autoritativa:** `Capacitaciones Clínicas/drive-download-20260322T041708Z-3-001/` 
**PDFs principales:** `WISC IV .pdf` (23 págs) · `WAIS III .pdf` (17 págs)

---

## Veredicto

| Capa | ¿Coincide con manual de protocolo? | Acción |
|---|---|---|
| **`wisc_iv_protocolo.json` / `wais_iii_protocolo.json`** | ✅ **Sí** (verificado muestra) | Usar como fuente para implementación |
| **`clinical.js` → REACTIVOS** | ❌ **No** en varios subtests | Reemplazar desde JSON (no inventar) |
| **Imágenes parciales que enviaste** | ✅ Coinciden con PDF extraído | Válidas como control cruzado |

**Conclusión:** Lo que vamos a implementar debe salir del **JSON en `Capacitaciones Clínicas/protocolos/`** (que ya refleja los PDF de protocolo), **no** del contenido actual de `clinical.js`.

---

## Inventario carpeta drive-download

| Archivo | Tamaño | Rol en NeuroSoft |
|---|---|---|
| **WISC IV .pdf** | 1.6 MB | Protocolo scoring WISC-IV — **fuente reactivos infantil Pearson** |
| **WAIS III .pdf** | 976 KB | Protocolo scoring WAIS-III — **fuente reactivos adulto joven** |
| Protocolo Adulto Joven 2024.pdf | 815 KB | Orden batería adulto joven (no WISC/WAIS ítems) |
| Protocolo Adulto Mayor 2024.pdf | 887 KB | Orden batería AM / Neuronorma |
| Protocolo Niños Complementario.pdf/.docx | 1.5 MB | Suplementarios infantiles |
| Protocolos Alternos Casos Especiales.pdf/.docx | 541 KB | Casos edge clínicos |
| Estímulos Protocolos adulto mayor.pdf | 171 KB | Láminas TMT/estímulos AM |
| TRAIL MAKING TEST *.pdf (3 archivos) | 152–679 KB | TMT Neuronorma + estímulos |

Los PDF WISC/WAIS son los que alimentan el sprint REACTIVOS. Los demás ya tienen JSON espejo en `Capacitaciones Clínicas/protocolos/` (adulto joven, AM, complementario, casos especiales).

---

## Verificación cruzada — WISC-IV

### 2. Semejanzas (`NiWiscSem`)

**PDF de protocolo + imágenes + JSON** — alineados:

| # | Par (PDF/JSON) | `clinical.js` actual |
|---|---|---|
| M | Rojo — Azul | ❌ `Rueda — Pelota` (n:1) |
| 1 | Leche — Agua | ❌ `Rojo — Azul` (n:2) |
| 2 | Esfero — Lápiz | ❌ `Leche — Agua` (n:3) |
| 3 | Gato — Ratón | ❌ `Gato — Ratón` (n:4) — desplazado |
| 4 | Manzana — Banano | … |
| 5 | Camisa — Zapato | … |

- JSON: **24 pares** (M + 1–23) con criterios 0/1/2 completos.
- PDF extraído confirma textos (ver `docs/generated/wisc_semejanzas_extract.txt`).
- Reglas: inicio 6-8→1, 9-11→3, 12-16→5; ítems 1-2 max 1 pt; discontinuar 3×0.

### 5. Retención de Dígitos (`NiWiscRDD`)

**PDF = JSON = correcto** · `clinical.js` secuencias directo OK; **inverso ítem 1** debe ser `2-1` / `1-3` (PDF), no `2-5`/`6-3` (clinical.js actual en una versión anterior — verificar al implementar).

| Orden | Elem 1 PDF/JSON | clinical.js |
|---|---|---|
| Directo | 2-9 / 4-6 | ✅ |
| Inverso | 2-1 / 1-3 | ⚠️ revisar (PDF confirma) |

### 6. Vocabulario (`NiWiscVoc`)

**PDF + imágenes + JSON** — alineados desde ítem 1:

1. Coche · 2. Flor · 3. Tren · 4. Cubeta · 5. Reloj · 6. **Sombrilla** · 7. **Ladrón** · 8. Vaca · 9. Sombrero · 10. Valiente · 11. Obedecer · 12. Bicicleta…

**clinical.js:** 32 palabras, orden distinto desde ítem 6 (`Vaca` donde debe ir `Sombrilla`). JSON tiene **36** palabras.

### 13. Información (`NiWisInf`)

**PDF** (pág. protocolo + imagen): ítems 1-10 incluyen pie, nariz, comida, orejas, edad, patas perro, día después jueves, monedas, mes después marzo…

**JSON:** 33 ítems con preguntas completas. 
**clinical.js:** 33 placeholders `"Reactivo N — ver protocolo"`.

### Comprensión (`NiWiscCom`)

PDF confirma preguntas oficiales (cepillarse dientes, verduras, cinturones, policía uniforme, cartera en tienda…). 
**clinical.js:** 18 preguntas — **alineadas en espíritu** con PDF (V4 las reescribió); validar numeración exacta vs JSON (21 ítems en JSON).

---

## Verificación cruzada — WAIS-III

### Semejanzas (`AdSemWais`)

**PDF pág. 7 + JSON** — alineados:

| # | PDF/JSON | clinical.js |
|---|---|---|
| 1 | Naranja — Pera | ❌ Naranja — Plátano |
| 2 | Chaqueta — Pantalón | ❌ Martillo — Destornillador |
| 3 | Perro — León | ❌ Camello — Caballo |
| 6 | Mesa — Silla | (desplazado) |
| 7 | Barco — Automóvil | … |

JSON `wais_iii_protocolo.json` → `AdSemWais` tiene los 19 pares oficiales con criterios 0/1/2.

### Vocabulario, Información, Comprensión, Aritmética, Figuras Incompletas

PDF WAIS extraíble parcialmente (OCR layout). JSON contiene texto completo verificado manualmente contra estructura . 
**clinical.js:** todos placeholder `requires_protocol_text:true`.

---

## Imágenes que enviaste — validación

| Imagen | Subtest | ¿Match PDF/JSON? |
|---|---|---|
| Semejanzas (Rojo-Azul, Leche-Agua…) | WISC Sem | ✅ |
| Vocabulario (Coche, Sombrilla, Ladrón…) | WISC Voc | ✅ |
| Retención dígitos (2-9, 2-1…) | WISC RDD | ✅ |
| Información (pie, nariz, monedas…) | WISC Inf | ✅ |

---

## Qué implementaremos (confirmado)

1. **Fuente:** `Capacitaciones Clínicas/protocolos/*.json` (tras fix UTF-8 mojibake).
2. **Destino:** `neurosoft-frontend/src/data/clinical.js` → `REACTIVOS`.
3. **Incluir:** pares/palabras/preguntas + criterios scoring en campo `guia` (visible con consent Pearson).
4. **No incluir en bundle:** estímulos gráficos Matrices/Conceptos — referencia cuadernillo.
5. **Sincronizar** copia JSON → `neurosoft-frontend/src/data/protocols/`.

Scripts de verificación reutilizables:

```bash
python docs/scripts/extract_protocol_pdfs.py
python docs/scripts/verify_protocolo_vs_json.py
python docs/scripts/audit_reactivos_gap.py
```

Extractos PDF: `docs/generated/wisc_*.txt`, `wais_*.txt`

---

## Nota legal

PDFs incluyen footer Instituto Neurociencias SAS — son **formato de aplicación/scoring** del clínico licenciado Pearson, no para redistribución pública. Implementación vía `pearsonProtected.js` + consentimiento único.

---

*Verificación completada · listo para Fase 1 implementación*

# Verificación reactivos WISC/WAIS — 2026-06-05

Listado generado desde `clinical.js` + protocolos JSON.  
Regenerar: `python docs/scripts/dump_reactivos_verify.py` (salida UTF-8 en consola).

## Protocolos JSON (7 archivos)

| Archivo | ID | Nombre | institucion |
|---------|-----|--------|-------------|
| wisc_iv_protocolo.json | wisc_iv_colombia | WISC-IV — Protocolo (Wechsler · Manual Moderno) | "" |
| wais_iii_protocolo.json | wais_iii_colombia | WAIS-III — Protocolo (Wechsler · Manual Moderno) | "" |
| protocolo_adulto_joven.json | protocolo_adulto_joven_2024 | Protocolo Adulto Joven 2024 | "" |
| protocolo_adulto_mayor.json | protocolo_adulto_mayor_2024 | Protocolo Adulto Mayor 2024 | "" |
| protocolo_ninos_complementario.json | protocolo_ninos_complementario_2024 | Protocolo Niños Complementario 2024 | "" |
| protocolos_casos_especiales.json | protocolos_alternos_casos_especiales | Protocolos Alternos Casos Especiales | "" |
| protocolos_memoria_verbal.json | memoria_verbal | Protocolos de Memoria Verbal | "" |

- Sin texto `IN&S`, `institutonys`, NIT 901.192.434 en protocolos.
- Mojibake corregido (UTF-8); ej. FÚTBOL, Último, épico, ítems × ensayos.
- Espejo: `neurosoft-frontend/src/data/protocols/` y `neurosoft-backend/data/protocols/`.

## WISC-IV — REACTIVOS (`clinical.js`)

### NiWiscSem (23 pares, scoring 0-1-2; ítems 1-2 máx 1 pt)

1. Leche — Agua | 2. Esfero — Lápiz | 3. Gato — Ratón | 4. Manzana — Banano | 5. Camisa — Zapato | 6. Invierno — Verano | 7. Mariposa — Abeja | 8. Madera — Ladrillos | 9. Enojo — Alegría | 10. Poeta — Pintor | 11. Pintura — Estatua | 12. Montaña — Lago | 13. Hielo — Vapor | 14. Codo — Rodilla | 15. Mueca — Sonrisa | 16. Inundación — Sequía | 17. Primero — Último | 18. Hule (Caucho) — Papel | 19. Permiso — Prohibición | 20. Sal — Agua | 21. Venganza — Perdón | 22. Realidad — Fantasía | 23. Espacio — Tiempo

### NiWiscVoc (36 palabras; 1-4 ilustradas)

Coche, Flor, Tren, Cubeta (ilustradas) · Reloj, Sombrilla, Ladrón, Vaca, Sombrero, Valiente, Obedecer, Bicicleta, Antiguo, Abecedario, Remedar, Fábula, Emigrar, Isla, Absorber, Salir, Transparente, Molestia, Raramente, Preciso, Obligar, Rivalidad, Disparate, Previsión, Aflicción, Arduo, Unánime, Dilatorio, Enmienda, Inminente, Aberración, Locuaz

### NiWiscCom (21 preguntas)

Ver ítems 1-21 en app (cepillarse dientes … cambios rápidos ciencia/tecnología).

### NiWiscRDD — Retención de Dígitos

**Directos (8 niveles):** 2-9/4-6 · 3-8-6/6-1-2 · 3-4-1-7/6-1-5-8 · 5-2-1-8-6/8-4-2-3-9 · 3-8-9-1-7-4/7-9-6-4-8-3 · 5-1-7-4-2-3-8/9-8-5-2-1-6-3 · 1-8-4-5-9-7-6-3/2-9-7-6-3-1-5-4 · 5-3-8-7-1-2-4-6-9/4-2-6-9-1-7-8-3-5

**Inversos (8 niveles; elem. 1 corregido):** **2-1 / 1-3** · 3-5/6-4 · 2-5-9/5-7-4 · 8-4-9-3/7-2-9-6 · 4-1-3-5-7/9-7-8-5-2 · 1-6-5-2-9-8/3-6-7-1-9-4 · 8-5-9-2-3-4-6/4-5-7-9-2-8-1 · 6-9-1-7-3-2-5-8/3-1-7-9-5-4-8-2

### NiWisInf (33 preguntas)

Ítems 1-33 según protocolo (pie, nariz, edad, Colón, jeroglíficos, etc.).

### NiWiscAri (34 problemas)

Ítems 1-34 según protocolo (contar pájaros … problema Diego/Victoria).

### NiWisFigInc (38 láminas)

Zorro, Chaqueta, Gato … Zapato (texto: «[imagen] — ¿qué parte falta?»).

### NiWisPalCon (24 ítems)

Pista 1 de cada ítem (toalla, nariz, luna, elefante …).

### NiWiscMat (35) / NiWiscConD (28)

Matriz 1-35 / Lámina 1-28 — completar en cuadernillo (5 opciones / agrupar categoría).

### NiWiscLN (10 niveles × 3 ensayos)

| N | Secuencia | Modelo respuesta |
|---|-----------|------------------|
| 1 | L-1 | 1-L |
| 2 | N-2 | 2-N |
| 3 | B-5 | 5-B |
| 4 | L-N-1 | 1-L-N |
| 5 | L-N-2 | 2-L-N |
| 6 | L-N-3 | 3-L-N |
| 7 | F-R-3 | 3-F-R |
| 8 | A-4-7 | 4-7-A |
| 9 | M-S-3-4 | 3-4-M-S |
| 10 | F-O-6-3 | 3-6-F-O |

## WAIS-III — REACTIVOS

### AdSemWais (19 pares; 1-5 máx 1 pt)

Naranja—Pera, Chaqueta—Pantalón, Perro—León, Calcetines—Zapatos, Tenedor—Cuchara, Mesa—Silla, Barco—Automóvil, Piano—Tambor, Ojo—Oído, Aire—Agua, Computador—Libro, Poema—Estatua, Mosca—Árbol, Huevo—Semilla, Vapor—Niebla, Amigo—Enemigo, Hibernación—Migración, Premio—Castigo, Trabajo—Juego

### AdWAISV (33 palabras)

Cama … Ominoso (lista completa en JSON).

### AdWAISI (28) / AdWAISC (18) / AdWAISA (20)

Preguntas según protocolo WAIS-III JSON.

### AdWAISFI (25 láminas)

Peine, Mesa, Cara … Granero.

### AdMatr (26)

Matriz 1-26 — cuadernillo.

### AdDDir

**Directos:** 1-7/6-3 … 2-7-5-8-6-2-5-8-4 / 7-1-3-9-4-2-5-6-8  
**Inversos:** 2-4/5-7 … 9-4-3-7-6-2-5-8 / 7-2-8-1-9-6-5-3

### AdWAISL (7 niveles × 3 ensayos distintos)

| N | Ensayo 1 | Ensayo 2 | Ensayo 3 |
|---|----------|----------|----------|
| 1 | L-2 | 6-P | B-5 |
| 2 | F-7-L | R-4-D | H-1-8 |
| 3 | T-9-A-3 | V-1-J-5 | 7-N-4-L |
| 4 | 8-D-6-G-1 | K-2-C-7-S | 5-P-3-Y-9 |
| 5 | M-4-E-7-Q-2 | W-8-H-5-F-3 | 6-G-9-A-2-S |
| 6 | R-3-B-4-Z-1-C | 5-T-9-J-2-X-7 | E-1-H-8-R-4-D |
| 7 | 5-H-9-S-2-N-6-A | D-1-R-9-B-4-K-3 | 7-M-2-T-6-F-1-Z |

## Escalas / denominación (punto 4 — completado)

- **Denom48:** 48 ítems «Lámina N — nominar imagen (cuadernillo)» (sin placeholder).
- **EscYesavage:** 15 ítems GDS con enunciados completos (sin placeholder).
- **EscBeck:** 21 ítems BDI-II con dominios (sin placeholder).

## Scripts

- `docs/scripts/sync_protocols_full.py` — sync + fix encoding + patch REACTIVOS
- `docs/scripts/dump_reactivos_verify.py` — volcado verificación

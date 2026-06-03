# Análisis de Cobertura de Tests Clínicos - NeuroSoft

**Fecha:** 2026-05-26
**Total de pruebas en BD_NEURO_MAESTRA.json:** 175
**Pruebas con test automatizado:** 77 (44%)
**Pruebas sin test:** 98 (56%)

## Resumen por Población

### Adulto Mayor (Vi*) - Neuronorma Colombia
**Cubiertas:** 25 pruebas
**Sin cobertura:** 10 pruebas

#### Pruebas SIN cobertura (prioritarias):
1. **ViTMTB** - Trail Making Test B (funciones ejecutivas)
2. **ViFCRO_Tiempo** - Figura Compleja Rey-Osterrieth (tiempo)
3. **ViGroberMC_Dif** - Grober-Buschke (memoria de reconocimiento - discriminabilidad)
4. **ViGroberRT** - Grober-Buschke (tiempo de reacción)
5. **ViMRemRec** - Memoria de trabajo (recuerdo)
6. **ViTLRes** - Torre de Londres (resolución)
7. **ViTLTC** - Torre de Londres (tiempo de ejecución)
8. **ViWCor** - Wisconsin Card Sorting Test (categorías correctas)
9. **ViWEAte** - Wisconsin (errores de atención)
10. **ViWEPer** - Wisconsin (errores perseverativos)

### Adulto Joven (Ad*) - WAIS-III y complementarias
**Cubiertas:** 30 pruebas
**Sin cobertura:** 4 pruebas

#### Pruebas SIN cobertura:
1. **AdTMTA** - Trail Making Test A
2. **AdTMTB** - Trail Making Test B
3. **AdFCRORec** - Figura Compleja Rey-Osterrieth (recuerdo)
4. **AdBusSim + ViBusSim** - Búsqueda de Símbolos

### Infantil (Ni*) - WISC-IV, K-ABC, ENI
**Cubiertas:** 20 pruebas
**Sin cobertura:** 75 pruebas

#### WISC-IV complementarias (prioritarias):
1. **NiWiscBusSim** - Búsqueda de Símbolos
2. **NiWiscConD** - Conocimientos (discontinuación)
3. **NiWiscMat** - Matrices
4. **NiWisFigInc** - Figuras Incompletas
5. **NiWisInf** - Información
6. **NiWisPalCon** - Palabras y Conceptos
7. **NiWisReg** - Registros
8. **NiWISCIndCapGen** - Índice de Capacidad General
9. **NiWISCIndCopCog** - Índice de Competencia Cognitiva

#### K-ABC (Kaufman Assessment Battery for Children):
10. **NiKABCCITot** - CI Total
11. **NiKABCIndEsc** - Índice Escalar
12. **NiKABCIndSec** - Índice Secuencial
13. **NiKABCIndSim** - Índice Simultáneo
14. **NiKabcCG** - Composición Global
15. **NiKabcMAna** - Memoria Analógica
16. **NiKabcMEsp** - Memoria Espacial
17. **NiKabcMMa** - Memoria de Matrices
18. **NiKabcOPa** - Ordenamiento de Palabras
19. **NiKabcRC** - Razonamiento Conceptual
20. **NiKabcRN** - Razonamiento Numérico
21. **NiKabcSFot** - Series de Fotos
22. **NiKabcTria** - Triángulos
23. **NiKabcVMag** - Vocabulario de Magos
24. **NiKabcTria** - Triángulos

#### ENI (Evaluación Neuropsicológica Infantil):
25-40. **NiENI*** - 16 subpruebas de ENI (dibujo, letras, memoria, etc.)

#### Otras infantiles:
41. **NiComp** - Comprensión
42. **NiCopTxt** - Copia de Texto
43. **NiDR** - Dibujo de Rey
44. **NiEADAL** - Escala de Desarrollo (adaptativa)
45. **NiEADMF/MG/PS/Tot** - Escala de Desarrollo (varios)
46. **NiFA** - Fluencia Alternante
47. **NiFCROCop** - Figura Compleja (copia)
48. **NiFCRORec** - Figura Compleja (recuerdo)
49. **NiFM** - Fluencia de Movimientos
50. **NiIntObj** - Inteligencia de Objetos
51. **NiLVS** - Letra y Vocabulario de Signos
52. **NiPrec** - Precisión
53. **NiRDD** - Recuerdo de Dígitos
54. **NiRecEmo** - Reconocimiento de Emociones
55. **NiSpenceGA/PIF/SA/SepAx** - Spence (subescalas)
56. **NiSt_Edades/Puntajes** - Stroop (versiones)
57. **NiTMTB** - Trail Making Test B
58. **NiVin** - Vineland

### Escalas y Otras
**Sin cobertura:** 9 pruebas

1. **Denom48** - Denominación de 48 objetos
2. **EscKertesz** - Escala de Kertesz (afasia)
3. **EscQueja** - Escala de Queja Subjetiva
4. **EscYesavage** - Yesavage (depresión geriátrica - versión alternativa)
5. **FluidAnim** - Fluencia de Animales
6. **FluidP** - Fluencia de Palabras
7. **GBTotal** - Grober-Buschke Total
8. **GoNoGoICO** - Go/No-Go (control inhibitorio)
9. **InstrConflICO** - Instrucciones Conflictivas
10. **OrDNpsi** - Orden Neuropsicológica
11. **OrSD** - Orden Simples/Dobles
12. **OrTMTA/OrTMTB** - Orden TMT
13. **RefranesICO** - Refranes
14. **SDMT** - Symbol Digit Modalities Test
15. **StroopAM** - Stroop Adulto Mayor

## Prioridades de Implementación

### PRIORIDAD 1 - Críticas (uso clínico frecuente)
1. **ViTMTB** - Complemento de ViTMTA (ya cubierta)
2. **AdTMTA/AdTMTB** - TMT completo para adulto joven
3. **NiTMTB** - TMT completo para infantil
4. **ViWCor/ViWEAte/ViWEPer** - Wisconsin completo
5. **NiWISCIndCapGen/NiWISCIndCopCog** - Índices WISC-IV alternativos

### PRIORIDAD 2 - Importantes (batería estándar)
6. **ViGroberMC_Dif** - Discriminabilidad Grober
7. **ViTLRes/ViTLTC** - Torre de Londres completo
8. **AdFCRORec** - Recuerdo Figura Rey
9. **NiWiscBusSim** - Búsqueda de Símbolos WISC-IV
10. **EscKertesz** - Evaluación de afasia

### PRIORIDAD 3 - Complementarias
11. K-ABC completo (15 subpruebas)
12. ENI completo (16 subpruebas)
13. Stroop variantes (StroopAM, NiSt_*)
14. Otras escalas (Denom48, EscQueja, etc.)

## Verificación de Baremos vs Literatura

### Fuentes de referencia:
1. **Neuronorma Colombia** (Ostrosky-Solís et al., 2010)
   - Adulto Mayor: todas las pruebas Vi*
   - Verificar: rangos de edad, ajustes por escolaridad

2. **WISC-IV Colombia** (Wechsler, 2014 - adaptación colombiana)
   - Infantil: todas las pruebas NiWisc*
   - Verificar: baremos por edad (6-16 años)

3. **WAIS-III** (Wechsler, 1997)
   - Adulto Joven: todas las pruebas AdWAIS*
   - Verificar: rangos de edad (16-89 años)

4. **K-ABC** (Kaufman & Kaufman, 1983)
   - Infantil: todas las pruebas NiKabc*
   - Verificar: baremos por edad

### Acciones requeridas:
1. ✅ Crear tests para PRIORIDAD 1 (10 pruebas)
2. ⏳ Verificar baremos vs literatura publicada
3. ⏳ Crear tests para PRIORIDAD 2 (5 pruebas)
4. ⏳ Crear tests para PRIORIDAD 3 (resto)

## Conclusiones

- **Cobertura actual:** 44% (aceptable pero mejorable)
- **Pruebas críticas sin test:** 5 (ViTMTB, AdTMTA/B, NiTMTB, Wisconsin)
- **Riesgo:** Si cambia un baremo sin test, el error pasa a producción
- **Recomendación:** Alcanzar 80% de cobertura antes de próximo release

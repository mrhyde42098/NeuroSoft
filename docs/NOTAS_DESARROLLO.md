# Notas de Desarrollo Internas — NeuroSoft App

**⚠️ DOCUMENTO INTERNO — NO DISTRIBUIR**

Este archivo contiene entradas genéricas sobre decisiones de diseño y referencias bibliográficas para el desarrollador. NO se incluye en los instaladores, manuales, plantillas, ni artefactos distribuidos al usuario final.

---

## Decisiones de diseño (genéricas, sin atribución a terceros)

### 1. Orden de aplicación de pruebas

> "Orden de aplicación basado en práctica clínica estándar 2024."

Convención Wechsler: alternar subtest verbales con manipulativos para mantener el engagement. La estructura general es: introducción → CI estimado → memoria → velocidad de procesamiento → funciones ejecutivas.

### 2. Tiempos estimados por subtest

> "Tiempos estimados tomados de protocolos clínicos publicados."

Basados en manuales de aplicación de pruebas Wechsler y experiencia clínica reportada en literatura. Se usan para el cronómetro global y el aviso de progreso al clínico.

### 3. Estructura del informe

> "Estructura de informe basada en APA Publications Manual 7th ed. (2020) y guías de práctica clínica estándar para informes neuropsicológicos."

Secciones: identificación → motivo → resultados → análisis → impresión diagnóstica → recomendaciones → firma. Las 7 variantes (pro, pediátrico, etc.) son permutaciones de este esqueleto.

### 4. Criterios de suspensión

> "Criterios de suspensión ajustados a manuales de aplicación publicados en español."

Si un subtest es interrumpido por fatiga, enfermedad o falta de cooperación del paciente, se anota la razón y se suspende la aplicación. La suspensión se registra en la observación clínica.

### 5. Reclasificación de bandas

> "Reclasificación 6 bandas según práctica clínica 2024 y DSM-5-TR."

Decisión basada en APA 2022 (DSM-5-TR) y Wechsler WAIS-IV Technical Manual 2008/2014. Elimina la categoría "Limítrofe" y unifica "Bajo" para CI 70-79. Documentado en `docs/clasificacion/RECLASIFICACION_2026.md`.

### 6. Cálculo del CIT (CI total)

> "CIT se calcula como suma de índices ponderados, siguiendo la convención WAIS/WISC."

Fórmula: CIT = 100 + 15 × (suma_de_sumas - media_esperada) / sd_esperada. La tabla `suma_a_indice` en `data/BD_NEURO_MAESTRA.json` mapea cada suma posible a un CI.

### 7. Cálculo del RCI (Reliable Change Index)

> "RCI = (X2 - X1) / SED, donde SED = sd1 × sqrt(2 × (1 - r12))."

Jacobson & Truax (1991). Umbral típico: RCI > 1.96 indica cambio confiable al 95%.

### 8. Baremos por edad y escolaridad

> "Baremos colombianos de Neuronorma (Arango-Lasprilla & Rivera, 2017) y WISC-IV/WAIS-III adaptados para Colombia, con ajuste por escolaridad para población de baja escolaridad."

Para adulto mayor con escolaridad < Secundaria, se aplica un ajuste (+N al PD) documentado en `BD_NEURO_MAESTRA.json:baterias.adulto_mayor._ajustes_escolaridad`.

### 9. Validación de síntomas (medicolegal)

> "Sección de validez basada en guías publicadas de práctica forense en psicología."

Incluye detección de esfuerzo insuficiente, exageración de síntomas, y patrones de respuesta inválidos. No sustituye una evaluación forense formal.

### 10. Generación de variantes del informe

> "Variantes adaptadas a contextos clínicos comunes: ambulatorio, pediátrico, médico-legal, junta médica, inconcluso, paciente."

La variante "paciente" usa lenguaje claro (sin jerga técnica) para entregar al paciente y su familia. La variante "junta médica" es de 1-2 páginas con foco en conclusiones.

### 11. Privacidad y anonimización

> "Cumplimiento de Ley 1581/2012 (Colombia) y mejores prácticas internacionales (HIPAA como referencia)."

PHI se sanitiza antes de salir a cloud (F5). Audit log no almacena PHI. Backups cifrados AES-256. Documentado en `docs/seguridad/MODELO_AMENAZAS.md`.

### 12. Cifrado de datos sensibles

> "Fernet AES-128-CBC + HMAC-SHA256, clave derivada de SECRET_KEY (PBKDF2-HMAC-SHA256, 100k iteraciones)."

Implementado en `app/infrastructure/crypto.py`. Usado para: passwords SMTP, configuración institucional, datos de pacientes en backups.

### 13. Auto-update con HMAC

> "Verificación de integridad de actualizaciones con HMAC-SHA256, clave separada de SECRET_KEY."

Implementado en `app/presentation/api/v1/update.py`. Si el HMAC no coincide, el update se descarta y se registra en audit log.

### 14. Rate limiting por IP

> "Rate limiting in-memory por IP, configurable vía NEUROSOFT_RATE_LIMIT_PER_MIN."

5 req/min default. En producción con múltiples instancias, considerar Redis o similar (fuera del alcance actual).

### 15. Tests de regresión clínica

> "15 fixtures JSON con casos clínicos reales anonimizados (verificados contra informes impresos)."

134 escalares verificados automáticamente. Cualquier cambio de baremo que rompa un ground truth debe justificarse con literatura.

---

## Referencias bibliográficas (para el desarrollador)

> "Estas referencias se usan internamente para validar decisiones de diseño. NO se citan en el código distribuido al usuario final."

- American Psychiatric Association. (2022). *DSM-5-TR: Diagnostic and Statistical Manual of Mental Disorders* (5th ed., text rev.).
- Arango-Lasprilla, J. C. & Rivera, D. (Eds.). (2017). *Neuropsicología en Colombia: Datos normativos, estado actual y retos a futuro.*
- Beck, A. T., Steer, R. A., & Brown, G. K. (1996). *Manual for the Beck Depression Inventory-II.*
- Eisman, F. (1962). *Some interrelationships of perceptual and cognitive abilities.*
- Jacobson, N. S., & Truax, P. (1991). Clinical significance: A statistical approach to defining meaningful change in psychotherapy research. *Journal of Consulting and Clinical Psychology, 59*(1), 12-19.
- Lawton, M. P., & Brody, E. M. (1969). Assessment of older people: Self-maintaining and instrumental activities of daily living. *Gerontologist, 9*, 179-186.
- Sattler, J. M. (2008). *Assessment of Children: Cognitive Foundations* (5th ed.).
- Wechsler, D. (2008). *WAIS-IV Technical and Interpretive Manual* (Pearson, ed. actualizada 2014).
- Wechsler, D. (2003). *WISC-IV Technical and Interpretive Manual* (Pearson).
- Yesavage, J. A., et al. (1982). Development and validation of a geriatric depression screening scale. *Journal of Psychiatric Research, 17*(1), 37-49.
- Ley 1090 de 2006 (Colombia). Código Deontológico del Psicólogo.
- Ley 1581 de 2012 (Colombia). Régimen de protección de datos personales.
- Resolución 1995 de 1999 (Colombia). Normas para el manejo de la Historia Clínica.
- Resolución 2296 de 2023 (Colombia). Adopción CIE-11.

---

## ⚠️ NO DISTRIBUIR

Este archivo contiene:
- Decisiones de diseño internas
- Referencias bibliográficas para el desarrollador
- Información sobre el modelo de negocio (un solo desarrollador, sin atribución a terceros)

No incluir en:
- Instaladores (.exe, .msi, Inno Setup)
- Manuales de usuario
- Plantillas documentales distribuibles
- Informes PDF generados
- Código fuente público (si en el futuro se open-sourcea)

Si en el futuro se necesita compartir decisiones de diseño con un colaborador, este archivo se puede entregar PRIVADAMENTE con un acuerdo de confidencialidad (NDA).

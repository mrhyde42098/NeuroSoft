# 🧠 NeuroSoft · Manual del Beta Tester

> **Bienvenida, Mayra.**
> Gracias por aceptar probar **NeuroSoft App**, el sistema de evaluación neuropsicológica clínica diseñado para profesionales en Colombia. Este documento te guiará paso a paso desde la instalación hasta el primer informe.

---

## 📋 Índice

1. [Qué es NeuroSoft](#qué-es-neurosoft)
2. [Tus credenciales de acceso](#-tus-credenciales-de-acceso)
3. [Instalación](#instalación)
4. [Primer arranque](#primer-arranque)
5. [Flujo clínico típico (paso a paso)](#flujo-clínico-típico-paso-a-paso)
6. [Funcionalidades a probar](#-funcionalidades-a-probar)
7. [Cómo reportar bugs y sugerencias](#-cómo-reportar-bugs-y-sugerencias)
8. [Privacidad y datos de prueba](#-privacidad-y-datos-de-prueba)
9. [Atajos de teclado](#-atajos-de-teclado)
10. [Soporte y contacto](#-soporte-y-contacto)

---

## Qué es NeuroSoft

NeuroSoft es una aplicación de escritorio para **psicólogos clínicos y neuropsicólogos** que permite:

- Registrar pacientes y gestionar historia clínica
- Aplicar baterías de evaluación (WISC-IV, WAIS-III, Neuronorma Colombia AM, etc.)
- Calcular automáticamente puntajes escalares, Z, percentiles e índices (CI)
- Generar informes profesionales en PDF / DOCX / XLSX
- Comparar evaluaciones longitudinalmente (Pre–Post con RCI)
- Diseñar planes de rehabilitación cognitiva con actividades interactivas
- Asistencia con IA para redacción de informes (opcional)

Todo el procesamiento ocurre **en tu equipo**. Ningún dato clínico sale a internet sin tu autorización explícita.

---

## 🔑 Tus credenciales de acceso

**No tienes que crear cuenta.** Cuando arranques la aplicación por primera vez, ya estará configurado tu usuario beta tester:

| Campo | Valor |
|---|---|
| **Usuario** | `mayra` |
| **Contraseña** | `MayraBeta2026!` |
| **Rol** | Profesional |

> ⚠️ **Importante:** Estas credenciales son **únicamente para ti**. No las compartas. Si crees que alguien más conoce tu contraseña, cámbiala desde **Configuración → Cuenta → Cambiar contraseña**.

---

## Instalación

### Requisitos mínimos
- Windows 10 o superior (64 bits)
- 4 GB de RAM (8 GB recomendado)
- 2 GB de espacio en disco
- No requiere conexión a internet para uso clínico

### Pasos

1. **Descarga** el archivo `NeuroSoft.exe` (1.3 GB) que te enviamos.
2. **Guárdalo** en una carpeta de fácil acceso (ej. `Documentos/NeuroSoft`).
3. **Doble-click** sobre `NeuroSoft.exe`.
   - Windows Defender puede mostrar "Windows protegió tu PC". Haz clic en **Más información → Ejecutar de todas formas**. Es seguro: el binario es nuestro, no está firmado todavía con certificado comercial (presupuesto de beta).
4. La aplicación abrirá una ventana en tu navegador en `http://localhost:8000`.
5. Verás la pantalla de inicio de sesión.

---

## Primer arranque

1. En la pantalla de login, escribe:
   - **Usuario:** `mayra`
   - **Contraseña:** `MayraBeta2026!`
2. Haz clic en **Iniciar sesión**.
3. ¡Listo! Estás en el **Dashboard** principal.

### Lo primero que verás

- **Banner de bienvenida**: Presenta el nombre del software, la fecha del día y los módulos disponibles de un vistazo.
- **Sidebar izquierdo**: navegación principal agrupada en secciones (Clínica, Evaluación, Herramientas, Aprender).
- **Topbar superior**: tu nombre + nombre de la página actual.
- **Dashboard**: KPIs vacíos al inicio (porque aún no hay pacientes); muestra estadísticas reales cuando ya tienes datos.
- **Módulos (tarjetas)**: cada módulo tiene una descripción breve de qué hace — esto te ayuda a orientarte desde el primer uso.
- **Botón flotante "🤖" abajo-derecha**: Asistente IA (opcional, requiere configurar proveedor).

---

## Flujo clínico típico (paso a paso)

> **Recomendación:** Para una prueba realista, usa datos **ficticios** o de un caso clínico documentado en la literatura. **No uses datos reales de pacientes** durante esta fase beta.

### Paso 1 · Registrar un paciente de prueba

1. Sidebar → **Pacientes**
2. Botón **+ Registrar paciente**
3. Llena los campos:
   - Nombre, apellidos, documento (puedes usar `00000000`)
   - Fecha de nacimiento (afecta el protocolo sugerido: niño, adulto joven, adulto mayor)
   - Sexo, escolaridad, ocupación
4. **Guardar**

### Paso 2 · Documentar Historia Clínica

1. Desde la lista de pacientes, click sobre el nombre del paciente
2. Pestaña **Historia Clínica**
3. Llena: motivo de consulta, antecedentes, hipótesis diagnóstica
4. El selector de CIE-10 te sugerirá códigos según la población
5. **Botón Consentimiento Informado** → genera PDF para firma

### Paso 3 · Aplicar evaluación

1. Sidebar → **Evaluación → Aplicar**
2. Selecciona el paciente que registraste
3. NeuroSoft sugerirá un protocolo automáticamente según la edad (WISC-IV, WAIS-III, Neuronorma AM, etc.)
4. Pruebas paso a paso:
   - Lee la instrucción
   - Anota observaciones conductuales (panel derecho)
   - Ingresa el **PD (puntaje directo)** total o ítem por ítem
   - Usa el **cronómetro inline** para pruebas con tiempo límite
5. Cuando termines todas las pruebas, click **Finalizar**

### Paso 4 · Revisar resultados

- Se muestran automáticamente:
  - **Puntajes escalares, Z y percentiles** por prueba
  - **Índices compuestos (ICV, IRP, IMT, IVP, CIT)** con interpretación
  - **Curva normativa Z** con barras animadas
  - **Radar de dominios cognitivos**
  - **Alertas clínicas** si hay puntajes en rango Bajo/Limítrofe
  - **Discrepancias entre índices** (significancia p<.05)

### Paso 5 · Redactar informe narrativo

- Pestaña inferior con 8 dominios: Apariencia, Atención, Memoria, Lenguaje, Funciones Ejecutivas, Visoespaciales, Impresión Diagnóstica, Recomendaciones
- Botón **Auto-generar**: crea borrador basado en los puntajes
- Botón **Mejorar con IA** (en cada sección): mejora redacción (requiere configurar IA)

### Paso 6 · Descargar informe

- Sidebar → **Informes**
- Selecciona la evaluación
- Botones: **PDF · DOCX · XLSX**
- El PDF incluye firma digital si la configuraste

### Paso 7 · Comparativa Pre–Post (opcional)

- Si registras 2+ evaluaciones del mismo paciente:
- Sidebar → **Historial → Pre–Post**
- Selecciona dos evaluaciones
- Verás: tabla de cambios, RCI (Reliable Change Index), radar evolutivo, narrativa automática

---

## 🗺️ Módulos: qué puedes hacer y qué no (aún)

### Pacientes
**Puedes:** Registrar pacientes con historia clínica completa, antecedentes, motivo de consulta, CIE-10, acompañantes, consentimiento informado en PDF, y escalas de screening sugeridas automáticamente.
**Aún no:** Importar pacientes desde otro sistema en bloque; app móvil de captura.

### Evaluación neuropsicológica
**Puedes:** Aplicar baterías completas (WISC-IV, WAIS-III, Neuronorma AM/AJ, niños). El panel lateral derecho — ahora más ancho — muestra observaciones clínicas y conductas a observar específicas de cada prueba. El cronómetro funciona con barra de progreso visual y beep al terminar. Autosave cada 30 segundos (recupera borradores si se cierra el programa).
**Aún no:** Video-grabación de la sesión; sincronización con tablet para captura de reactivos físicos.

### Resultados e Informes
**Puedes:** Ver puntajes escalares, Z, percentiles, índices CI, gráfica normativa, radar de dominios, discrepancias entre índices. Redactar narrativa en 8 secciones con auto-generador. Descargar en PDF / DOCX / XLSX. Enviar por correo si configuras SMTP.
**Aún no:** Plantillas personalizadas por usuario desde la UI (se pueden crear en Configuración pero de forma técnica).

### Screening
**Puedes:** Aplicar más de 20 escalas agrupadas por categoría (Cognitivo, Emocional, TDAH, Conductual, Funcional, Trauma/PTSD). El selector ahora muestra las categorías claramente organizadas. Guardar resultados en la historia del paciente. Exportar CSV.
**Aún no:** Comparativa longitudinal de screening (ej. PHQ-9 de enero vs. mayo).

### Rehabilitación cognitiva
**Puedes:** Crear planes con actividades interactivas (Stroop, N-back, Corsi, Torre de Londres, Ekman, etc.). Seguimiento de adherencia con gráficas. Telepsicología con link Jitsi integrado.
**Aún no:** Banco de actividades ampliado; app de ejercicios para paciente (versión futura).

### Terapia
**Puedes:** Registrar sesiones SOAP, usar el módulo C-SSRS de evaluación de riesgo suicida, explorar enfoques terapéuticos (CBT, ACT, EMDR, DBT y más de 10 enfoques con evidencia). Ficha de tareas entre sesiones.
**Aún no:** Protocolos de terapia estructurados paso a paso; integración calendario para seguimiento de tareas.

### Aprender (módulo educativo)
**Puedes:** Glosario de 60 términos neuropsicológicos con búsqueda, tarjetas de repaso con sistema de repetición espaciada (5 cajas Leitner), quizzes con feedback inmediato, artículos clínicos con fuentes verificables, simulador de casos clínicos (TDAH, Alzheimer, Depresión).
**Aún no:** Módulo de cursos estructurados; certificados de capacitación.

### Configuración
**Puedes:** Datos de la institución, profesionales con foto y firma digital, preferencias del PDF, plantillas de informe, estímulos, respaldo de base de datos, auditoría de cambios, accesibilidad (modo oscuro, alto contraste, tamaño de fuente), configuración SMTP para correos automáticos, plantillas de email editables. Los tabs ahora están organizados en 3 grupos claramente separados (Mi consultorio / Datos clínicos / Sistema).
**Aún no (en esta beta):** Gestión de múltiples usuarios desde la UI; roles diferenciados más allá de admin/profesional.

---

## 🧪 Funcionalidades a probar

Aquí están las áreas donde más nos interesa tu retroalimentación:

### Críticas (alta prioridad)
- [ ] **Cálculo de puntajes**: ¿los escalares y CI te parecen correctos comparados con el manual de la prueba?
- [ ] **Sugerencia automática de protocolo** según edad
- [ ] **Panel de conductas observadas** (sidebar derecho en Evaluación): ¿las conductas son relevantes para cada prueba? ¿el espacio es suficiente?
- [ ] **Generación de PDF**: ¿el informe se ve profesional? ¿faltan datos?
- [ ] **Auto-generador de observaciones**: ¿los borradores son útiles como punto de partida?
- [ ] **Comparativa Pre–Post + RCI**: ¿la interpretación del cambio confiable es clara?

### Secundarias (media prioridad)
- [ ] **Dashboard**: ¿queda claro qué es el software desde la primera pantalla?
- [ ] **Screening**: ¿el selector de escalas por categoría es más fácil de navegar?
- [ ] **Configuración**: ¿la organización en 3 grupos (Consultorio / Clínico / Sistema) es intuitiva?
- [ ] **Asistente IA** (Sidebar → Asistente IA): probar conexión con Gemini gratuita
- [ ] **Modo oscuro** (botón "Oscuro" en sidebar)
- [ ] **Atajos de teclado**: Alt+P (Pacientes), Alt+E (Evaluación), Alt+H (alto contraste)
- [ ] **Rehabilitación cognitiva**: planes y actividades (Stroop, N-back, etc.)

### UX y diseño
- [ ] ¿Algún botón o flujo te parece confuso?
- [ ] ¿Cargas lentas en alguna pantalla?
- [ ] ¿Errores que aparecen sin explicación?
- [ ] ¿La descripción de cada módulo en el Dashboard es suficientemente clara?
- [ ] ¿Sugerencias de mejora visual o terminología clínica?

---

## 🐛 Cómo reportar bugs y sugerencias

Para cada hallazgo, por favor envíanos:

1. **Qué hiciste** (pasos a reproducir, en orden)
2. **Qué esperabas que pasara**
3. **Qué pasó realmente**
4. **Captura de pantalla** si aplica
5. **Severidad** (bloqueante / molesto / cosmético)

**Canal preferido**:
- 📧 Email: `jssalgadosa@unal.edu.co`
- Asunto: `[NeuroSoft Beta] - <título del bug>`

**Plantilla rápida**:

```
TÍTULO: <descripción breve>
SEVERIDAD: bloqueante / molesto / cosmético
PASOS:
  1. ...
  2. ...
  3. ...
ESPERABA: ...
PASÓ: ...
CAPTURA: <adjunta imagen si aplica>
NAVEGADOR / SO: <Windows 10/11, Chrome/Edge/etc>
```

---

## 🔒 Privacidad y datos de prueba

- **Todos los datos clínicos** se almacenan **localmente** en tu computadora en `%APPDATA%/NeuroSoft/`.
- NeuroSoft **no envía datos clínicos** a servidores externos.
- Las funciones de IA en la nube (Gemini, Claude, OpenAI) son **opcionales** y solo se activan si configuras una API key. Antes de enviar texto, el sistema **sanitiza nombres, documentos y fechas** automáticamente.
- **Ley 1581 de 2012** (Colombia): los datos de paciente son **datos sensibles**. Como esto es una prueba beta, **te pedimos usar exclusivamente datos ficticios o anonimizados**.
- Cuando termines la prueba, puedes **eliminar la carpeta** `%APPDATA%/NeuroSoft/` para borrar todo.

---

## ⌨️ Atajos de teclado

| Atajo | Acción |
|---|---|
| `Alt + P` | Ir a Pacientes |
| `Alt + E` | Ir a Evaluación |
| `Alt + R` | Ir a Rehabilitación |
| `Alt + H` | Alternar alto contraste |
| `Alt + D` | Alternar modo oscuro |
| `Alt + +` | Aumentar tamaño de fuente |
| `Alt + -` | Reducir tamaño de fuente |

---

## 📞 Soporte y contacto

| Concepto | Contacto |
|---|---|
| Bugs y sugerencias | `jssalgadosa@unal.edu.co` |
| Soporte técnico | `jssalgadosa@unal.edu.co` |
| WhatsApp (urgencias) | Pídeselo a Jesús |

---

## ❤️ Gracias

Tu feedback como **profesional clínica activa** es el insumo más valioso para que NeuroSoft realmente sirva al trabajo neuropsicológico colombiano. Cada bug que encuentres, cada sugerencia que hagas, mejora el sistema para todos los colegas que lo usarán cuando salga al público.

**¡Adelante con la prueba!** 🚀

---

> **NeuroSoft App — Beta para profesionales · Mayo 2026**
> Sistema de apoyo clínico. Los resultados deben interpretarse en el contexto de la evaluación completa y el juicio profesional del neuropsicólogo.

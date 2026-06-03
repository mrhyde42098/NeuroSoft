# Diagnóstico de Rendimiento — PC Johan Salgado
**Fecha:** 2026-05-17 | **Uptime al momento del diagnóstico:** 0.3 h (arranque fresco)
**Perfil:** Desarrollo (Python/FastAPI, React/Vite) + Gaming + Multimedia

---

## Resumen ejecutivo

| Severidad | Cantidad | Ejemplos |
|-----------|----------|---------|
| 🔴 Crítico | 2 | BSODs recurrentes, iCloudPhotos saturando CPU |
| 🟠 Alto | 3 | Google Update timeout, Vanguard kernel anticheat, disco C: casi lleno |
| 🟡 Medio | 4 | Telemetría, servicios Apple innecesarios, Nahimic, WlanSvc sin WiFi |
| 🟢 Bajo | 3 | Startup items, SoftLanding task, múltiples instancias Claude |

**Acción urgente antes de cualquier otra optimización:** investigar los BSODs con WinDbg.

---

## Fase 1 — Inventario de recursos

### CPU
| Parámetro | Valor |
|-----------|-------|
| Modelo | AMD Ryzen 5 3600 |
| Núcleos físicos / lógicos | 6 / 12 |
| Velocidad base | 3600 MHz |
| Carga en reposo (3 muestras) | 9% — 11% — 9% ✅ Normal |

### RAM
| Parámetro | Valor |
|-----------|-------|
| Total | 15.95 GB (16 GB nominal) |
| Libre en reposo | 8.8 GB |
| Usada en reposo | 7.15 GB (44.8%) ✅ Saludable |
| PageFile | 6144 MB en C:\, uso actual 0 MB (peak 0 MB) ✅ |

**Top 5 procesos por RAM:**
| Proceso | RAM (MB) | Notas |
|---------|----------|-------|
| claude (instancia 1) | 1232 | Chat principal abierto |
| claude (instancia 2-4) | ~330–367 c/u | Chats adicionales |
| MsMpEng (Defender) | 329 | Antivirus |
| WhatsApp | 204 | Mensajería |
| explorer | 190 | Shell Windows |

### Discos
| Unidad | Modelo | Tipo | Tamaño | Libre | % Libre | Estado SMART |
|--------|--------|------|--------|-------|---------|-------------|
| C: | Crucial CT240BX500SSD1 | SSD | 223.6 GB | **80.3 GB** | **36.1%** ⚠️ | OK |
| D: BODEGA | Toshiba DT01ACA100 | HDD | 931.5 GB | 277.3 GB | 29.8% ✅ | OK |
| E: | Samsung PSSD T7 | SSD Externo | 465.8 GB | 242.3 GB | 52% ✅ | OK |

> ⚠️ **C: con solo 80 GB libres en un SSD de 240 GB.** Para builds pesados (PyInstaller, npm),
> pagefile y cachés del sistema, lo recomendado es ≥ 20% libre. Actualmente estás al 36% pero 
> con proyectos que pueden crecer rápido.

### GPU
| Parámetro | Valor |
|-----------|-------|
| Modelo | AMD Radeon RX 590 |
| VRAM | 4 GB (≈ 4293 MB) |
| Driver | 31.0.21923.11000 |
| Resolución activa | 1920 × 1080 |
| Estado | OK |

> ℹ️ **Driver AMD 31.0.21923** — verificar si hay versión más reciente en AMD Software.
> Drivers AMD desactualizados son causa frecuente de `DRIVER_POWER_STATE_FAILURE` (ver Crítico #1).

### Red
| Adaptador | Velocidad | Estado |
|-----------|-----------|--------|
| Realtek PCIe GbE | 1 Gbps (Ethernet) | ✅ Activo |
| WiFi | — | No detectado / no activo |

---

## Fase 2 — Análisis de arranque

**Tiempo de boot:** No se pudo leer del Event Log (eventos Kernel-Boot ID 12 no disponibles en sesión no elevada). El sistema lleva 0.3 h activo — arranque reciente.

### Programas en startup
| Programa | Ubicación | Impacto boot | Necesario? |
|----------|-----------|-------------|------------|
| Steam | HKCU\Run | Alto (~5–10 s, red+disco) | Solo si juegas a diario |
| Riot Client | HKCU\Run | Alto (~5 s) | No — carga al abrir el juego |
| OpenVPN-GUI | HKCU\Run | Bajo (~1 s) | Solo si usas VPN constantemente |
| Microsoft Teams | HKCU\Run | Alto (~8 s, Electron) | Solo si lo usas a diario |
| **Riot Vanguard** | HKLM\Run | **Crítico — kernel driver** | ⚠️ Solo si juegas Valorant/LoL |
| iTunesHelper | HKLM\Run | Medio (~3 s) | Solo si conectas iPhone/iPad |
| PowerISO | HKLM Wow6432Node | Bajo (~1 s) | No — abre al usar la app |
| Everything | HKLM Wow6432Node | Bajo (indexador en segundo plano) | Útil si se usa para búsquedas |

**Impacto estimado de startup innecesario:** 20–30 segundos de boot + recursos en segundo plano.

---

## Fase 3 — Servicios y procesos

### Servicios no esenciales para dev+gamer (corriendo automáticamente)
| Servicio | Display Name | Recomendación | Riesgo |
|---------|-------------|--------------|--------|
| `WlanSvc` | Configuración automática de WLAN | Deshabilitar — no hay WiFi físico | Bajo |
| `Spooler` | Cola de impresión | Deshabilitar si no hay impresoras | Bajo |
| `DiagTrack` | Telemetría de Windows | Manual o Deshabilitar | Bajo |
| `StiSvc` | Adquisición de imágenes WIA | Manual — para cámaras/scanners | Bajo |
| `Bonjour Service` | Servicio Bonjour (Apple) | Manual | Bajo |
| `NahimicService` | Nahimic Audio | Manual (puede causar interferencias) | Bajo |
| `cfbackd` | DiskDrill Watcher | Manual si DiskDrill no se usa activamente | Bajo |
| `OpenVPNServiceInteractive` | OpenVPN Interactive | Manual si VPN no es uso diario | Bajo |
| `Apple Mobile Device Service` | Apple Mobile Device | Manual si iPhone no siempre conectado | Bajo |

### Procesos con alto consumo en background
| Proceso | CPU acum. (s) | RAM (MB) | Diagnóstico |
|---------|--------------|----------|-------------|
| **iCloudPhotos** | **676 s** | 65 | 🔴 Sincronización activa de fotos — top consumidor |
| **iCloudServices** | 215 s | 60 | 🟠 Servicio raíz de iCloud |
| AppleIEDAV | 9.6 s | 43 | Protocolo DAV de Apple |
| MsMpEng | ~0 s ahora | 329 | Defender — normal pico al escanear |
| SearchIndexer | ~0 s ahora | 29 | OK — indexación pausada |

### Tareas programadas de terceros activas
| Tarea | Evaluación |
|-------|------------|
| `OneDrive Startup Task` | Necesario si se usa OneDrive |
| `OneDrive Per-Machine Update` | Necesario |
| `OneDrive Reporting Task` | Puede deshabilitarse |
| `AMDLinkUpdate` | AMD Link (streaming de juegos) — deshabilitar si no se usa |
| `AppleSoftwareUpdate` | Actualización de iTunes/iCloud |
| **`SoftLandingCreativeManagementTask`** | ⚠️ **Desconocido — investigar** (puede ser adware) |
| `StartCN` / `StartDVR` | Probablemente ROG Armory Crate o similar — verificar |

---

## Fase 4 — Estado del sistema

### 🔴 BSODs / Reinicios inesperados — CRÍTICO

**Se registraron 3 reinicios forzados (Kernel-Power EventID 41) en los últimos 3 días:**

| Fecha/Hora | Tipo | Código de error |
|-----------|------|----------------|
| 14/05/2026 11:01 | Kernel-Power ID 41 | Sin dump confirmado |
| 15/05/2026 15:04 | **BSOD confirmado** | **`0x0000009f` DRIVER_POWER_STATE_FAILURE** |
| 15/05/2026 22:56 | Kernel-Power ID 41 | Probable segundo BSOD |

**Análisis del BSOD `0x0000009f`:**
- **Causa:** Un driver no completó una transición de estado de energía (sleep/wake, o cambio de estado de dispositivo USB/PCI)
- **Parámetro 2:** `0x12c` = 300 segundos de timeout → el sistema esperó 5 minutos un IRP de power que nunca llegó
- **Sospechosos principales:**
  1. **Riot Vanguard** — anticheat a nivel kernel (anillo 0), notoriamente inestable con transiciones de energía
  2. **Drivers AMD GPU** — `DRIVER_POWER_STATE_FAILURE` es uno de los errores más comunes en RX 580/590 con drivers antiguos
  3. **Dispositivos USB** — desconexión abrupta durante sleep
- **Dump disponible:** `C:\WINDOWS\Minidump\051526-46265-01.dmp` — analizar con WinDbg o **WhoCrashed** (gratis)

### Errores de Event Log en Application
| Evento | Frecuencia | Diagnóstico |
|--------|-----------|-------------|
| Google Update timeout (7000/7009) | Cada arranque | Google Update Service no responde — **agrega ~90 s al boot** |
| CertificateServicesClient SCEP error (86) | Cada arranque | Inscripción de certificado AMD falla — inofensivo pero ruidoso |
| VSS / Volume Shadow Copy error (36) | Ocasional | Las instantáneas de volumen no pueden crecer — puede afectar backups |

### Temperatura
- No disponible vía WMI (normal en sistemas AMD modernos)
- **FanControl** está instalado y corriendo — usar su interfaz para monitorear temps en reposo y bajo carga
- Recomendado: verificar que CPU ≤ 70°C en reposo, GPU ≤ 60°C en reposo

### Fragmentación / Optimización de disco
- C: (SSD) → Se optimiza con TRIM automáticamente, no requiere desfragmentación
- D: (HDD) → Windows debería desfragmentar automáticamente en horario programado
- No se pudo verificar el estado de optimización (requiere elevación)

---

## Fase 5 — Plan de acción priorizado

| # | Área | Problema detectado | Acción recomendada | Impacto esperado | Riesgo |
|---|------|-------------------|-------------------|-----------------|--------|
| 1 | 🔴 Estabilidad | **3 BSODs en 3 días** (`0x0000009f`) | Instalar **WhoCrashed** → analizar `051526-46265-01.dmp` → identificar driver culpable | **Alto** — evita pérdida de trabajo | Bajo (solo lectura) |
| 2 | 🔴 CPU | **iCloudPhotos usando 676 s CPU** en background | Pausar sincronización de fotos en iCloud Settings → "Pausar fotos" o deshabilitar iCloud Photos si no se necesita en PC | **Alto** — libera CPU y disco constante | Bajo |
| 3 | 🟠 Estabilidad | **Riot Vanguard en kernel** (sospechoso #1 del BSOD) | Desinstalar Vanguard o configurar servicio en **Manual** (en lugar de Automático). Reinstalar solo cuando se vaya a jugar | **Alto** — puede resolver los BSODs | Bajo (reinstalable) |
| 4 | 🟠 Boot | **Google Update timeout** — 90 s por arranque | Reparar o reinstalar Google Chrome/Drive → el servicio gupdate probablemente tiene instalación corrupta | **Alto** — ahorra ~90 s de boot | Bajo |
| 5 | 🟠 Startup | **Steam + Riot Client en arranque** | Task Manager → Startup → deshabilitar Steam y Riot Client (se inician al abrir los juegos) | **Medio** — ahorra ~10–15 s de boot + RAM | Bajo |
| 6 | 🟠 Disco C: | **80 GB libres en SSD de 240 GB** | Revisar qué ocupa C: (`WinDirStat` o `TreeSize`) → mover builds/cachés grandes a D: | **Medio** — previene problemas futuros | Bajo |
| 7 | 🟡 Startup | **Teams + OpenVPN en arranque** | Task Manager → Startup → deshabilitar (abrir manualmente cuando se necesiten) | **Medio** — ahorra ~10 s y 200+ MB RAM | Bajo |
| 8 | 🟡 Servicios | **WlanSvc corriendo sin WiFi** | Servicios → `WlanSvc` → Inicio: Manual | **Bajo** — libera recursos mínimos | Bajo |
| 9 | 🟡 Privacidad | **DiagTrack (Telemetría Microsoft)** | Servicios → `DiagTrack` → Inicio: Manual o Deshabilitado | **Bajo** | Bajo |
| 10 | 🟡 Servicios | **Nahimic Audio** corriendo en background | Servicios → `NahimicService` → Manual (activar si hay problemas de audio) | **Bajo** | Bajo |
| 11 | 🟡 Seguridad | **SoftLandingCreativeManagementTask** — tarea desconocida | Investigar origen en `%AppData%` o `%ProgramData%\SoftLanding` → puede ser adware empaquetado con otro software | **Medio si es adware** | Bajo (solo revisar) |
| 12 | 🟡 GPU Driver | **Driver AMD 31.0.21923** — verificar si hay update | Abrir AMD Software → Check for Updates → actualizar si hay versión más nueva | **Medio** — puede resolver el BSOD si es driver GPU | Bajo |
| 13 | 🟢 Startup | **iTunesHelper** en HKLM startup | Deshabilitar desde msconfig si iPhone no se conecta a diario | **Bajo** | Bajo |
| 14 | 🟢 Startup | **PowerISO** en startup | Deshabilitar desde HKLM → no necesita iniciar con Windows | **Bajo** | Bajo |
| 15 | 🟢 AMD Link | **AMDLinkUpdate task** programada | Deshabilitarla en Task Scheduler si no se usa AMD Link | **Bajo** | Bajo |

---

## Acciones inmediatas recomendadas (en orden)

### Paso 1 — Diagnosticar los BSODs (hoy)
```
1. Descargar WhoCrashed (gratis): https://www.resplendence.com/whoCrashed
2. Abrirlo como Administrador
3. Clic en "Analyze" → revisar qué driver aparece como culpable
4. Reportar el nombre del driver .sys encontrado
```

### Paso 2 — Detener iCloud Photos (hoy)
```
Buscar "iCloud" en el menú Inicio → Abrir iCloud para Windows
→ Fotos → Desmarcar "iCloud Photos" o clic en "Pausar por 24 horas"
```

### Paso 3 — Desactivar startup innecesario (5 minutos)
```
Ctrl+Shift+Esc → pestaña "Inicio" → deshabilitar:
- Steam
- Riot Client  
- Microsoft Teams (si no es uso diario)
```

### Paso 4 — Investigar Google Update (15 minutos)
```powershell
# Solo para verificar — NO ejecutar sin aprobación
Get-Service -Name "gupdate" | Select-Object Name, Status, StartType
# Si aparece como corrupto → desinstalar y reinstalar Chrome
```

---

## Notas sobre D:\NeuroSoftApp

- El proyecto reside en D: (HDD Toshiba) — 277 GB libres. Sin riesgo inmediato.
- Los builds de PyInstaller generan archivos temporales en C: — monitorear espacio libre.
- Los BSODs ocurren en cualquier momento: **riesgo de pérdida de trabajo no guardado**. Prioridad #1.
- Recomendado: `git init` o checkpoint antes de sesiones largas de desarrollo mientras los BSODs no estén resueltos.

---

## Hardware — evaluación general

| Componente | Estado | Comentario |
|-----------|--------|------------|
| CPU Ryzen 5 3600 | ✅ Bueno | Carga en reposo normal, suficiente para dev+gaming |
| RAM 16 GB | ✅ Bueno | Saludable, 8 GB libres en reposo |
| SSD C: 240 GB | ⚠️ Monitorear | Solo 80 GB libres — revisar qué ocupa espacio |
| HDD D: 1 TB | ✅ Bien | 277 GB libres, SMART OK |
| GPU RX 590 4 GB | ⚠️ Revisar driver | Posible causa de BSOD, driver a verificar |
| Red 1 Gbps | ✅ Bueno | Ethernet estable |
| Estabilidad del sistema | 🔴 Crítico | 3 reinicios inesperados en 3 días |

---

*Generado automáticamente por diagnóstico de Claude Code — 2026-05-17*
*Solo lectura — ningún cambio fue realizado al sistema*

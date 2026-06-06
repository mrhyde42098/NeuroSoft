# Protección de propiedad intelectual y licencias — NeuroSoft

**Propietario:** Johan Salgado (`jssalgadosa@unal.edu.co`)  
**Producto:** NeuroSoft App — software de apoyo neuropsicológico (Ley 1090/2006 art. 36)

---

## 1. Qué controlas tú (administrador) vs. qué controla el cliente

| Capa | Quién la controla | Herramienta en NeuroSoft |
|------|-------------------|--------------------------|
| **Licencia de uso** (beta / trial / perpetua) | Tú generas la clave; el tester la activa offline | `generate_license.py` |
| **Baremos y motor clínico** | Tú en el build; el cliente solo los usa en memoria | `build_protected.py` (AES + Cython) |
| **Código fuente Python/JS** | Solo en tu repo `D:\NeuroSoftApp` | No se distribuye; PyInstaller empaqueta bytecode |
| **Datos clínicos (PHI)** | Profesional + cifrado de disco | BitLocker + `docs/SEGURIDAD_DATOS_CLINICOS.md` |
| **Claves Fernet/JWT del servidor** | Se generan en primer arranque local | `%APPDATA%\NeuroSoft\` — no las compartes |

**No necesitas un software externo de KMS** para la beta cerrada. Ya tienes:

1. **`python generate_license.py`** — GUI para una licencia (nombre, email, tipo, días).
2. **Lote para beta testers:**
   ```powershell
   cd D:\NeuroSoftApp
   python generate_license.py --batch 100 --type beta --out licenses_beta_2026.csv
   ```
3. **`build_protected.py`** — build “duro” con baremos cifrados y módulos críticos en `.pyd` (Cython).

Tu flujo de trabajo **no se rompe**: sigues editando en `D:\NeuroSoftApp`. Solo al entregar al cliente corres `build.py` o `build_protected.py` y envías `NeuroSoft-Setup.exe`.

---

## 2. Modelo de claves (offline, sin internet)

### ¿Cómo funciona?

1. Tú generas una clave `NSFT-XXXX-XXXX-XXXX-XXXX`.
2. El beta tester instala NeuroSoft e ingresa la clave **una vez**.
3. Se guarda en `%APPDATA%\NeuroSoft\license.dat` (atada al `machine_id` del PC).
4. **No se actualiza sola** — no hay servidor de licencias en beta cerrada.

### ¿10.000 claves pregeneradas?

Sí, es válido y recomendable para beta:

```powershell
python generate_license.py --batch 10000 --type beta --prefix BETA2026 --out licenses_beta_2026.csv
```

Tú llevas un Excel/CSV con: índice, nombre asignado, email, clave, fecha de entrega.  
Cuando asignas a alguien, pones su nombre real en tu registro (la clave ya existe).

### Tipos de licencia

| Tipo | Expira | Marca de agua PDF | Uso |
|------|--------|-------------------|-----|
| `trial` | N días (en la clave) | Sí | Demos cortas |
| `beta` | No (revocación manual) | Sí “VERSIÓN BETA” | Beta testers |
| `perpetual` | No | No | Cliente pagador |
| `master` | No | No | Solo Johan (dev) |

### ¿Se pueden “descubrir” las claves?

- Las claves **no están dentro del .exe** — las generas tú fuera.
- En modo desarrollo (sin clave pública RSA embebida) la validación es más laxa; en **producción** el build debe inyectar la clave pública RSA y firmar cada licencia con tu clave privada (solo en tu PC).
- Un atacante avanzado puede extraer bytecode de PyInstaller; **Cython + cifrado de baremos** sube mucho el costo, pero ningún software desktop es 100% irrobable.

---

## 3. Blindaje de baremos y código

### Build estándar (`build.py`)

- Frontend minificado en el .exe.
- Backend empaquetado con PyInstaller.
- Baremos en JSON dentro del bundle (legible con esfuerzo).

### Build protegido (`build_protected.py`) — recomendado antes de beta amplia

| Paso | Qué hace |
|------|----------|
| Cython | `strategies.py`, `engine.py`, `baremos_loader.py`, etc. → `.pyd` (binario nativo) |
| AES-256-GCM | `BD_NEURO_MAESTRA.json` → `.enc`; se descifra solo en RAM al arrancar |
| Limpieza | Elimina `.py` fuente, tests, `.git` del artefacto de build |
| Inno Setup | Instalador con copyright Johan Salgado / jssalgadosa |

**Tu repo de desarrollo nunca se toca** — el script copia a `D:\NeuroSoftApp-FINAL\build\`.

### ¿Dónde aparece tu nombre como desarrollador?

| Lugar | Visible al cliente final | Recomendación |
|-------|--------------------------|---------------|
| Informes PDF | **No** — usa nombre/logo de la clínica (Configuración → Institución) | ✅ |
| Dashboard / app diaria | **No** — marca neutral o nombre de la clínica | ✅ |
| Instalador Windows (Add/Remove Programs) | Sí — copyright legal mínimo | Opcional, recomendado para IP |
| `docs/` y repo de desarrollo | Sí — solo tú lo ves | ✅ |
| Claves de licencia | No llevan tu email | ✅ |

El comprador personaliza: **Configuración → Institución** (nombre, logo, email, pie de informe).

---

## 4. Instalador: disco, carpeta, informes

**Ya implementado en `installer/NeuroSoft.iss`:**

- El usuario elige **disco y carpeta** de instalación (`DisableDirPage=no`).
- Ollama va separado en `{app}\vendor\ollama\` (no dentro del .exe).

**Carpeta de informes PDF:** hoy la define la app en primer uso / Configuración (no el instalador).  
Roadmap: página custom Inno Setup o wizard de primer arranque para `%USERPROFILE%\Documentos\NeuroSoft\Informes`.

---

## 5. Datos clínicos — resumen

Ver `docs/SEGURIDAD_DATOS_CLINICOS.md`:

1. **BitLocker NO es parte de NeuroSoft** — es opcional de Windows; la instalación no lo pide ni lo configura.
2. Backups en `.7z` con contraseña (recomendación para la clínica).
3. `audit_log` append-only (ya en SQLite).
4. Ollama/IA: sanitización PHI antes de enviar texto al modelo local.

SQLCipher (BD cifrada) queda como mejora post-beta — requiere migración y `pysqlcipher3`.

---

## 6. Sección 2 — Vanguardia tecnológica (estado junio 2026)

| Upgrade | Estado | Nota |
|---------|--------|------|
| `busy_timeout=5000` SQLite | ✅ Hecho | `engine.py` |
| orjson baremos | ✅ Hecho | boot más rápido |
| FastAPI 0.115.6 | ✅ Pin conservador | 0.136.x post-beta (riesgo breaking) |
| Lazy load baremos por protocolo | ⏳ Post-beta | requiere refactor loader |
| Vite 6 / React 19 | ⏳ Post-beta | validar PyInstaller + e2e |
| RSA firma en producción | ⏳ Activar en build protegido | generar par de claves una vez |

---

## 7. Checklist antes de enviar a un beta tester

- [ ] `python generate_license.py` → clave tipo **Beta** con nombre/email del tester
- [ ] Build: `python build.py --skip-ollama` + Inno Setup (o `build_protected.py` para máxima protección)
- [ ] Verificar `NeuroSoft.exe` < 100 MB (si pesa ~1.4 GB, Ollama se bundleó mal)
- [ ] Enviar `NeuroSoft-Setup.exe` + clave por canal separado (WhatsApp clave, Drive instalador)
- [ ] Recordar al tester: activar BitLocker; no compartir la clave

---

## 8. Alcance realista (importante)

**Protege bien contra:** copia casual, curiosos, extracción trivial del JSON de baremos, uso sin licencia en beta.

**No protege al 100% contra:** ingeniero inverso dedicado con semanas de tiempo, dump de memoria en runtime, captura de pantalla de reactivos Pearson.

Para baremos con copyright Pearson, la protección legal (licencia de uso, contrato beta, Ley 23/1982 Colombia) complementa la técnica.

**Contacto propiedad intelectual:** jssalgadosa@unal.edu.co

# Seguridad de datos clínicos — NeuroSoft (desktop)

## Cifrado en reposo

NeuroSoft cifra campos puntuales (SMTP, API keys) con **Fernet** derivado de `NEUROSOFT_SECRET_KEY`.  
El archivo SQLite (`neurosoft.db`) **no** usa SQLCipher; contiene PHI completo.

### Recomendación operativa (opcional, no bloquea la instalación)

**BitLocker** es una función **de Windows**, no de NeuroSoft. Muchos equipos ya la traen activada (especialmente portátiles corporativos); otros no. NeuroSoft **no la instala ni la exige** — la app funciona igual con o sin ella.

Si la clínica quiere una capa extra de protección del disco (por ejemplo, si roban el PC apagado), el administrador de TI puede activar:

1. **BitLocker** (Windows Pro/Enterprise) o **FileVault** (macOS) en el disco del sistema.
2. Backups en unidad cifrada o contenedor `.7z` con contraseña fuerte.
3. No copiar `neurosoft.db` a USB sin cifrar.

Esto es responsabilidad del **consultorio o institución**, igual que cerrar con llave la carpeta de historias clínicas en papel.

### Auditoría clínica

La tabla `audit_log` es **append-only** (triggers SQLite impiden UPDATE/DELETE).

## Personalización por clínica

Cada comprador configura su identidad en **Configuración → Institución**:

- Nombre, NIT, dirección, teléfono, email, logo
- Esos datos aparecen en informes PDF, emails y pantalla de activación
- **No** se muestra el nombre del desarrollador al usuario final

## Licencias y propiedad intelectual

Guía para Johan (administrador del producto): **`docs/GUIA_PROTECCION_Y_LICENCIAS.md`**

- Generar claves: `python generate_license.py`
- El copyright del desarrollador queda solo en metadatos del instalador Windows (Add/Remove Programs), no en informes ni dashboard

## SQLCipher (roadmap P1)

Cifrado de volumen SQLite con SQLCipher queda planificado post-beta. Requiere migración de `neurosoft.db` y re-cifrado de backups. Hoy: BitLocker opcional + backups `.7z` con contraseña.
